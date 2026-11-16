"""Category: sorting & binary search.

Replace wasteful full sorts or linear scans with a targeted single pass (O(n)) or
a binary search (O(log n)) on already-sorted data.
"""

EXAMPLES = [
    {
        "name": "second_largest",
        "category": "sorting",
        "technique": "Track the largest and second-largest in one O(n) pass instead of "
                     "building a deduplicated list with O(n^2) membership checks.",
        "description": "Return the second-largest distinct value in nums, or -1 if there are fewer than 2 distinct values.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def second_largest(nums):
    unique = []
    for x in nums:
        if x not in unique:
            unique.append(x)
    if len(unique) < 2:
        return -1
    best = unique[0]
    for v in unique:
        if v > best:
            best = v
    second = None
    for v in unique:
        if v == best:
            continue
        if second is None or v > second:
            second = v
    return second
""".strip(),
        "optimized": """
def second_largest(nums):
    first = second = None
    for x in nums:
        if first is None or x > first:
            second = first
            first = x
        elif x != first and (second is None or x > second):
            second = x
    return second if second is not None else -1
""".strip(),
        "tests": [
            {"args": [[1, 2, 2, 3]], "expected": 2},
            {"args": [[5, 5, 5]], "expected": -1},
            {"args": [[7]], "expected": -1},
            {"args": [[10, 9, 8]], "expected": 9},
            {"args": [[1, 1]], "expected": -1},
        ],
        "benchmark": {"args": [list(range(1000))]},
    },
    {
        "name": "dedupe",
        "category": "sorting",
        "technique": "Drop duplicates while preserving order with dict.fromkeys (O(n)) "
                     "instead of an O(n^2) 'x not in out' append loop.",
        "description": "Return a copy of nums with duplicate values removed, keeping first occurrence order.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def dedupe(nums):
    out = []
    for x in nums:
        if x not in out:
            out.append(x)
    return out
""".strip(),
        "optimized": """
def dedupe(nums):
    return list(dict.fromkeys(nums))
""".strip(),
        "tests": [
            {"args": [[1, 2, 2, 3, 1, 4, 3]], "expected": [1, 2, 3, 4]},
            {"args": [[]], "expected": []},
            {"args": [["a", "b", "a", "a", "b"]], "expected": ["a", "b"]},
            {"args": [[42]], "expected": [42]},
        ],
        "benchmark": {"args": [[i % 50 for i in range(5000)]]},
    },
    {
        "name": "count_inversions",
        "category": "sorting",
        "technique": "Count inversions while doing a merge sort (O(n log n)) instead of "
                     "comparing every pair of indices (O(n^2)).",
        "description": "Return the number of pairs (i, j) with i < j and nums[i] > nums[j].",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def count_inversions(nums):
    count = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] > nums[j]:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_inversions(nums):
    def sort_count(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, inv_l = sort_count(a[:mid])
        right, inv_r = sort_count(a[mid:])
        merged = []
        i = j = 0
        inv = inv_l + inv_r
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
                inv += len(left) - i
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, inv
    return sort_count(nums)[1]
""".strip(),
        "tests": [
            {"args": [[2, 4, 1, 3, 5]], "expected": 3},
            {"args": [[1, 2, 3, 4]], "expected": 0},
            {"args": [[4, 3, 2, 1]], "expected": 6},
            {"args": [[7, 6, 5, 4, 3, 2, 1]], "expected": 21},
            {"args": [[]], "expected": 0},
            {"args": [[1]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 97 % 3001 for i in range(3000)]]},
    },
    {
        "name": "lower_bound",
        "category": "sorting",
        "technique": "Find the first index with value >= x via bisect (O(log n)) on the "
                     "sorted list instead of a linear scan (O(n)).",
        "description": "Given a sorted list, return the first index i with nums[i] >= x (or len(nums) if none).",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(log n) time, O(1) space",
        "unoptimized": """
def lower_bound(nums, x):
    for i, v in enumerate(nums):
        if v >= x:
            return i
    return len(nums)
""".strip(),
        "optimized": """
def lower_bound(nums, x):
    import bisect
    return bisect.bisect_left(nums, x)
""".strip(),
        "tests": [
            {"args": [[1, 3, 4, 6, 8], 4], "expected": 2},
            {"args": [[1, 3, 4, 6, 8], 5], "expected": 3},
            {"args": [[1, 3, 4, 6, 8], 0], "expected": 0},
            {"args": [[1, 3, 4, 6, 8], 9], "expected": 5},
            {"args": [[], 5], "expected": 0},
        ],
        "benchmark": {"args": [list(range(20000)), 10000]},
    },
    {
        "name": "kth_largest",
        "category": "sorting",
        "technique": "Keep a size-k heap with heapq.nlargest (O(n log k)) instead of "
                     "repeatedly scanning and removing the current maximum k times (O(n * k)).",
        "description": "Return the kth largest value in nums (1-indexed, duplicates counted separately).",
        "complexity_before": "O(n * k) time, O(n) space",
        "complexity_after": "O(n log k) time, O(k) space",
        "unoptimized": """
def kth_largest(nums, k):
    remaining = list(nums)
    for _ in range(k - 1):
        best_i = 0
        for i in range(1, len(remaining)):
            if remaining[i] > remaining[best_i]:
                best_i = i
        remaining.pop(best_i)
    best = remaining[0]
    for x in remaining:
        if x > best:
            best = x
    return best
""".strip(),
        "optimized": """
def kth_largest(nums, k):
    import heapq
    return heapq.nlargest(k, nums)[-1]
""".strip(),
        "tests": [
            {"args": [[3, 2, 1, 5, 6, 4], 2], "expected": 5},
            {"args": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], "expected": 4},
            {"args": [[1], 1], "expected": 1},
            {"args": [[7, 6, 5], 3], "expected": 5},
        ],
        "benchmark": {"args": [[i * 97 % 10007 for i in range(10000)], 50]},
    },
    {
        "name": "merge_intervals",
        "category": "sorting",
        "technique": "Sort by start and merge in one pass (O(n log n)) instead of "
                     "repeatedly rescanning all pairs until nothing overlaps (O(n^3)).",
        "description": "Merge all overlapping closed intervals and return the sorted list of merged intervals.",
        "complexity_before": "O(n^3) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def merge_intervals(intervals):
    intervals = [list(iv) for iv in intervals]
    merged = True
    while merged:
        merged = False
        for i in range(len(intervals)):
            for j in range(i + 1, len(intervals)):
                a, b = intervals[i], intervals[j]
                if a[0] <= b[1] and b[0] <= a[1]:
                    a[0] = min(a[0], b[0])
                    a[1] = max(a[1], b[1])
                    intervals.pop(j)
                    merged = True
                    break
            if merged:
                break
    return sorted(intervals)
""".strip(),
        "optimized": """
def merge_intervals(intervals):
    if not intervals:
        return []
    ordered = sorted([list(iv) for iv in intervals])
    out = [ordered[0]]
    for start, end in ordered[1:]:
        if start <= out[-1][1]:
            if end > out[-1][1]:
                out[-1][1] = end
        else:
            out.append([start, end])
    return out
""".strip(),
        "tests": [
            {"args": [[[1, 3], [2, 6], [8, 10], [15, 18]]],
             "expected": [[1, 6], [8, 10], [15, 18]]},
            {"args": [[[1, 4], [4, 5]]], "expected": [[1, 5]]},
            {"args": [[[1, 4], [0, 4]]], "expected": [[0, 4]]},
            {"args": [[[5, 6], [1, 2]]], "expected": [[1, 2], [5, 6]]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[[i, i + 2] for i in range(150)]]},
    },
    {
        "name": "sort_by_frequency",
        "category": "sorting",
        "technique": "Count with collections.Counter (O(n)) instead of scanning a list of "
                     "counts for every element (O(n^2)), then sort by (-count, value).",
        "description": "Return nums sorted by decreasing frequency, breaking ties by increasing value.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_by_frequency(nums):
    counts = []
    for x in nums:
        found = False
        for item in counts:
            if item[0] == x:
                item[1] += 1
                found = True
                break
        if not found:
            counts.append([x, 1])
    counts.sort(key=lambda item: (-item[1], item[0]))
    out = []
    for x, c in counts:
        out.extend([x] * c)
    return out
""".strip(),
        "optimized": """
def sort_by_frequency(nums):
    from collections import Counter
    counts = Counter(nums)
    return sorted(nums, key=lambda x: (-counts[x], x))
""".strip(),
        "tests": [
            {"args": [[1, 1, 2, 2, 2, 3]], "expected": [2, 2, 2, 1, 1, 3]},
            {"args": [[2, 3, 1, 3, 2]], "expected": [2, 2, 3, 3, 1]},
            {"args": [[4, 4, 1, 1, 2]], "expected": [1, 1, 4, 4, 2]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 200 for i in range(5000)]]},
    },
    {
        "name": "majority_element",
        "category": "sorting",
        "technique": "Use Boyer-Moore voting (O(n), O(1) space) instead of counting every "
                     "candidate with a full rescan (O(n^2)).",
        "description": "Return the majority value that appears more than n/2 times (guaranteed to exist).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def majority_element(nums):
    n = len(nums)
    for x in nums:
        count = 0
        for y in nums:
            if x == y:
                count += 1
        if count > n // 2:
            return x
    return None
""".strip(),
        "optimized": """
def majority_element(nums):
    candidate = None
    count = 0
    for x in nums:
        if count == 0:
            candidate = x
            count = 1
        elif x == candidate:
            count += 1
        else:
            count -= 1
    return candidate
""".strip(),
        "tests": [
            {"args": [[3, 2, 3]], "expected": 3},
            {"args": [[2, 2, 1, 1, 1, 2, 2]], "expected": 2},
            {"args": [[1]], "expected": 1},
            {"args": [[6, 6, 6, 1, 2]], "expected": 6},
        ],
        "benchmark": {"args": [list(range(1, 2001)) + [0] * 2001]},
    },
    {
        "name": "three_sum",
        "category": "sorting",
        "technique": "Sort once and use two pointers per anchor (O(n^2)) instead of "
                     "enumerating every triple (O(n^3)).",
        "description": "Return all unique triplets [a, b, c] with a + b + c == 0, sorted ascending.",
        "complexity_before": "O(n^3) time, O(t) space",
        "complexity_after": "O(n^2) time, O(t) space",
        "unoptimized": """
def three_sum(nums):
    n = len(nums)
    found = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    found.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in sorted(found)]
""".strip(),
        "optimized": """
def three_sum(nums):
    nums = sorted(nums)
    n = len(nums)
    out = []
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        target = -nums[i]
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[lo] + nums[hi]
            if s == target:
                out.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi + 1]:
                    hi -= 1
            elif s < target:
                lo += 1
            else:
                hi -= 1
    return out
""".strip(),
        "tests": [
            {"args": [[-1, 0, 1, 2, -1, -4]], "expected": [[-1, -1, 2], [-1, 0, 1]]},
            {"args": [[0, 1, 1]], "expected": []},
            {"args": [[0, 0, 0, 0]], "expected": [[0, 0, 0]]},
            {"args": [[-2, 0, 1, 1, 2]], "expected": [[-2, 0, 2], [-2, 1, 1]]},
            {"args": [[1, 2, -2, -1]], "expected": []},
        ],
        "benchmark": {"args": [[i * 37 % 41 - 20 for i in range(200)]]},
    },
    {
        "name": "largest_number",
        "category": "sorting",
        "technique": "Sort with the pairwise comparator a+b vs b+a (O(n log n)) instead of "
                     "trying every permutation (O(n!)).",
        "description": "Arrange the non-negative integers to form the largest possible number and return it as a string.",
        "complexity_before": "O(n! * n) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def largest_number(nums):
    from itertools import permutations
    strings = [str(x) for x in nums]
    best = ""
    for perm in permutations(strings):
        candidate = "".join(perm)
        if candidate > best:
            best = candidate
    return str(int(best)) if best else "0"
""".strip(),
        "optimized": """
def largest_number(nums):
    from functools import cmp_to_key
    strings = [str(x) for x in nums]

    def compare(a, b):
        if a + b > b + a:
            return -1
        if a + b < b + a:
            return 1
        return 0

    result = "".join(sorted(strings, key=cmp_to_key(compare)))
    return str(int(result)) if result else "0"
""".strip(),
        "tests": [
            {"args": [[10, 2]], "expected": "210"},
            {"args": [[3, 30, 34, 5, 9]], "expected": "9534330"},
            {"args": [[0, 0]], "expected": "0"},
            {"args": [[1]], "expected": "1"},
            {"args": [[]], "expected": "0"},
        ],
        "benchmark": {"args": [[(i * 37) % 90 + 10 for i in range(8)]]},
    },
    {
        "name": "minimum_absolute_difference",
        "category": "sorting",
        "technique": "Sort once and compare only adjacent values (O(n log n)) instead of "
                     "checking every pair (O(n^2)).",
        "description": "Return the smallest absolute difference between any two values in nums (None for fewer than 2 values).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def minimum_absolute_difference(nums):
    best = None
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            d = abs(nums[i] - nums[j])
            if best is None or d < best:
                best = d
    return best
""".strip(),
        "optimized": """
def minimum_absolute_difference(nums):
    if len(nums) < 2:
        return None
    nums = sorted(nums)
    best = None
    for i in range(1, len(nums)):
        d = nums[i] - nums[i - 1]
        if best is None or d < best:
            best = d
    return best
""".strip(),
        "tests": [
            {"args": [[4, 2, 1, 3]], "expected": 1},
            {"args": [[1, 3, 6, 10, 15]], "expected": 2},
            {"args": [[40, 10, 20]], "expected": 10},
            {"args": [[5, 5]], "expected": 0},
            {"args": [[7]], "expected": None},
        ],
        "benchmark": {"args": [[i * 97 % 10007 for i in range(3000)]]},
    },
    {
        "name": "sort_by_absolute_value",
        "category": "sorting",
        "technique": "Use sorted(key=abs) with the C sort implementation instead of a "
                     "Python insertion sort with O(n^2) shifts.",
        "description": "Return nums stably sorted by absolute value, ascending.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_by_absolute_value(nums):
    out = list(nums)
    for i in range(1, len(out)):
        key = out[i]
        j = i - 1
        while j >= 0 and abs(out[j]) > abs(key):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_by_absolute_value(nums):
    return sorted(nums, key=abs)
""".strip(),
        "tests": [
            {"args": [[3, -1, -2, 2]], "expected": [-1, -2, 2, 3]},
            {"args": [[0, -5, 5]], "expected": [0, -5, 5]},
            {"args": [[-3, 2, -1]], "expected": [-1, 2, -3]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 - 500 for i in range(2000)]]},
    },
    {
        "name": "sort_colors",
        "category": "sorting",
        "technique": "Partition 0/1/2 values with the Dutch national flag algorithm (O(n)) "
                     "instead of an O(n^2) bubble sort.",
        "description": "Sort a list containing only 0, 1, and 2 into ascending order.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def sort_colors(nums):
    out = list(nums)
    n = len(out)
    for i in range(n):
        for j in range(0, n - i - 1):
            if out[j] > out[j + 1]:
                out[j], out[j + 1] = out[j + 1], out[j]
    return out
""".strip(),
        "optimized": """
def sort_colors(nums):
    out = list(nums)
    low, mid, high = 0, 0, len(out) - 1
    while mid <= high:
        if out[mid] == 0:
            out[low], out[mid] = out[mid], out[low]
            low += 1
            mid += 1
        elif out[mid] == 1:
            mid += 1
        else:
            out[mid], out[high] = out[high], out[mid]
            high -= 1
    return out
""".strip(),
        "tests": [
            {"args": [[2, 0, 2, 1, 1, 0]], "expected": [0, 0, 1, 1, 2, 2]},
            {"args": [[2, 0, 1]], "expected": [0, 1, 2]},
            {"args": [[0]], "expected": [0]},
            {"args": [[1, 1]], "expected": [1, 1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 3 for i in range(3000)]]},
    },
    {
        "name": "min_meeting_rooms",
        "category": "sorting",
        "technique": "Sort starts and ends and sweep with two pointers (O(n log n)) instead "
                     "of counting overlaps for every interval (O(n^2)).",
        "description": "Return the minimum number of meeting rooms needed for half-open intervals [start, end).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def min_meeting_rooms(intervals):
    best = 0
    n = len(intervals)
    for i in range(n):
        start = intervals[i][0]
        count = 0
        for j in range(n):
            if intervals[j][0] <= start < intervals[j][1]:
                count += 1
        if count > best:
            best = count
    return best
""".strip(),
        "optimized": """
def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    starts = sorted(iv[0] for iv in intervals)
    ends = sorted(iv[1] for iv in intervals)
    rooms = 0
    best = 0
    i = j = 0
    n = len(intervals)
    while i < n:
        if starts[i] < ends[j]:
            rooms += 1
            if rooms > best:
                best = rooms
            i += 1
        else:
            rooms -= 1
            j += 1
    return best
""".strip(),
        "tests": [
            {"args": [[[0, 30], [5, 10], [15, 20]]], "expected": 2},
            {"args": [[[7, 10], [2, 4]]], "expected": 1},
            {"args": [[[0, 10], [5, 15], [10, 20]]], "expected": 2},
            {"args": [[[1, 5], [2, 6], [3, 7]]], "expected": 3},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[i, i + 100] for i in range(800)]]},
    },
    {
        "name": "largest_perimeter_triangle",
        "category": "sorting",
        "technique": "Sort descending and check adjacent triples (O(n log n)) instead of "
                     "enumerating every triple (O(n^3)).",
        "description": "Return the largest perimeter of any non-degenerate triangle formable from nums, or 0 if none.",
        "complexity_before": "O(n^3) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def largest_perimeter_triangle(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                a, b, c = nums[i], nums[j], nums[k]
                if a + b > c and a + c > b and b + c > a:
                    perimeter = a + b + c
                    if perimeter > best:
                        best = perimeter
    return best
""".strip(),
        "optimized": """
def largest_perimeter_triangle(nums):
    nums = sorted(nums, reverse=True)
    for i in range(len(nums) - 2):
        a, b, c = nums[i], nums[i + 1], nums[i + 2]
        if b + c > a:
            return a + b + c
    return 0
""".strip(),
        "tests": [
            {"args": [[2, 1, 2]], "expected": 5},
            {"args": [[1, 2, 1]], "expected": 0},
            {"args": [[3, 2, 3, 4]], "expected": 10},
            {"args": [[2, 3, 4, 5, 10]], "expected": 12},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 37 % 100 + 1 for i in range(200)]]},
    },
    {
        "name": "relative_sort_array",
        "category": "sorting",
        "technique": "Rank values with a dict and sort once (O(n log n)) instead of "
                     "repeatedly scanning and popping matches (O(n^2)).",
        "description": "Sort arr1 so values appear in arr2 order first, with the remaining values ascending afterward.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def relative_sort_array(arr1, arr2):
    remaining = list(arr1)
    out = []
    for target in arr2:
        i = 0
        while i < len(remaining):
            if remaining[i] == target:
                out.append(remaining.pop(i))
            else:
                i += 1
    out.extend(sorted(remaining))
    return out
""".strip(),
        "optimized": """
def relative_sort_array(arr1, arr2):
    order = {value: i for i, value in enumerate(arr2)}
    return sorted(arr1, key=lambda x: (order.get(x, len(arr2)), x))
""".strip(),
        "tests": [
            {"args": [[2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6]],
             "expected": [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]},
            {"args": [[28, 6, 22, 8, 44, 17], [22, 28, 8, 6]],
             "expected": [22, 28, 8, 6, 17, 44]},
            {"args": [[1, 2, 3], []], "expected": [1, 2, 3]},
            {"args": [[], [1, 2]], "expected": []},
        ],
        "benchmark": {"args": [[i % 500 for i in range(3000)], list(range(0, 500, 2))]},
    },
    {
        "name": "sort_strings_by_length",
        "category": "sorting",
        "technique": "Use sorted(key=len) with the C sort implementation instead of a "
                     "Python insertion sort with O(n^2) shifts.",
        "description": "Return words stably sorted by increasing length.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_strings_by_length(words):
    out = list(words)
    for i in range(1, len(out)):
        key = out[i]
        j = i - 1
        while j >= 0 and len(out[j]) > len(key):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_strings_by_length(words):
    return sorted(words, key=len)
""".strip(),
        "tests": [
            {"args": [["apple", "bat", "car", "banana"]], "expected": ["bat", "car", "apple", "banana"]},
            {"args": [["a", "bb", "ccc"]], "expected": ["a", "bb", "ccc"]},
            {"args": [["bb", "a", "cc"]], "expected": ["a", "bb", "cc"]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [["w" * ((i * 37) % 50 + 1) for i in range(2000)]]},
    },
    {
        "name": "find_duplicate_number",
        "category": "sorting",
        "technique": "Use Floyd's tortoise-and-hare cycle detection (O(n), O(1) space) "
                     "instead of comparing every pair (O(n^2)).",
        "description": "Given n+1 values in the range 1..n with exactly one duplicate, return the duplicate.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def find_duplicate_number(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return nums[i]
    return -1
""".strip(),
        "optimized": """
def find_duplicate_number(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
""".strip(),
        "tests": [
            {"args": [[1, 3, 4, 2, 2]], "expected": 2},
            {"args": [[3, 1, 3, 4, 2]], "expected": 3},
            {"args": [[1, 1]], "expected": 1},
            {"args": [[1, 2, 2]], "expected": 2},
        ],
        "benchmark": {"args": [list(range(1, 3001)) + [1500]]},
    },
    {
        "name": "sort_by_parity",
        "category": "sorting",
        "technique": "Partition into evens and odds in one pass (O(n)) instead of "
                     "searching forward for an even value for every odd index (O(n^2)).",
        "description": "Return a copy of nums with all even values first and all odd values after, preserving relative order.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def sort_by_parity(nums):
    out = list(nums)
    for i in range(1, len(out)):
        key = out[i]
        j = i - 1
        while j >= 0 and out[j] % 2 > key % 2:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_by_parity(nums):
    evens = [x for x in nums if x % 2 == 0]
    odds = [x for x in nums if x % 2 == 1]
    return evens + odds
""".strip(),
        "tests": [
            {"args": [[3, 1, 2, 4]], "expected": [2, 4, 3, 1]},
            {"args": [[1, 2, 3, 4]], "expected": [2, 4, 1, 3]},
            {"args": [[0]], "expected": [0]},

            {"args": [[1, 3]], "expected": [1, 3]},
            {"args": [[2, 4]], "expected": [2, 4]},
        ],
        "benchmark": {"args": [[1] * 1500 + [0] * 1500]},
    },
    {
        "name": "max_gap",
        "category": "sorting",
        "technique": "Sort once and scan adjacent values (O(n log n)) instead of searching "
                     "for the next larger value for every element (O(n^2)).",
        "description": "Return the largest difference between consecutive values after sorting (0 for fewer than 2 values).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def max_gap(nums):
    if len(nums) < 2:
        return 0
    best = 0
    for x in nums:
        next_larger = None
        for y in nums:
            if y > x and (next_larger is None or y < next_larger):
                next_larger = y
        if next_larger is not None:
            gap = next_larger - x
            if gap > best:
                best = gap
    return best
""".strip(),
        "optimized": """
def max_gap(nums):
    if len(nums) < 2:
        return 0
    ordered = sorted(nums)
    best = 0
    for i in range(1, len(ordered)):
        gap = ordered[i] - ordered[i - 1]
        if gap > best:
            best = gap
    return best
""".strip(),
        "tests": [
            {"args": [[3, 6, 9, 1]], "expected": 3},
            {"args": [[1, 5, 3, 9]], "expected": 4},
            {"args": [[10]], "expected": 0},
            {"args": [[1, 100]], "expected": 99},
            {"args": [[1, 1, 1]], "expected": 0},
        ],
        "benchmark": {"args": [[i * 97 % 10007 for i in range(3000)]]},
    },
    {
        "name": "sort_by_binary_ones",
        "category": "sorting",
        "technique": "Sort once with a (popcount, value) key (O(n log n)) instead of a "
                     "Python insertion sort that recomputes popcounts (O(n^2)).",
        "description": "Return nums sorted by increasing number of set bits, breaking ties by increasing value.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_by_binary_ones(nums):
    out = list(nums)
    for i in range(1, len(out)):
        key = out[i]
        key_count = bin(key).count("1")
        j = i - 1
        while j >= 0 and (bin(out[j]).count("1"), out[j]) > (key_count, key):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_by_binary_ones(nums):
    return sorted(nums, key=lambda x: (bin(x).count("1"), x))
""".strip(),
        "tests": [
            {"args": [[3, 1, 2, 4]], "expected": [1, 2, 4, 3]},
            {"args": [[0, 1, 2, 3]], "expected": [0, 1, 2, 3]},
            {"args": [[7, 8]], "expected": [8, 7]},
            {"args": [[5, 3, 6]], "expected": [3, 5, 6]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 for i in range(2000)]]},
    },
    {
        "name": "sort_by_digit_sum",
        "category": "sorting",
        "technique": "Sort once with a (digit sum, value) key (O(n log n)) instead of a "
                     "Python insertion sort that recomputes digit sums (O(n^2)).",
        "description": "Return nums sorted by increasing digit sum, breaking ties by increasing value.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_by_digit_sum(nums):
    out = list(nums)

    def digit_sum(x):
        total = 0
        while x:
            total += x % 10
            x //= 10
        return total

    for i in range(1, len(out)):
        key = out[i]
        key_sum = digit_sum(key)
        j = i - 1
        while j >= 0 and (digit_sum(out[j]), out[j]) > (key_sum, key):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_by_digit_sum(nums):
    return sorted(nums, key=lambda x: (sum(int(c) for c in str(x)), x))
""".strip(),
        "tests": [
            {"args": [[12, 21, 3]], "expected": [3, 12, 21]},
            {"args": [[10, 2, 30]], "expected": [10, 2, 30]},
            {"args": [[99, 1, 9]], "expected": [1, 9, 99]},
            {"args": [[0]], "expected": [0]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 for i in range(2000)]]},
    },
    {
        "name": "sort_by_distance_to_target",
        "category": "sorting",
        "technique": "Sort once with a (distance, value) key (O(n log n)) instead of a "
                     "Python insertion sort (O(n^2)).",
        "description": "Return nums sorted by increasing absolute distance to target, breaking ties by increasing value.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def sort_by_distance_to_target(nums, target):
    out = list(nums)
    for i in range(1, len(out)):
        key = out[i]
        j = i - 1
        while j >= 0 and (abs(out[j] - target), out[j]) > (abs(key - target), key):
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out
""".strip(),
        "optimized": """
def sort_by_distance_to_target(nums, target):
    return sorted(nums, key=lambda x: (abs(x - target), x))
""".strip(),
        "tests": [
            {"args": [[1, 5, 3], 3], "expected": [3, 1, 5]},
            {"args": [[10, 1, 5], 5], "expected": [5, 1, 10]},
            {"args": [[2, 2], 2], "expected": [2, 2]},
            {"args": [[], 3], "expected": []},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 for i in range(2000)], 500]},
    },
    {
        "name": "max_product_of_three",
        "category": "sorting",
        "technique": "Sort and check the two candidate triples (O(n log n)) instead of "
                     "enumerating every triple (O(n^3)).",
        "description": "Return the maximum product of any three values in nums.",
        "complexity_before": "O(n^3) time, O(1) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def max_product_of_three(nums):
    best = None
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                product = nums[i] * nums[j] * nums[k]
                if best is None or product > best:
                    best = product
    return best
""".strip(),
        "optimized": """
def max_product_of_three(nums):
    nums = sorted(nums)
    n = len(nums)
    return max(nums[-1] * nums[-2] * nums[-3], nums[0] * nums[1] * nums[-1])
""".strip(),
        "tests": [
            {"args": [[1, 2, 3]], "expected": 6},
            {"args": [[1, 2, 3, 4]], "expected": 24},
            {"args": [[-1, -2, -3]], "expected": -6},
            {"args": [[-10, -10, 1, 2, 3]], "expected": 300},
            {"args": [[0, 0, 0]], "expected": 0},
        ],
        "benchmark": {"args": [[(i * 37) % 201 - 100 for i in range(200)]]},
    },
]
