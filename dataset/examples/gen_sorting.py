"""Generated sorting families: 5 proven patterns x 20 data variants each."""

from __future__ import annotations

from .gen_common import make, rng

EXAMPLES = []


def _ref_min_abs(nums):
    if len(nums) < 2:
        return None
    ordered = sorted(nums)
    return min(ordered[i] - ordered[i - 1] for i in range(1, len(ordered)))


def _bubble_sort(variants):
    unopt = """
def __NAME__(nums):
    out = list(nums)
    n = len(out)
    for i in range(n):
        for j in range(0, n - i - 1):
            if out[j] > out[j + 1]:
                out[j], out[j + 1] = out[j + 1], out[j]
    return out
"""
    opt = """
def __NAME__(nums):
    return sorted(nums)
"""
    for i in range(variants):
        n = 300 + (i % 20) * 10
        sample = rng(i).sample(range(1000), 6)
        EXAMPLES.append(make(
            f"gen_bubble_sort_{i:02d}", "sorting",
            "Use the C-implemented sorted() (O(n log n)) instead of bubble sort (O(n^2)).",
            "Return nums sorted in ascending order.",
            "O(n^2) time, O(n) space", "O(n log n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": sorted(sample)},
                {"args": [[3, 1, 2]], "expected": [1, 2, 3]},
                {"args": [[5, 4, 3, 2, 1]], "expected": [1, 2, 3, 4, 5]},
                {"args": [[]], "expected": []},
            ],
            {"args": [[(j * 37 + i * 11) % 100 for j in range(n)]]},
        ))


def _insertion_sort(variants):
    unopt = """
def __NAME__(nums):
    out = list(nums)
    for i in range(1, len(out)):
        key = out[i]
        j = i - 1
        while j >= 0 and out[j] > key:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
"""
    opt = """
def __NAME__(nums):
    return sorted(nums)
"""
    for i in range(variants):
        n = 350 + (i % 20) * 10
        sample = rng(100 + i).sample(range(1000), 6)
        EXAMPLES.append(make(
            f"gen_insertion_sort_{i:02d}", "sorting",
            "Use the C-implemented sorted() (O(n log n)) instead of Python insertion sort (O(n^2)).",
            "Return nums sorted in ascending order.",
            "O(n^2) time, O(n) space", "O(n log n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": sorted(sample)},
                {"args": [[2, 3, 1]], "expected": [1, 2, 3]},
                {"args": [[1, 1, 2]], "expected": [1, 1, 2]},
                {"args": [[]], "expected": []},
            ],
            {"args": [[(j * 53 + i * 17) % 100 for j in range(n)]]},
        ))


def _kth_smallest(variants):
    unopt = """
def __NAME__(nums, k):
    remaining = list(nums)
    for _ in range(k - 1):
        best_i = 0
        for j in range(1, len(remaining)):
            if remaining[j] < remaining[best_i]:
                best_i = j
        remaining.pop(best_i)
    best = remaining[0]
    for x in remaining:
        if x < best:
            best = x
    return best
"""
    opt = """
def __NAME__(nums, k):
    import heapq
    return heapq.nsmallest(k, nums)[-1]
"""
    for i in range(variants):
        n = 700 + (i % 20) * 20
        k = 20 + i % 20
        sample = rng(200 + i).sample(range(500), 9)
        kk = i % 9 + 1
        EXAMPLES.append(make(
            f"gen_kth_smallest_{i:02d}", "sorting",
            "Keep a size-k heap with heapq.nsmallest (O(n log k)) instead of repeated "
            "minimum scans and removals (O(n * k)).",
            "Return the kth smallest value in nums (1-indexed).",
            "O(n * k) time, O(n) space", "O(n log k) time, O(k) space",
            unopt, opt,
            [
                {"args": [sample, kk], "expected": sorted(sample)[kk - 1]},
                {"args": [[3, 1, 2], 1], "expected": 1},
                {"args": [[3, 1, 2], 3], "expected": 3},
                {"args": [[5, 4, 3, 2, 1], 2], "expected": 2},
            ],
            {"args": [[(j * 37 + i * 11) % 1000 for j in range(n)], k]},
        ))


def _binary_search(variants):
    unopt = """
def __NAME__(nums, target):
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1
"""
    opt = """
def __NAME__(nums, target):
    import bisect
    i = bisect.bisect_left(nums, target)
    if i < len(nums) and nums[i] == target:
        return i
    return -1
"""
    for i in range(variants):
        start = i
        sample = list(range(start, start + 10))
        n = 1200 + (i % 20) * 20
        EXAMPLES.append(make(
            f"gen_binary_search_{i:02d}", "sorting",
            "Use bisect (O(log n)) on the sorted list instead of a linear scan (O(n)).",
            "Return the index of target in the sorted list nums, or -1.",
            "O(n) time, O(1) space", "O(log n) time, O(1) space",
            unopt, opt,
            [
                {"args": [sample, start + 4], "expected": 4},
                {"args": [sample, start + 100], "expected": -1},
                {"args": [[1, 3, 5, 7], 5], "expected": 2},
                {"args": [[1, 3, 5, 7], 2], "expected": -1},
                {"args": [[], 1], "expected": -1},
            ],
            {"args": [list(range(n)), n]},
        ))


def _minimum_absolute_difference(variants):
    unopt = """
def __NAME__(nums):
    best = None
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            d = abs(nums[i] - nums[j])
            if best is None or d < best:
                best = d
    return best
"""
    opt = """
def __NAME__(nums):
    if len(nums) < 2:
        return None
    ordered = sorted(nums)
    best = None
    for i in range(1, len(ordered)):
        d = ordered[i] - ordered[i - 1]
        if best is None or d < best:
            best = d
    return best
"""
    for i in range(variants):
        n = 500 + (i % 20) * 10
        sample = rng(300 + i).sample(range(200), 6)
        EXAMPLES.append(make(
            f"gen_min_abs_diff_{i:02d}", "sorting",
            "Sort once and compare adjacent values (O(n log n)) instead of checking "
            "every pair (O(n^2)).",
            "Return the smallest absolute difference between any two values in nums.",
            "O(n^2) time, O(1) space", "O(n log n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": _ref_min_abs(sample)},
                {"args": [[4, 2, 1, 3]], "expected": 1},
                {"args": [[1, 3, 6, 10, 15]], "expected": 2},
                {"args": [[5, 5]], "expected": 0},
                {"args": [[7]], "expected": None},
            ],
            {"args": [[(j * 37 + i * 11) % 1000 for j in range(n)]]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _bubble_sort(variants)
    _insertion_sort(variants)
    _kth_smallest(variants)
    _binary_search(variants)
    _minimum_absolute_difference(variants)
    return EXAMPLES


EXAMPLES = build(20)
