"""Generated dynamic-programming families: 5 patterns x 20 variants."""

from __future__ import annotations

from .gen_common import make, rng

EXAMPLES = []


def _ref_coin_ways(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for t in range(c, amount + 1):
            dp[t] += dp[t - c]
    return dp[amount]


def _ref_lcs(a, b):
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def _ref_knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        for t in range(capacity, weights[i] - 1, -1):
            candidate = dp[t - weights[i]] + values[i]
            if candidate > dp[t]:
                dp[t] = candidate
    return dp[capacity]


def _ref_min_path(grid):
    rows = len(grid)
    cols = len(grid[0])
    dp = [0] * cols
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if i == rows - 1 and j == cols - 1:
                dp[j] = grid[i][j]
            elif i == rows - 1:
                dp[j] = grid[i][j] + dp[j + 1]
            elif j == cols - 1:
                dp[j] = grid[i][j] + dp[j]
            else:
                dp[j] = grid[i][j] + min(dp[j], dp[j + 1])
    return dp[0]


def _fib(variants):
    unopt = """
def __NAME__(n):
    if n < 2:
        return n
    return __NAME__(n - 1) + __NAME__(n - 2)
"""
    opt = """
def __NAME__(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
"""
    for i in range(variants):
        n = 18 + i % 10
        check = 5 + i % 10
        a, b = 0, 1
        for _ in range(check):
            a, b = b, a + b
        expected = a
        EXAMPLES.append(make(
            f"gen_fib_{i:02d}", "dynamic-programming",
            "Compute Fibonacci iteratively in O(n) instead of recomputing overlapping "
            "subproblems in the naive recursion.",
            "Return the n-th Fibonacci number with F(0)=0 and F(1)=1.",
            "O(2^n) time, O(n) space", "O(n) time, O(1) space",
            unopt, opt,
            [
                {"args": [0], "expected": 0},
                {"args": [1], "expected": 1},
                {"args": [2], "expected": 1},
                {"args": [10], "expected": 55},
                {"args": [check], "expected": expected},
            ],
            {"args": [n]},
        ))


def _coin_change_ways(variants):
    unopt = """
def __NAME__(coins, amount):
    def rec(i, remaining):
        if remaining == 0:
            return 1
        if i == len(coins) or remaining < 0:
            return 0
        return rec(i, remaining - coins[i]) + rec(i + 1, remaining)
    return rec(0, amount)
"""
    opt = """
def __NAME__(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for t in range(c, amount + 1):
            dp[t] += dp[t - c]
    return dp[amount]
"""
    coin_sets = [[1, 2, 5], [1, 3, 4], [2, 3, 5], [1, 2, 3]]
    for i in range(variants):
        coins = coin_sets[i % len(coin_sets)]
        amount = 12 + i % 5
        test_coins = coin_sets[(i + 1) % len(coin_sets)]
        test_amount = 5 + i % 4
        EXAMPLES.append(make(
            f"gen_coin_ways_{i:02d}", "dynamic-programming",
            "Count combinations with a bottom-up O(amount * k) table instead of "
            "re-exploring the same states recursively.",
            "Return the number of unordered coin combinations that sum to amount.",
            "O(k^amount) time, O(amount) space", "O(amount * k) time, O(amount) space",
            unopt, opt,
            [
                {"args": [test_coins, test_amount],
                 "expected": _ref_coin_ways(test_coins, test_amount)},
                {"args": [[1, 2, 5], 5], "expected": 4},
                {"args": [[2], 3], "expected": 0},
                {"args": [[], 0], "expected": 1},
            ],
            {"args": [coins, amount]},
        ))


def _lcs_length(variants):
    unopt = """
def __NAME__(a, b):
    if not a or not b:
        return 0
    if a[-1] == b[-1]:
        return 1 + __NAME__(a[:-1], b[:-1])
    return max(__NAME__(a[:-1], b), __NAME__(a, b[:-1]))
"""
    opt = """
def __NAME__(a, b):
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]
"""
    for i in range(variants):
        r = rng(400 + i)
        length = 9 + i % 3
        a = "".join(r.choice("abcde") for _ in range(length))
        b = "".join(r.choice("abcde") for _ in range(length))
        rt = rng(500 + i)
        ta = "".join(rt.choice("abcde") for _ in range(5 + i % 3))
        tb = "".join(rt.choice("abcde") for _ in range(5 + i % 3))
        EXAMPLES.append(make(
            f"gen_lcs_length_{i:02d}", "dynamic-programming",
            "Fill an O(m * n) DP table instead of recursively branching on every "
            "mismatching suffix pair.",
            "Return the length of the longest common subsequence of strings a and b.",
            "O(2^(m+n)) time, O(m+n) space", "O(m * n) time, O(n) space",
            unopt, opt,
            [
                {"args": [ta, tb], "expected": _ref_lcs(ta, tb)},
                {"args": ["abcde", "ace"], "expected": 3},
                {"args": ["abc", "abc"], "expected": 3},
                {"args": ["abc", "def"], "expected": 0},
                {"args": ["", "abc"], "expected": 0},
            ],
            {"args": [a, b]},
        ))


def _knapsack_01(variants):
    unopt = """
def __NAME__(weights, values, capacity):
    def rec(i, w):
        if i == len(weights):
            return 0
        best = rec(i + 1, w)
        if weights[i] <= w:
            candidate = values[i] + rec(i + 1, w - weights[i])
            if candidate > best:
                best = candidate
        return best
    return rec(0, capacity)
"""
    opt = """
def __NAME__(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        wt = weights[i]
        val = values[i]
        for w in range(capacity, wt - 1, -1):
            candidate = dp[w - wt] + val
            if candidate > dp[w]:
                dp[w] = candidate
    return dp[capacity]
"""
    for i in range(variants):
        n = 14 + i % 5
        capacity = 25 + i % 6
        weights = [(j * 7 + i) % 10 + 1 for j in range(n)]
        values = [(j * 11 + i * 3) % 20 + 1 for j in range(n)]
        tn = 4 + i % 4
        tw = [(j * 5 + i) % 8 + 1 for j in range(tn)]
        tv = [(j * 7 + i * 2) % 15 + 1 for j in range(tn)]
        tc = 8 + i % 5
        EXAMPLES.append(make(
            f"gen_knapsack_01_{i:02d}", "dynamic-programming",
            "Use a bottom-up O(n * capacity) table instead of exploring every "
            "include/exclude subset.",
            "Return the maximum value of items that fit within capacity (0/1 knapsack).",
            "O(2^n) time, O(n) space", "O(n * capacity) time, O(capacity) space",
            unopt, opt,
            [
                {"args": [tw, tv, tc], "expected": _ref_knapsack(tw, tv, tc)},
                {"args": [[1, 3, 4, 5], [1, 4, 5, 7], 7], "expected": 9},
                {"args": [[10, 20, 30], [60, 100, 120], 50], "expected": 220},
                {"args": [[], [], 10], "expected": 0},
            ],
            {"args": [weights, values, capacity]},
        ))


def _min_path_sum(variants):
    unopt = """
def __NAME__(grid):
    rows = len(grid)
    cols = len(grid[0])
    def rec(i, j):
        if i == rows - 1 and j == cols - 1:
            return grid[i][j]
        best = None
        if i + 1 < rows:
            best = rec(i + 1, j)
        if j + 1 < cols:
            right = rec(i, j + 1)
            if best is None or right < best:
                best = right
        return grid[i][j] + best
    return rec(0, 0)
"""
    opt = """
def __NAME__(grid):
    rows = len(grid)
    cols = len(grid[0])
    dp = [0] * cols
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if i == rows - 1 and j == cols - 1:
                dp[j] = grid[i][j]
            elif i == rows - 1:
                dp[j] = grid[i][j] + dp[j + 1]
            elif j == cols - 1:
                dp[j] = grid[i][j] + dp[j]
            else:
                dp[j] = grid[i][j] + min(dp[j], dp[j + 1])
    return dp[0]
"""
    for i in range(variants):
        size = 8 + i % 3
        grid = [[(r * 7 + c * 11 + i) % 9 + 1 for c in range(size)]
                for r in range(size)]
        tsize = 3 + i % 2
        tgrid = [[(r * 5 + c * 3 + i) % 9 + 1 for c in range(tsize)]
                 for r in range(tsize)]
        EXAMPLES.append(make(
            f"gen_min_path_sum_{i:02d}", "dynamic-programming",
            "Fill a one-row DP table (O(m * n)) instead of recursively revisiting "
            "every suffix path.",
            "Return the minimum path sum from top-left to bottom-right moving only right or down.",
            "O(2^(m+n)) time, O(m+n) space", "O(m * n) time, O(n) space",
            unopt, opt,
            [
                {"args": [tgrid], "expected": _ref_min_path(tgrid)},
                {"args": [[[1, 3, 1], [1, 5, 1], [4, 2, 1]]], "expected": 7},
                {"args": [[[1, 2], [3, 4]]], "expected": 7},
                {"args": [[[5]]], "expected": 5},
            ],
            {"args": [grid]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _fib(variants)
    _coin_change_ways(variants)
    _lcs_length(variants)
    _knapsack_01(variants)
    _min_path_sum(variants)
    return EXAMPLES


EXAMPLES = build(20)
