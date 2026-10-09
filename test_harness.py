'''
WORK IN PROGRESS
'''

from harness import evaluate, compare

problem = {
    "tests": [
        "assert has_dup([1, 2, 3]) == False",
        "assert has_dup([1, 2, 1]) == True",
        "assert has_dup([]) == False",
    ],
    "bench_setup": "data = list(range(3000))",
    "bench_stmt": "has_dup(data)",
}

SLOW = """
def has_dup(xs):
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] == xs[j]:
                return True
    return False
"""
FAST = """
def has_dup(xs):
    return len(set(xs)) != len(xs)
"""
WRONG = "def has_dup(xs):\n    return False\n"
LOOP = "def has_dup(xs):\n    while True:\n        pass\n"
CRASH = "def has_dup(xs):\n    return 1/0\n"
SYNTAX = "def has_dup(xs) return"

print("--- 1. slow vs fast (expect big speedup) ---")
r = compare(SLOW, FAST, problem)
print(f"speedup={r['speedup']:.0f}x  correct_and_faster={r['correct_and_faster']}")

print("--- 2. identical code twice (expect speedup ~1.0, NOT faster) ---")
speeds = []
for _ in range(5):
    r = compare(FAST, FAST, problem)
    speeds.append(r["speedup"])
print("speedups:", [round(s, 2) for s in speeds], "-> noise band")

print("--- 3. failure modes ---")
for name, code in [("wrong", WRONG), ("infinite loop", LOOP),
                   ("runtime error", CRASH), ("syntax error", SYNTAX)]:
    res = evaluate(code, problem, timeout=3)
    print(f"{name:14s} -> {res['status']}: {res['error']}")
