"""Category: loops, sliding windows, and prefix sums.

Replace O(n^2) (or O(n*k)) nested loops with linear scans (Kadane, two pointers,
sliding window) or O(1)-per-query prefix sums.
"""

EXAMPLES = [
    {
        "name": "max_subarray_sum",
        "category": "loops",
        "technique": "Use Kadane's algorithm (single O(n) pass) instead of summing every "
                     "possible subarray in O(n^2).",
        "description": "Return the maximum sum of any non-empty contiguous subarray (None for empty input).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def max_subarray_sum(nums):
    best = None
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if best is None or s > best:
                best = s
    return best
""".strip(),
        "optimized": """
def max_subarray_sum(nums):
    if not nums:
        return None
    best = nums[0]
    cur = 0
    for x in nums:
        cur = x if cur < 0 else cur + x
        if cur > best:
            best = cur
    return best
""".strip(),
        "tests": [
            {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
            {"args": [[1, 2, 3]], "expected": 6},
            {"args": [[-1, -2, -3]], "expected": -1},
            {"args": [[]], "expected": None},
            {"args": [[42]], "expected": 42},
        ],
        "benchmark": {"args": [[i % 10 - 5 for i in range(2000)]]},
    },
    {
        "name": "max_product_subarray",
        "category": "loops",
        "technique": "Track the running max and min products in one O(n) pass (to handle "
                     "negatives) instead of O(n^2) subarray products.",
        "description": "Return the maximum product of any non-empty contiguous subarray.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def max_product_subarray(nums):
    best = None
    for i in range(len(nums)):
        p = 1
        for j in range(i, len(nums)):
            p *= nums[j]
            best = p if best is None or p > best else best
    return best
""".strip(),
        "optimized": """
def max_product_subarray(nums):
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        t_max, t_min = cur_max, cur_min
        cur_max = max(x, x * t_max, x * t_min)
        cur_min = min(x, x * t_max, x * t_min)
        if cur_max > best:
            best = cur_max
    return best
""".strip(),
        "tests": [
            {"args": [[2, 3, -2, 4]], "expected": 6},
            {"args": [[-2, 0, -1]], "expected": 0},
            {"args": [[-2, 3, -4]], "expected": 24},
            {"args": [[5]], "expected": 5},
        ],
        "benchmark": {"args": [[i % 3 - 1 for i in range(1500)]]},
    },
    {
        "name": "max_k_window_sum",
        "category": "loops",
        "technique": "Use a sliding-window running sum (O(1) per step) instead of "
                     "re-summing each window of length k (O(k) per step).",
        "description": "Return the maximum sum of any contiguous window of length k (None if k is invalid).",
        "complexity_before": "O(n * k) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def max_k_window_sum(nums, k):
    best = None
    for i in range(len(nums) - k + 1):
        s = 0
        for j in range(i, i + k):
            s += nums[j]
        best = s if best is None or s > best else best
    return best
""".strip(),
        "optimized": """
def max_k_window_sum(nums, k):
    if k <= 0 or k > len(nums):
        return None
    total = sum(nums[:k])
    best = total
    for i in range(k, len(nums)):
        total += nums[i] - nums[i - k]
        if total > best:
            best = total
    return best
""".strip(),
        "tests": [
            {"args": [[2, 1, 5, 1, 3, 2], 3], "expected": 9},
            {"args": [[1, 2, 3], 3], "expected": 6},
            {"args": [[9, 1, 2], 1], "expected": 9},
            {"args": [[1, 2], 5], "expected": None},
        ],
        "benchmark": {"args": [list(range(5000)), 100]},
    },
    {
        "name": "min_subarray_len",
        "category": "loops",
        "technique": "Use a two-pointer sliding window (positive values) to find the "
                     "shortest subarray with sum >= target in O(n) instead of O(n^2).",
        "description": "Return the minimum length of a contiguous subarray whose sum is at least target, or 0 if none.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def min_subarray_len(nums, target):
    n = len(nums)
    best = n + 1
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s >= target:
                if (j - i + 1) < best:
                    best = j - i + 1
                break
    return best if best <= n else 0
""".strip(),
        "optimized": """
def min_subarray_len(nums, target):
    best = len(nums) + 1
    start = 0
    s = 0
    for end, v in enumerate(nums):
        s += v
        while s >= target:
            length = end - start + 1
            if length < best:
                best = length
            s -= nums[start]
            start += 1
    return best if best <= len(nums) else 0
""".strip(),
        "tests": [
            {"args": [[2, 3, 1, 2, 4, 3], 7], "expected": 2},
            {"args": [[1, 1, 1, 1, 1], 3], "expected": 3},
            {"args": [[5], 5], "expected": 1},
            {"args": [[1, 2], 10], "expected": 0},
        ],
        "benchmark": {"args": [list(range(1, 1500)), 100000]},
    },
    {
        "name": "has_subarray_sum",
        "category": "loops",
        "technique": "Use a running prefix sum plus a set of seen prefixes (O(n)) instead "
                     "of testing every pair of indices (O(n^2)).",
        "description": "Return True if any contiguous subarray of nums sums to exactly k.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def has_subarray_sum(nums, k):
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s == k:
                return True
    return False
""".strip(),
        "optimized": """
def has_subarray_sum(nums, k):
    seen = {0}
    prefix = 0
    for x in nums:
        prefix += x
        if prefix - k in seen:
            return True
        seen.add(prefix)
    return False
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4], 5], "expected": True},
            {"args": [[2, 4], 7], "expected": False},
            {"args": [[5], 5], "expected": True},
            {"args": [[1, -1, 0, 1], 1], "expected": True},
            {"args": [[], 0], "expected": False},
        ],
        "benchmark": {"args": [list(range(1, 1001)), 10**9]},
    },
    {
        "name": "longest_unique_substr",
        "category": "loops",
        "technique": "Use a sliding window with a last-seen index map (O(n)) instead of "
                     "restarting and rebuilding a set for every start index (O(n^2)).",
        "description": "Return the length of the longest substring of s with all distinct characters.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def longest_unique_substr(s):
    best = 0
    n = len(s)
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen:
                break
            seen.add(s[j])
        if len(seen) > best:
            best = len(seen)
    return best
""".strip(),
        "optimized": """
def longest_unique_substr(s):
    last = {}
    start = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        if i - start + 1 > best:
            best = i - start + 1
    return best
""".strip(),
        "tests": [
            {"args": ["abcabcbb"], "expected": 3},
            {"args": ["bbbbb"], "expected": 1},
            {"args": ["pwwkew"], "expected": 3},
            {"args": [""], "expected": 0},
            {"args": ["abcdef"], "expected": 6},
        ],
        "benchmark": {"args": ["abcde" * 150]},
    },
    {
        "name": "longest_palindrome",
        "category": "loops",
        "technique": "Expand around each center to find the longest palindromic substring in "
                     "O(n^2) instead of testing every substring (O(n^3)).",
        "description": "Return the length of the longest palindromic substring of s (a contiguous substring that reads the same forwards and backwards).",
        "complexity_before": "O(n^3) time, O(n) space",
        "complexity_after": "O(n^2) time, O(1) space",
        "unoptimized": """
def longest_palindrome(s):
    best = 0
    n = len(s)
    for i in range(n):
        for j in range(i, n):
            sub = s[i:j + 1]
            if sub == sub[::-1]:
                if len(sub) > best:
                    best = len(sub)
    return best
""".strip(),
        "optimized": """
def longest_palindrome(s):
    if not s:
        return 0
    best = 1
    n = len(s)
    for k in range(n):
        i = j = k
        while i >= 0 and j < n and s[i] == s[j]:
            i -= 1
            j += 1
        best = max(best, j - i - 1)
        i, j = k, k + 1
        while i >= 0 and j < n and s[i] == s[j]:
            i -= 1
            j += 1
        best = max(best, j - i - 1)
    return best
""".strip(),
        "tests": [
            {"args": ["a"], "expected": 1},
            {"args": ["aa"], "expected": 2},
            {"args": ["aabb"], "expected": 2},
            {"args": ["abc"], "expected": 1},
            {"args": ["abbaa"], "expected": 4},
            {"args": ["babad"], "expected": 3},
            {"args": ["cbbd"], "expected": 2},
            {"args": [""], "expected": 0},
        ],
        "benchmark": {"args": ["ab" * 100]},
    },
    {
        "name": "lis_length",
        "category": "loops",
        "technique": "Compute the longest-increasing-subsequence length with patience "
                     "sorting + bisect (O(n log n)) instead of the O(n^2) DP table.",
        "description": "Return the length of the longest strictly increasing subsequence of nums.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def lis_length(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                if dp[j] + 1 > dp[i]:
                    dp[i] = dp[j] + 1
    return max(dp)
""".strip(),
        "optimized": """
def lis_length(nums):
    import bisect
    tails = []
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)
""".strip(),
        "tests": [
            {"args": [[10, 9, 2, 5, 3, 7, 101, 18]], "expected": 4},
            {"args": [[0, 1, 0, 3, 6, 2, 3, 4, 5, 2, 6]], "expected": 7},
            {"args": [[7, 7, 7, 7]], "expected": 1},
            {"args": [[]], "expected": 0},
            {"args": [[1, 2, 3, 4, 5]], "expected": 5},
        ],
        "benchmark": {"args": [list(range(0, 1500, 2))]},
    },
    {
        "name": "range_sums",
        "category": "loops",
        "technique": "Answer many [l, r] range-sum queries with a prefix-sum array "
                     "(O(1) per query) instead of re-summing the range each time.",
        "description": "Given arr and a list of [l, r] inclusive queries, return the sum of arr[l..r] for each query.",
        "complexity_before": "O(total range length) time, O(1) space",
        "complexity_after": "O(n + q) time, O(n) space",
        "unoptimized": """
def range_sums(arr, queries):
    out = []
    for l, r in queries:
        s = 0
        for i in range(l, r + 1):
            s += arr[i]
        out.append(s)
    return out
""".strip(),
        "optimized": """
def range_sums(arr, queries):
    prefix = [0]
    for v in arr:
        prefix.append(prefix[-1] + v)
    return [prefix[r + 1] - prefix[l] for l, r in queries]
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4], [(0, 2), (1, 3)]], "expected": [6, 9]},
            {"args": [[10], [(0, 0)]], "expected": [10]},
            {"args": [[1, 2, 3], [(0, 0), (2, 2)]], "expected": [1, 3]},
        ],
        "benchmark": {"args": [list(range(1000)), [(i, 999) for i in range(500)]]},
    },
    {
        "name": "longest_subarray_with_sum",
        "category": "loops",
        "technique": "Remember the first index of each prefix sum (O(n)) instead of "
                     "summing every subarray in a double loop (O(n^2)).",
        "description": "Return the length of the longest contiguous subarray whose sum is exactly k, or 0 if none.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def longest_subarray_with_sum(nums, k):
    best = 0
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == k and j - i + 1 > best:
                best = j - i + 1
    return best
""".strip(),
        "optimized": """
def longest_subarray_with_sum(nums, k):
    first = {0: -1}
    prefix = 0
    best = 0
    for i, x in enumerate(nums):
        prefix += x
        if prefix - k in first:
            length = i - first[prefix - k]
            if length > best:
                best = length
        if prefix not in first:
            first[prefix] = i
    return best
""".strip(),
        "tests": [
            {"args": [[1, -1, 5, -2, 3], 3], "expected": 4},
            {"args": [[1, 2, 3], 3], "expected": 2},
            {"args": [[1, 0, -1], 0], "expected": 3},
            {"args": [[1, 2, 3], 10], "expected": 0},
            {"args": [[], 0], "expected": 0},
        ],
        "benchmark": {"args": [[i % 7 - 3 for i in range(2000)], 5]},
    },
    {
        "name": "product_except_self",
        "category": "loops",
        "technique": "Combine a prefix-product pass and a suffix-product pass (O(n)) "
                     "instead of recomputing the product for every index (O(n^2)).",
        "description": "Return out where out[i] is the product of every element of nums except nums[i], without division.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def product_except_self(nums):
    out = []
    for i in range(len(nums)):
        p = 1
        for j in range(len(nums)):
            if i != j:
                p *= nums[j]
        out.append(p)
    return out
""".strip(),
        "optimized": """
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    prefix = 1
    for i in range(n):
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]
    return out
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [24, 12, 8, 6]},
            {"args": [[-1, 1, 0, -3, 3]], "expected": [0, 0, 9, 0, 0]},
            {"args": [[2, 3]], "expected": [3, 2]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 4 - 1 for i in range(1500)]]},
    },
    {
        "name": "container_with_most_water",
        "category": "loops",
        "technique": "Move two pointers inward from both ends (O(n)) instead of evaluating "
                     "every pair of lines (O(n^2)).",
        "description": "Return the maximum water area formed by two vertical lines at the given heights.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def container_with_most_water(heights):
    best = 0
    n = len(heights)
    for i in range(n):
        for j in range(i + 1, n):
            area = (j - i) * min(heights[i], heights[j])
            if area > best:
                best = area
    return best
""".strip(),
        "optimized": """
def container_with_most_water(heights):
    best = 0
    i, j = 0, len(heights) - 1
    while i < j:
        h = heights[i] if heights[i] < heights[j] else heights[j]
        area = (j - i) * h
        if area > best:
            best = area
        if heights[i] < heights[j]:
            i += 1
        else:
            j -= 1
    return best
""".strip(),
        "tests": [
            {"args": [[1, 8, 6, 2, 5, 4, 8, 3, 7]], "expected": 49},
            {"args": [[1, 1]], "expected": 1},
            {"args": [[4, 3, 2, 1, 4]], "expected": 16},
            {"args": [[1, 2, 1]], "expected": 2},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 37 % 101 for i in range(3000)]]},
    },
    {
        "name": "trapping_rain_water",
        "category": "loops",
        "technique": "Advance two pointers while tracking the best left/right walls (O(n)) "
                     "instead of rescanning both sides for every position (O(n^2)).",
        "description": "Return the total rainwater trapped between the bars of the elevation map.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def trapping_rain_water(heights):
    total = 0
    n = len(heights)
    for i in range(n):
        left_max = 0
        for j in range(i + 1):
            if heights[j] > left_max:
                left_max = heights[j]
        right_max = 0
        for j in range(i, n):
            if heights[j] > right_max:
                right_max = heights[j]
        water = min(left_max, right_max) - heights[i]
        if water > 0:
            total += water
    return total
""".strip(),
        "optimized": """
def trapping_rain_water(heights):
    total = 0
    i, j = 0, len(heights) - 1
    left_max = right_max = 0
    while i <= j:
        if heights[i] <= heights[j]:
            if heights[i] >= left_max:
                left_max = heights[i]
            else:
                total += left_max - heights[i]
            i += 1
        else:
            if heights[j] >= right_max:
                right_max = heights[j]
            else:
                total += right_max - heights[j]
            j -= 1
    return total
""".strip(),
        "tests": [
            {"args": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "expected": 6},
            {"args": [[4, 2, 0, 3, 2, 5]], "expected": 9},
            {"args": [[1, 2, 3]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 37 % 51 for i in range(3000)]]},
    },
    {
        "name": "longest_consecutive_ones",
        "category": "loops",
        "technique": "Track the current run in one pass (O(n)) instead of restarting a "
                     "scan from every index (O(n^2)).",
        "description": "Return the length of the longest run of consecutive 1s in a binary list.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def longest_consecutive_ones(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        length = 0
        for j in range(i, n):
            if nums[j] == 1:
                length += 1
            else:
                break
        if length > best:
            best = length
    return best
""".strip(),
        "optimized": """
def longest_consecutive_ones(nums):
    best = cur = 0
    for x in nums:
        if x == 1:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best
""".strip(),
        "tests": [
            {"args": [[1, 1, 0, 1, 1, 1]], "expected": 3},
            {"args": [[1, 0, 1, 1, 0, 1]], "expected": 2},
            {"args": [[0, 0]], "expected": 0},
            {"args": [[1]], "expected": 1},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[1] * 4000]},
    },
    {
        "name": "max_consecutive_ones_with_flip",
        "category": "loops",
        "technique": "Slide a window with at most k zeros (O(n)) instead of restarting the "
                     "scan at every index (O(n^2)).",
        "description": "Return the longest run of 1s possible in a binary list if at most k zeros may be flipped to 1.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def max_consecutive_ones_with_flip(nums, k):
    best = 0
    n = len(nums)
    for i in range(n):
        zeros = 0
        for j in range(i, n):
            if nums[j] == 0:
                zeros += 1
                if zeros > k:
                    break
            if j - i + 1 > best:
                best = j - i + 1
    return best
""".strip(),
        "optimized": """
def max_consecutive_ones_with_flip(nums, k):
    best = 0
    start = 0
    zeros = 0
    for end, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[start] == 0:
                zeros -= 1
            start += 1
        if end - start + 1 > best:
            best = end - start + 1
    return best
""".strip(),
        "tests": [
            {"args": [[1, 0, 1, 1, 0], 1], "expected": 4},
            {"args": [[1, 1, 0, 1, 1], 1], "expected": 5},
            {"args": [[0, 0], 1], "expected": 1},
            {"args": [[1, 1, 1], 0], "expected": 3},
            {"args": [[0, 1, 0, 1], 2], "expected": 4},
        ],
        "benchmark": {"args": [[1] * 1500 + [0] + [1] * 1500, 1]},
    },
    {
        "name": "count_negatives_in_sorted_matrix",
        "category": "loops",
        "technique": "Walk from the top-right corner moving only left or down (O(m + n)) "
                     "instead of inspecting every cell (O(m * n)).",
        "description": "Count negative values in a matrix whose rows and columns are sorted in non-increasing order.",
        "complexity_before": "O(m * n) time, O(1) space",
        "complexity_after": "O(m + n) time, O(1) space",
        "unoptimized": """
def count_negatives_in_sorted_matrix(grid):
    count = 0
    for row in grid:
        for x in row:
            if x < 0:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_negatives_in_sorted_matrix(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    count = 0
    i, j = 0, cols - 1
    while i < rows and j >= 0:
        if grid[i][j] < 0:
            count += rows - i
            j -= 1
        else:
            i += 1
    return count
""".strip(),
        "tests": [
            {"args": [[[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]]], "expected": 8},
            {"args": [[[3, 2], [1, 0]]], "expected": 0},
            {"args": [[[-1]]], "expected": 1},
            {"args": [[[1]]], "expected": 0},
        ],
        "benchmark": {"args": [[[500 - i - j for j in range(500)] for i in range(500)]]},
    },
    {
        "name": "subarray_product_less_than_k",
        "category": "loops",
        "technique": "Maintain a sliding window whose product stays below k (O(n)) "
                     "instead of multiplying out every subarray (O(n^2)).",
        "description": "Return the number of contiguous subarrays of positive integers whose product is strictly less than k.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def subarray_product_less_than_k(nums, k):
    count = 0
    n = len(nums)
    for i in range(n):
        product = 1
        for j in range(i, n):
            product *= nums[j]
            if product < k:
                count += 1
            else:
                break
    return count
""".strip(),
        "optimized": """
def subarray_product_less_than_k(nums, k):
    if k <= 1:
        return 0
    product = 1
    start = 0
    count = 0
    for end, x in enumerate(nums):
        product *= x
        while product >= k and start <= end:
            product //= nums[start]
            start += 1
        count += end - start + 1
    return count
""".strip(),
        "tests": [
            {"args": [[10, 5, 2, 6], 100], "expected": 8},
            {"args": [[1, 1, 1], 2], "expected": 6},
            {"args": [[1, 2, 3], 7], "expected": 6},
            {"args": [[1, 2, 3], 0], "expected": 0},
            {"args": [[], 5], "expected": 0},
        ],
        "benchmark": {"args": [[1] * 3000, 2]},
    },
    {
        "name": "move_zeroes",
        "category": "loops",
        "technique": "Compact non-zero values with a write index in one pass (O(n)) "
                     "instead of swapping each zero across the remaining elements (O(n^2)).",
        "description": "Return a copy of nums with all zeroes moved to the end while preserving the order of non-zero values.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def move_zeroes(nums):
    out = list(nums)
    for i in range(len(out)):
        if out[i] == 0:
            for j in range(i + 1, len(out)):
                if out[j] != 0:
                    out[i], out[j] = out[j], out[i]
                    break
    return out
""".strip(),
        "optimized": """
def move_zeroes(nums):
    out = list(nums)
    write = 0
    for x in out:
        if x != 0:
            out[write] = x
            write += 1
    for i in range(write, len(out)):
        out[i] = 0
    return out
""".strip(),
        "tests": [
            {"args": [[0, 1, 0, 3, 12]], "expected": [1, 3, 12, 0, 0]},
            {"args": [[0, 0, 1]], "expected": [1, 0, 0]},
            {"args": [[1, 2]], "expected": [1, 2]},
            {"args": [[0]], "expected": [0]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[0] * 3000]},
    },
    {
        "name": "find_pivot_index",
        "category": "loops",
        "technique": "Use the total sum and a running left sum (O(n)) instead of "
                     "recomputing both sides for every index (O(n^2)).",
        "description": "Return the leftmost index where the sum of values to its left equals the sum to its right, or -1.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def find_pivot_index(nums):
    n = len(nums)
    for i in range(n):
        left = 0
        for j in range(i):
            left += nums[j]
        right = 0
        for j in range(i + 1, n):
            right += nums[j]
        if left == right:
            return i
    return -1
""".strip(),
        "optimized": """
def find_pivot_index(nums):
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left += x
    return -1
""".strip(),
        "tests": [
            {"args": [[1, 7, 3, 6, 5, 6]], "expected": 3},
            {"args": [[1, 2, 3]], "expected": -1},
            {"args": [[2, 1, -1]], "expected": 0},
            {"args": [[1]], "expected": 0},
            {"args": [[]], "expected": -1},
        ],
        "benchmark": {"args": [[1] * 3000]},
    },
    {
        "name": "best_time_buy_sell_stock",
        "category": "loops",
        "technique": "Track the minimum price so far in one pass (O(n)) instead of "
                     "checking every buy/sell pair (O(n^2)).",
        "description": "Return the maximum profit from buying one day and selling on a later day, or 0 if none.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def best_time_buy_sell_stock(prices):
    best = 0
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            if profit > best:
                best = profit
    return best
""".strip(),
        "optimized": """
def best_time_buy_sell_stock(prices):
    best = 0
    min_price = None
    for price in prices:
        if min_price is None or price < min_price:
            min_price = price
        elif price - min_price > best:
            best = price - min_price
    return best
""".strip(),
        "tests": [
            {"args": [[7, 1, 5, 3, 6, 4]], "expected": 5},
            {"args": [[7, 6, 4, 3, 1]], "expected": 0},
            {"args": [[1, 2]], "expected": 1},
            {"args": [[2, 1, 2]], "expected": 1},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 37 % 1000 for i in range(3000)]]},
    },
    {
        "name": "count_subarrays_sum_less_than_k",
        "category": "loops",
        "technique": "Maintain a sliding window whose sum stays below k (O(n)) instead "
                     "of summing every subarray (O(n^2)).",
        "description": "Return the number of contiguous subarrays of positive integers whose sum is strictly less than k.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def count_subarrays_sum_less_than_k(nums, k):
    count = 0
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total < k:
                count += 1
            else:
                break
    return count
""".strip(),
        "optimized": """
def count_subarrays_sum_less_than_k(nums, k):
    count = 0
    total = 0
    start = 0
    for end, x in enumerate(nums):
        total += x
        while total >= k and start <= end:
            total -= nums[start]
            start += 1
        count += end - start + 1
    return count
""".strip(),
        "tests": [
            {"args": [[1, 2, 3], 4], "expected": 4},
            {"args": [[1, 1, 1], 2], "expected": 3},
            {"args": [[1, 2, 3], 10], "expected": 6},
            {"args": [[1, 2, 3], 0], "expected": 0},
            {"args": [[], 5], "expected": 0},
        ],
        "benchmark": {"args": [[1] * 3000, 3001]},
    },
    {
        "name": "remove_duplicates_sorted",
        "category": "loops",
        "technique": "Build the result with a two-pointer scan (O(n)) instead of "
                     "popping duplicates from the middle of a list (O(n^2)).",
        "description": "Return the sorted list with duplicate values removed.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def remove_duplicates_sorted(nums):
    out = list(nums)
    i = 1
    while i < len(out):
        if out[i] == out[i - 1]:
            out.pop(i)
        else:
            i += 1
    return out
""".strip(),
        "optimized": """
def remove_duplicates_sorted(nums):
    if not nums:
        return []
    out = [nums[0]]
    for x in nums[1:]:
        if x != out[-1]:
            out.append(x)
    return out
""".strip(),
        "tests": [
            {"args": [[1, 1, 2]], "expected": [1, 2]},
            {"args": [[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]], "expected": [0, 1, 2, 3, 4]},
            {"args": [[1, 2, 2]], "expected": [1, 2]},
            {"args": [[1]], "expected": [1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[0] * 3000]},
    },
    {
        "name": "longest_substring_k_distinct",
        "category": "loops",
        "technique": "Maintain a sliding window with at most k distinct characters (O(n)) "
                     "instead of extending a fresh window from every index (O(n^2)).",
        "description": "Return the length of the longest substring of s containing at most k distinct characters.",
        "complexity_before": "O(n^2) time, O(k) space",
        "complexity_after": "O(n) time, O(k) space",
        "unoptimized": """
def longest_substring_k_distinct(s, k):
    best = 0
    n = len(s)
    for i in range(n):
        counts = {}
        distinct = 0
        for j in range(i, n):
            c = s[j]
            if c not in counts:
                counts[c] = 1
                distinct += 1
            else:
                counts[c] += 1
            if distinct > k:
                break
            if j - i + 1 > best:
                best = j - i + 1
    return best
""".strip(),
        "optimized": """
def longest_substring_k_distinct(s, k):
    if k == 0:
        return 0
    counts = {}
    best = 0
    start = 0
    for end, c in enumerate(s):
        counts[c] = counts.get(c, 0) + 1
        while len(counts) > k:
            left = s[start]
            counts[left] -= 1
            if counts[left] == 0:
                del counts[left]
            start += 1
        if end - start + 1 > best:
            best = end - start + 1
    return best
""".strip(),
        "tests": [
            {"args": ["eceba", 2], "expected": 3},
            {"args": ["ccaabbb", 2], "expected": 5},
            {"args": ["abc", 2], "expected": 2},
            {"args": ["a", 1], "expected": 1},
            {"args": ["abc", 0], "expected": 0},
            {"args": ["", 1], "expected": 0},
        ],
        "benchmark": {"args": ["abcdefghijklmnopqrstuvwxyz" * 115, 26]},
    },
    {
        "name": "max_distance_between_equal",
        "category": "loops",
        "technique": "Remember the first index of each value (O(n)) instead of scanning "
                     "backwards from every position (O(n^2)).",
        "description": "Return the maximum j - i such that nums[i] == nums[j], or 0 if no value repeats.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def max_distance_between_equal(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(n - 1, i, -1):
            if nums[i] == nums[j]:
                if j - i > best:
                    best = j - i
                break
    return best
""".strip(),
        "optimized": """
def max_distance_between_equal(nums):
    first = {}
    best = 0
    for i, x in enumerate(nums):
        if x not in first:
            first[x] = i
        elif i - first[x] > best:
            best = i - first[x]
    return best
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 1, 4]], "expected": 3},
            {"args": [[1, 2, 1, 2, 1]], "expected": 4},
            {"args": [[1, 2, 3]], "expected": 0},
            {"args": [[1, 1]], "expected": 1},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i % 1000 for i in range(3000)]]},
    },
    {
        "name": "two_sum_sorted",
        "category": "loops",
        "technique": "Move two pointers inward on the sorted list (O(n)) instead of "
                     "checking every pair (O(n^2)).",
        "description": "Return the indices of two values in the sorted list nums that add to target, or [] if none.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def two_sum_sorted(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""".strip(),
        "optimized": """
def two_sum_sorted(nums, target):
    i, j = 0, len(nums) - 1
    while i < j:
        total = nums[i] + nums[j]
        if total == target:
            return [i, j]
        if total < target:
            i += 1
        else:
            j -= 1
    return []
""".strip(),
        "tests": [
            {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"args": [[1, 2, 3, 4, 6], 6], "expected": [1, 3]},
            {"args": [[1, 1, 2], 2], "expected": [0, 1]},
            {"args": [[1, 2], 5], "expected": []},
            {"args": [[], 3], "expected": []},
        ],
        "benchmark": {"args": [list(range(3000)), 5997]},
    },
    {
        "name": "count_subarrays_with_odd_sum",
        "category": "loops",
        "technique": "Count prefix sums by parity (O(n)) instead of summing every "
                     "subarray (O(n^2)).",
        "description": "Return the number of contiguous subarrays whose sum is odd.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def count_subarrays_with_odd_sum(nums):
    count = 0
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total % 2 == 1:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_subarrays_with_odd_sum(nums):
    even_prefixes = 1
    odd_prefixes = 0
    prefix = 0
    count = 0
    for x in nums:
        prefix += x
        if prefix % 2:
            count += even_prefixes
            odd_prefixes += 1
        else:
            count += odd_prefixes
            even_prefixes += 1
    return count
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": 6},
            {"args": [[2, 4]], "expected": 0},
            {"args": [[1]], "expected": 1},
            {"args": [[1, 1]], "expected": 2},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i % 2 for i in range(3000)]]},
    },
    {
        "name": "find_peak_element",
        "category": "loops",
        "technique": "Binary search toward the higher neighbor (O(log n)) instead of "
                     "scanning every index for a peak (O(n)).",
        "description": "Return the index of any local peak (strictly greater than its neighbors, with out-of-range treated as smaller).",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(log n) time, O(1) space",
        "unoptimized": """
def find_peak_element(nums):
    for i in range(len(nums)):
        left_ok = i == 0 or nums[i] > nums[i - 1]
        right_ok = i == len(nums) - 1 or nums[i] > nums[i + 1]
        if left_ok and right_ok:
            return i
    return -1
""".strip(),
        "optimized": """
def find_peak_element(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 1]], "expected": 2},
            {"args": [[1, 2, 1, 3, 5, 6, 4]], "acceptable": [1, 5]},
            {"args": [[1]], "expected": 0},
            {"args": [[1, 2]], "expected": 1},
            {"args": [[2, 1]], "expected": 0},
        ],
        "benchmark": {"args": [list(range(20000)) + list(range(19998, -1, -1))]},
    },
    {
        "name": "count_subarrays_with_at_most_k_distinct",
        "category": "loops",
        "technique": "Maintain a sliding window with at most k distinct values (O(n)) "
                     "instead of extending a fresh window from every index (O(n^2)).",
        "description": "Return the number of contiguous subarrays containing at most k distinct values.",
        "complexity_before": "O(n^2) time, O(k) space",
        "complexity_after": "O(n) time, O(k) space",
        "unoptimized": """
def count_subarrays_with_at_most_k_distinct(nums, k):
    count = 0
    n = len(nums)
    for i in range(n):
        counts = {}
        distinct = 0
        for j in range(i, n):
            x = nums[j]
            if x not in counts:
                counts[x] = 1
                distinct += 1
            else:
                counts[x] += 1
            if distinct > k:
                break
            count += 1
    return count
""".strip(),
        "optimized": """
def count_subarrays_with_at_most_k_distinct(nums, k):
    counts = {}
    count = 0
    start = 0
    for end, x in enumerate(nums):
        counts[x] = counts.get(x, 0) + 1
        while len(counts) > k:
            left = nums[start]
            counts[left] -= 1
            if counts[left] == 0:
                del counts[left]
            start += 1
        count += end - start + 1
    return count
""".strip(),
        "tests": [
            {"args": [[1, 2, 1, 2, 3], 2], "expected": 12},
            {"args": [[1, 2, 3], 3], "expected": 6},
            {"args": [[1, 2, 3], 2], "expected": 5},
            {"args": [[1, 1, 1], 1], "expected": 6},
            {"args": [[], 2], "expected": 0},
        ],
        "benchmark": {"args": [[i % 3 for i in range(3000)], 3]},
    },
    {
        "name": "longest_increasing_run",
        "category": "loops",
        "technique": "Track the current increasing run in one pass (O(n)) instead of "
                     "restarting the scan at every index (O(n^2)).",
        "description": "Return the length of the longest strictly increasing contiguous run.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def longest_increasing_run(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        length = 1
        for j in range(i + 1, n):
            if nums[j] > nums[j - 1]:
                length += 1
            else:
                break
        if length > best:
            best = length
    return best
""".strip(),
        "optimized": """
def longest_increasing_run(nums):
    if not nums:
        return 0
    best = 1
    cur = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 1
    return best
""".strip(),
        "tests": [
            {"args": [[1, 3, 5, 4, 7]], "expected": 3},
            {"args": [[2, 2, 2, 2]], "expected": 1},
            {"args": [[1, 2]], "expected": 2},
            {"args": [[5, 4, 3, 2, 1]], "expected": 1},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i for i in range(3000)]]},
    },
    {
        "name": "max_average_subarray",
        "category": "loops",
        "technique": "Slide the window sum in O(1) per step (O(n)) instead of re-summing "
                     "every window (O(n * k)).",
        "description": "Return the maximum average of any contiguous subarray of length k.",
        "complexity_before": "O(n * k) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def max_average_subarray(nums, k):
    best = None
    for i in range(len(nums) - k + 1):
        total = 0
        for j in range(i, i + k):
            total += nums[j]
        avg = total / k
        if best is None or avg > best:
            best = avg
    return best
""".strip(),
        "optimized": """
def max_average_subarray(nums, k):
    total = sum(nums[:k])
    best = total / k
    for i in range(k, len(nums)):
        total += nums[i] - nums[i - k]
        avg = total / k
        if avg > best:
            best = avg
    return best
""".strip(),
        "tests": [
            {"args": [[1, 12, -5, -6, 50, 3], 4], "expected": 12.75},
            {"args": [[5], 1], "expected": 5.0},
            {"args": [[1, 2, 3], 2], "expected": 2.5},
            {"args": [[1, 2, 3], 1], "expected": 3.0},
        ],
        "benchmark": {"args": [[i * 37 % 1000 for i in range(3000)], 500]},
    },
]
