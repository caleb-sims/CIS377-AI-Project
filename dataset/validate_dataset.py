#!/usr/bin/env python3
"""Validation / testing harness for the code-performance dataset.

For every example this harness:
  1. execs the ``unoptimized`` and ``optimized`` code in isolated namespaces,
  2. runs every correctness test (both versions must match ``expected`` /
     ``acceptable``),
  3. runs the ``benchmark`` input to (a) verify the two versions agree and
     (b) measure original-vs-optimized median wall time and peak memory.

This is the "test then time original vs new" step from the project plan.

Usage:
    python validate_dataset.py [--in data/all.jsonl] [--out reports/validation_report.json]
                               [--runs 3] [--cap 6]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import tracemalloc

TOL = 1e-9


def load_records(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_func(code, name, ns):
    exec(compile(code, name, "exec"), ns)  # noqa: S102
    if name not in ns:
        raise RuntimeError(f"function {name!r} not defined in namespace")
    return ns[name]


def materialize(res, materialize_output):
    return list(res) if materialize_output else res


def deep_eq(a, b):
    """Tolerant structural equality (floats via isclose, sequences elementwise)."""
    if hasattr(a, "tolist") and not isinstance(a, (list, str)):
        a = a.tolist()
    if hasattr(b, "tolist") and not isinstance(b, (list, str)):
        b = b.tolist()
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(deep_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, (set, frozenset)) and isinstance(b, (set, frozenset)):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return False
        return all(deep_eq(a[k], b[k]) for k in a)
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(a, b, rel_tol=TOL, abs_tol=TOL)
        except (TypeError, ValueError):
            return a == b
    return a == b


def check_test(res, test):
    if "acceptable" in test:
        return any(deep_eq(res, cand) for cand in test["acceptable"])
    if "expected" in test:
        return deep_eq(res, test["expected"])
    raise ValueError("test has neither 'expected' nor 'acceptable'")


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2.0


def time_call(fn, args, runs, cap):
    """Return (median_seconds, n_runs_done). Times the call only (so lazy
    generator creation is O(1), matching the semantics the examples claim)."""
    vals = []
    for _ in range(runs):
        t0 = time.perf_counter()
        res = fn(*args)  # noqa: F841
        dt = time.perf_counter() - t0
        vals.append(dt)
        if dt > cap:
            break
    return median(vals), len(vals)


def peak_memory(fn, args):
    tracemalloc.start()
    try:
        fn(*args)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak


def validate_record(rec, runs, cap):
    name = rec["name"]
    mat = rec.get("materialize_output", False)
    errors = []

    ns_u, ns_o = {}, {}
    try:
        fn_u = load_func(rec["unoptimized"], name, ns_u)
        fn_o = load_func(rec["optimized"], name, ns_o)
    except Exception as e:  # noqa: BLE001
        errors.append(f"load: {type(e).__name__}: {e}")
        return {"name": name, "category": rec.get("category"), "correct": False,
                "benchmark_agrees": False, "errors": errors}

    # --- correctness tests ---
    correct = True
    for ti, test in enumerate(rec["tests"]):
        args = test["args"]
        try:
            ru = materialize(fn_u(*args), mat)
            ro = materialize(fn_o(*args), mat)
        except Exception as e:  # noqa: BLE001
            correct = False
            errors.append(f"test[{ti}] raised {type(e).__name__}: {e}")
            continue
        ok_u = check_test(ru, test)
        ok_o = check_test(ro, test)
        if "acceptable" in test:
            if not (ok_u and ok_o):
                correct = False
                errors.append(f"test[{ti}] not acceptable: u={ru!r} o={ro!r}")
        else:
            if not (ok_u and ok_o and deep_eq(ru, ro)):
                correct = False
                errors.append(
                    f"test[{ti}] mismatch: u={ru!r} o={ro!r} ok_u={ok_u} ok_o={ok_o} "
                    f"agree={deep_eq(ru, ro)}"
                )

    # --- benchmark: agreement + timing + memory ---
    bargs = rec["benchmark"]["args"]
    agrees = None
    t_u = t_o = mem_u = mem_o = None
    try:
        ru_b = materialize(fn_u(*bargs), mat)
        ro_b = materialize(fn_o(*bargs), mat)
        agrees = deep_eq(ru_b, ro_b)
        if not agrees:
            errors.append(f"benchmark disagreement: u!=o (types {type(ru_b).__name__}/{type(ro_b).__name__})")
        t_u, _ = time_call(fn_u, bargs, runs, cap)
        t_o, _ = time_call(fn_o, bargs, runs, cap)
        mem_u = peak_memory(fn_u, bargs)
        mem_o = peak_memory(fn_o, bargs)
    except Exception as e:  # noqa: BLE001
        errors.append(f"benchmark raised {type(e).__name__}: {e}")
        correct = False

    result = {
        "name": name,
        "category": rec.get("category"),
        "correct": correct,
        "benchmark_agrees": bool(agrees) if agrees is not None else False,
        "unoptimized_median_s": t_u,
        "optimized_median_s": t_o,
        "errors": errors,
    }
    if t_u and t_o and t_o > 0:
        result["speedup"] = round(t_u / t_o, 3)
    if mem_u is not None and mem_o is not None:
        result["unoptimized_peak_bytes"] = mem_u
        result["optimized_peak_bytes"] = mem_o
        if mem_o > 0:
            result["mem_ratio"] = round(mem_u / mem_o, 3)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", default="data/all.jsonl", dest="infile")
    ap.add_argument("--out", default="reports/validation_report.json")
    ap.add_argument("--runs", type=int, default=3, help="timing runs (median)")
    ap.add_argument("--cap", type=float, default=6.0, help="stop early if a run exceeds this many seconds")
    args = ap.parse_args()

    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    results = []
    for rec in load_records(args.infile):
        results.append(validate_record(rec, args.runs, args.cap))

    n_correct = sum(1 for r in results if r["correct"] and r["benchmark_agrees"])
    speedups = [r["speedup"] for r in results if r.get("speedup")]
    faster = [r for r in results if r.get("speedup") and r["speedup"] > 1.0]
    correct_and_faster = [r for r in faster if r["correct"] and r["benchmark_agrees"]]

    report = {
        "python": sys.version.split()[0],
        "n_examples": len(results),
        "n_correct_and_agreeing": n_correct,
        "n_failed": len(results) - n_correct,
        "median_speedup": round(median(speedups), 3) if speedups else None,
        "pct_correct_and_faster": round(100.0 * len(correct_and_faster) / len(results), 1) if results else 0.0,
        "results": results,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    # --- console summary ---
    print(f"{'name':26} {'cat':18} {'ok':>3} {'u(s)':>10} {'o(s)':>10} {'speedup':>8} {'memx':>7}")
    print("-" * 86)
    for r in results:
        flag = "Y" if (r["correct"] and r["benchmark_agrees"]) else "N"
        u = f"{r['unoptimized_median_s']:.4f}" if r.get("unoptimized_median_s") is not None else "-"
        o = f"{r['optimized_median_s']:.4f}" if r.get("optimized_median_s") is not None else "-"
        sp = f"{r['speedup']:.2f}x" if r.get("speedup") else "-"
        mx = f"{r['mem_ratio']:.1f}x" if r.get("mem_ratio") else "-"
        print(f"{r['name']:26} {r['category']:18} {flag:>3} {u:>10} {o:>10} {sp:>8} {mx:>7}")

    print("-" * 86)
    print(f"total: {len(results)}  correct+agreeing: {n_correct}  "
          f"failed: {len(results) - n_correct}")
    print(f"median speedup: {report['median_speedup']}x   "
          f"% correct AND faster: {report['pct_correct_and_faster']}")

    failed = [r for r in results if not (r["correct"] and r["benchmark_agrees"])]
    if failed:
        print("\nFAILURES:")
        for r in failed:
            print(f"  {r['name']}: {r['errors']}")
    else:
        print("\nAll examples passed correctness + benchmark agreement.")


if __name__ == "__main__":
    main()
