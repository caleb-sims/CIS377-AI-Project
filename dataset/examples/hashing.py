"""Category: hashing / set & dict lookups.

These examples replace an O(n^2) nested-loop scan with a single O(n) pass that
uses a ``set`` or ``dict`` for membership / lookup.
"""

EXAMPLES = [
    {
        "name": "two_sum",
        "category": "hashing",
        "technique": "Replace the O(n^2) nested loop with a single pass that stores "
                     "seen values in a hash table, giving O(n) time.",
        "description": "Return the indices of two numbers in nums that add up to target.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""".strip(),
        "optimized": """
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []
""".strip(),
        "tests": [
            {"args": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"args": [[3, 2, 4], 6], "expected": [1, 2]},
            {"args": [[1, 5, 4, 5], 9], "expected": [1, 2]},
            # Non-unique answer: any valid pair is acceptable.
            {"args": [[4, 2, 5, 3], 7], "acceptable": [[0, 3], [1, 2]]},
        ],
        "benchmark": {"args": [list(range(300)), 599]},
    },
    {
        "name": "has_duplicate",
        "category": "hashing",
        "technique": "Detect a repeat in one pass with a set instead of comparing "
                     "every pair, turning O(n^2) into O(n).",
        "description": "Return True if nums contains any value more than once.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def has_duplicate(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False
""".strip(),
        "optimized": """
def has_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": False},
            {"args": [[1, 2, 3, 2]], "expected": True},
            {"args": [[]], "expected": False},
            {"args": [[0, 0]], "expected": True},
        ],
        "benchmark": {"args": [list(range(300)) + [5]]},
    },
    {
        "name": "common_elements",
        "category": "hashing",
        "technique": "Compute the intersection with set algebra (O(n+m)) instead of "
                     "testing membership of every element against the other list.",
        "description": "Return a sorted list of values present in both a and b.",
        "complexity_before": "O(n*m) time, O(k) space",
        "complexity_after": "O(n+m) time, O(n+m) space",
        "unoptimized": """
def common_elements(a, b):
    out = []
    for x in a:
        for y in b:
            if x == y and x not in out:
                out.append(x)
    return sorted(out)
""".strip(),
        "optimized": """
def common_elements(a, b):
    return sorted(set(a) & set(b))
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4], [3, 4, 5]], "expected": [3, 4]},
            {"args": [[1, 2, 3], [4, 5]], "expected": []},
            {"args": [[1, 1, 2, 2], [2, 2, 3]], "expected": [2]},
            {"args": [[], [1, 2]], "expected": []},
        ],
        "benchmark": {"args": [list(range(150)), list(range(75, 225))]},
    },
    {
        "name": "first_duplicate",
        "category": "hashing",
        "technique": "Return the first value seen twice using a set of already-seen "
                     "values, avoiding the inner rescan for every index.",
        "description": "Return the first value (in scan order) that appears a second time, else -1.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def first_duplicate(nums):
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] == nums[j]:
                return nums[j]
    return -1
""".strip(),
        "optimized": """
def first_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    return -1
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 2, 1]], "expected": 2},
            {"args": [[1, 2, 3, 4]], "expected": -1},
            {"args": [[5, 5, 5]], "expected": 5},
            {"args": [[]], "expected": -1},
        ],
        "benchmark": {"args": [list(range(300)) + [7]]},
    },
    {
        "name": "max_frequency",
        "category": "hashing",
        "technique": "Count with collections.Counter in O(n) instead of counting each "
                     "distinct value with a full O(n) rescan (O(n^2)).",
        "description": "Return the highest number of times any single value appears in nums.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def max_frequency(nums):
    best = 0
    for x in nums:
        c = 0
        for y in nums:
            if x == y:
                c += 1
        if c > best:
            best = c
    return best
""".strip(),
        "optimized": """
def max_frequency(nums):
    from collections import Counter
    if not nums:
        return 0
    return Counter(nums).most_common(1)[0][1]
""".strip(),
        "tests": [
            {"args": [[1, 2, 2, 3, 3, 3]], "expected": 3},
            {"args": [[5]], "expected": 1},
            {"args": [[]], "expected": 0},
            {"args": [[1, 1, 2, 2]], "expected": 2},
        ],
        "benchmark": {"args": [[i % 7 for i in range(1500)]]},
    },
    {
        "name": "count_pairs_sum",
        "category": "hashing",
        "technique": "Count value pairs with a frequency table (O(n)) rather than "
                     "checking every pair of indices (O(n^2)).",
        "description": "Return how many unordered index pairs (i, j) with i < j have nums[i] + nums[j] == target.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def count_pairs_sum(nums, target):
    count = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_pairs_sum(nums, target):
    from collections import Counter
    c = Counter(nums)
    count = 0
    for x in c:
        y = target - x
        if x < y:
            count += c[x] * c[y]
        elif x == y:
            count += c[x] * (c[x] - 1) // 2
    return count
""".strip(),
        "tests": [
            {"args": [[1, 1, 2, 3, 4], 5], "expected": 3},
            {"args": [[2, 2, 2, 2], 4], "expected": 6},
            {"args": [[1, 2, 3], 100], "expected": 0},
            {"args": [[], 0], "expected": 0},
        ],
        "benchmark": {"args": [list(range(300)), 299]},
    },
    {
        "name": "unique_count",
        "category": "hashing",
        "technique": "Count distinct values with a set (O(n)) instead of rescanning a "
                     "growing list of already-seen values for every element (O(n^2)).",
        "description": "Return the number of distinct values in nums.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def unique_count(nums):
    unique = []
    for x in nums:
        found = False
        for y in unique:
            if x == y:
                found = True
                break
        if not found:
            unique.append(x)
    return len(unique)
""".strip(),
        "optimized": """
def unique_count(nums):
    return len(set(nums))
""".strip(),
        "tests": [
            {"args": [[1, 2, 2, 3, 1]], "expected": 3},
            {"args": [[]], "expected": 0},
            {"args": [[5, 5, 5]], "expected": 1},
            {"args": [["a", "b", "a"]], "expected": 2},
        ],
        "benchmark": {"args": [[i % 1000 for i in range(6000)]]},
    },
    {
        "name": "group_anagrams",
        "category": "hashing",
        "technique": "Use a dict keyed by the sorted-letter signature (O(n)) instead of "
                     "linearly searching the list of existing groups for every word (O(n^2)).",
        "description": "Group words into anagrams; return a dict mapping each sorted-letter signature to its words in input order.",
        "complexity_before": "O(n^2 * k) time, O(n * k) space",
        "complexity_after": "O(n * k log k) time, O(n * k) space",
        "unoptimized": """
def group_anagrams(words):
    signatures = []
    groups = []
    for w in words:
        sig = "".join(sorted(w))
        found = False
        for i, s in enumerate(signatures):
            if s == sig:
                groups[i].append(w)
                found = True
                break
        if not found:
            signatures.append(sig)
            groups.append([w])
    return {sig: group for sig, group in zip(signatures, groups)}
""".strip(),
        "optimized": """
def group_anagrams(words):
    groups = {}
    for w in words:
        sig = "".join(sorted(w))
        groups.setdefault(sig, []).append(w)
    return groups
""".strip(),
        "tests": [
            {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]],
             "expected": {"aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"]}},
            {"args": [["abc", "bca", "xyz"]], "expected": {"abc": ["abc", "bca"], "xyz": ["xyz"]}},
            {"args": [[""]], "expected": {"": [""]}},
            {"args": [[]], "expected": {}},
        ],
        "benchmark": {"args": [["w%d" % i for i in range(2000)]]},
    },
    {
        "name": "first_missing_positive",
        "category": "hashing",
        "technique": "Test candidate presence with a set (O(n)) instead of rescanning the "
                     "list for each candidate integer (O(n^2)).",
        "description": "Return the smallest positive integer that does not appear in nums.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def first_missing_positive(nums):
    candidate = 1
    while True:
        found = False
        for x in nums:
            if x == candidate:
                found = True
                break
        if not found:
            return candidate
        candidate += 1
""".strip(),
        "optimized": """
def first_missing_positive(nums):
    seen = set(nums)
    candidate = 1
    while candidate in seen:
        candidate += 1
    return candidate
""".strip(),
        "tests": [
            {"args": [[1, 2, 0]], "expected": 3},
            {"args": [[3, 4, -1, 1]], "expected": 2},
            {"args": [[7, 8, 9]], "expected": 1},
            {"args": [[]], "expected": 1},
            {"args": [[1, 1, 2, 2]], "expected": 3},
        ],
        "benchmark": {"args": [list(range(1, 1501))]},
    },
    {
        "name": "subarray_sum_count",
        "category": "hashing",
        "technique": "Count subarrays with a prefix-sum frequency table (O(n)) instead of "
                     "summing every subarray in a double loop (O(n^2)).",
        "description": "Return the number of contiguous subarrays of nums whose sum is exactly k.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def subarray_sum_count(nums, k):
    count = 0
    for i in range(len(nums)):
        s = 0
        for j in range(i, len(nums)):
            s += nums[j]
            if s == k:
                count += 1
    return count
""".strip(),
        "optimized": """
def subarray_sum_count(nums, k):
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
""".strip(),
        "tests": [
            {"args": [[1, 1, 1], 2], "expected": 2},
            {"args": [[1, 2, 3], 3], "expected": 2},
            {"args": [[1, -1, 0], 0], "expected": 3},
            {"args": [[1, 2, 3], 7], "expected": 0},
            {"args": [[], 0], "expected": 0},
        ],
        "benchmark": {"args": [[i % 5 - 2 for i in range(2000)], 3]},
    },
    {
        "name": "longest_consecutive",
        "category": "hashing",
        "technique": "Use a set for O(1) predecessor/successor checks instead of rescanning "
                     "the list for each candidate value (O(n^2)).",
        "description": "Return the length of the longest run of consecutive integers present in nums.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def longest_consecutive(nums):
    best = 0
    for x in nums:
        prev_exists = False
        for y in nums:
            if y == x - 1:
                prev_exists = True
                break
        if prev_exists:
            continue
        length = 0
        while True:
            found = False
            for y in nums:
                if y == x + length:
                    found = True
                    break
            if not found:
                break
            length += 1
        if length > best:
            best = length
    return best
""".strip(),
        "optimized": """
def longest_consecutive(nums):
    seen = set(nums)
    best = 0
    for x in seen:
        if x - 1 not in seen:
            length = 1
            while x + length in seen:
                length += 1
            if length > best:
                best = length
    return best
""".strip(),
        "tests": [
            {"args": [[100, 4, 200, 1, 3, 2]], "expected": 4},
            {"args": [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "expected": 9},
            {"args": [[]], "expected": 0},
            {"args": [[1, 2, 0, 1]], "expected": 3},
        ],
        "benchmark": {"args": [list(range(800, 0, -1))]},
    },
    {
        "name": "contains_nearby_duplicate",
        "category": "hashing",
        "technique": "Remember the last index of each value in a dict (O(n)) instead of "
                     "checking every pair within the window (O(n * k)).",
        "description": "Return True if nums has two equal values whose indices differ by at most k.",
        "complexity_before": "O(n * k) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def contains_nearby_duplicate(nums, k):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, min(i + k + 1, n)):
            if nums[i] == nums[j]:
                return True
    return False
""".strip(),
        "optimized": """
def contains_nearby_duplicate(nums, k):
    last = {}
    for i, x in enumerate(nums):
        if x in last and i - last[x] <= k:
            return True
        last[x] = i
    return False
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 1], 3], "expected": True},
            {"args": [[1, 0, 1, 1], 1], "expected": True},
            {"args": [[1, 2, 3, 1, 2, 3], 2], "expected": False},
            {"args": [[1, 2], 0], "expected": False},
        ],
        "benchmark": {"args": [list(range(3000)), 500]},
    },
    {
        "name": "find_disappeared_numbers",
        "category": "hashing",
        "technique": "Subtract sets (O(n)) instead of rescanning the input for every "
                     "candidate integer from 1 to n (O(n^2)).",
        "description": "Return the sorted list of integers in [1, len(nums)] that do not appear in nums.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def find_disappeared_numbers(nums):
    n = len(nums)
    missing = []
    for candidate in range(1, n + 1):
        found = False
        for x in nums:
            if x == candidate:
                found = True
                break
        if not found:
            missing.append(candidate)
    return missing
""".strip(),
        "optimized": """
def find_disappeared_numbers(nums):
    return sorted(set(range(1, len(nums) + 1)) - set(nums))
""".strip(),
        "tests": [
            {"args": [[4, 3, 2, 7, 8, 2, 3, 1]], "expected": [5, 6]},
            {"args": [[1, 1]], "expected": [2]},
            {"args": [[1, 2, 3]], "expected": []},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[1] * 2000]},
    },
    {
        "name": "pairs_with_difference",
        "category": "hashing",
        "technique": "Count complements with a frequency table (O(n)) instead of checking "
                     "every pair of indices (O(n^2)).",
        "description": "Return the number of unordered index pairs (i, j), i < j, with abs(nums[i] - nums[j]) == k (k >= 0).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def pairs_with_difference(nums, k):
    count = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(nums[i] - nums[j]) == k:
                count += 1
    return count
""".strip(),
        "optimized": """
def pairs_with_difference(nums, k):
    from collections import Counter
    counts = Counter(nums)
    total = 0
    for x, c in counts.items():
        if k == 0:
            total += c * (c - 1) // 2
        else:
            total += c * counts[x + k]
    return total
""".strip(),
        "tests": [
            {"args": [[1, 5, 3, 4, 2], 2], "expected": 3},
            {"args": [[1, 2, 3], 0], "expected": 0},
            {"args": [[1, 1, 1], 0], "expected": 3},
            {"args": [[8, 12, 16, 4], 4], "expected": 3},
            {"args": [[], 2], "expected": 0},
        ],
        "benchmark": {"args": [[i % 100 for i in range(3000)], 25]},
    },
    {
        "name": "find_all_duplicates",
        "category": "hashing",
        "technique": "Count frequencies with a Counter (O(n)) instead of rescanning the "
                     "whole list for every element and searching a list of results.",
        "description": "Return the sorted list of values that appear more than once in nums.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def find_all_duplicates(nums):
    duplicates = []
    for x in nums:
        count = 0
        for y in nums:
            if y == x:
                count += 1
        if count > 1 and x not in duplicates:
            duplicates.append(x)
    return sorted(duplicates)
""".strip(),
        "optimized": """
def find_all_duplicates(nums):
    from collections import Counter
    counts = Counter(nums)
    return sorted(x for x, c in counts.items() if c > 1)
""".strip(),
        "tests": [
            {"args": [[4, 3, 2, 7, 8, 2, 3, 1]], "expected": [2, 3]},
            {"args": [[1, 1, 2, 3, 3, 3]], "expected": [1, 3]},
            {"args": [[1, 2, 3]], "expected": []},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 400 for i in range(3000)]]},
    },
    {
        "name": "isomorphic_strings",
        "category": "hashing",
        "technique": "Track both directions of the character mapping with two dicts "
                     "(O(n)) instead of comparing every pair of positions (O(n^2)).",
        "description": "Return True if characters in s can be replaced one-to-one to obtain t.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def isomorphic_strings(s, t):
    if len(s) != len(t):
        return False
    for i in range(len(s)):
        for j in range(i):
            if (s[i] == s[j]) != (t[i] == t[j]):
                return False
    return True
""".strip(),
        "optimized": """
def isomorphic_strings(s, t):
    if len(s) != len(t):
        return False
    forward = {}
    backward = {}
    for a, b in zip(s, t):
        if a in forward and forward[a] != b:
            return False
        if b in backward and backward[b] != a:
            return False
        forward[a] = b
        backward[b] = a
    return True
""".strip(),
        "tests": [
            {"args": ["egg", "add"], "expected": True},
            {"args": ["foo", "bar"], "expected": False},
            {"args": ["paper", "title"], "expected": True},
            {"args": ["ab", "aa"], "expected": False},
            {"args": ["", ""], "expected": True},
        ],
        "benchmark": {"args": ["a" * 2000, "b" * 2000]},
    },
    {
        "name": "top_k_frequent",
        "category": "hashing",
        "technique": "Count with a Counter and sort once (O(n log n)) instead of searching "
                     "a list of counts for every element (O(n^2)).",
        "description": "Return the k most frequent values, ordered by decreasing frequency then increasing value.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n log n) time, O(n) space",
        "unoptimized": """
def top_k_frequent(nums, k):
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
    return [x for x, c in counts[:k]]
""".strip(),
        "optimized": """
def top_k_frequent(nums, k):
    from collections import Counter
    counts = Counter(nums)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [x for x, c in ordered[:k]]
""".strip(),
        "tests": [
            {"args": [[1, 1, 1, 2, 2, 3], 2], "expected": [1, 2]},
            {"args": [[1, 2], 2], "expected": [1, 2]},
            {"args": [[4, 4, 5, 5, 6], 1], "expected": [4]},
            {"args": [[1, 1, 2, 2, 3, 3], 2], "expected": [1, 2]},
        ],
        "benchmark": {"args": [[i % 300 for i in range(5000)], 10]},
    },
    {
        "name": "subarray_sum_multiple_of_k",
        "category": "hashing",
        "technique": "Detect a repeated prefix-sum remainder with a dict (O(n)) instead of "
                     "summing every subarray in a double loop (O(n^2)).",
        "description": "Return True if some non-empty contiguous subarray of nums has a sum divisible by k (k > 0).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def subarray_sum_multiple_of_k(nums, k):
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total % k == 0:
                return True
    return False
""".strip(),
        "optimized": """
def subarray_sum_multiple_of_k(nums, k):
    remainder = {0: -1}
    prefix = 0
    for i, x in enumerate(nums):
        prefix += x
        r = prefix % k
        if r in remainder:
            return True
        remainder[r] = i
    return False
""".strip(),
        "tests": [
            {"args": [[23, 2, 4, 6, 7], 6], "expected": True},
            {"args": [[23, 2, 6, 4, 7], 6], "expected": True},
            {"args": [[1, 2, 3], 7], "expected": False},
            {"args": [[0], 5], "expected": True},
            {"args": [[5], 5], "expected": True},
            {"args": [[1, 1, 1], 2], "expected": True},
        ],
        "benchmark": {"args": [[1] * 3000, 3001]},
    },
    {
        "name": "first_repeated_element",
        "category": "hashing",
        "technique": "Track seen values in a set (O(n)) instead of comparing each element "
                     "against every earlier element (O(n^2)).",
        "description": "Return the first value encountered that has already appeared, or None if all values are distinct.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def first_repeated_element(nums):
    for i in range(len(nums)):
        for j in range(i):
            if nums[i] == nums[j]:
                return nums[i]
    return None
""".strip(),
        "optimized": """
def first_repeated_element(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    return None
""".strip(),
        "tests": [
            {"args": [[2, 1, 3, 5, 3, 2]], "expected": 3},
            {"args": [[1, 2, 3]], "expected": None},
            {"args": [[1, 1]], "expected": 1},
            {"args": [["a", "b", "a"]], "expected": "a"},
            {"args": [[]], "expected": None},
        ],
        "benchmark": {"args": [list(range(2000)) + [1999]]},
    },
    {
        "name": "unique_number_of_occurrences",
        "category": "hashing",
        "technique": "Count frequencies with a Counter and compare against a set (O(n)) "
                     "instead of searching a list of counts for every element (O(n^2)).",
        "description": "Return True if every distinct value in nums occurs a distinct number of times.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def unique_number_of_occurrences(nums):
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
    frequencies = [c for x, c in counts]
    for i in range(len(frequencies)):
        for j in range(i + 1, len(frequencies)):
            if frequencies[i] == frequencies[j]:
                return False
    return True
""".strip(),
        "optimized": """
def unique_number_of_occurrences(nums):
    from collections import Counter
    frequencies = list(Counter(nums).values())
    return len(frequencies) == len(set(frequencies))
""".strip(),
        "tests": [
            {"args": [[1, 2, 2, 1, 1, 3]], "expected": True},
            {"args": [[1, 2]], "expected": False},
            {"args": [[1, 1]], "expected": True},
            {"args": [[1, 1, 2, 2, 3]], "expected": False},
            {"args": [[]], "expected": True},
        ],
        "benchmark": {"args": [[i % 300 for i in range(5000)]]},
    },
    {
        "name": "count_subarrays_with_equal_zeros_ones",
        "category": "hashing",
        "technique": "Map 0 to -1 and count equal prefix sums with a dict (O(n)) instead "
                     "of scanning every subarray (O(n^2)).",
        "description": "Return the number of contiguous subarrays containing an equal number of 0s and 1s.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def count_subarrays_with_equal_zeros_ones(nums):
    count = 0
    n = len(nums)
    for i in range(n):
        zeros = 0
        ones = 0
        for j in range(i, n):
            if nums[j] == 0:
                zeros += 1
            else:
                ones += 1
            if zeros == ones:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_subarrays_with_equal_zeros_ones(nums):
    first = {0: 1}
    diff = 0
    count = 0
    for x in nums:
        diff += 1 if x == 1 else -1
        if diff in first:
            count += first[diff]
            first[diff] += 1
        else:
            first[diff] = 1
    return count
""".strip(),
        "tests": [
            {"args": [[0, 1]], "expected": 1},
            {"args": [[0, 1, 0]], "expected": 2},
            {"args": [[0, 0, 1, 1]], "expected": 2},
            {"args": [[1, 0, 1, 0]], "expected": 4},
            {"args": [[1, 1]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i % 2 for i in range(3000)]]},
    },
    {
        "name": "longest_harmonious_subsequence",
        "category": "hashing",
        "technique": "Count values with a Counter and look up v+1 (O(n)) instead of "
                     "rescanning the list for every possible lower value (O(n^2)).",
        "description": "Return the length of the longest subsequence whose maximum minus minimum equals exactly 1.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def longest_harmonious_subsequence(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        v = nums[i]
        count_v = 0
        count_v1 = 0
        for x in nums:
            if x == v:
                count_v += 1
            elif x == v + 1:
                count_v1 += 1
        if count_v1 and count_v + count_v1 > best:
            best = count_v + count_v1
    return best
""".strip(),
        "optimized": """
def longest_harmonious_subsequence(nums):
    from collections import Counter
    counts = Counter(nums)
    best = 0
    for v, c in counts.items():
        if v + 1 in counts:
            total = c + counts[v + 1]
            if total > best:
                best = total
    return best
""".strip(),
        "tests": [
            {"args": [[1, 3, 2, 2, 5, 2, 3, 7]], "expected": 5},
            {"args": [[1, 2, 3, 4]], "expected": 2},
            {"args": [[1, 1, 1]], "expected": 0},
            {"args": [[1, 2]], "expected": 2},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i % 100 for i in range(3000)]]},
    },
    {
        "name": "find_common_characters",
        "category": "hashing",
        "technique": "Take the minimum character count across words with Counters (O(total)) "
                     "instead of rescanning each word for every shared character.",
        "description": "Return the sorted list of characters common to every word, including duplicates up to the minimum count.",
        "complexity_before": "O(total^2) time, O(total) space",
        "complexity_after": "O(total) time, O(total) space",
        "unoptimized": """
def find_common_characters(words):
    if not words:
        return []
    common = list(words[0])
    for w in words[1:]:
        next_common = []
        used = [False] * len(w)
        for c in common:
            for j, d in enumerate(w):
                if not used[j] and c == d:
                    used[j] = True
                    next_common.append(c)
                    break
        common = next_common
    return sorted(common)
""".strip(),
        "optimized": """
def find_common_characters(words):
    from collections import Counter
    if not words:
        return []
    common = Counter(words[0])
    for w in words[1:]:
        counts = Counter(w)
        for c in list(common):
            common[c] = min(common[c], counts.get(c, 0))
    out = []
    for c, n in common.items():
        out.extend([c] * n)
    return sorted(out)
""".strip(),
        "tests": [
            {"args": [["bella", "label", "roller"]], "expected": ["e", "l", "l"]},
            {"args": [["cool", "lock", "cook"]], "expected": ["c", "o"]},
            {"args": [["a", "aa"]], "expected": ["a"]},
            {"args": [["abc", "def"]], "expected": []},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [["ab" * 100] * 200]},
    },
    {
        "name": "find_anagrams_in_string",
        "category": "hashing",
        "technique": "Maintain a sliding character-count window (O(n)) instead of sorting "
                     "every window from scratch (O(n * m log m)).",
        "description": "Return the sorted starting indices of all substrings of s that are anagrams of p.",
        "complexity_before": "O(n * m log m) time, O(m) space",
        "complexity_after": "O(n) time, O(m) space",
        "unoptimized": """
def find_anagrams_in_string(s, p):
    m = len(p)
    if m == 0 or m > len(s):
        return []
    target = sorted(p)
    out = []
    for i in range(len(s) - m + 1):
        if sorted(s[i:i + m]) == target:
            out.append(i)
    return out
""".strip(),
        "optimized": """
def find_anagrams_in_string(s, p):
    from collections import Counter
    m = len(p)
    if m == 0 or m > len(s):
        return []
    target = Counter(p)
    window = Counter(s[:m])
    out = []
    if window == target:
        out.append(0)
    for i in range(m, len(s)):
        left = s[i - m]
        window[left] -= 1
        if window[left] == 0:
            del window[left]
        window[s[i]] += 1
        if window == target:
            out.append(i - m + 1)
    return out
""".strip(),
        "tests": [
            {"args": ["cbaebabacd", "abc"], "expected": [0, 6]},
            {"args": ["abab", "ab"], "expected": [0, 1, 2]},
            {"args": ["a", "b"], "expected": []},
            {"args": ["a", "a"], "expected": [0]},
            {"args": ["", "a"], "expected": []},
        ],
        "benchmark": {"args": ["abcdefghij" * 600, "abcdefghij" * 10]},
    },
    {
        "name": "longest_subarray_equal_zeros_ones",
        "category": "hashing",
        "technique": "Track the first occurrence of each prefix-sum difference (O(n)) "
                     "instead of scanning every subarray (O(n^2)).",
        "description": "Return the length of the longest contiguous subarray with an equal number of 0s and 1s.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def longest_subarray_equal_zeros_ones(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        zeros = 0
        ones = 0
        for j in range(i, n):
            if nums[j] == 0:
                zeros += 1
            else:
                ones += 1
            if zeros == ones and j - i + 1 > best:
                best = j - i + 1
    return best
""".strip(),
        "optimized": """
def longest_subarray_equal_zeros_ones(nums):
    first = {0: -1}
    diff = 0
    best = 0
    for i, x in enumerate(nums):
        diff += 1 if x == 1 else -1
        if diff in first:
            length = i - first[diff]
            if length > best:
                best = length
        else:
            first[diff] = i
    return best
""".strip(),
        "tests": [
            {"args": [[0, 1]], "expected": 2},
            {"args": [[0, 1, 0]], "expected": 2},
            {"args": [[0, 0, 1, 1]], "expected": 4},
            {"args": [[1, 0, 1, 0, 1]], "expected": 4},
            {"args": [[1, 1]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[i % 2 for i in range(3000)]]},
    },
    {
        "name": "difference_of_arrays",
        "category": "hashing",
        "technique": "Use set differences (O(n + m)) instead of checking every element "
                     "against the other list (O(n * m)).",
        "description": "Return [values only in a, values only in b], each sorted and deduplicated.",
        "complexity_before": "O(n * m) time, O(n + m) space",
        "complexity_after": "O(n + m) time, O(n + m) space",
        "unoptimized": """
def difference_of_arrays(a, b):
    only_a = []
    for x in a:
        found = False
        for y in b:
            if x == y:
                found = True
                break
        if not found and x not in only_a:
            only_a.append(x)
    only_b = []
    for x in b:
        found = False
        for y in a:
            if x == y:
                found = True
                break
        if not found and x not in only_b:
            only_b.append(x)
    return [sorted(only_a), sorted(only_b)]
""".strip(),
        "optimized": """
def difference_of_arrays(a, b):
    set_a = set(a)
    set_b = set(b)
    return [sorted(set_a - set_b), sorted(set_b - set_a)]
""".strip(),
        "tests": [
            {"args": [[1, 2, 3], [2, 4, 6]], "expected": [[1, 3], [4, 6]]},
            {"args": [[1, 2], [1, 2]], "expected": [[], []]},
            {"args": [[1], [2]], "expected": [[1], [2]]},
            {"args": [[1, 1, 2], [2, 3]], "expected": [[1], [3]]},
            {"args": [[], []], "expected": [[], []]},
        ],
        "benchmark": {"args": [list(range(3000)), list(range(1500, 4500))]},
    },
    {
        "name": "count_subarrays_divisible_by_k",
        "category": "hashing",
        "technique": "Count prefix-sum remainders with a dict (O(n)) instead of checking "
                     "every subarray (O(n^2)).",
        "description": "Return the number of contiguous subarrays whose sum is divisible by k (k > 0).",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(k) space",
        "unoptimized": """
def count_subarrays_divisible_by_k(nums, k):
    count = 0
    n = len(nums)
    for i in range(n):
        total = 0
        for j in range(i, n):
            total += nums[j]
            if total % k == 0:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_subarrays_divisible_by_k(nums, k):
    counts = {0: 1}
    prefix = 0
    total = 0
    for x in nums:
        prefix += x
        r = prefix % k
        if r in counts:
            total += counts[r]
            counts[r] += 1
        else:
            counts[r] = 1
    return total
""".strip(),
        "tests": [
            {"args": [[4, 5, 0, -2, -3, 1], 5], "expected": 7},
            {"args": [[5], 5], "expected": 1},
            {"args": [[1, 2, 3], 3], "expected": 3},
            {"args": [[1, 2], 3], "expected": 1},
            {"args": [[], 5], "expected": 0},
        ],
        "benchmark": {"args": [[i % 7 - 3 for i in range(3000)], 5]},
    },
]
