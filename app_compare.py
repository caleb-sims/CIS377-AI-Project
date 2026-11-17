"""Python Code Optimizer - three-way comparison demo.

Compares the original function, the fine-tuned CodeT5 model's rewrite, and a rewrite
written by Claude. Every version is scored by the same harness used for the project's
evaluation (run_code in evaluate.py), so the numbers are directly comparable.

Launch:   python app_compare.py        (then open http://127.0.0.1:7861)

Environment variables (all optional):
    MODEL_DIR   folder containing the fine-tuned model   (default ./checkpoints/best)
    DEMO_PATH   demo data in JSONL format                (default ./data/demo.jsonl)

Claude's answers are PRE-GENERATED (stored in CLAUDE_OUTPUTS below), not live API
calls, so the demo needs no API key or internet. Pasted functions run in a subprocess
on your own machine; this is not a real sandbox, so do not expose the app publicly.
"""
import ast
import html
import importlib.util
import inspect
import json
import math
import os
import pprint
import random
import re
import statistics
import subprocess
import sys
import tempfile
import threading
import time

import gradio as gr
import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

# =====================================================================
# Configuration
# =====================================================================
MODEL_DIR = os.environ.get("MODEL_DIR", "./checkpoints/best")
DEMO_PATH = os.environ.get("DEMO_PATH", "./data/demo.jsonl")
EVAL_RESULTS = os.environ.get("EVAL_RESULTS", "./eval_results.json")   # optional, written by evaluate.py
PORT = 7861

PREFIX = ""        # task prefix used during training (leave "" if none)
MAX_LEN = 256      # same limits as evaluate.py
NUM_BEAMS = 4
FASTER_THRESHOLD = 1.1   # evaluate.py counts "correct AND faster" as speedup > 1.1

# Numbers from the 5,000-item evaluation of the small model.
OVERALL = [
    ("Tests passed", "99.6%"),
    ("Correct and faster", "99.3%"),
    ("Median speedup", "84.4×"),
    ("Median latency", "848 ms"),
]
VALID_ITEMS = "4,347 of 5,000"

HERE = os.path.dirname(os.path.abspath(__file__))


def resolve(path):
    if os.path.isabs(path) or os.path.exists(path):
        return os.path.abspath(path)
    return os.path.join(HERE, path)


