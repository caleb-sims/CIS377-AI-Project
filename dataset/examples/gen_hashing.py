"""Generated hashing families: 5 proven patterns x 20 data variants each."""

from __future__ import annotations

from .gen_common import make

EXAMPLES = []


def _ref_subarray_count(nums, target):
    count = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total == target:
                count += 1
    return count


def _two_sum(variants):
    unopt = """
def __NAME__(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    opt = """
def __NAME__(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []
"""
    for i in range(variants):
        start = i
        nums = list(range(start, start + 6))
        target = nums[-1] + nums[-2]
        n = 500 + (i % 20) * 25
        EXAMPLES.append(make(
            f"gen_two_sum_{i:02d}", "hashing",
            "Store previously seen values in a dict for O(1) complement lookup "
            "instead of checking every pair.",
            "Return the indices of two values in nums that add up to target, or [].",
            "O(n^2) time, O(1) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [nums, target], "expected": [4, 5]},
                {"args": [nums, -1], "expected": []},
                {"args": [[1, 2, 3, 4], 7], "expected": [2, 3]},
            ],
            {"args": [list(range(n)), 2 * n - 3]},
        ))


def _has_duplicate(variants):
    unopt = """
def __NAME__(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
"""
    opt = """
def __NAME__(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
"""
    for i in range(variants):
        start = i
        n = 300 + (i % 20) * 20
        EXAMPLES.append(make(
            f"gen_has_duplicate_{i:02d}", "hashing",
            "Track seen values in a set (O(n)) instead of comparing every pair (O(n^2)).",
            "Return True if nums contains any repeated value.",
            "O(n^2) time, O(1) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [[start, start + 1, start + 2]], "expected": False},
                {"args": [[start, start + 1, start]], "expected": True},
                {"args": [[]], "expected": False},
                {"args": [[start, start]], "expected": True},
            ],
            {"args": [list(range(n)) + [n // 2]]},
        ))


def _count_frequency(variants):
    unopt = """
def __NAME__(nums):
    pairs = []
    for x in nums:
        found = False
        for item in pairs:
            if item[0] == x:
                item[1] += 1
                found = True
                break
        if not found:
            pairs.append([x, 1])
    return {x: c for x, c in pairs}
"""
    opt = """
def __NAME__(nums):
    from collections import Counter
    return dict(Counter(nums))
"""
    for i in range(variants):
        start = i
        n = 1200 + (i % 20) * 30
        EXAMPLES.append(make(
            f"gen_count_frequency_{i:02d}", "hashing",
            "Count with collections.Counter (O(n)) instead of scanning a list of "
            "counts for every element (O(n^2)).",
            "Return a dict mapping each value in nums to its frequency.",
            "O(n^2) time, O(n) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [["k%d" % start, "k%d" % start, "k%d" % (start + 1)]],
                 "expected": {"k%d" % start: 2, "k%d" % (start + 1): 1}},
                {"args": [["a", "b", "a"]], "expected": {"a": 2, "b": 1}},
                {"args": [["a", "a", "b", "c", "c"]], "expected": {"a": 2, "b": 1, "c": 2}},
                {"args": [[]], "expected": {}},
            ],
            {"args": [[j % (50 + i % 5) for j in range(n)]]},
        ))


def _dedupe_preserve_order(variants):
    unopt = """
def __NAME__(nums):
    out = []
    for x in nums:
        if x not in out:
            out.append(x)
    return out
"""
    opt = """
def __NAME__(nums):
    seen = set()
    out = []
    for x in nums:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
"""
    for i in range(variants):
        start = i
        n = 1000 + (i % 20) * 20
        EXAMPLES.append(make(
            f"gen_dedupe_order_{i:02d}", "hashing",
            "Use a set for membership and keep a list for order (O(n)) instead of "
            "searching the output list for every element (O(n^2)).",
            "Return the distinct values of nums in first-seen order.",
            "O(n^2) time, O(n) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [[start, start, start + 1, start]], "expected": [start, start + 1]},
                {"args": [[1, 2, 1, 3, 2]], "expected": [1, 2, 3]},
                {"args": [["a", "b", "a"]], "expected": ["a", "b"]},
                {"args": [[]], "expected": []},
            ],
            {"args": [[j % (100 + i % 10) for j in range(n)]]},
        ))


def _subarray_sum_count(variants):
    unopt = """
def __NAME__(nums, k):
    count = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total == k:
                count += 1
    return count
"""
    opt = """
def __NAME__(nums, k):
    from collections import defaultdict
    counts = defaultdict(int)
    counts[0] = 1
    prefix = 0
    total = 0
    for x in nums:
        prefix += x
        total += counts[prefix - k]
        counts[prefix] += 1
    return total
"""
    for i in range(variants):
        n = 400 + (i % 20) * 10
        test_nums = [(j * 3 + i) % 7 - 3 for j in range(4 + i % 4)]
        test_target = i % 5 - 2
        EXAMPLES.append(make(
            f"gen_subarray_sum_count_{i:02d}", "hashing",
            "Count matching subarray sums with a prefix-sum frequency table (O(n)) "
            "instead of summing every subarray (O(n^2)).",
            "Return the number of contiguous subarrays whose sum equals k.",
            "O(n^2) time, O(1) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [test_nums, test_target],
                 "expected": _ref_subarray_count(test_nums, test_target)},
                {"args": [[1, 1, 1], 2], "expected": 2},
                {"args": [[1, 2, 3], 3], "expected": 2},
                {"args": [[1, -1, 0], 0], "expected": 3},
                {"args": [[], 0], "expected": 0},
            ],
            {"args": [[j % 5 - 2 for j in range(n)], 3]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _two_sum(variants)
    _has_duplicate(variants)
    _count_frequency(variants)
    _dedupe_preserve_order(variants)
    _subarray_sum_count(variants)
    return EXAMPLES


EXAMPLES = build(20)
