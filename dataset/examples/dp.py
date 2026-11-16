"""Category: memoization / dynamic programming.

Replace exponential naive recursion with an O(n) iterative DP, a bottom-up table, or
memoization.
"""

EXAMPLES = [
    {
        "name": "fib",
        "category": "dynamic-programming",
        "technique": "Compute the nth Fibonacci number with an iterative two-variable "
                     "recurrence (O(n)) instead of naive exponential recursion.",
        "description": "Return the nth Fibonacci number (fib(0)=0, fib(1)=1).",
        "complexity_before": "O(2^n) time, O(n) space (recursion stack)",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
""".strip(),
        "optimized": """
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 1},
            {"args": [6], "expected": 8},
            {"args": [10], "expected": 55},
            {"args": [20], "expected": 6765},
        ],
        "benchmark": {"args": [22]},
    },
    {
        "name": "climb_stairs",
        "category": "dynamic-programming",
        "technique": "Count ways to climb n stairs with a bottom-up two-variable DP "
                     "(O(n)) instead of naive exponential recursion.",
        "description": "Return the number of distinct ways to reach step n using 1- or 2-step moves (ways(0)=1).",
        "complexity_before": "O(2^n) time, O(n) space (recursion stack)",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def climb_stairs(n):
    if n == 0:
        return 1
    if n == 1:
        return 1
    return climb_stairs(n - 1) + climb_stairs(n - 2)
""".strip(),
        "optimized": """
def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
""".strip(),
        "tests": [
            {"args": [0], "expected": 1},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 2},
            {"args": [4], "expected": 5},
            {"args": [10], "expected": 89},
        ],
        "benchmark": {"args": [25]},
    },
    {
        "name": "edit_distance",
        "category": "dynamic-programming",
        "technique": "Use the classic O(m*n) two-row DP table for Levenshtein distance "
                     "instead of exponential naive recursion.",
        "description": "Return the minimum number of single-character insertions, deletions, or substitutions to turn a into b.",
        "complexity_before": "O(2^(m+n)) time, O(m+n) space",
        "complexity_after": "O(m*n) time, O(n) space",
        "unoptimized": """
def edit_distance(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    cost = 0 if a[0] == b[0] else 1
    return min(
        cost + edit_distance(a[1:], b[1:]),
        1 + edit_distance(a[1:], b),
        1 + edit_distance(a, b[1:]),
    )
""".strip(),
        "optimized": """
def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return dp[n]
""".strip(),
        "tests": [
            {"args": ["", ""], "expected": 0},
            {"args": ["horse", "ros"], "expected": 3},
            {"args": ["intention", "execution"], "expected": 5},
            {"args": ["a", "a"], "expected": 0},
            {"args": ["kitten", "sitting"], "expected": 3},
        ],
        "benchmark": {"args": ["abcdefghij", "abcxyzghij"]},
    },
    {
        "name": "lcs_length",
        "category": "dynamic-programming",
        "technique": "Compute the longest-common-subsequence length with a two-row "
                     "O(m*n) DP table instead of exponential naive recursion.",
        "description": "Return the length of the longest subsequence common to both strings a and b.",
        "complexity_before": "O(2^(m+n)) time, O(m+n) space",
        "complexity_after": "O(m*n) time, O(n) space",
        "unoptimized": """
def lcs_length(a, b):
    if not a or not b:
        return 0
    if a[0] == b[0]:
        return 1 + lcs_length(a[1:], b[1:])
    return max(lcs_length(a[1:], b), lcs_length(a, b[1:]))
""".strip(),
        "optimized": """
def lcs_length(a, b):
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]
""".strip(),
        "tests": [
            {"args": ["abcde", "ace"], "expected": 3},
            {"args": ["", "xyz"], "expected": 0},
            {"args": ["xyz", "xyz"], "expected": 3},
            {"args": ["abc", "def"], "expected": 0},
        ],
        "benchmark": {"args": ["abcdefghijklmn", "nmlkjihgfedcba"]},
    },
    {
        "name": "min_coins",
        "category": "dynamic-programming",
        "technique": "Solve the coin-change problem with a bottom-up O(amount*len(coins)) "
                     "DP table instead of exponential naive recursion.",
        "description": "Return the minimum number of coins to make amount (using unlimited coins), or -1 if impossible.",
        "complexity_before": "O(k^amount) time, O(amount) space",
        "complexity_after": "O(amount * k) time, O(amount) space",
        "unoptimized": """
def min_coins(coins, amount):
    if amount == 0:
        return 0
    if amount < 0:
        return float("inf")
    best = float("inf")
    for c in coins:
        r = min_coins(coins, amount - c)
        if r != -1 and r != float("inf") and r + 1 < best:
            best = r + 1
    return -1 if best == float("inf") else best
""".strip(),
        "optimized": """
def min_coins(coins, amount):
    dp = [0] + [float("inf")] * amount
    for i in range(1, amount + 1):
        for c in coins:
            if c <= i and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
    return dp[amount] if dp[amount] != float("inf") else -1
""".strip(),
        "tests": [
            {"args": [[1, 2, 5], 11], "expected": 3},
            {"args": [[2], 3], "expected": -1},
            {"args": [[1], 5], "expected": 5},
            {"args": [[], 0], "expected": 0},
            {"args": [[1, 5, 10], 9], "expected": 5},
        ],
        "benchmark": {"args": [[2, 3, 5], 15]},
    },
    {
        "name": "coin_change_ways",
        "category": "dynamic-programming",
        "technique": "Count combinations with a bottom-up O(amount * k) DP table instead of "
                     "re-exploring the same (index, remaining) states exponentially.",
        "description": "Return the number of unordered combinations of coins that sum to amount (unlimited coins).",
        "complexity_before": "O(k^amount) time, O(amount) space",
        "complexity_after": "O(amount * k) time, O(amount) space",
        "unoptimized": """
def coin_change_ways(coins, amount):
    def rec(i, remaining):
        if remaining == 0:
            return 1
        if i == len(coins) or remaining < 0:
            return 0
        return rec(i, remaining - coins[i]) + rec(i + 1, remaining)
    return rec(0, amount)
""".strip(),
        "optimized": """
def coin_change_ways(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for i in range(c, amount + 1):
            dp[i] += dp[i - c]
    return dp[amount]
""".strip(),
        "tests": [
            {"args": [[1, 2, 5], 5], "expected": 4},
            {"args": [[2], 3], "expected": 0},
            {"args": [[1, 2], 4], "expected": 3},
            {"args": [[], 0], "expected": 1},
            {"args": [[], 5], "expected": 0},
        ],
        "benchmark": {"args": [[1, 2, 5], 16]},
    },
    {
        "name": "unique_paths",
        "category": "dynamic-programming",
        "technique": "Fill a one-row DP table (O(m * n)) instead of recursively recounting "
                     "the same grid positions exponentially.",
        "description": "Return the number of paths from the top-left to bottom-right of an m by n grid moving only right or down.",
        "complexity_before": "O(2^(m+n)) time, O(m+n) space",
        "complexity_after": "O(m * n) time, O(n) space",
        "unoptimized": """
def unique_paths(m, n):
    if m == 1 or n == 1:
        return 1
    return unique_paths(m - 1, n) + unique_paths(m, n - 1)
""".strip(),
        "optimized": """
def unique_paths(m, n):
    dp = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]
""".strip(),
        "tests": [
            {"args": [3, 7], "expected": 28},
            {"args": [3, 2], "expected": 3},
            {"args": [1, 1], "expected": 1},
            {"args": [3, 3], "expected": 6},
            {"args": [1, 5], "expected": 1},
        ],
        "benchmark": {"args": [12, 12]},
    },
    {
        "name": "house_robber",
        "category": "dynamic-programming",
        "technique": "Track the best totals for the previous two houses (O(n), O(1) space) "
                     "instead of exponential naive recursion.",
        "description": "Return the maximum sum obtainable by choosing non-adjacent values from nums.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def house_robber(nums):
    def rec(i):
        if i >= len(nums):
            return 0
        return max(nums[i] + rec(i + 2), rec(i + 1))
    return rec(0)
""".strip(),
        "optimized": """
def house_robber(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 1]], "expected": 4},
            {"args": [[2, 7, 9, 3, 1]], "expected": 12},
            {"args": [[2, 1, 1, 2]], "expected": 4},
            {"args": [[]], "expected": 0},
            {"args": [[5]], "expected": 5},
        ],
        "benchmark": {"args": [[(i * 7) % 10 + 1 for i in range(30)]]},
    },
    {
        "name": "knapsack_01",
        "category": "dynamic-programming",
        "technique": "Use a bottom-up O(n * capacity) DP table instead of exploring every "
                     "include/exclude subset exponentially.",
        "description": "Return the maximum total value of items whose total weight fits within capacity (0/1 knapsack).",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n * capacity) time, O(capacity) space",
        "unoptimized": """
def knapsack_01(weights, values, capacity):
    def rec(i, w):
        if i == len(weights):
            return 0
        best = rec(i + 1, w)
        if weights[i] <= w:
            best = max(best, values[i] + rec(i + 1, w - weights[i]))
        return best
    return rec(0, capacity)
""".strip(),
        "optimized": """
def knapsack_01(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for i in range(len(weights)):
        wt = weights[i]
        val = values[i]
        for w in range(capacity, wt - 1, -1):
            if dp[w - wt] + val > dp[w]:
                dp[w] = dp[w - wt] + val
    return dp[capacity]
""".strip(),
        "tests": [
            {"args": [[1, 3, 4, 5], [1, 4, 5, 7], 7], "expected": 9},
            {"args": [[10, 20, 30], [60, 100, 120], 50], "expected": 220},
            {"args": [[1], [1], 0], "expected": 0},
            {"args": [[], [], 10], "expected": 0},
        ],
        "benchmark": {"args": [[(i % 5) + 1 for i in range(22)], [(i * 3 % 7) + 1 for i in range(22)], 60]},
    },
    {
        "name": "longest_common_substring",
        "category": "dynamic-programming",
        "technique": "Use the O(m * n) two-row DP table for contiguous matches instead of "
                     "restarting a character-by-character comparison at every pair of indices.",
        "description": "Return the length of the longest contiguous substring common to both strings a and b.",
        "complexity_before": "O(m * n * min(m, n)) time, O(1) space",
        "complexity_after": "O(m * n) time, O(n) space",
        "unoptimized": """
def longest_common_substring(a, b):
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            length = 0
            while (i + length < len(a) and j + length < len(b)
                   and a[i + length] == b[j + length]):
                length += 1
            if length > best:
                best = length
    return best
""".strip(),
        "optimized": """
def longest_common_substring(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best
""".strip(),
        "tests": [
            {"args": ["abcde", "abfce"], "expected": 2},
            {"args": ["abc", "abc"], "expected": 3},
            {"args": ["abc", "def"], "expected": 0},
            {"args": ["", "abc"], "expected": 0},
            {"args": ["aaaa", "aa"], "expected": 2},
        ],
        "benchmark": {"args": ["ab" * 70, "ba" * 70]},
    },
    {
        "name": "min_path_sum",
        "category": "dynamic-programming",
        "technique": "Fill a one-row DP table from the bottom-right (O(m * n)) instead of "
                     "recursively revisiting every grid cell along every path.",
        "description": "Return the minimum sum along a path from top-left to bottom-right of a positive-number grid, moving only right or down.",
        "complexity_before": "O(2^(m+n)) time, O(m+n) space",
        "complexity_after": "O(m * n) time, O(n) space",
        "unoptimized": """
def min_path_sum(grid):
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
""".strip(),
        "optimized": """
def min_path_sum(grid):
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
""".strip(),
        "tests": [
            {"args": [[[1, 3, 1], [1, 5, 1], [4, 2, 1]]], "expected": 7},
            {"args": [[[1, 2], [3, 4]]], "expected": 7},
            {"args": [[[5]]], "expected": 5},
            {"args": [[[1, 2, 3]]], "expected": 6},
        ],
        "benchmark": {"args": [[[(i + j) % 5 + 1 for j in range(12)] for i in range(12)]]},
    },
    {
        "name": "decode_ways",
        "category": "dynamic-programming",
        "technique": "Track only the previous two DP values (O(n), O(1) space) instead of "
                     "re-decoding the same suffixes exponentially.",
        "description": "Return the number of ways to decode a digit string where '1'..'26' map to 'A'..'Z'.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def decode_ways(s):
    def rec(i):
        if i == len(s):
            return 1
        if s[i] == "0":
            return 0
        total = rec(i + 1)
        if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26:
            total += rec(i + 2)
        return total
    return rec(0)
""".strip(),
        "optimized": """
def decode_ways(s):
    if not s or s[0] == "0":
        return 0
    prev2 = 1
    prev1 = 1
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1
        two = int(s[i - 1:i + 1])
        if 10 <= two <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1
""".strip(),
        "tests": [
            {"args": ["12"], "expected": 2},
            {"args": ["226"], "expected": 3},
            {"args": ["06"], "expected": 0},
            {"args": ["10"], "expected": 1},
            {"args": ["11106"], "expected": 2},
        ],
        "benchmark": {"args": ["1" * 30]},
    },
    {
        "name": "partition_equal_subset",
        "category": "dynamic-programming",
        "technique": "Track all reachable subset sums with a Python integer bitset "
                     "(O(n * sum / word)) instead of exploring every subset exponentially.",
        "description": "Return True if nums can be split into two subsets with equal sums.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n * sum / word) time, O(sum / word) space",
        "unoptimized": """
def partition_equal_subset(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2

    def rec(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums) or remaining < 0:
            return False
        return rec(i + 1, remaining - nums[i]) or rec(i + 1, remaining)

    return rec(0, target)
""".strip(),
        "optimized": """
def partition_equal_subset(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    reachable = 1
    for x in nums:
        reachable |= reachable << x
    return (reachable >> target) & 1 == 1
""".strip(),
        "tests": [
            {"args": [[1, 5, 11, 5]], "expected": True},
            {"args": [[1, 2, 3, 5]], "expected": False},
            {"args": [[1, 1]], "expected": True},
            {"args": [[2, 2, 2, 2]], "expected": True},
            {"args": [[]], "expected": True},
        ],
        "benchmark": {"args": [[2] * 19 + [4]]},
    },
    {
        "name": "longest_palindromic_subsequence",
        "category": "dynamic-programming",
        "technique": "Fill an O(n^2) DP table for all index ranges instead of recursively "
                     "re-solving the same ranges exponentially.",
        "description": "Return the length of the longest palindromic subsequence of s.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n^2) time, O(n^2) space",
        "unoptimized": """
def longest_palindromic_subsequence(s):
    def rec(i, j):
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + rec(i + 1, j - 1)
        return max(rec(i + 1, j), rec(i, j - 1))

    return rec(0, len(s) - 1)
""".strip(),
        "optimized": """
def longest_palindromic_subsequence(s):
    n = len(s)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2 if i + 1 <= j - 1 else 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
""".strip(),
        "tests": [
            {"args": ["bbbab"], "expected": 4},
            {"args": ["cbbd"], "expected": 2},
            {"args": ["agbdba"], "expected": 5},
            {"args": ["a"], "expected": 1},
            {"args": [""], "expected": 0},
        ],
        "benchmark": {"args": ["abcdefghijklmnopqrst"]},
    },
    {
        "name": "subset_sum_exists",
        "category": "dynamic-programming",
        "technique": "Propagate reachable sums with a bitset shift (O(n * target / word)) "
                     "instead of recursively trying every include/exclude subset.",
        "description": "Return True if some subset of the non-negative values in nums sums exactly to target.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n * target / word) time, O(target / word) space",
        "unoptimized": """
def subset_sum_exists(nums, target):
    def rec(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums) or remaining < 0:
            return False
        return rec(i + 1, remaining - nums[i]) or rec(i + 1, remaining)

    return rec(0, target)
""".strip(),
        "optimized": """
def subset_sum_exists(nums, target):
    if target < 0:
        return False
    reachable = 1
    for x in nums:
        reachable |= reachable << x
    return (reachable >> target) & 1 == 1
""".strip(),
        "tests": [
            {"args": [[3, 34, 4, 12, 5, 2], 9], "expected": True},
            {"args": [[3, 34, 4, 12, 5, 2], 30], "expected": False},
            {"args": [[1, 2, 3], 7], "expected": False},
            {"args": [[2], 3], "expected": False},
            {"args": [[], 0], "expected": True},
        ],
        "benchmark": {"args": [[2] * 20, 3]},
    },
    {
        "name": "rod_cutting",
        "category": "dynamic-programming",
        "technique": "Build the best revenue for every length bottom-up (O(n^2)) instead of "
                     "recursively re-solving every remaining length exponentially.",
        "description": "Given prices[i] for a rod of length i+1, return the maximum revenue for a rod of length n.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n^2) time, O(n) space",
        "unoptimized": """
def rod_cutting(prices, n):
    def rec(length):
        if length == 0:
            return 0
        best = 0
        for cut in range(1, length + 1):
            if cut <= len(prices):
                revenue = prices[cut - 1] + rec(length - cut)
                if revenue > best:
                    best = revenue
        return best

    return rec(n)
""".strip(),
        "optimized": """
def rod_cutting(prices, n):
    dp = [0] * (n + 1)
    for length in range(1, n + 1):
        best = 0
        for cut in range(1, length + 1):
            if cut <= len(prices):
                revenue = prices[cut - 1] + dp[length - cut]
                if revenue > best:
                    best = revenue
        dp[length] = best
    return dp[n]
""".strip(),
        "tests": [
            {"args": [[1, 5, 8, 9], 4], "expected": 10},
            {"args": [[1, 5, 8, 9], 5], "expected": 13},
            {"args": [[3, 5, 8], 3], "expected": 9},
            {"args": [[1], 0], "expected": 0},
            {"args": [[1], 3], "expected": 3},
        ],
        "benchmark": {"args": [[i + 1 for i in range(20)], 20]},
    },
    {
        "name": "matrix_chain_multiplication",
        "category": "dynamic-programming",
        "technique": "Fill the interval DP table (O(n^3)) instead of recursively trying "
                     "every parenthesization exponentially.",
        "description": "Given matrix dimensions dims (matrix i is dims[i] by dims[i+1]), return the minimum scalar multiplications needed.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n^3) time, O(n^2) space",
        "unoptimized": """
def matrix_chain_multiplication(dims):
    n = len(dims) - 1
    if n < 1:
        return 0

    def rec(i, j):
        if i == j:
            return 0
        best = None
        for k in range(i, j):
            cost = rec(i, k) + rec(k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1]
            if best is None or cost < best:
                best = cost
        return best

    return rec(0, n - 1)
""".strip(),
        "optimized": """
def matrix_chain_multiplication(dims):
    n = len(dims) - 1
    if n < 1:
        return 0
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            best = None
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if best is None or cost < best:
                    best = cost
            dp[i][j] = best
    return dp[0][n - 1]
""".strip(),
        "tests": [
            {"args": [[10, 30, 5, 60]], "expected": 4500},
            {"args": [[30, 35, 15, 5, 10, 20, 25]], "expected": 15125},
            {"args": [[5, 10]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i + 1 for i in range(14)]]},
    },
    {
        "name": "minimum_path_sum_triangle",
        "category": "dynamic-programming",
        "technique": "Collapse the triangle bottom-up with a one-row DP table (O(n^2)) "
                     "instead of exploring every top-to-bottom path exponentially.",
        "description": "Return the minimum path sum from the top to the bottom of a triangle, moving to adjacent values.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n^2) time, O(n) space",
        "unoptimized": """
def minimum_path_sum_triangle(triangle):
    if not triangle:
        return 0

    def rec(row, col):
        if row == len(triangle) - 1:
            return triangle[row][col]
        return triangle[row][col] + min(rec(row + 1, col), rec(row + 1, col + 1))

    return rec(0, 0)
""".strip(),
        "optimized": """
def minimum_path_sum_triangle(triangle):
    if not triangle:
        return 0
    dp = list(triangle[-1])
    for row in range(len(triangle) - 2, -1, -1):
        for col in range(len(triangle[row])):
            dp[col] = triangle[row][col] + min(dp[col], dp[col + 1])
    return dp[0]
""".strip(),
        "tests": [
            {"args": [[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]], "expected": 11},
            {"args": [[[-10]]], "expected": -10},
            {"args": [[[1], [2, 3]]], "expected": 3},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[(i * 3 + j * 7) % 10 for j in range(i + 1)] for i in range(20)]]},
    },
    {
        "name": "count_paths_with_obstacles",
        "category": "dynamic-programming",
        "technique": "Fill a one-row DP table (O(m * n)) instead of recursively walking "
                     "every path around the obstacles exponentially.",
        "description": "Count paths from the top-left to bottom-right of a 0/1 grid moving right or down, where 1 cells are blocked.",
        "complexity_before": "O(2^(m+n)) time, O(m+n) space",
        "complexity_after": "O(m * n) time, O(n) space",
        "unoptimized": """
def count_paths_with_obstacles(grid):
    rows = len(grid)
    cols = len(grid[0])

    def rec(i, j):
        if i >= rows or j >= cols or grid[i][j] == 1:
            return 0
        if i == rows - 1 and j == cols - 1:
            return 1
        return rec(i + 1, j) + rec(i, j + 1)

    return rec(0, 0)
""".strip(),
        "optimized": """
def count_paths_with_obstacles(grid):
    rows = len(grid)
    cols = len(grid[0])
    dp = [0] * cols
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1:
                dp[j] = 0
            elif i == 0 and j == 0:
                dp[j] = 1
            else:
                from_left = dp[j - 1] if j > 0 else 0
                from_up = dp[j] if i > 0 else 0
                dp[j] = from_left + from_up
    return dp[cols - 1]
""".strip(),
        "tests": [
            {"args": [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], "expected": 2},
            {"args": [[[0, 1], [0, 0]]], "expected": 1},
            {"args": [[[1]]], "expected": 0},
            {"args": [[[0]]], "expected": 1},
            {"args": [[[0, 0], [1, 1]]], "expected": 0},
        ],
        "benchmark": {"args": [[[1 if (i * 7 + j * 11) % 13 == 0 and (i, j) != (0, 0) and (i, j) != (11, 11) else 0 for j in range(12)] for i in range(12)]]},
    },
    {
        "name": "maximal_square",
        "category": "dynamic-programming",
        "technique": "Track the largest all-ones square ending at each cell (O(m * n)) "
                     "instead of testing every possible square brute-force.",
        "description": "Return the area of the largest square of 1s in a binary matrix.",
        "complexity_before": "O(m * n * min(m, n)^3) time, O(1) space",
        "complexity_after": "O(m * n) time, O(n) space",
        "unoptimized": """
def maximal_square(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    best = 0
    for i in range(rows):
        for j in range(cols):
            max_side = min(rows - i, cols - j)
            for side in range(1, max_side + 1):
                ok = True
                for r in range(i, i + side):
                    for c in range(j, j + side):
                        if matrix[r][c] != 1:
                            ok = False
                            break
                    if not ok:
                        break
                if ok and side > best:
                    best = side
                elif not ok:
                    break
    return best * best
""".strip(),
        "optimized": """
def maximal_square(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    dp = [0] * (cols + 1)
    best = 0
    for i in range(1, rows + 1):
        prev = 0
        for j in range(1, cols + 1):
            temp = dp[j]
            if matrix[i - 1][j - 1] == 1:
                dp[j] = min(dp[j], dp[j - 1], prev) + 1
                if dp[j] > best:
                    best = dp[j]
            else:
                dp[j] = 0
            prev = temp
    return best * best
""".strip(),
        "tests": [
            {"args": [[[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]], "expected": 4},
            {"args": [[[0, 1], [1, 0]]], "expected": 1},
            {"args": [[[0]]], "expected": 0},
            {"args": [[[1]]], "expected": 1},
            {"args": [[[1, 1], [1, 1]]], "expected": 4},
        ],
        "benchmark": {"args": [[[1 if (i * 7 + j * 11) % 5 != 0 else 0 for j in range(30)] for i in range(30)]]},
    },
    {
        "name": "word_break",
        "category": "dynamic-programming",
        "technique": "Mark reachable split positions with a boolean DP table (O(n^2)) "
                     "instead of recursively re-exploring the same suffixes exponentially.",
        "description": "Return True if s can be segmented into one or more words from word_dict.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n^2) time, O(n) space",
        "unoptimized": """
def word_break(s, word_dict):
    words = set(word_dict)

    def rec(start):
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in words and rec(end):
                return True
        return False

    return rec(0)
""".strip(),
        "optimized": """
def word_break(s, word_dict):
    words = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for end in range(1, n + 1):
        for start in range(end):
            if dp[start] and s[start:end] in words:
                dp[end] = True
                break
    return dp[n]
""".strip(),
        "tests": [
            {"args": ["leetcode", ["leet", "code"]], "expected": True},
            {"args": ["applepenapple", ["apple", "pen"]], "expected": True},
            {"args": ["catsandog", ["cats", "dog", "sand", "and", "cat"]], "expected": False},
            {"args": ["a", ["a"]], "expected": True},
            {"args": ["", []], "expected": True},
        ],
        "benchmark": {"args": ["a" * 18 + "b", ["a", "aa", "aaa"]]},
    },
    {
        "name": "count_subsets_with_sum",
        "category": "dynamic-programming",
        "technique": "Count subset sums with a one-dimensional DP table (O(n * target)) "
                     "instead of exploring every subset exponentially.",
        "description": "Return the number of subsets of nums whose sum equals target.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n * target) time, O(target) space",
        "unoptimized": """
def count_subsets_with_sum(nums, target):
    def rec(i, remaining):
        if remaining == 0:
            return 1
        if i == len(nums) or remaining < 0:
            return 0
        return rec(i + 1, remaining - nums[i]) + rec(i + 1, remaining)

    return rec(0, target)
""".strip(),
        "optimized": """
def count_subsets_with_sum(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for x in nums:
        for t in range(target, x - 1, -1):
            dp[t] += dp[t - x]
    return dp[target]
""".strip(),
        "tests": [
            {"args": [[1, 2, 3], 3], "expected": 2},
            {"args": [[1, 1, 1], 2], "expected": 3},
            {"args": [[1, 2], 3], "expected": 1},
            {"args": [[2], 3], "expected": 0},
            {"args": [[], 0], "expected": 1},
        ],
        "benchmark": {"args": [[1] * 20, 10]},
    },
    {
        "name": "paint_house",
        "category": "dynamic-programming",
        "technique": "Carry the best cost per color row by row (O(n * k^2)) instead of "
                     "recursively trying every valid color sequence exponentially.",
        "description": "Return the minimum cost to paint all houses so that no two adjacent houses share a color.",
        "complexity_before": "O(k^n) time, O(n) space",
        "complexity_after": "O(n * k^2) time, O(k) space",
        "unoptimized": """
def paint_house(costs):
    n = len(costs)

    def rec(i, prev_color):
        if i == n:
            return 0
        best = None
        for color in range(len(costs[i])):
            if color == prev_color:
                continue
            total = costs[i][color] + rec(i + 1, color)
            if best is None or total < best:
                best = total
        return best

    return rec(0, -1)
""".strip(),
        "optimized": """
def paint_house(costs):
    if not costs:
        return 0
    prev = list(costs[0])
    for row in costs[1:]:
        cur = [0] * len(row)
        for c in range(len(row)):
            best = None
            for pc in range(len(prev)):
                if pc != c:
                    val = prev[pc]
                    if best is None or val < best:
                        best = val
            cur[c] = row[c] + best
        prev = cur
    return min(prev)
""".strip(),
        "tests": [
            {"args": [[[17, 2, 17], [16, 16, 5], [14, 3, 19]]], "expected": 10},
            {"args": [[[7, 6, 2]]], "expected": 2},
            {"args": [[[1, 2, 3], [1, 2, 3]]], "expected": 3},
            {"args": [[[5, 5, 5], [1, 1, 1]]], "expected": 6},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[(i * 7 + j * 11) % 20 + 1 for j in range(3)] for i in range(12)]]},
    },
    {
        "name": "minimum_falling_path_sum",
        "category": "dynamic-programming",
        "technique": "Collapse the matrix bottom-up with a one-row DP table (O(n^2)) "
                     "instead of recursively trying all falling paths exponentially.",
        "description": "Return the minimum sum of a falling path from the top row to the bottom row of a square matrix.",
        "complexity_before": "O(3^n) time, O(n) space",
        "complexity_after": "O(n^2) time, O(n) space",
        "unoptimized": """
def minimum_falling_path_sum(matrix):
    n = len(matrix)

    def rec(row, col):
        if row == n - 1:
            return matrix[row][col]
        best = None
        for dc in (-1, 0, 1):
            nc = col + dc
            if 0 <= nc < n:
                val = rec(row + 1, nc)
                if best is None or val < best:
                    best = val
        return matrix[row][col] + best

    return min(rec(0, c) for c in range(n))
""".strip(),
        "optimized": """
def minimum_falling_path_sum(matrix):
    n = len(matrix)
    dp = list(matrix[-1])
    for row in range(n - 2, -1, -1):
        cur = [0] * n
        for col in range(n):
            best = dp[col]
            if col > 0 and dp[col - 1] < best:
                best = dp[col - 1]
            if col + 1 < n and dp[col + 1] < best:
                best = dp[col + 1]
            cur[col] = matrix[row][col] + best
        dp = cur
    return min(dp)
""".strip(),
        "tests": [
            {"args": [[[2, 1, 3], [6, 5, 4], [7, 8, 9]]], "expected": 13},
            {"args": [[[-19, 57], [-40, -5]]], "expected": -59},
            {"args": [[[-48]]], "expected": -48},
            {"args": [[[1, 2], [3, 4]]], "expected": 4},
        ],
        "benchmark": {"args": [[[(i * 7 + j * 11) % 20 - 10 for j in range(12)] for i in range(12)]]},
    },
    {
        "name": "integer_break",
        "category": "dynamic-programming",
        "technique": "Use the optimal 3s pattern (O(n)) instead of recursively trying "
                     "every first part of the integer (O(2^n)).",
        "description": "Return the maximum product obtainable by breaking n into at least two positive integers.",
        "complexity_before": "O(2^n) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def integer_break(n):
    def rec(remaining):
        if remaining == 1:
            return 1
        best = 0
        for first in range(1, remaining):
            best = max(best, first * max(remaining - first, rec(remaining - first)))
        return best

    return rec(n)
""".strip(),
        "optimized": """
def integer_break(n):
    if n == 2:
        return 1
    if n == 3:
        return 2
    product = 1
    while n > 4:
        product *= 3
        n -= 3
    return product * n
""".strip(),
        "tests": [
            {"args": [2], "expected": 1},
            {"args": [3], "expected": 2},
            {"args": [4], "expected": 4},
            {"args": [10], "expected": 36},
            {"args": [20], "expected": 1458},
        ],
        "benchmark": {"args": [20]},
    },
]