# =====================================================================
# Claude's pre-generated answers (item id -> optimized function source)
# =====================================================================
CLAUDE_OUTPUTS = {
    "codeopt_0009": "def subarray_sum_count(nums, k):\n    counts = {0: 1}\n    prefix = 0\n    total = 0\n    for x in nums:\n        prefix += x\n        total += counts.get(prefix - k, 0)\n        counts[prefix] = counts.get(prefix, 0) + 1\n    return total",
    "codeopt_0019": "def unique_number_of_occurrences(nums):\n    from collections import Counter\n    freqs = Counter(nums).values()\n    return len(set(freqs)) == len(freqs)",
    "codeopt_0045": "def sort_by_parity(nums):\n    return sorted(nums, key=lambda x: x % 2)",
    "codeopt_0053": "def edit_distance(a, b):\n    if not a:\n        return len(b)\n    if not b:\n        return len(a)\n    prev = list(range(len(b) + 1))\n    for i, x in enumerate(a, 1):\n        cur = [i]\n        for j, y in enumerate(b, 1):\n            cur.append(min(prev[j - 1] + (x != y), prev[j] + 1, cur[j - 1] + 1))\n        prev = cur\n    return prev[-1]",
    "codeopt_0058": "def house_robber(nums):\n    a = b = 0\n    for x in nums:\n        a, b = b, max(b, a + x)\n    return b",
    "codeopt_0059": "def knapsack_01(weights, values, capacity):\n    if capacity < 0:\n        return 0\n    dp = [0] * (capacity + 1)\n    for w, v in zip(weights, values):\n        for c in range(capacity, w - 1, -1):\n            cand = dp[c - w] + v\n            if cand > dp[c]:\n                dp[c] = cand\n    return dp[capacity]",
    "codeopt_0060": "def longest_common_substring(a, b):\n    best = 0\n    prev = [0] * (len(b) + 1)\n    for x in a:\n        cur = [0] * (len(b) + 1)\n        for j, y in enumerate(b, 1):\n            if x == y:\n                v = prev[j - 1] + 1\n                cur[j] = v\n                if v > best:\n                    best = v\n        prev = cur\n    return best",
    "codeopt_0061": "def min_path_sum(grid):\n    cols = len(grid[0])\n    dp = [0] * cols\n    for i, row in enumerate(grid):\n        for j in range(cols):\n            if i == 0 and j == 0:\n                dp[j] = row[j]\n            elif i == 0:\n                dp[j] = dp[j - 1] + row[j]\n            elif j == 0:\n                dp[j] += row[j]\n            else:\n                dp[j] = min(dp[j], dp[j - 1]) + row[j]\n    return dp[-1]",
    "codeopt_0070": "def maximal_square(matrix):\n    rows = len(matrix)\n    cols = len(matrix[0]) if rows else 0\n    prev = [0] * (cols + 1)\n    best = 0\n    for i in range(rows):\n        cur = [0] * (cols + 1)\n        for j in range(cols):\n            if matrix[i][j] == 1:\n                v = min(prev[j], prev[j + 1], cur[j]) + 1\n                cur[j + 1] = v\n                if v > best:\n                    best = v\n        prev = cur\n    return best * best",
    "codeopt_0145": "def batch_affine_transform(X, W, b):\n    from operator import mul\n    n = len(X)\n    d = len(X[0]) if n else 0\n    m = len(W[0]) if d else 0\n    cols = list(zip(*W)) if m else []\n    return [[sum(map(mul, row, col), b[j]) for j, col in enumerate(cols)] for row in X]",
    "codeopt_0151": "def sum_of_cubes(n):\n    if n <= 0:\n        return 0\n    s = n * (n + 1) // 2\n    return s * s",
    "codeopt_0155": "def trailing_zeros_factorial(n):\n    count = 0\n    p = 5\n    while p <= n:\n        count += n // p\n        p *= 5\n    return count",
    "codeopt_0157": "def sum_of_primes_below(n):\n    if n < 3:\n        return 0\n    sieve = bytearray([1]) * n\n    sieve[0] = sieve[1] = 0\n    for i in range(2, int(n ** 0.5) + 1):\n        if sieve[i]:\n            sieve[i * i::i] = bytearray(len(range(i * i, n, i)))\n    return sum(i for i in range(n) if sieve[i])",
    "codeopt_0171": "def max_product_subarray(nums):\n    if not nums:\n        return None\n    cur_max = cur_min = best = nums[0]\n    for x in nums[1:]:\n        cands = (x, cur_max * x, cur_min * x)\n        cur_max = max(cands)\n        cur_min = min(cands)\n        if cur_max > best:\n            best = cur_max\n    return best",
    "codeopt_0180": "def product_except_self(nums):\n    n = len(nums)\n    out = [1] * n\n    p = 1\n    for i in range(n):\n        out[i] = p\n        p *= nums[i]\n    p = 1\n    for i in range(n - 1, -1, -1):\n        out[i] *= p\n        p *= nums[i]\n    return out",
    "codeopt_0186": "def subarray_product_less_than_k(nums, k):\n    if k <= 1:\n        return 0\n    count = 0\n    prod = 1\n    left = 0\n    for right, x in enumerate(nums):\n        prod *= x\n        while prod >= k and left <= right:\n            prod //= nums[left]\n            left += 1\n        count += right - left + 1\n    return count",
    "codeopt_0188": "def find_pivot_index(nums):\n    total = sum(nums)\n    left = 0\n    for i, x in enumerate(nums):\n        if left == total - left - x:\n            return i\n        left += x\n    return -1",
    "codeopt_0193": "def max_distance_between_equal(nums):\n    first = {}\n    best = 0\n    for i, x in enumerate(nums):\n        j = first.setdefault(x, i)\n        if i - j > best:\n            best = i - j\n    return best",
    "codeopt_0198": "def longest_increasing_run(nums):\n    best = cur = 0\n    for i, x in enumerate(nums):\n        cur = cur + 1 if i and x > nums[i - 1] else 1\n        if cur > best:\n            best = cur\n    return best",
    "codeopt_0219": "def gen_gram_matrix_838(X):\n    from operator import mul\n    n = len(X)\n    out = [[0] * n for _ in range(n)]\n    for i in range(n):\n        xi = X[i]\n        for j in range(i, n):\n            v = sum(map(mul, xi, X[j]))\n            out[i][j] = v\n            out[j][i] = v\n    return out",
    "codeopt_0223": "def gen_max_pool_2d_302(image, k):\n    cols = len(image[0])\n    out = []\n    for i in range(len(image) // k):\n        block = image[i * k:(i + 1) * k]\n        out.append([max(max(r[j * k:(j + 1) * k]) for r in block) for j in range(cols // k)])\n    return out",
    "codeopt_0234": "def gen_kth_smallest_1241(nums, k):\n    s = sorted(nums)\n    return s[max(k, 1) - 1]",
    "codeopt_0236": "def gen_sum_to_n_510(n):\n    return n * (n + 1) // 2 if n > 0 else 0",
    "codeopt_0244": "def gen_fib_235(n):\n    if n < 2:\n        return n\n    a, b = 0, 1\n    for _ in range(n - 1):\n        a, b = b, a + b\n    return b",
    "codeopt_0253": "def gen_lcs_length_519(a, b):\n    if not a or not b:\n        return 0\n    prev = [0] * (len(b) + 1)\n    for x in a:\n        cur = [0]\n        for j, y in enumerate(b, 1):\n            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))\n        prev = cur\n    return prev[-1]",
    "codeopt_0255": "def gen_remove_spaces_859(s):\n    return s.replace(\" \", \"\")",
    "codeopt_0266": "def gen_convolve_valid_155(a, kernel):\n    from operator import mul\n    m = len(kernel)\n    rk = kernel[::-1]\n    return [sum(map(mul, a[i:i + m], rk)) for i in range(len(a) - m + 1)]",
    "codeopt_0290": "def gen_binary_search_575(nums, target):\n    from bisect import bisect_left\n    i = bisect_left(nums, target)\n    return i if i < len(nums) and nums[i] == target else -1",
    "codeopt_0301": "def gen_is_anagram_514(a, b):\n    if len(a) != len(b):\n        return False\n    from collections import Counter\n    return Counter(a) == Counter(b)",
    "codeopt_0306": "def gen_longest_unique_718(s):\n    last = {}\n    start = 0\n    best = 0\n    for i, c in enumerate(s):\n        if c in last and last[c] >= start:\n            start = last[c] + 1\n        last[c] = i\n        if i - start + 1 > best:\n            best = i - start + 1\n    return best",
    "codeopt_0309": "def gen_max_subarray_959(nums):\n    if not nums:\n        return None\n    best = cur = nums[0]\n    for x in nums[1:]:\n        cur = x if cur < 0 else cur + x\n        if cur > best:\n            best = cur\n    return best",
    "codeopt_0314": "def gen_coin_ways_787(coins, amount):\n    if amount < 0:\n        return 0\n    dp = [0] * (amount + 1)\n    dp[0] = 1\n    for c in coins:\n        for a in range(c, amount + 1):\n            dp[a] += dp[a - c]\n    return dp[amount]",
    "codeopt_0317": "def gen_is_palindrome_1224(s):\n    return s == s[::-1]",
    "codeopt_0347": "def gen_count_frequency_953(nums):\n    from collections import Counter\n    return dict(Counter(nums))",
    "codeopt_0354": "def gen_bubble_sort_1183(nums):\n    return sorted(nums)",
    "codeopt_0361": "def gen_min_subarray_len_1086(nums, target):\n    best = None\n    total = 0\n    left = 0\n    for right, x in enumerate(nums):\n        total += x\n        while total >= target and left <= right:\n            length = right - left + 1\n            if best is None or length < best:\n                best = length\n            total -= nums[left]\n            left += 1\n    return 0 if best is None else best",
    "codeopt_0405": "def gen_best_stock_49(prices):\n    best = 0\n    low = None\n    for p in prices:\n        if low is None or p < low:\n            low = p\n        elif p - low > best:\n            best = p - low\n    return best",
    "codeopt_0410": "def gen_pow_mod_150(base, exp, mod):\n    if exp <= 0:\n        return 1\n    return pow(base, exp, mod)",
    "codeopt_0438": "def gen_count_substring_691(s, sub):\n    return s.count(sub)",
    "codeopt_0449": "def gen_pairwise_abs_1104(values):\n    s = sorted(values)\n    n = len(s)\n    return sum(x * (2 * i - n + 1) for i, x in enumerate(s))",
    "codeopt_0460": "def gen_factorial_317(n):\n    import math\n    return math.factorial(n) if n > 1 else 1",
    "codeopt_0474": "def gen_sum_of_squares_787(n):\n    if n <= 0:\n        return 0\n    return n * (n + 1) * (2 * n + 1) // 6",
    "codeopt_0494": "def gen_min_abs_diff_1083(nums):\n    if len(nums) < 2:\n        return None\n    s = sorted(nums)\n    return min(b - a for a, b in zip(s, s[1:]))",
    "codeopt_0507": "def gen_is_prime_688(n):\n    if n < 2:\n        return False\n    if n < 4:\n        return True\n    if n % 2 == 0:\n        return False\n    import math\n    for d in range(3, math.isqrt(n) + 1, 2):\n        if n % d == 0:\n            return False\n    return True",
    "codeopt_0578": "def gen_matrix_multiply_259(A, B):\n    from operator import mul\n    cols = list(zip(*B))\n    return [[sum(map(mul, row, col)) for col in cols] for row in A]",
    "codeopt_0843": "def gen_two_sum_1088(nums, target):\n    from bisect import bisect_right\n    pos = {}\n    for idx, x in enumerate(nums):\n        pos.setdefault(x, []).append(idx)\n    for i, x in enumerate(nums):\n        lst = pos.get(target - x)\n        if lst:\n            k = bisect_right(lst, i)\n            if k < len(lst):\n                return [i, lst[k]]\n    return []",
    "codeopt_0997": "def gen_insertion_sort_243(nums):\n    return sorted(nums)",
    "codeopt_1001": "def gen_dedupe_order_376(nums):\n    return list(dict.fromkeys(nums))",
    "codeopt_1119": "def gen_has_duplicate_775(nums):\n    return len(set(nums)) != len(nums)",
    "codeopt_1483": "def gen_max_k_window_754(nums, k):\n    if k > len(nums):\n        return None\n    total = sum(nums[:k])\n    best = total\n    for i in range(k, len(nums)):\n        total += nums[i] - nums[i - k]\n        if total > best:\n            best = total\n    return best",
    "codeopt_2004": "def gen_reverse_string_1208(s):\n    return s[::-1]"
}

