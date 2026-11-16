"""Python Code Optimizer - Gradio demo for a fine-tuned CodeT5-small model.

Launch:   python app.py        (then open http://127.0.0.1:7860)

Environment variables (all optional):
    MODEL_DIR   folder containing the fine-tuned model   (default ./codet5-small-finetuned)
    TEST_PATH   held-out test set in JSONL format        (default ./test.jsonl)
"""
import html
import inspect
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict

import gradio as gr
import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

# =====================================================================
# Configuration
# =====================================================================
MODEL_DIR = os.environ.get("MODEL_DIR", "./checkpoints/best")
TEST_PATH = os.environ.get("TEST_PATH", "./data/demo.jsonl")

PREFIX = ""        # task prefix used during training, e.g. "optimize: " (leave "" if none)
MAX_LEN = 512      # max input / output tokens
NUM_BEAMS = 4      # match the decoding settings you used for evaluation

# Which test functions appear in the dropdown. Set DEMO_IDS to hand-pick
# (e.g. ["codeopt_0009", "codeopt_0058"]); otherwise PER_CATEGORY items are
# sampled (seeded, so the list is stable) from every category.
DEMO_IDS = []
PER_CATEGORY = 15
EXCLUDE_CATEGORIES = {"memory"}   # demo is about runtime, so skip the memory task

BENCH_TIMEOUT = 90   # seconds allowed for one benchmark subprocess

# Numbers from your 5,000-item evaluation (edit if you re-run it).
OVERALL = [
    ("Tests passed", "99.6%"),
    ("Correct and faster", "99.3%"),
    ("Median speedup", "84.4×"),
    ("Median latency", "848 ms"),
]
VALID_ITEMS = "4,347 of 5,000"
CATEGORY_RESULTS = [
    ("Dynamic programming", 607, 611),
    ("Hashing", 599, 601),
    ("Loops", 626, 633),
    ("Math", 633, 636),
    ("Memory", 0, 1),
    ("Sorting", 643, 644),
    ("Strings", 638, 638),
    ("Vectorization", 582, 583),
]

HERE = os.path.dirname(os.path.abspath(__file__))


def resolve(path):
    """Resolve relative paths against the working directory, then this file's folder."""
    if os.path.isabs(path) or os.path.exists(path):
        return os.path.abspath(path)
    return os.path.join(HERE, path)


# =====================================================================
# Model
# =====================================================================
device = "cuda" if torch.cuda.is_available() else "cpu"
model_dir = resolve(MODEL_DIR)
if not os.path.isdir(model_dir):
    raise SystemExit(
        f"Model folder not found: {model_dir}\n"
        "Set MODEL_DIR to the folder that contains config.json and the model weights."
    )
try:
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
except Exception:  # checkpoint folders sometimes lack tokenizer files
    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-small")
model = T5ForConditionalGeneration.from_pretrained(model_dir).to(device).eval()


def generate(code):
    """Return (optimized_code, latency_ms)."""
    inputs = tokenizer(PREFIX + code, return_tensors="pt",
                       truncation=True, max_length=MAX_LEN).to(device)
    if device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=MAX_LEN, num_beams=NUM_BEAMS)
    if device == "cuda":
        torch.cuda.synchronize()
    latency_ms = (time.perf_counter() - start) * 1000
    return tokenizer.decode(out[0], skip_special_tokens=True), latency_ms


generate("def f(x):\n    return x")  # warm-up so the first reported latency is representative

# =====================================================================
# Test items
# =====================================================================


