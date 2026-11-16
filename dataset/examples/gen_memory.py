"""Generated memory/lazy families: 5 generator patterns x 20 variants."""

from __future__ import annotations

from .gen_common import make

EXAMPLES = []


def _squares(variants):
    unopt = """
def __NAME__(n):
    return [i * i for i in range(n)]
"""
    opt = """
def __NAME__(n):
    for i in range(n):
        yield i * i
"""
    for i in range(variants):
        n = 10000 + (i % 20) * 500
        test_n = 3 + i % 4
        EXAMPLES.append(make(
            f"gen_squares_lazy_{i:02d}", "memory",
            "Yield squares lazily instead of allocating the entire result list.",
            "Yield 0^2, 1^2, ..., (n-1)^2 lazily.",
            "O(n) time, O(n) space (full list)", "O(1) space (lazy)",
            unopt, opt,
            [
                {"args": [test_n], "expected": [x * x for x in range(test_n)]},
                {"args": [5], "expected": [0, 1, 4, 9, 16]},
                {"args": [0], "expected": []},
                {"args": [1], "expected": [0]},
            ],
            {"args": [n]}, materialize=True,
        ))


def _even_filter(variants):
    unopt = """
def __NAME__(nums):
    out = []
    for x in nums:
        if x % 2 == 0:
            out.append(x)
    return out
"""
    opt = """
def __NAME__(nums):
    for x in nums:
        if x % 2 == 0:
            yield x
"""
    for i in range(variants):
        n = 10000 + (i % 20) * 500
        test = list(range(8 + i % 4))
        EXAMPLES.append(make(
            f"gen_even_filter_lazy_{i:02d}", "memory",
            "Yield even values lazily instead of building the full filtered list.",
            "Yield the even values of nums in order.",
            "O(n) time, O(n) space (full list)", "O(1) space (lazy)",
            unopt, opt,
            [
                {"args": [test], "expected": [x for x in test if x % 2 == 0]},
                {"args": [[1, 2, 3, 4]], "expected": [2, 4]},
                {"args": [[]], "expected": []},
                {"args": [[1, 3]], "expected": []},
            ],
            {"args": [list(range(n))]}, materialize=True,
        ))


def _running_sum(variants):
    unopt = """
def __NAME__(nums):
    out = []
    total = 0
    for x in nums:
        total += x
        out.append(total)
    return out
"""
    opt = """
def __NAME__(nums):
    total = 0
    for x in nums:
        total += x
        yield total
"""
    for i in range(variants):
        n = 10000 + (i % 20) * 500
        test = list(range(1, 6 + i % 4))
        expected = []
        total = 0
        for x in test:
            total += x
            expected.append(total)
        EXAMPLES.append(make(
            f"gen_running_sum_lazy_{i:02d}", "memory",
            "Yield prefix sums lazily instead of materializing the full list.",
            "Yield the running total after each element of nums.",
            "O(n) time, O(n) space (full list)", "O(1) space (lazy)",
            unopt, opt,
            [
                {"args": [test], "expected": expected},
                {"args": [[1, 2, 3, 4]], "expected": [1, 3, 6, 10]},
                {"args": [[]], "expected": []},
                {"args": [[5]], "expected": [5]},
            ],
            {"args": [list(range(n))]}, materialize=True,
        ))


def _take_while_positive(variants):
    unopt = """
def __NAME__(nums):
    out = []
    for x in nums:
        if x <= 0:
            break
        out.append(x)
    return out
"""
    opt = """
def __NAME__(nums):
    for x in nums:
        if x <= 0:
            break
        yield x
"""
    for i in range(variants):
        n = 10000 + (i % 20) * 500
        test = list(range(1, 5 + i % 4)) + [0, 9]
        expected = list(range(1, 5 + i % 4))
        EXAMPLES.append(make(
            f"gen_take_positive_lazy_{i:02d}", "memory",
            "Yield the leading positive values lazily instead of building a list.",
            "Yield values of nums up to the first non-positive value.",
            "O(n) time, O(n) space (full list)", "O(1) space (lazy)",
            unopt, opt,
            [
                {"args": [test], "expected": expected},
                {"args": [[1, 2, 0, 3]], "expected": [1, 2]},
                {"args": [[-1, 2]], "expected": []},
                {"args": [[]], "expected": []},
            ],
            {"args": [list(range(1, n))]}, materialize=True,
        ))


def _dedupe(variants):
    unopt = """
def __NAME__(nums):
    seen = set()
    out = []
    for x in nums:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
"""
    opt = """
def __NAME__(nums):
    seen = set()
    for x in nums:
        if x not in seen:
            seen.add(x)
            yield x
"""
    for i in range(variants):
        n = 10000
        modulus = 200 + i % 50
        EXAMPLES.append(make(
            f"gen_dedupe_lazy_{i:02d}", "memory",
            "Yield first occurrences lazily instead of materializing the whole "
            "deduplicated list.",
            "Yield distinct values of nums in first-seen order.",
            "O(n) time, O(n) space (full list)", "O(1) output space (lazy)",
            unopt, opt,
            [
                {"args": [[1, 2, 1, 3, 2]], "expected": [1, 2, 3]},
                {"args": [[5, 5]], "expected": [5]},
                {"args": [["a", "b", "a"]], "expected": ["a", "b"]},
                {"args": [[]], "expected": []},
            ],
            {"args": [[j % modulus for j in range(n)]]}, materialize=True,
        ))


def build(variants=20):
    EXAMPLES.clear()
    _squares(variants)
    _even_filter(variants)
    _running_sum(variants)
    _take_while_positive(variants)
    _dedupe(variants)
    return EXAMPLES


EXAMPLES = build(20)