# Pre-measured timings, filled in by:  python app_compare.py --score-claude
# (id -> {"base": original runtime in s, "time": Claude runtime in s, "passed": bool})
# While this is empty, the demo scores Claude's code live instead.
# BEGIN CLAUDE_SCORES
CLAUDE_SCORES = {}
# END CLAUDE_SCORES

# =====================================================================
# Scoring harness (shared with evaluate.py)
# =====================================================================


def load_run_code():
    path = resolve("evaluate.py")
    if not os.path.isfile(path):
        raise SystemExit("evaluate.py not found next to app_compare.py. Keep both files in the repo root.")
    spec = importlib.util.spec_from_file_location("project_evaluate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_code


run_code = load_run_code()

# =====================================================================
# Demo items
# =====================================================================
KEEP = ("id", "name", "category", "description", "complexity_before", "unoptimized", "tests", "benchmark")
ID_RE = re.compile(r'\{\s*"id"\s*:\s*"([^"]+)"')


def load_items():
    path = resolve(DEMO_PATH)
    if not os.path.isfile(path):
        raise SystemExit(f"Demo data not found: {path}\nSet DEMO_PATH or place demo.jsonl in ./data/.")
    items = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            m = ID_RE.match(line)
            if m and m.group(1) in CLAUDE_OUTPUTS:   # only parse the lines we need
                r = json.loads(line)
                items[r["id"]] = {k: r.get(k) for k in KEEP}
    missing = [i for i in CLAUDE_OUTPUTS if i not in items]
    if missing:
        print(f"Warning: {len(missing)} cached Claude answers have no matching item in {path}.")
    if not items:
        raise SystemExit("No demo items matched the cached Claude answers.")
    return items


def base_name(n):
    return re.sub(r"_\d+$", "", n[4:]) if n.startswith("gen_") else n


def pretty(n):
    return base_name(n).replace("_", " ").title()


ITEMS = load_items()
ORDER = sorted(ITEMS, key=lambda i: (ITEMS[i]["category"], pretty(ITEMS[i]["name"])))
CHOICES = [(f"{pretty(ITEMS[i]['name'])}  ·  {ITEMS[i]['category']}", i) for i in ORDER]



def score_claude_main():
    """One-time: time the original and Claude's rewrite on THIS machine and store the results in this file."""
    scores = {}
    order = sorted(ITEMS, key=lambda i: (ITEMS[i]["category"], ITEMS[i]["name"]))
    for n, i in enumerate(order, 1):
        item = ITEMS[i]
        base = run_code(item["unoptimized"], item)
        claude = run_code(CLAUDE_OUTPUTS[i], item)
        if not base.get("passed"):
            print(f"[{n}/{len(order)}] {item['name']}: original failed ({base.get('error')}), skipped")
            continue
        scores[i] = {"base": base["time"], "passed": bool(claude.get("passed")),
                     "time": claude.get("time") if claude.get("passed") else None}
        sp = base["time"] / claude["time"] if claude.get("passed") else None
        print(f"[{n}/{len(order)}] {item['name']}: passed={scores[i]['passed']} speedup={sp and round(sp, 1)}", flush=True)
    path = os.path.abspath(__file__)
    with open(path, encoding="utf-8") as f:
        src = f.read()
    block = "# BEGIN CLAUDE_SCORES\nCLAUDE_SCORES = " + pprint.pformat(scores, width=100) + "\n# END CLAUDE_SCORES"
    new, count = re.subn(r"# BEGIN CLAUDE_SCORES.*?# END CLAUDE_SCORES", lambda m: block, src, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("Could not find the CLAUDE_SCORES block in this file.")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    ok = sum(v["passed"] for v in scores.values())
    print(f"\nSaved timings for {len(scores)} items ({ok} passed) into {path}. Now run: python app_compare.py")


if "--score-claude" in sys.argv:
    score_claude_main()
    sys.exit(0)

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
except Exception:
    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-small")
model = T5ForConditionalGeneration.from_pretrained(model_dir).to(device).eval()


def generate(code):
    """Return (optimized_code, latency_ms)."""
    inputs = tokenizer(PREFIX + code, return_tensors="pt", truncation=True, max_length=MAX_LEN).to(device)
    if device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=MAX_LEN, num_beams=NUM_BEAMS)
    if device == "cuda":
        torch.cuda.synchronize()
    latency_ms = (time.perf_counter() - start) * 1000
    return tokenizer.decode(out[0], skip_special_tokens=True), latency_ms


generate("def f(x):\n    return x")  # warm-up

# =====================================================================
# Custom (pasted) functions
# =====================================================================
CUSTOM_RUNNER = r'''
import ast, json, sys
sys.setrecursionlimit(5000)
job = json.load(open(sys.argv[1]))
name = job["name"]
ns = {}
exec(job["code"], ns)
fn = ns[name]


def parse(call):
    node = ast.parse(call.strip(), mode="eval").body
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name):
        raise ValueError("each call must look like %s(...)" % name)
    if node.keywords:
        raise ValueError("use positional arguments only")
    return [eval(compile(ast.Expression(a), "<arg>", "eval"), ns) for a in node.args]


def clone(x):
    return json.loads(json.dumps(x))


out = {"tests": [], "bench": None}
for c in job["calls"]:
    args = clone(parse(c))
    expected = clone(fn(*clone(args)))
    out["tests"].append({"args": args, "expected": expected})
if job["bench"]:
    out["bench"] = {"args": clone(parse(job["bench"]))}
print(json.dumps(out))
'''
CUSTOM_PATH = os.path.join(tempfile.mkdtemp(prefix="codeopt_cmp_"), "custom_runner.py")
with open(CUSTOM_PATH, "w", encoding="utf-8") as _f:
    _f.write(CUSTOM_RUNNER)

SAMPLE_CODE = '''def count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count'''
SAMPLE_CALLS = "count_pairs([1, 2, 3, 4], 5)\ncount_pairs([2, 2, 2], 4)\ncount_pairs([], 3)"
SAMPLE_BENCH = "count_pairs(list(range(2000)), 2001)"


def build_custom_item(code, calls_text, bench_text):
    """Return (item, error_message)."""
    code = (code or "").strip()
    if not code:
        return None, "Paste a function first."
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return None, f"The function has a syntax error: {exc.msg} (line {exc.lineno})."
    funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    if not funcs:
        return None, "Could not find a function. The code must contain a line starting with 'def'."
    name = funcs[0]
    calls = [c.strip() for c in (calls_text or "").splitlines() if c.strip()]
    if not calls:
        return None, f"Add at least one example call, for example {name}([1, 2, 3])."
    job = {"code": code, "name": name, "calls": calls, "bench": (bench_text or "").strip()}
    with tempfile.TemporaryDirectory() as d:
        jp = os.path.join(d, "job.json")
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(job, f)
        try:
            p = subprocess.run([sys.executable, CUSTOM_PATH, jp], capture_output=True, text=True, timeout=45, cwd=d)
        except subprocess.TimeoutExpired:
            return None, "Running your example calls took too long (over 45 s)."
    if p.returncode != 0:
        last = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "unknown error"
        hint = ""
        if "JSON" in last or "serializable" in last:
            hint = " Inputs and outputs must be plain numbers, strings, lists, or dicts."
        return None, f"Your example calls failed: {last}.{hint}"
    try:
        data = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return None, "Could not read the results of your example calls."
    bench = data["bench"] or {"args": data["tests"][0]["args"]}
    item = {"id": "custom", "name": name, "category": "your function", "unoptimized": code,
            "tests": data["tests"], "benchmark": bench, "description": "", "complexity_before": "n/a",
            "bench_is_fallback": data["bench"] is None}
    return item, None


# =====================================================================
# Scoring helpers
# =====================================================================
LOCK = threading.Lock()   # timing is sensitive, so only one run at a time


def squash(code):
    return "".join(code.split())


def score_one(base, run, code, orig_code):
    """Combine a run_code result with the baseline into display fields."""
    passed = bool(run.get("passed"))
    t = run.get("time") if passed else None
    speed = (base["time"] / t) if (passed and base.get("passed") and t) else None
    if squash(code) == squash(orig_code):
        verdict, cls = "Unchanged", "warn"
    elif not passed:
        verdict, cls = "Failed tests", "bad"
    elif speed and speed > FASTER_THRESHOLD:
        verdict, cls = "Correct & faster", "good"
    else:
        verdict, cls = "Correct, not faster", "warn"
    return {"passed": passed, "time": t, "speed": speed, "verdict": verdict, "cls": cls,
            "error": run.get("error"), "code": code}


def score_item(item, small_code, claude_code):
    orig_code = item["unoptimized"]
    base = run_code(orig_code, item)
    small = score_one(base, run_code(small_code, item), small_code, orig_code)
    claude = None
    if claude_code is not None:
        claude = score_one(base, run_code(claude_code, item), claude_code, orig_code)
    return base, small, claude


# =====================================================================
# HTML rendering
# =====================================================================
CSS = """
.gradio-container { max-width: 1320px !important; margin: 0 auto !important; }
footer { display: none !important; }

.hero { text-align: center; padding: 28px 12px 6px; }
.hero h1 { font-size: 2.6rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 10px;
           background: linear-gradient(90deg, #6366f1, #3b82f6 60%, #06b6d4);
           -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p  { max-width: 760px; margin: 0 auto; font-size: 1.05rem; line-height: 1.55;
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

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin: 6px 0 18px; }
.stat { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 14px; padding: 16px 18px; text-align: center;
        background: var(--block-background-fill, transparent); }
.stat .v { font-size: 1.9rem; font-weight: 800; line-height: 1.15; color: var(--body-text-color, #111); }
.stat .l { margin-top: 4px; font-size: .8rem; text-transform: uppercase; letter-spacing: .06em;
           color: var(--body-text-color-subdued, #6b7280); }
.stat .s { margin-top: 2px; font-size: .85rem; font-weight: 600; }
.stat.good .v, .stat.good .s { color: #16a34a; } .stat.warn .v, .stat.warn .s { color: #d97706; }
.stat.bad .v, .stat.bad .s { color: #dc2626; } .stat.accent .v { color: #6366f1; }

table.m { width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: .95rem; }
table.m th, table.m td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border-color-primary, #e5e7eb); }
table.m th { font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; color: var(--body-text-color-subdued, #6b7280); }
table.m td.n, table.m th.n { text-align: right; font-variant-numeric: tabular-nums; }
.ok { color: #16a34a; font-weight: 700; } .no { color: #dc2626; font-weight: 700; }

.chart { border: 1px solid var(--border-color-primary, #e5e7eb); border-radius: 14px; padding: 16px 18px;
         background: var(--block-background-fill, transparent); }
.chart h4 { margin: 0 0 12px; font-size: .95rem; }
.bar-row { display: grid; grid-template-columns: 110px 1fr 100px; align-items: center; gap: 12px; margin: 8px 0; font-size: .9rem; }
.bar-track { height: 22px; border-radius: 6px; background: rgba(107,114,128,.12); overflow: hidden; }
.bar { height: 100%; border-radius: 6px; }
.bar.orig { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.bar.small { background: linear-gradient(90deg, #6366f1, #06b6d4); }
.bar.claude { background: linear-gradient(90deg, #d97757, #e9a27d); }
.bar-row .t { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }
.chart .foot, .foot { margin-top: 8px; font-size: .78rem; color: var(--body-text-color-subdued, #6b7280); }

.note { border-radius: 10px; padding: 10px 14px; margin-bottom: 14px; font-size: .9rem; }
.note.bad { background: rgba(220,38,38,.10); color: #dc2626; }
.note.warn { background: rgba(217,119,6,.12); color: #b45309; }
.empty { text-align: center; padding: 34px 12px; border: 1px dashed var(--border-color-primary, #d1d5db);
         border-radius: 14px; color: var(--body-text-color-subdued, #6b7280); }
"""

EMPTY_HTML = '<div class="empty">Click <b>Optimize</b> to see the three-way comparison here.</div>'


def e(x):
    return html.escape(str(x))


def fmt_s(sec):
    if sec is None:
        return "—"
    ms = sec * 1000
    if ms < 1:
        return f"{ms * 1000:.0f} µs"
    if ms < 10:
        return f"{ms:.2f} ms"
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{ms / 1000:.2f} s"


def fmt_speed(x):
    return "—" if x is None else (f"{x:,.0f}×" if x >= 100 else f"{x:.1f}×")


def n_lines(code):
    return len([ln for ln in code.strip().splitlines() if ln.strip()])


def section(num, text):
    return f'<div class="sec"><span class="num">{num}</span>{text}</div>'


def info_html(item):
    return (
        '<div class="info">'
        f'<span class="chip">{e(item.get("category", ""))}</span>'
        f'<span class="chip ghost">Original complexity: {e(item.get("complexity_before") or "n/a")}</span>'
        f'<p>{e(item.get("description") or "")}</p></div>'
    )


def friendly_error(err):
    return {"wrong_answer": "wrong answer", "timeout": "timed out", "harness_error": "could not run",
            "KeyError": "function name missing"}.get(err, err or "failed")


def render_results(base, small, claude, latency, orig_code, fallback_bench=False, cached=False):
    # ---- headline cards
    def model_card(title, r):
        val = fmt_speed(r["speed"]) if r["speed"] and r["passed"] else "—"
        return (f'<div class="stat {r["cls"]}"><div class="v">{val}</div>'
                f'<div class="l">{title} speedup</div><div class="s">{e(r["verdict"])}</div></div>')

    cards = model_card("Small model", small)
    if claude:
        cards += model_card("Claude", claude)
    cards += f'<div class="stat"><div class="v">{latency:,.0f} ms</div><div class="l">Small-model latency</div></div>'
    if claude:
        winner = "Neither"
        ok_s = small["passed"] and small["speed"]
        ok_c = claude["passed"] and claude["speed"]
        if ok_s and ok_c:
            ratio = small["speed"] / claude["speed"]
            winner = "Tie" if 1 / 1.1 <= ratio <= 1.1 else ("Small model" if ratio > 1 else "Claude")
        elif ok_s:
            winner = "Small model"
        elif ok_c:
            winner = "Claude"
        cards += f'<div class="stat accent"><div class="v">{winner}</div><div class="l">Fastest correct solution</div></div>'
    cards = f'<div class="stat-grid">{cards}</div>'

    # ---- table
    def passed_cell(r):
        if r["passed"]:
            return '<span class="ok">✓</span> all tests'
        return f'<span class="no">✗</span> {e(friendly_error(r["error"]))}'

    base_pass = ('<span class="ok">✓</span> all tests' if base.get("passed")
                 else f'<span class="no">✗</span> {e(friendly_error(base.get("error")))}')
    head = '<th>Metric</th><th class="n">Original</th><th class="n">Small model</th>' + ('<th class="n">Claude</th>' if claude else "")

    def row(label, o, s, c):
        return f'<tr><td>{label}</td><td class="n">{o}</td><td class="n">{s}</td>' + (f'<td class="n">{c}</td>' if claude else "") + "</tr>"

    rows = [
        row("Runtime on benchmark input (median of 7)", fmt_s(base.get("time")), fmt_s(small["time"]), fmt_s(claude["time"]) if claude else ""),
        row("Speedup vs. original", "—", fmt_speed(small["speed"]), fmt_speed(claude["speed"]) if claude else ""),
        row("Correct on the test cases", base_pass, passed_cell(small), passed_cell(claude) if claude else ""),
        row("Lines of code", n_lines(orig_code), n_lines(small["code"]), n_lines(claude["code"]) if claude else ""),
        row("Time to generate", "—", f"{latency:,.0f} ms", "pre-generated" if claude else ""),
    ]
    table = f'<table class="m"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'

    # ---- chart
    series = [("Original", base.get("time") if base.get("passed") else None, "orig"),
              ("Small model", small["time"], "small")]
    if claude:
        series.append(("Claude", claude["time"], "claude"))
    vals = [t for _, t, _ in series if t]
    chart = ""
    if len(vals) >= 2:
        lo = math.log10(min(vals)) - 1
        hi = math.log10(max(vals))
        span = (hi - lo) or 1

        def width(v):
            return max(3.0, 100 * (math.log10(v) - lo) / span)

        bars = "".join(
            f'<div class="bar-row"><span>{lab}</span><div class="bar-track"><div class="bar {cls}" style="width:{width(t):.1f}%"></div></div>'
            f'<span class="t">{fmt_s(t)}</span></div>'
            for lab, t, cls in series if t
        )
        chart = (f'<div class="chart"><h4>Runtime comparison</h4>{bars}'
                 '<div class="foot">Log scale, so large speedups stay visible. Timings are measured live and vary slightly between runs.</div></div>')

    notes = ""
    if fallback_bench:
        notes += '<div class="note warn">No benchmark call was given, so timing used your first example call. Small inputs make speedups look small or noisy.</div>'
    if cached:
        notes += ('<div class="foot">The original and Claude were timed ahead of time on this computer; '
                  'the small model was timed just now.</div>')
    return cards + notes + table + chart


def overall_html():
    cards = "".join(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>' for l, v in OVERALL)
    return (
        f'<p>The small model was evaluated on {VALID_ITEMS} held-out test items. Items whose reference solution '
        'failed the harness (mostly the memory category) are excluded. Speed is the median across items.</p>'
        f'<div class="stat-grid">{cards}</div>'
    )


HEADER = """
<div class="hero">
  <h1>Python Code Optimizer</h1>
  <p>A small CodeT5 model (about 60M parameters) fine-tuned to rewrite slow Python functions into faster
  versions that behave identically. This page puts it head to head with a rewrite written by Claude, and
  scores both with the same tests and timing.</p>
</div>
"""

HOWTO = """
1. **Choose an input.** Pick a built-in function, or switch to **Paste my own** and enter a function plus a few example calls.
2. **Click Optimize.** The small model rewrites the function live. For built-in examples, Claude's rewrite is shown too.
3. **Compare.** All versions run in an isolated process: the tests check the answers are still correct, and a larger
   input measures the runtime (median of 7 runs). Claude's answers were pre-generated, not live API calls.
"""

# =====================================================================
# App logic
# =====================================================================
MODE_EX, MODE_PASTE = "Pick an example", "Paste my own"
CLAUDE_NA = "# Claude's answers were pre-generated for the built-in examples only,\n# so there is no Claude version of a pasted function."


def on_select(item_id):
    item = ITEMS[item_id]
    return item["unoptimized"], "", CLAUDE_OUTPUTS[item_id], info_html(item), EMPTY_HTML


def clear_for_mode(mode):
    return ("", "", EMPTY_HTML, gr.update(visible=mode == MODE_EX), gr.update(visible=mode == MODE_PASTE))


def optimize(mode, item_id, p_code, p_calls, p_bench, progress=gr.Progress()):
    if mode == MODE_EX:
        if not item_id:
            return "", "", EMPTY_HTML
        item = ITEMS[item_id]
        claude_code = CLAUDE_OUTPUTS.get(item_id)
    else:
        progress(0.05, desc="Reading your example calls…")
        item, err = build_custom_item(p_code, p_calls, p_bench)
        if err:
            return "", CLAUDE_NA, f'<div class="note bad">{e(err)}</div>'
        claude_code = None

    orig_code = item["unoptimized"]
    with LOCK:
        progress(0.15, desc="Small model is rewriting the function…")
        small_code, latency = generate(orig_code)
        cached = CLAUDE_SCORES.get(item["id"]) if mode == MODE_EX else None
        progress(0.35, desc="Running the original…")
        base = {"passed": True, "time": cached["base"]} if cached else run_code(orig_code, item)
        if not base.get("passed"):
            msg = ("The original function did not reproduce its own example outputs "
                   f"({friendly_error(base.get('error'))}). Results are returned as plain numbers, strings, lists, "
                   "and dicts, so avoid tuples, sets, or generators as return values.")
            return "", claude_code or CLAUDE_NA, f'<div class="note bad">{e(msg)}</div>'
        progress(0.6, desc="Scoring the small model…")
        small = score_one(base, run_code(small_code, item), small_code, orig_code)
        claude = None
        if claude_code is not None:
            progress(0.85, desc="Scoring Claude's version…")
            c_run = ({"passed": cached["passed"], "time": cached["time"],
                      "error": None if cached["passed"] else "wrong_answer"} if cached
                     else run_code(claude_code, item))
            claude = score_one(base, c_run, claude_code, orig_code)
    html_out = render_results(base, small, claude, latency, orig_code, item.get("bench_is_fallback", False), bool(cached))
    return small_code, (claude_code if claude_code is not None else CLAUDE_NA), html_out


SUMMARY = {"html": None}


def load_eval_results():
    path = resolve(EVAL_RESULTS)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            return {r["id"]: r for r in json.load(f)}
    except Exception:
        return {}


def summarize(progress=gr.Progress()):
    if SUMMARY["html"]:
        return SUMMARY["html"]
    ev = load_eval_results()
    rows, lat, live = [], [], False
    with LOCK:
        for n, i in enumerate(ORDER):
            progress(n / len(ORDER), desc=f"Scoring example {n + 1} of {len(ORDER)}…")
            item = ITEMS[i]
            cs = CLAUDE_SCORES.get(i)
            e_row = ev.get(i)
            # Small model: take the stored evaluation result if there is one, else run it now.
            if e_row and e_row.get("base_ok"):
                small = {"passed": bool(e_row["passed"]), "speed": e_row.get("speedup")}
                lat.append(e_row["latency"] * 1000)
                base_ok = True
            else:
                live = True
                code, latency = generate(item["unoptimized"])
                lat.append(latency)
                base = run_code(item["unoptimized"], item)
                r = score_one(base, run_code(code, item), code, item["unoptimized"])
                small = {"passed": r["passed"], "speed": r["speed"]}
                base_ok = bool(base.get("passed"))
            # Claude: stored timings if there are any, else run now.
            if cs:
                claude = {"passed": cs["passed"], "speed": (cs["base"] / cs["time"]) if cs["passed"] and cs["time"] else None}
            else:
                live = True
                base = run_code(item["unoptimized"], item)
                r = score_one(base, run_code(CLAUDE_OUTPUTS[i], item), CLAUDE_OUTPUTS[i], item["unoptimized"])
                claude = {"passed": r["passed"], "speed": r["speed"]}
                base_ok = base_ok and bool(base.get("passed"))
            if base_ok:
                rows.append((item, small, claude))
    n = len(rows)

    def stat(which):
        rs = [r[1] if which == "small" else r[2] for r in rows]
        passed = [r for r in rs if r["passed"]]
        sp = [r["speed"] for r in passed if r["speed"]]
        faster = sum(1 for r in passed if r["speed"] and r["speed"] > FASTER_THRESHOLD)
        return (f"{len(passed)}/{n}", f"{faster / n:.1%}", f"{statistics.median(sp):.1f}×" if sp else "n/a")

    sm, cl = stat("small"), stat("claude")
    cats = {}
    for item, small, claude in rows:
        d = cats.setdefault(item["category"], [0, 0, 0])
        d[0] += 1
        d[1] += small["passed"]
        d[2] += claude["passed"]
    cat_rows = "".join(
        f'<tr><td>{e(k)}</td><td class="n">{v[0]}</td><td class="n">{v[1]}</td><td class="n">{v[2]}</td></tr>'
        for k, v in sorted(cats.items())
    )
    src = "scored just now" if live else "from the stored evaluation results"
    out = (
        f'<p>{n} built-in examples (one per distinct function), {src}, using the same harness as the main evaluation. '
        'This is a small demo set, not a benchmark.</p>'
        '<table class="m"><thead><tr><th>Model</th><th class="n">Tests passed</th><th class="n">Correct and faster</th>'
        '<th class="n">Median speedup</th></tr></thead><tbody>'
        f'<tr><td>Small model (CodeT5)</td><td class="n">{sm[0]}</td><td class="n">{sm[1]}</td><td class="n">{sm[2]}</td></tr>'
        f'<tr><td>Claude (pre-generated)</td><td class="n">{cl[0]}</td><td class="n">{cl[1]}</td><td class="n">{cl[2]}</td></tr>'
        '</tbody></table>'
        '<table class="m"><thead><tr><th>Category</th><th class="n">Items</th><th class="n">Small model passed</th>'
        f'<th class="n">Claude passed</th></tr></thead><tbody>{cat_rows}</tbody></table>'
        f'<div class="foot">Small-model median latency on these items: {statistics.median(lat):,.0f} ms. '
        'Claude has no latency figure because its answers were pre-generated.</div>'
    )
    SUMMARY["html"] = out
    return out


# =====================================================================
# UI
# =====================================================================
THEME = gr.themes.Soft(primary_hue="indigo", secondary_hue="blue", neutral_hue="slate",
                       font=["Inter", "system-ui", "sans-serif"])
_style = {"theme": THEME, "css": CSS}
if "css" in inspect.signature(gr.Blocks.launch).parameters:   # Gradio 6 moved theme/css to launch()
    blocks_kwargs, launch_kwargs = {}, dict(_style)
else:
    blocks_kwargs, launch_kwargs = dict(_style), {}
launch_kwargs["server_port"] = PORT

first_id = ORDER[0]
first = ITEMS[first_id]

with gr.Blocks(title="Python Code Optimizer - Comparison", **blocks_kwargs) as demo:
    gr.HTML(HEADER)
    with gr.Accordion("How it works", open=True):
        gr.Markdown(HOWTO)

    gr.HTML(section(1, "Choose an input"))
    mode = gr.Radio([MODE_EX, MODE_PASTE], value=MODE_EX, label="Input", show_label=False)

    with gr.Column(visible=True) as ex_group:
        with gr.Row():
            dropdown = gr.Dropdown(choices=CHOICES, value=first_id, label="Function to optimize", scale=5, interactive=True)
            random_btn = gr.Button("🎲 Random", scale=1, variant="secondary")
        info = gr.HTML(info_html(first))

    with gr.Column(visible=False) as paste_group:
        p_code = gr.Code(value=SAMPLE_CODE, language="python", label="Your function", lines=10, interactive=True)
        with gr.Row():
            p_calls = gr.Textbox(value=SAMPLE_CALLS, lines=4, label="Example calls (one per line)",
                                 info="Used to check the rewrite still gives the same answers.")
            p_bench = gr.Textbox(value=SAMPLE_BENCH, lines=4, label="Benchmark call (a larger input)",
                                 info="Used to time the functions. Leave blank to time the first example call.")

    gr.HTML(section(2, "Optimize"))
    run_btn = gr.Button("⚡ Optimize", variant="primary", size="lg")

    with gr.Row(equal_height=True):
        orig_box = gr.Code(value=first["unoptimized"], language="python", label="Original", interactive=False, lines=16)
        small_box = gr.Code(value="", language="python", label="Small model (CodeT5, live)", interactive=False, lines=16)
        claude_box = gr.Code(value=CLAUDE_OUTPUTS[first_id], language="python", label="Claude (pre-generated)",
                             interactive=False, lines=16)

    gr.HTML(section(3, "Results"))
    results = gr.HTML(EMPTY_HTML)

    with gr.Accordion("Head-to-head on all built-in examples", open=False):
        gr.Markdown("Scores both models on every built-in example. This can take a few minutes the first time.")
        sum_btn = gr.Button("Run comparison", variant="secondary")
        sum_out = gr.HTML()
    with gr.Accordion("Small model: overall evaluation results", open=False):
        gr.HTML(overall_html())

    dropdown.change(on_select, dropdown, [orig_box, small_box, claude_box, info, results])
    random_btn.click(lambda: random.choice(ORDER), None, dropdown)
    mode.change(clear_for_mode, mode, [small_box, claude_box, results, ex_group, paste_group]).then(
        lambda m, i, c: (ITEMS[i]["unoptimized"] if m == MODE_EX else c, CLAUDE_OUTPUTS[i] if m == MODE_EX else CLAUDE_NA),
        [mode, dropdown, p_code], [orig_box, claude_box])
    p_code.change(lambda m, c: c if m == MODE_PASTE else gr.update(), [mode, p_code], orig_box)
    run_btn.click(lambda: "", None, results).then(
        optimize, [mode, dropdown, p_code, p_calls, p_bench], [small_box, claude_box, results])
    sum_btn.click(summarize, None, sum_out)

if __name__ == "__main__":
    demo.launch(**launch_kwargs)