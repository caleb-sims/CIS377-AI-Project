"""Evaluate a fine-tuned CodeT5 checkpoint with an execution harness.

Usage:
    python evaluate.py
    python evaluate.py --limit 20          # quick smoke test
    python evaluate.py --checkpoint checkpoints/final --beams 1
"""
import argparse, json, statistics, subprocess, sys, tempfile, time
from collections import defaultdict
from pathlib import Path

import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

# ---------------------------------------------------------------- harness
RUNNER = r'''
import json, sys, time, statistics
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
except (ImportError, OSError, ValueError):
    # "resource" is Unix-only; Windows runs without the address-space cap.
    pass
job = json.load(open(sys.argv[1]))
src, name, tests, bench = job["code"], job["name"], job["tests"], job["benchmark"]
sys.setrecursionlimit(5000)
ns = {}
status = None
try:
    exec(src, ns)
    fn = ns[name]
    for t in tests:
        if fn(*json.loads(json.dumps(t["args"]))) != t["expected"]:
            status = "wrong_answer"
            break
except BaseException as e:
    status = type(e).__name__
if status:
    print(json.dumps({"passed": False, "error": status}))
    sys.exit(0)
    
def once():
    args = json.loads(json.dumps(bench["args"]))
    s = time.perf_counter(); fn(*args); return time.perf_counter() - s

try:
    once()
    times = [once() for _ in range(7)]
    print(json.dumps({"passed": True, "time": statistics.median(times)}))
except BaseException as e:
    print(json.dumps({"passed": False, "error": "bench_" + type(e).__name__}))
'''

def run_code(code, ex, timeout=60):
    with tempfile.TemporaryDirectory() as d:
        Path(f"{d}/runner.py").write_text(RUNNER, encoding="utf-8")
        with open(f"{d}/job.json", "w", encoding="utf-8") as f:
            json.dump({"code": code, "name": ex["name"], "tests": ex["tests"],
                       "benchmark": ex["benchmark"]}, f)
        try:
            r = subprocess.run([sys.executable, f"{d}/runner.py", f"{d}/job.json"],
                               capture_output=True, text=True, timeout=timeout)
            return json.loads(r.stdout.strip().splitlines()[-1])
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "timeout"}
        except Exception:
            return {"passed": False, "error": "harness_error"}

# ------------------------------------------------------------- evaluation
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default="checkpoints/best")
    p.add_argument("--test-file", default="data/test.jsonl")
    p.add_argument("--train-file", default="data/train.jsonl")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--beams", type=int, default=4)
    p.add_argument("--out", default="eval_results.json")
    a = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(a.checkpoint)
    model = T5ForConditionalGeneration.from_pretrained(a.checkpoint).to(device).eval()

    test_set = [json.loads(l) for l in open(a.test_file, encoding="utf-8") if l.strip()]
    if a.limit:
        test_set = test_set[:a.limit]

    # leakage check
    if Path(a.train_file).exists():
        train_names = {json.loads(l)["name"] for l in open(a.train_file, encoding="utf-8") if l.strip()}
        overlap = {e["name"] for e in test_set} & train_names
        print(f"overlapping function names with train: {len(overlap)}")

    def sync():
        if device == "cuda":
            torch.cuda.synchronize()

    def generate(src):
        inp = tok(src, return_tensors="pt", truncation=True, max_length=256).to(device)
        sync(); t0 = time.perf_counter()
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=256, num_beams=a.beams)
        sync()
        return tok.decode(out[0], skip_special_tokens=True), time.perf_counter() - t0

    generate(test_set[0]["unoptimized"])  # warmup

    rows = []
    for i, ex in enumerate(test_set, 1):
        pred, latency = generate(ex["unoptimized"])
        base = run_code(ex["unoptimized"], ex)
        ref = run_code(ex["optimized"], ex)
        new = run_code(pred, ex)
        ok = base.get("passed") and new.get("passed")
        rows.append({
            "id": ex["id"], "category": ex.get("category"), "latency": latency,
            "passed": bool(new.get("passed")), "error": new.get("error"),
            "speedup": base["time"] / new["time"] if ok else None,
            "copied": pred.strip() == ex["unoptimized"].strip(),
            "ref_ok": bool(ref.get("passed")), "base_ok": bool(base.get("passed")),
            "prediction": pred,
        })
        print(f"[{i}/{len(test_set)}] {ex['id']} passed={rows[-1]['passed']} "
              f"speedup={rows[-1]['speedup']}", flush=True)

    valid = [r for r in rows if r["base_ok"] and r["ref_ok"]]
    n = len(valid)
    if n == 0:
        print("No valid test items (baseline/reference failed). Check your data.")
        return
    passed = [r for r in valid if r["passed"]]
    sp = [r["speedup"] for r in passed if r["speedup"]]

    print("\n===== RESULTS =====")
    print(f"valid test items:   {n}/{len(rows)}")
    print(f"tests passed:       {len(passed)/n:.1%}")
    print(f"median speedup:     {statistics.median(sp):.2f}x" if sp else "median speedup:     n/a")
    print(f"correct AND faster: {sum(s > 1.1 for s in sp)/n:.1%}")
    print(f"copied input:       {sum(r['copied'] for r in valid)/n:.1%}")
    print(f"median latency:     {statistics.median(r['latency'] for r in valid)*1000:.0f} ms")

    by_cat = defaultdict(list)
    for r in valid:
        by_cat[r["category"]].append(r)
    print("\nby category (passed / total):")
    for c, rs in sorted(by_cat.items(), key=lambda kv: str(kv[0])):
        print(f"  {c}: {sum(x['passed'] for x in rs)}/{len(rs)}")

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"\nsaved per-item results to {a.out}")

if __name__ == "__main__":
    main()