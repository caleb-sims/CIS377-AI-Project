"""
candidates.py - your hand-written slow/fast pairs. Add one dict per pair.

Keys:
  id          unique name, e.g. "mbpp_11_a"
  task_id     MBPP task id (optional). If given, tests come from MBPP automatically.
  tests       list of assert strings (only needed if no task_id)
  slow, fast  the two versions of the function (same name + signature)
  bench_setup builds a LARGE input (not timed)
  bench_stmt  the call that gets timed
  Don't mutate the input inside bench_stmt.
"""

CANDIDATES = [
    {
        "id": "dup_nested_vs_set",
        "tests": [
            "assert has_dup([1, 2, 3]) == False",
            "assert has_dup([1, 2, 1]) == True",
            "assert has_dup([]) == False",
        ],
        "slow": '''
def has_dup(xs):
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] == xs[j]:
                return True
    return False
''',
        "fast": '''
def has_dup(xs):
    return len(set(xs)) != len(xs)
''',
        "bench_setup": "data = list(range(3000))",
        "bench_stmt": "has_dup(data)",
    },
    # add 20-30 more here ...
]
