"""
WORK IN PROGRESS

verify_pairs.py - run every candidate pair through the harness.

  python verify_pairs.py

Outputs (in ./data/):
  pairs.jsonl  only pairs that PASSED (correct AND >= MIN_SPEEDUP faster). Training data.
  runs.csv     every attempt, pass or fail (append-only log of runs/runtimes/progress)
"""
import csv
import hashlib
import json
import os
import time

from harness import compare
from candidates import CANDIDATES

MIN_SPEEDUP = 1.5
DATA_DIR = "data"
PAIRS_PATH = os.path.join(DATA_DIR, "pairs.jsonl")
RUNS_PATH = os.path.join(DATA_DIR, "runs.csv")
RUN_FIELDS = ["timestamp", "id", "model", "slow_status", "fast_status",
              "slow_runtime", "fast_runtime", "speedup", "correct_and_faster", "error"]


def get_tests(c):
    if c.get("tests"):
        return c["tests"], ""
    from mbpp_data import load_mbpp, row_to_problem
    for split in ("train", "validation", "test", "prompt"):
        try:
            ds = load_mbpp(split)
        except Exception:
            continue
        for row in ds:
            if row["task_id"] == c["task_id"]:
                p = row_to_problem(row)
                return p["tests"], p["test_setup"]
    raise ValueError(f"task_id {c['task_id']} not found in MBPP")


def split_for(key):
    """Deterministic split by problem, so variants of one problem never leak
    across train/test. ~10% of problems go to test."""
    h = int(hashlib.md5(str(key).encode()).hexdigest(), 16) % 10
    return "test" if h == 0 else "train"


def log_run(row):
    os.makedirs(DATA_DIR, exist_ok=True)
    new = not os.path.exists(RUNS_PATH)
    with open(RUNS_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RUN_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    done = set()
    if os.path.exists(PAIRS_PATH):
        with open(PAIRS_PATH) as f:
            done = {json.loads(l)["id"] for l in f}

    kept = 0
    for c in CANDIDATES:
        if c["id"] in done:
            print(f"skip   {c['id']} (already in pairs.jsonl)")
            continue
        tests, setup = get_tests(c)
        problem = {"tests": tests, "test_setup": setup,
                   "bench_setup": c["bench_setup"], "bench_stmt": c["bench_stmt"]}
        r = compare(c["slow"], c["fast"], problem, min_speedup=MIN_SPEEDUP)

        # the slow version must be correct too, otherwise the pair is meaningless
        ok = r["correct_and_faster"] and r["slow"]["status"] == "ok"
        err = r["fast"]["error"] or r["slow"]["error"] or ""
        if not ok and not err:
            err = ("outputs differ on bench input" if r["same_bench_output"] is False
                   else f"speedup {r['speedup']:.2f}x < {MIN_SPEEDUP}x" if r["speedup"] else "")

        log_run({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "id": c["id"], "model": "human",
            "slow_status": r["slow"]["status"], "fast_status": r["fast"]["status"],
            "slow_runtime": r["slow"]["runtime"], "fast_runtime": r["fast"]["runtime"],
            "speedup": r["speedup"], "correct_and_faster": ok, "error": err,
        })

        if ok:
            kept += 1
            group = c.get("task_id", c["id"])
            with open(PAIRS_PATH, "a") as f:
                f.write(json.dumps({
                    "id": c["id"], "task_id": c.get("task_id"), "split": split_for(group),
                    "slow": c["slow"].strip(), "fast": c["fast"].strip(),
                    "tests": tests, "test_setup": setup,
                    "bench_setup": c["bench_setup"], "bench_stmt": c["bench_stmt"],
                    "speedup": r["speedup"],
                }) + "\n")
            print(f"PASS   {c['id']}  {r['speedup']:.1f}x")
        else:
            print(f"REJECT {c['id']}  {err}")
    print(f"\n{kept} new pairs saved to {PAIRS_PATH}; all attempts logged in {RUNS_PATH}")


if __name__ == "__main__":
    main()
