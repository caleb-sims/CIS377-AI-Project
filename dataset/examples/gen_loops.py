"""Generated loop families: 5 sliding-window patterns x 20 variants."""

from __future__ import annotations

from .gen_common import make, rng

EXAMPLES = []


def _ref_max_subarray(nums):
    best = None
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if best is None or total > best:
                best = total
    return best


def _ref_min_subarray_len(nums, target):
    best = None
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total >= target:
                length = j - i + 1
                if best is None or length < best:
                    best = length
                break
    return 0 if best is None else best


def _ref_max_k_window(nums, k):
    best = None
    for i in range(len(nums) - k + 1):
        total = sum(nums[i:i + k])
        if best is None or total > best:
            best = total
    return best


def _ref_longest_unique(s):
    best = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            if s[j] in seen:
                break
            seen.add(s[j])
            if j - i + 1 > best:
                best = j - i + 1
    return best


def _ref_best_stock(prices):
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            profit = prices[j] - prices[i]
            if profit > best:
                best = profit
    return best


def _max_subarray_sum(variants):
    unopt = """
def __NAME__(nums):
    best = None
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if best is None or total > best:
                best = total
    return best
"""
    opt = """
def __NAME__(nums):
    best = nums[0]
    current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        if current > best:
            best = current
    return best
"""
    for i in range(variants):
        n = 600 + (i % 20) * 20
        test = [(j * 7 + i * 3) % 21 - 10 for j in range(7 + i % 4)]
        EXAMPLES.append(make(
            f"gen_max_subarray_{i:02d}", "loops",
            "Use Kadane's one-pass algorithm (O(n)) instead of summing every subarray (O(n^2)).",
            "Return the maximum sum of any non-empty contiguous subarray.",
            "O(n^2) time, O(1) space", "O(n) time, O(1) space",
            unopt, opt,
            [
                {"args": [test], "expected": _ref_max_subarray(test)},
                {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
                {"args": [[1]], "expected": 1},
                {"args": [[-1, -2]], "expected": -1},
            ],
            {"args": [[(j * 37 + i * 11) % 101 - 50 for j in range(n)]]},
        ))


def _min_subarray_len(variants):
    unopt = """
def __NAME__(nums, target):
    best = None
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total >= target:
                length = j - i + 1
                if best is None or length < best:
                    best = length
                break
    return 0 if best is None else best
"""
    opt = """
def __NAME__(nums, target):
    best = None
    total = 0
    start = 0
    for end, x in enumerate(nums):
        total += x
        while total >= target:
            length = end - start + 1
            if best is None or length < best:
                best = length
            total -= nums[start]
            start += 1
    return 0 if best is None else best
"""
    for i in range(variants):
        n = 600 + (i % 20) * 20
        benchmark = [(j * 7 + i) % 10 + 1 for j in range(n)]
        target = sum(benchmark) + 1
        test = [(j * 3 + i) % 9 + 1 for j in range(5 + i % 4)]
        test_target = 10 + i % 5
        EXAMPLES.append(make(
            f"gen_min_subarray_len_{i:02d}", "loops",
            "Maintain a sliding window of positive values (O(n)) instead of trying "
            "every subarray (O(n^2)).",
            "Return the length of the shortest subarray with sum at least target, or 0.",
            "O(n^2) time, O(1) space", "O(n) time, O(1) space",
            unopt, opt,
            [
                {"args": [test, test_target],
                 "expected": _ref_min_subarray_len(test, test_target)},
                {"args": [[2, 3, 1, 2, 4, 3], 7], "expected": 2},
                {"args": [[1, 1, 1], 4], "expected": 0},
                {"args": [[1, 2, 3], 3], "expected": 1},
            ],
            {"args": [benchmark, target]},
        ))


def _max_k_window_sum(variants):
    unopt = """
def __NAME__(nums, k):
    best = None
    for i in range(len(nums) - k + 1):
        total = 0
        for j in range(i, i + k):
            total += nums[j]
        if best is None or total > best:
            best = total
    return best
"""
    opt = """
def __NAME__(nums, k):
    total = sum(nums[:k])
    best = total
    for i in range(k, len(nums)):
        total += nums[i] - nums[i - k]
        if total > best:
            best = total
    return best
"""
    for i in range(variants):
        n = 1500 + (i % 20) * 50
        k = 50 + i % 20
        test = [(j * 7 + i) % 20 for j in range(7 + i % 4)]
        tk = 2 + i % 4
        EXAMPLES.append(make(
            f"gen_max_k_window_{i:02d}", "loops",
            "Slide the window sum in O(1) per step (O(n)) instead of re-summing each window (O(n * k)).",
            "Return the maximum sum of any contiguous window of length k.",
            "O(n * k) time, O(1) space", "O(n) time, O(1) space",
            unopt, opt,
            [
                {"args": [test, tk], "expected": _ref_max_k_window(test, tk)},
                {"args": [[1, 2, 3, 4, 5], 2], "expected": 9},
                {"args": [[1, 2, 3], 3], "expected": 6},
                {"args": [[5], 1], "expected": 5},
            ],
            {"args": [[(j * 37 + i * 11) % 1000 for j in range(n)], k]},
        ))


def _longest_unique_substr(variants):
    unopt = """
def __NAME__(s):
    best = 0
    n = len(s)
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen:
                break
            seen.add(s[j])
            if j - i + 1 > best:
                best = j - i + 1
    return best
"""
    opt = """
def __NAME__(s):
    seen = set()
    best = 0
    start = 0
    for end, c in enumerate(s):
        while c in seen:
            seen.remove(s[start])
            start += 1
        seen.add(c)
        if end - start + 1 > best:
            best = end - start + 1
    return best
"""
    for i in range(variants):
        length = 300 + (i % 20) * 10
        text = "".join(chr(0x4E00 + j) for j in range(length))
        r = rng(800 + i)
        sample = "".join(r.choice("abcdef") for _ in range(6))
        EXAMPLES.append(make(
            f"gen_longest_unique_{i:02d}", "loops",
            "Maintain a sliding window with a set (O(n)) instead of restarting the "
            "scan from every index (O(n^2)).",
            "Return the length of the longest substring without repeating characters.",
            "O(n^2) time, O(k) space", "O(n) time, O(k) space",
            unopt, opt,
            [
                {"args": [sample], "expected": _ref_longest_unique(sample)},
                {"args": ["abcabcbb"], "expected": 3},
                {"args": ["bbbbb"], "expected": 1},
                {"args": ["pwwkew"], "expected": 3},
                {"args": [""], "expected": 0},
            ],
            {"args": [text]},
        ))


def _best_time_stock(variants):
    unopt = """
def __NAME__(prices):
    best = 0
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            if profit > best:
                best = profit
    return best
"""
    opt = """
def __NAME__(prices):
    best = 0
    min_price = None
    for price in prices:
        if min_price is None or price < min_price:
            min_price = price
        elif price - min_price > best:
            best = price - min_price
    return best
"""
    for i in range(variants):
        n = 800 + (i % 20) * 20
        test = [(j * 7 + i * 3) % 50 for j in range(7 + i % 4)]
        EXAMPLES.append(make(
            f"gen_best_stock_{i:02d}", "loops",
            "Track the minimum price so far in one pass (O(n)) instead of checking "
            "every buy/sell pair (O(n^2)).",
            "Return the maximum profit from one buy followed by a later sell, or 0.",
            "O(n^2) time, O(1) space", "O(n) time, O(1) space",
            unopt, opt,
            [
                {"args": [test], "expected": _ref_best_stock(test)},
                {"args": [[7, 1, 5, 3, 6, 4]], "expected": 5},
                {"args": [[7, 6, 4, 3, 1]], "expected": 0},
                {"args": [[1, 2]], "expected": 1},
                {"args": [[]], "expected": 0},
            ],
            {"args": [[(j * 37 + i * 11) % 1000 for j in range(n)]]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _max_subarray_sum(variants)
    _min_subarray_len(variants)
    _max_k_window_sum(variants)
    _longest_unique_substr(variants)
    _best_time_stock(variants)
    return EXAMPLES


EXAMPLES = build(20)