def load_items():
    path = resolve(TEST_PATH)
    if not os.path.isfile(path):
        raise SystemExit(f"Test file not found: {path}\nSet TEST_PATH or place test.jsonl next to app.py.")
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if all(k in r for k in ("id", "name", "unoptimized", "tests", "benchmark")):
                rows.append(r)

    if DEMO_IDS:
        wanted = set(DEMO_IDS)
        chosen = [r for r in rows if r["id"] in wanted]
    else:
        by_cat = defaultdict(list)
        for r in rows:
            if r.get("category") not in EXCLUDE_CATEGORIES:
                by_cat[r.get("category", "other")].append(r)
        rng = random.Random(0)
        chosen = []
        for cat in sorted(by_cat):
            pool = by_cat[cat]
            rng.shuffle(pool)
            chosen += pool[:PER_CATEGORY]
    if not chosen:
        raise SystemExit("No usable items found in the test file.")
    chosen.sort(key=lambda r: (r.get("category", ""), r["name"]))
    return chosen


def pretty(s):
    return s.replace("_", " ").title()


_items = load_items()
ITEMS = {r["id"]: r for r in _items}
IDS = [r["id"] for r in _items]
CHOICES = [(f"{pretty(r['name'])}  ·  {r.get('category', 'other')}", r["id"]) for r in _items]

# =====================================================================
# Sandboxed correctness check + benchmark
# =====================================================================
RUNNER = r'''
import copy, json, math, sys, time
sys.setrecursionlimit(10000)
payload = json.load(open(sys.argv[1]))
tests = payload["tests"]
out = {"passed": 0, "total": len(tests), "error": None, "median_ms": None}


def norm(x):
    if isinstance(x, (list, tuple)):
        return [norm(i) for i in x]
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items()}
    return x


def same(a, b):
    a, b = norm(a), norm(b)
    if a == b:
        return True
    return isinstance(a, float) and isinstance(b, float) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


try:
    ns = {}
    exec(payload["code"], ns)
    fn = ns[payload["name"]]
except BaseException as e:
    out["error"] = "%s: %s" % (type(e).__name__, e)
    print(json.dumps(out))
    sys.exit(0)

for t in tests:
    try:
        r = fn(*copy.deepcopy(t["args"]))
        if same(r, t["expected"]):
            out["passed"] += 1
    except BaseException as e:
        if out["error"] is None:
            out["error"] = "%s: %s" % (type(e).__name__, e)

args = payload.get("bench_args")
if args is not None:
    def once():
        a = copy.deepcopy(args)
        t0 = time.perf_counter()
        fn(*a)
        return time.perf_counter() - t0
    try:
        first = once()
        if first > 0.5:
            times = [first]
        else:
            reps = min(25, max(3, int(1.0 / max(first, 1e-6))))
            times = sorted(once() for _ in range(reps))
        out["median_ms"] = times[len(times) // 2] * 1000
    except BaseException as e:
        if out["error"] is None:
            out["error"] = "%s: %s" % (type(e).__name__, e)
print(json.dumps(out))
'''
RUNNER_PATH = os.path.join(tempfile.mkdtemp(prefix="codeopt_"), "runner.py")
with open(RUNNER_PATH, "w", encoding="utf-8") as _f:
    _f.write(RUNNER)


