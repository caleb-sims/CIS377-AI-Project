"""
WORK IN PROGRESS

harness.py - run tests and time Python functions safely.

Usage from your own code:
    from harness import evaluate, compare

    problem = {
        "tests": ["assert has_dup([1,2,3]) == False"],   # MBPP test_list
        "test_setup": "",                                # MBPP test_setup_code
        "bench_setup": "data = list(range(3000))",       # built once, NOT timed
        "bench_stmt": "has_dup(data)",                   # this is what gets timed
    }
    result = compare(slow_code, fast_code, problem)

Each candidate runs in its own subprocess, so infinite loops, crashes and
memory blowups can't take down your session.
"""
import hashlib
import json
import os
import statistics
import subprocess
import sys
import timeit

TEST_TIMEOUT_S = 10      # wall-clock limit for the whole subprocess
MEM_LIMIT_MB = 1024      # Linux/Mac only (Colab/Kaggle are Linux)


# --------------------------------------------------------------------------
# Worker: runs INSIDE the subprocess. Executes untrusted code.
# --------------------------------------------------------------------------
def _worker():
    payload = json.load(sys.stdin)
    real_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")  # silence prints from candidate code

    result = {"status": "ok", "error": None, "runtime": None, "bench_hash": None}

    def finish():
        real_stdout.write(json.dumps(result))
        real_stdout.flush()

    try:
        import resource
        limit = MEM_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except Exception:
        pass  # Windows: no resource module

    ns = {}
    try:
        exec(payload["code"], ns)
    except BaseException as e:
        result.update(status="error", error=f"{type(e).__name__}: {e}")
        return finish()

    # 1) correctness
    try:
        if payload["test_setup"]:
            exec(payload["test_setup"], ns)
        for t in payload["tests"]:
            exec(t, ns)
    except AssertionError:
        result.update(status="wrong_answer", error="AssertionError")
        return finish()
    except BaseException as e:
        result.update(status="error", error=f"{type(e).__name__}: {e}")
        return finish()

    # 2) timing (only if a benchmark was provided)
    if payload.get("bench_stmt"):
        try:
            exec(payload.get("bench_setup") or "", ns)

            # fingerprint the output so compare() can check slow == fast on the big input
            out = eval(payload["bench_stmt"], ns)
            result["bench_hash"] = hashlib.md5(repr(out).encode()).hexdigest()

            timer = timeit.Timer(payload["bench_stmt"], globals=ns)
            number, _ = timer.autorange()          # loops so each repeat takes >= 0.2s
            number = max(1, min(number, 100000))
            timer.timeit(number)                   # warmup, discarded
            times = [t / number for t in timer.repeat(repeat=payload["repeats"], number=number)]
            result["runtime"] = statistics.median(times)
            result["runtime_spread"] = (max(times) - min(times)) / result["runtime"]
        except BaseException as e:
            result.update(status="error", error=f"bench {type(e).__name__}: {e}")
    finish()


# --------------------------------------------------------------------------
# Host side
# --------------------------------------------------------------------------
def evaluate(code, problem, repeats=7, timeout=TEST_TIMEOUT_S):
    """Run tests (and timing) for one code string. Returns a dict with:
    status: ok | wrong_answer | error | timeout
    runtime: median seconds per call (None if not benchmarked / failed)
    """
    payload = {
        "code": code,
        "tests": problem["tests"],
        "test_setup": problem.get("test_setup", ""),
        "bench_setup": problem.get("bench_setup", ""),
        "bench_stmt": problem.get("bench_stmt", ""),
        "repeats": repeats,
    }
    try:
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--worker"],
            input=json.dumps(payload), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "timeout", "runtime": None, "bench_hash": None}

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        err = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "crash"
        return {"status": "error", "error": err, "runtime": None, "bench_hash": None}


def compare(slow_code, fast_code, problem, repeats=7, min_speedup=1.5):
    """Evaluate both versions and report whether `fast` is correct AND faster."""
    slow = evaluate(slow_code, problem, repeats)
    fast = evaluate(fast_code, problem, repeats)

    out = {"slow": slow, "fast": fast, "speedup": None,
           "correct": fast["status"] == "ok",
           "same_bench_output": None, "faster": False}

    if slow["runtime"] and fast["runtime"]:
        out["speedup"] = slow["runtime"] / fast["runtime"]
        out["same_bench_output"] = slow["bench_hash"] == fast["bench_hash"]
        out["faster"] = out["speedup"] >= min_speedup
    out["correct_and_faster"] = bool(
        out["correct"] and out["faster"] and out["same_bench_output"]
    )
    return out


if __name__ == "__main__":
    if "--worker" in sys.argv:
        _worker()
