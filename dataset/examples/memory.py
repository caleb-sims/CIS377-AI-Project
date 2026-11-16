"""Category: memory & lazy evaluation.

These trade peak memory (and often also time) by yielding lazily, avoiding large
intermediate collections, or using a closed-form instead of materializing a big list.
"""

EXAMPLES = [
    {
        "name": "squares",
        "category": "memory",
        "technique": "Yield a lazy generator instead of building the whole list up front; "
                     "the caller only materializes as much as it consumes.",
        "description": "Yield the squares 0^2, 1^2, ..., (n-1)^2 lazily.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def squares(n):
    return [i * i for i in range(n)]
""".strip(),
        "optimized": """
def squares(n):
    for i in range(n):
        yield i * i
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [5], "expected": [0, 1, 4, 9, 16]},
            {"args": [0], "expected": []},
            {"args": [1], "expected": [0]},
        ],
        "benchmark": {"args": [5000]},
    },
    {
        "name": "sum_of_first_even_numbers",
        "category": "memory",
        "technique": "Use the closed-form arithmetic series k*(k+1) instead of building "
                     "and summing a k-element list (avoids O(k) space and O(k) time).",
        "description": "Return the sum of the first k even positive integers (2 + 4 + ... + 2k).",
        "complexity_before": "O(k) time, O(k) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_first_even_numbers(k):
    nums = []
    i = 2
    while len(nums) < k:
        nums.append(i)
        i += 2
    return sum(nums)
""".strip(),
        "optimized": """
def sum_of_first_even_numbers(k):
    return k * (k + 1)
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 2},
            {"args": [3], "expected": 12},
            {"args": [10], "expected": 110},
        ],
        "benchmark": {"args": [100000]},
    },
    {
        "name": "even_sums_of_pairs",
        "category": "memory",
        "technique": "Accumulate the answer in one pass instead of building an "
                     "intermediate list of every pair-sum and then looping it again.",
        "description": "Return the sum of all even values among the sums a+b of each pair (a, b) in pairs.",
        "complexity_before": "O(n) time, O(n) space (intermediate list)",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def even_sums_of_pairs(pairs):
    total = 0
    sums = []
    for a, b in pairs:
        s = a + b
        sums.append(s)
    for s in sums:
        if s % 2 == 0:
            total += s
    return total
""".strip(),
        "optimized": """
def even_sums_of_pairs(pairs):
    total = 0
    for a, b in pairs:
        s = a + b
        if s % 2 == 0:
            total += s
    return total
""".strip(),
        "tests": [
            {"args": [[(1, 1), (2, 3), (4, 4)]], "expected": 10},
            {"args": [[]], "expected": 0},
            {"args": [[(1, 2)]], "expected": 0},
        ],
        "benchmark": {"args": [[(i, i) for i in range(5000)]], },
    },
    {
        "name": "is_prime",
        "category": "memory",
        "technique": "Trial-divide only up to sqrt(n) and skip even divisors, cutting the "
                     "loop from ~n/2 iterations to ~sqrt(n)/2.",
        "description": "Return True if n is a prime number.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(sqrt(n)) time, O(1) space",
        "unoptimized": """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
""".strip(),
        "optimized": """
def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True
""".strip(),
        "tests": [
            {"args": [1], "expected": False},
            {"args": [2], "expected": True},
            {"args": [3], "expected": True},
            {"args": [17], "expected": True},
            {"args": [18], "expected": False},
            {"args": [97], "expected": True},
            {"args": [100], "expected": False},
        ],
        "benchmark": {"args": [999983]},
    },
    {
        "name": "sum_even_squares",
        "category": "memory",
        "technique": "Sum a generator expression (O(1) extra space) instead of building "
                     "intermediate lists of even values and then of their squares.",
        "description": "Return the sum of the squares of the even values in nums.",
        "complexity_before": "O(n) time, O(n) space (intermediate lists)",
        "complexity_after": "O(n) time, O(1) extra space",
        "unoptimized": """
def sum_even_squares(nums):
    evens = []
    for x in nums:
        if x % 2 == 0:
            evens.append(x)
    squares = []
    for x in evens:
        squares.append(x * x)
    total = 0
    for s in squares:
        total += s
    return total
""".strip(),
        "optimized": """
def sum_even_squares(nums):
    return sum(x * x for x in nums if x % 2 == 0)
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": 20},
            {"args": [[]], "expected": 0},
            {"args": [[2, 2]], "expected": 8},
            {"args": [[1, 3]], "expected": 0},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "running_maximum",
        "category": "memory",
        "technique": "Yield each running maximum lazily instead of allocating the full "
                     "output list before returning anything.",
        "description": "Yield the maximum value seen so far after each element of nums.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def running_maximum(nums):
    out = []
    best = None
    for x in nums:
        if best is None or x > best:
            best = x
        out.append(best)
    return out
""".strip(),
        "optimized": """
def running_maximum(nums):
    best = None
    for x in nums:
        if best is None or x > best:
            best = x
        yield best
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 3, 2, 5, 4]], "expected": [1, 3, 3, 5, 5]},
            {"args": [[3, 2, 1]], "expected": [3, 3, 3]},
            {"args": [[-2, -1, -3]], "expected": [-2, -1, -1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i * 37 % 1000 for i in range(20000)]]},
    },
    {
        "name": "flatten_sum",
        "category": "memory",
        "technique": "Stream values through a nested generator instead of building a flat "
                     "list of every element before summing it.",
        "description": "Return the sum of every number in a list of lists.",
        "complexity_before": "O(total) time, O(total) space (flat list)",
        "complexity_after": "O(total) time, O(1) extra space",
        "unoptimized": """
def flatten_sum(nested):
    flat = []
    for sub in nested:
        for x in sub:
            flat.append(x)
    total = 0
    for x in flat:
        total += x
    return total
""".strip(),
        "optimized": """
def flatten_sum(nested):
    return sum(x for sub in nested for x in sub)
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3], [4, 5]]], "expected": 15},
            {"args": [[[], [1]]], "expected": 1},
            {"args": [[[1, -2], [3]]], "expected": 2},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[j for j in range(20)] for i in range(2000)]]},
    },
    {
        "name": "prefix_averages",
        "category": "memory",
        "technique": "Yield running averages lazily instead of storing the whole output "
                     "list before the caller can consume any value.",
        "description": "Yield the running mean after each element of nums.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def prefix_averages(nums):
    out = []
    total = 0
    for i, x in enumerate(nums):
        total += x
        out.append(total / (i + 1))
    return out
""".strip(),
        "optimized": """
def prefix_averages(nums):
    total = 0
    for i, x in enumerate(nums):
        total += x
        yield total / (i + 1)
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [1.0, 1.5, 2.0, 2.5]},
            {"args": [[2]], "expected": [2.0]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "fibonacci_sequence",
        "category": "memory",
        "technique": "Yield Fibonacci numbers one at a time instead of allocating the "
                     "entire n-element result list up front.",
        "description": "Yield the first n Fibonacci numbers starting with 0, 1.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def fibonacci_sequence(n):
    out = []
    a, b = 0, 1
    for _ in range(n):
        out.append(a)
        a, b = b, a + b
    return out
""".strip(),
        "optimized": """
def fibonacci_sequence(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [5], "expected": [0, 1, 1, 2, 3]},
            {"args": [1], "expected": [0]},
            {"args": [0], "expected": []},
            {"args": [8], "expected": [0, 1, 1, 2, 3, 5, 8, 13]},
        ],
        "benchmark": {"args": [20000]},
    },
    {
        "name": "running_product",
        "category": "memory",
        "technique": "Yield cumulative products lazily instead of storing the entire "
                     "output list before returning.",
        "description": "Yield the running product after each element of nums.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def running_product(nums):
    out = []
    product = 1
    for x in nums:
        product *= x
        out.append(product)
    return out
""".strip(),
        "optimized": """
def running_product(nums):
    product = 1
    for x in nums:
        product *= x
        yield product
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [1, 2, 6, 24]},
            {"args": [[2, 0, 3]], "expected": [2, 0, 0]},
            {"args": [[5]], "expected": [5]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[1] * 20000]},
    },
    {
        "name": "elementwise_sum_lazy",
        "category": "memory",
        "technique": "Yield pairwise sums on demand instead of materializing the whole "
                     "result list eagerly.",
        "description": "Yield a[i] + b[i] for two equal-length sequences.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def elementwise_sum_lazy(a, b):
    out = []
    for i in range(len(a)):
        out.append(a[i] + b[i])
    return out
""".strip(),
        "optimized": """
def elementwise_sum_lazy(a, b):
    for x, y in zip(a, b):
        yield x + y
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2], [3, 4]], "expected": [4, 6]},
            {"args": [[1, -2], [2, 2]], "expected": [3, 0]},
            {"args": [[1], [2]], "expected": [3]},
            {"args": [[], []], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000)), list(range(20000))]},
    },
    {
        "name": "take_while_positive",
        "category": "memory",
        "technique": "Yield the leading positive values lazily instead of allocating a "
                     "result list before returning.",
        "description": "Yield the values of nums up to (but not including) the first non-positive value.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def take_while_positive(nums):
    out = []
    for x in nums:
        if x <= 0:
            break
        out.append(x)
    return out
""".strip(),
        "optimized": """
def take_while_positive(nums):
    for x in nums:
        if x <= 0:
            break
        yield x
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 0, 3]], "expected": [1, 2]},
            {"args": [[-1, 2]], "expected": []},
            {"args": [[3, 4, 5]], "expected": [3, 4, 5]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(1, 20000))]},
    },
    {
        "name": "chunked_sums",
        "category": "memory",
        "technique": "Yield each chunk sum lazily instead of building the complete list "
                     "of chunk sums up front.",
        "description": "Yield the sum of each consecutive chunk of length size in nums.",
        "complexity_before": "O(n) time, O(n / size) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def chunked_sums(nums, size):
    out = []
    for i in range(0, len(nums), size):
        total = 0
        for x in nums[i:i + size]:
            total += x
        out.append(total)
    return out
""".strip(),
        "optimized": """
def chunked_sums(nums, size):
    for i in range(0, len(nums), size):
        total = 0
        for x in nums[i:i + size]:
            total += x
        yield total
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4, 5], 2], "expected": [3, 7, 5]},
            {"args": [[1, 2, 3], 5], "expected": [6]},
            {"args": [[1, 2, 3, 4], 2], "expected": [3, 7]},
            {"args": [[], 3], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000)), 100]},
    },
    {
        "name": "dedupe_lazy",
        "category": "memory",
        "technique": "Yield first occurrences lazily instead of materializing the whole "
                     "deduplicated list.",
        "description": "Yield the distinct values of nums in first-seen order.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) output space (lazy), O(unique) for the seen set",
        "unoptimized": """
def dedupe_lazy(nums):
    seen = set()
    out = []
    for x in nums:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
""".strip(),
        "optimized": """
def dedupe_lazy(nums):
    seen = set()
    for x in nums:
        if x not in seen:
            seen.add(x)
            yield x
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 1, 3, 2]], "expected": [1, 2, 3]},
            {"args": [[5, 5]], "expected": [5]},
            {"args": [["a", "b", "a"]], "expected": ["a", "b"]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 500 for i in range(20000)]]},
    },
    {
        "name": "filter_even_lazy",
        "category": "memory",
        "technique": "Yield matching values lazily instead of allocating the full "
                     "filtered list before returning.",
        "description": "Yield the even values of nums in order.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def filter_even_lazy(nums):
    out = []
    for x in nums:
        if x % 2 == 0:
            out.append(x)
    return out
""".strip(),
        "optimized": """
def filter_even_lazy(nums):
    for x in nums:
        if x % 2 == 0:
            yield x
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [2, 4]},
            {"args": [[1, 3]], "expected": []},
            {"args": [[0, 2]], "expected": [0, 2]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "sliding_window_sums_lazy",
        "category": "memory",
        "technique": "Yield each window sum lazily instead of materializing all "
                     "n - k + 1 sums up front.",
        "description": "Yield the sum of every contiguous window of length k.",
        "complexity_before": "O(n * k) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n * k) total when fully consumed",
        "unoptimized": """
def sliding_window_sums_lazy(nums, k):
    out = []
    for i in range(len(nums) - k + 1):
        total = 0
        for x in nums[i:i + k]:
            total += x
        out.append(total)
    return out
""".strip(),
        "optimized": """
def sliding_window_sums_lazy(nums, k):
    for i in range(len(nums) - k + 1):
        total = 0
        for x in nums[i:i + k]:
            total += x
        yield total
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4], 2], "expected": [3, 5, 7]},
            {"args": [[1, 2, 3], 3], "expected": [6]},
            {"args": [[1, 2], 3], "expected": []},
            {"args": [[], 2], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000)), 50]},
    },
    {
        "name": "pairwise_products_lazy",
        "category": "memory",
        "technique": "Yield adjacent products lazily instead of materializing the whole "
                     "result list up front.",
        "description": "Yield nums[i] * nums[i + 1] for each adjacent pair.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def pairwise_products_lazy(nums):
    out = []
    for i in range(len(nums) - 1):
        out.append(nums[i] * nums[i + 1])
    return out
""".strip(),
        "optimized": """
def pairwise_products_lazy(nums):
    for i in range(len(nums) - 1):
        yield nums[i] * nums[i + 1]
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [2, 6, 12]},
            {"args": [[2, 3]], "expected": [6]},
            {"args": [[-1, 2, -3]], "expected": [-2, -6]},
            {"args": [[5]], "expected": []},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "chunked_max_lazy",
        "category": "memory",
        "technique": "Yield each chunk maximum lazily instead of building the complete "
                     "list of maxima before returning.",
        "description": "Yield the maximum of each consecutive chunk of length size.",
        "complexity_before": "O(n) time, O(n / size) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def chunked_max_lazy(nums, size):
    out = []
    for i in range(0, len(nums), size):
        chunk = nums[i:i + size]
        best = chunk[0]
        for x in chunk[1:]:
            if x > best:
                best = x
        out.append(best)
    return out
""".strip(),
        "optimized": """
def chunked_max_lazy(nums, size):
    for i in range(0, len(nums), size):
        chunk = nums[i:i + size]
        best = chunk[0]
        for x in chunk[1:]:
            if x > best:
                best = x
        yield best
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 3, 2, 5, 4], 2], "expected": [3, 5, 4]},
            {"args": [[1, 2, 3], 5], "expected": [3]},
            {"args": [[5], 1], "expected": [5]},
            {"args": [[], 3], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000)), 100]},
    },
    {
        "name": "flatten_lazy",
        "category": "memory",
        "technique": "Yield values from nested lists lazily instead of building a flat "
                     "list of every element.",
        "description": "Yield every number from a list of lists in order.",
        "complexity_before": "O(total) time, O(total) space (flat list)",
        "complexity_after": "O(1) space (lazy), O(total) total when fully consumed",
        "unoptimized": """
def flatten_lazy(nested):
    out = []
    for sub in nested:
        for x in sub:
            out.append(x)
    return out
""".strip(),
        "optimized": """
def flatten_lazy(nested):
    for sub in nested:
        for x in sub:
            yield x
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[[1, 2], [3], [4, 5]]], "expected": [1, 2, 3, 4, 5]},
            {"args": [[[], []]], "expected": []},
            {"args": [[[1]]], "expected": [1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[list(range(100)) for _ in range(200)]]},
    },
    {
        "name": "running_minimum",
        "category": "memory",
        "technique": "Yield each running minimum lazily instead of allocating the full "
                     "output list before returning.",
        "description": "Yield the minimum value seen so far after each element of nums.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def running_minimum(nums):
    out = []
    best = None
    for x in nums:
        if best is None or x < best:
            best = x
        out.append(best)
    return out
""".strip(),
        "optimized": """
def running_minimum(nums):
    best = None
    for x in nums:
        if best is None or x < best:
            best = x
        yield best
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[3, 1, 2, 0, 4]], "expected": [3, 1, 1, 0, 0]},
            {"args": [[5]], "expected": [5]},
            {"args": [[2, 2]], "expected": [2, 2]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "cumulative_sums_lazy",
        "category": "memory",
        "technique": "Yield prefix sums lazily instead of materializing the whole "
                     "cumulative-sum list.",
        "description": "Yield the running total after each element of nums.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) space (lazy), O(n) total when fully consumed",
        "unoptimized": """
def cumulative_sums_lazy(nums):
    out = []
    total = 0
    for x in nums:
        total += x
        out.append(total)
    return out
""".strip(),
        "optimized": """
def cumulative_sums_lazy(nums):
    total = 0
    for x in nums:
        total += x
        yield total
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 3, 4]], "expected": [1, 3, 6, 10]},
            {"args": [[5]], "expected": [5]},
            {"args": [[-1, 1, -1]], "expected": [-1, 0, -1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "unique_squares_lazy",
        "category": "memory",
        "technique": "Yield squares of first-seen values lazily instead of building the "
                     "whole output list up front.",
        "description": "Yield the square of each distinct value of nums in first-seen order.",
        "complexity_before": "O(n) time, O(n) space (full list)",
        "complexity_after": "O(1) output space (lazy), O(unique) for the seen set",
        "unoptimized": """
def unique_squares_lazy(nums):
    seen = set()
    out = []
    for x in nums:
        if x not in seen:
            seen.add(x)
            out.append(x * x)
    return out
""".strip(),
        "optimized": """
def unique_squares_lazy(nums):
    seen = set()
    for x in nums:
        if x not in seen:
            seen.add(x)
            yield x * x
""".strip(),
        "materialize_output": True,
        "tests": [
            {"args": [[1, 2, 1, 3, 2]], "expected": [1, 4, 9]},
            {"args": [[2, 2]], "expected": [4]},
            {"args": [[-1, 1]], "expected": [1, 1]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[i % 500 for i in range(20000)]]},
    },
]