def run_sandboxed(code, item, timeout=BENCH_TIMEOUT):
    result = {"passed": 0, "total": len(item["tests"]), "error": None,
              "median_ms": None, "timeout": False}
    payload = {"code": code, "name": item["name"], "tests": item["tests"],
               "bench_args": item["benchmark"]["args"]}
    with tempfile.TemporaryDirectory() as d:
        pj = os.path.join(d, "payload.json")
        with open(pj, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        try:
            p = subprocess.run([sys.executable, RUNNER_PATH, pj], capture_output=True,
                               text=True, timeout=timeout, cwd=d)
        except subprocess.TimeoutExpired:
            result["timeout"] = True
            result["error"] = f"Timed out after {timeout} s"
            return result
    try:
        result.update(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception:
        lines = p.stderr.strip().splitlines()
        result["error"] = lines[-1] if lines else "The code crashed."
    return result


# =====================================================================
# HTML rendering
# =====================================================================
CSS = """
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
footer { display: none !important; }

.hero { text-align: center; padding: 28px 12px 6px; }
.hero h1 { font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 10px;
           background: linear-gradient(90deg, #6366f1, #3b82f6 60%, #06b6d4);
           -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p  { max-width: 720px; margin: 0 auto; font-size: 1.05rem; line-height: 1.55;
           color: var(--body-text-color-subdued, #6b7280); }

.sec { display: flex; align-items: center; gap: 10px; margin: 26px 0 6px;
       font-size: 1.15rem; font-weight: 700; color: var(--body-text-color, #111); }
.sec .num { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px;
            border-radius: 50%; background: #6366f1; color: #fff; font-size: .9rem; }

.info { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 12px; padding: 12px 16px;
        background: var(--block-background-fill, transparent); }
.info p { margin: 8px 0 0; line-height: 1.5; color: var(--body-text-color, #111); }
.chip { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .78rem; font-weight: 600;
        background: rgba(99,102,241,.14); color: #6366f1; margin-right: 8px; }
.chip.ghost { background: rgba(107,114,128,.14); color: var(--body-text-color-subdued, #6b7280); }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 6px 0 18px; }
.stat { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 14px; padding: 16px 18px; text-align: center;
        background: var(--block-background-fill, transparent); }
.stat .v { font-size: 2rem; font-weight: 800; line-height: 1.15; color: var(--body-text-color, #111); }
.stat .l { margin-top: 4px; font-size: .82rem; text-transform: uppercase; letter-spacing: .06em;
           color: var(--body-text-color-subdued, #6b7280); }
.stat.good .v { color: #16a34a; } .stat.warn .v { color: #d97706; } .stat.bad .v { color: #dc2626; }
.stat.accent .v { color: #6366f1; }

table.m { width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: .95rem; }
table.m th, table.m td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border-color-primary, #e5e7eb); }
table.m th { font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; color: var(--body-text-color-subdued, #6b7280); }
table.m td.n, table.m th.n { text-align: right; font-variant-numeric: tabular-nums; }
.ok { color: #16a34a; font-weight: 700; } .no { color: #dc2626; font-weight: 700; }

.chart { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 14px; padding: 16px 18px;
         background: var(--block-background-fill, transparent); }
.chart h4 { margin: 0 0 12px; font-size: .95rem; }
.bar-row { display: grid; grid-template-columns: 90px 1fr 90px; align-items: center; gap: 12px; margin: 8px 0; font-size: .9rem; }
.bar-track { height: 22px; border-radius: 6px; background: rgba(107,114,128,.12); overflow: hidden; }
.bar { height: 100%; border-radius: 6px; }
.bar.orig { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.bar.opt  { background: linear-gradient(90deg, #6366f1, #06b6d4); }
.bar-row .t { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }
.chart .foot { margin-top: 8px; font-size: .78rem; color: var(--body-text-color-subdued, #6b7280); }

.note { border-radius: 10px; padding: 10px 14px; margin-bottom: 14px; font-size: .9rem; }
.note.bad { background: rgba(220,38,38,.10); color: #dc2626; }
.empty { text-align: center; padding: 34px 12px; border: 1px dashed var(--border-color-primary, #d1d5db);
         border-radius: 14px; color: var(--body-text-color-subdued, #6b7280); }
"""

EMPTY_HTML = '<div class="empty">Choose a function above and click <b>Optimize</b> to see the results here.</div>'


def e(x):
    return html.escape(str(x))


def fmt_ms(ms):
    if ms is None:
        return "—"
    if ms < 1:
        return f"{ms * 1000:.0f} µs"
    if ms < 10:
        return f"{ms:.2f} ms"
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{ms / 1000:.2f} s"


def fmt_speed(x):
    return f"{x:,.0f}×" if x >= 100 else f"{x:.1f}×"


def squash(code):
    return "".join(code.split())


def n_lines(code):
    return len([ln for ln in code.strip().splitlines() if ln.strip()])


def section(num, text):
    return f'<div class="sec"><span class="num">{num}</span>{text}</div>'


def info_html(item):
    return (
        '<div class="info">'
        f'<span class="chip">{e(item.get("category", "other"))}</span>'
        f'<span class="chip ghost">Original complexity: {e(item.get("complexity_before", "n/a"))}</span>'
        f'<p>{e(item.get("description", ""))}</p></div>'
    )


def render_metrics(orig_code, new_code, orig, new, latency):
    o_ms, n_ms = orig["median_ms"], new["median_ms"]
    if orig["timeout"]:
        o_ms = BENCH_TIMEOUT * 1000.0  # lower bound
    passed_all = new["total"] > 0 and new["passed"] == new["total"]
    speedup = (o_ms / n_ms) if (o_ms and n_ms) else None

    if squash(new_code) == squash(orig_code):
        verdict, vcls = "Unchanged", "warn"
    elif not passed_all:
        verdict, vcls = "Failed tests", "bad"
    elif speedup and speedup > 1.05:
        verdict, vcls = "Correct & faster", "good"
    else:
        verdict, vcls = "Correct, not faster", "warn"

    if speedup and passed_all:
        speed_txt = ("≥ " if orig["timeout"] else "") + fmt_speed(speedup)
    else:
        speed_txt = "—"

    cards = (
        '<div class="stat-grid">'
        f'<div class="stat {vcls}"><div class="v">{verdict}</div><div class="l">Verdict</div></div>'
        f'<div class="stat accent"><div class="v">{speed_txt}</div><div class="l">Speedup</div></div>'
        f'<div class="stat"><div class="v">{new["passed"]}/{new["total"]}</div><div class="l">Tests passed</div></div>'
        f'<div class="stat"><div class="v">{latency:,.0f} ms</div><div class="l">Model latency</div></div>'
        "</div>"
    )

    def ok(r):
        good = r["total"] > 0 and r["passed"] == r["total"]
        return f'<span class="{"ok" if good else "no"}">{"✓" if good else "✗"}</span> {r["passed"]}/{r["total"]}'

    o_rt = f"≥ {fmt_ms(o_ms)} (timed out)" if orig["timeout"] else fmt_ms(o_ms)
    n_rt = "timed out" if new["timeout"] else fmt_ms(n_ms)
    table = (
        '<table class="m"><thead><tr><th>Metric</th><th class="n">Original</th><th class="n">Optimized</th></tr></thead><tbody>'
        f'<tr><td>Runtime on benchmark input (median)</td><td class="n">{o_rt}</td><td class="n">{n_rt}</td></tr>'
        f'<tr><td>Test cases passed</td><td class="n">{ok(orig)}</td><td class="n">{ok(new)}</td></tr>'
        f'<tr><td>Lines of code</td><td class="n">{n_lines(orig_code)}</td><td class="n">{n_lines(new_code)}</td></tr>'
        "</tbody></table>"
    )

    note = ""
    if new["error"]:
        msg = new["error"][:300]
        note = f'<div class="note bad"><b>Optimized code reported an error:</b> {e(msg)}</div>'

    chart = ""
    if o_ms and n_ms:
        lo = math.log10(min(o_ms, n_ms)) - 1
        hi = math.log10(max(o_ms, n_ms))

        def width(v):
            return max(3.0, 100 * (math.log10(v) - lo) / (hi - lo))

        chart = (
            '<div class="chart"><h4>Runtime comparison</h4>'
            f'<div class="bar-row"><span>Original</span><div class="bar-track"><div class="bar orig" style="width:{width(o_ms):.1f}%"></div></div><span class="t">{fmt_ms(o_ms)}</span></div>'
            f'<div class="bar-row"><span>Optimized</span><div class="bar-track"><div class="bar opt" style="width:{width(n_ms):.1f}%"></div></div><span class="t">{fmt_ms(n_ms)}</span></div>'
            '<div class="foot">Bar lengths use a logarithmic scale, so large speedups stay visible.</div></div>'
        )
    return cards + note + table + chart


def overall_html():
    cards = "".join(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>' for l, v in OVERALL)
    rows = "".join(
        f'<tr><td>{c}</td><td class="n">{p:,}</td><td class="n">{t:,}</td><td class="n">{(100 * p / t):.1f}%</td></tr>'
        for c, p, t in CATEGORY_RESULTS
    )
    return (
        f'<p>Evaluated on {VALID_ITEMS} held-out test items. '
        'Speed is the median across items; every output was checked against its test cases.</p>'
        f'<div class="stat-grid">{cards}</div>'
        '<table class="m"><thead><tr><th>Category</th><th class="n">Passed</th><th class="n">Total</th>'
        f'<th class="n">Pass rate</th></tr></thead><tbody>{rows}</tbody></table>'
    )


HEADER = """
<div class="hero">
  <h1>Python Code Optimizer</h1>
  <p>A small CodeT5 model (about 60M parameters) fine-tuned to rewrite slow Python functions into
  faster versions that behave identically. It runs entirely on your machine and responds in about a second.</p>
</div>
"""

HOWTO = """
1. **Choose a function.** Pick a slow Python function from the list, or press **Random**. Its original code appears on the left.
2. **Click Optimize.** The model rewrites the function and its optimized version appears on the right.
3. **Check the results.** Both versions are run in an isolated process: the test cases verify the output is still correct,
   and a larger benchmark input measures the runtime (median of several runs).
"""

# =====================================================================
# App logic
# =====================================================================
LOCK = threading.Lock()  # benchmarks are timing-sensitive, so run one at a time


def on_select(item_id):
    item = ITEMS[item_id]
    return item["unoptimized"], "", info_html(item), EMPTY_HTML


def optimize(item_id, progress=gr.Progress()):
    if not item_id:
        return "", EMPTY_HTML
    item = ITEMS[item_id]
    orig_code = item["unoptimized"]
    with LOCK:
        progress(0.1, desc="Generating optimized code…")
        new_code, latency = generate(orig_code)
        progress(0.4, desc="Benchmarking the original…")
        orig = run_sandboxed(orig_code, item)
        progress(0.8, desc="Benchmarking the optimized version…")
        new = run_sandboxed(new_code, item)
    return new_code, render_metrics(orig_code, new_code, orig, new, latency)


# =====================================================================
# UI
# =====================================================================
THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="blue", neutral_hue="slate",
                       font=["Inter", "system-ui", "sans-serif"])

# Gradio 6 moved theme/css from Blocks() to launch(); support both.
_style = {"theme": THEME, "css": CSS}
if "css" in inspect.signature(gr.Blocks.launch).parameters:
    blocks_kwargs, launch_kwargs = {}, _style
else:
    blocks_kwargs, launch_kwargs = _style, {}

first = ITEMS[IDS[0]]

with gr.Blocks(title="Python Code Optimizer", **blocks_kwargs) as demo:
    gr.HTML(HEADER)

    with gr.Accordion("How it works", open=True):
        gr.Markdown(HOWTO)

    gr.HTML(section(1, "Choose a function"))
    with gr.Row():
        dropdown = gr.Dropdown(choices=CHOICES, value=IDS[0], label="Function to optimize",
                               scale=5, interactive=True)
        random_btn = gr.Button("🎲 Random", scale=1, variant="secondary")
    info = gr.HTML(info_html(first))

    gr.HTML(section(2, "Optimize"))
    run_btn = gr.Button("⚡ Optimize", variant="primary", size="lg")

    with gr.Row(equal_height=True):
        orig_box = gr.Code(value=first["unoptimized"], language="python", label="Original function",
                           interactive=False, lines=16)
        new_box = gr.Code(value="", language="python", label="Optimized by the model",
                          interactive=False, lines=16)

    gr.HTML(section(3, "Results"))
    metrics = gr.HTML(EMPTY_HTML)

    with gr.Accordion("Overall evaluation results", open=False):
        gr.HTML(overall_html())

    dropdown.change(on_select, dropdown, [orig_box, new_box, info, metrics])
    random_btn.click(lambda: random.choice(IDS), None, dropdown)
    run_btn.click(optimize, dropdown, [new_box, metrics])

if __name__ == "__main__":
    demo.launch(**launch_kwargs)