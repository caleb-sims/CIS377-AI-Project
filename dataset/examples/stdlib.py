"""Category: standard library / closed-form math.

Replace manual loops with a mathematical closed form or an efficient stdlib algorithm
(Euclidean gcd, built-in modular exponentiation).
"""

EXAMPLES = [
    {
        "name": "sum_of_ranges",
        "category": "math",
        "technique": "Use the arithmetic-series closed form n*(start+end)/2 instead of "
                     "adding every term in a loop.",
        "description": "Return the sum of every integer from start to end inclusive.",
        "complexity_before": "O(end - start) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_ranges(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total
""".strip(),
        "optimized": """
def sum_of_ranges(start, end):
    n = end - start + 1
    return n * (start + end) // 2
""".strip(),
        "tests": [
            {"args": [1, 10], "expected": 55},
            {"args": [5, 5], "expected": 5},
            {"args": [-3, 3], "expected": 0},
            {"args": [1, 1], "expected": 1},
        ],
        "benchmark": {"args": [1, 1000000]},
    },
    {
        "name": "gcd",
        "category": "math",
        "technique": "Use the Euclidean algorithm (O(log min(a,b))) instead of trial "
                     "division up to min(a, b).",
        "description": "Return the greatest common divisor of the two integers a and b (non-negative inputs).",
        "complexity_before": "O(min(a, b)) time, O(1) space",
        "complexity_after": "O(log(min(a, b))) time, O(1) space",
        "unoptimized": """
def gcd(a, b):
    a, b = abs(a), abs(b)
    g = 0
    for i in range(1, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            g = i
    return g if g else 1
""".strip(),
        "optimized": """
def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
""".strip(),
        "tests": [
            {"args": [12, 18], "expected": 6},
            {"args": [7, 13], "expected": 1},
            {"args": [270, 192], "expected": 6},
            {"args": [100, 25], "expected": 25},
        ],
        "benchmark": {"args": [1000000, 999999]},
    },
    {
        "name": "pow_mod",
        "category": "math",
        "technique": "Use the built-in three-argument pow (fast modular exponentiation, "
                     "O(log exp)) instead of exp repeated multiplications.",
        "description": "Return (base ** exp) % mod using efficient modular exponentiation.",
        "complexity_before": "O(exp) time, O(1) space",
        "complexity_after": "O(log exp) time, O(1) space",
        "unoptimized": """
def pow_mod(base, exp, mod):
    result = 1 % mod
    b = base % mod
    for _ in range(exp):
        result = (result * b) % mod
    return result
""".strip(),
        "optimized": """
def pow_mod(base, exp, mod):
    return pow(base, exp, mod)
""".strip(),
        "tests": [
            {"args": [2, 10, 1000], "expected": 24},
            {"args": [3, 0, 7], "expected": 1},
            {"args": [5, 3, 7], "expected": 6},
        ],
        "benchmark": {"args": [3, 10**6, 10**9 + 7]},
    },
    {
        "name": "sum_of_squares",
        "category": "math",
        "technique": "Use the closed form n(n+1)(2n+1)/6 instead of adding every square "
                     "in a loop.",
        "description": "Return 1^2 + 2^2 + ... + n^2.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_squares(n):
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total
""".strip(),
        "optimized": """
def sum_of_squares(n):
    return n * (n + 1) * (2 * n + 1) // 6
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [4], "expected": 30},
            {"args": [10], "expected": 385},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "sum_of_cubes",
        "category": "math",
        "technique": "Use the identity sum of cubes = (n(n+1)/2)^2 instead of looping "
                     "over every cube.",
        "description": "Return 1^3 + 2^3 + ... + n^3.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_cubes(n):
    total = 0
    for i in range(1, n + 1):
        total += i ** 3
    return total
""".strip(),
        "optimized": """
def sum_of_cubes(n):
    t = n * (n + 1) // 2
    return t * t
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [3], "expected": 36},
            {"args": [4], "expected": 100},
            {"args": [10], "expected": 3025},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "sum_of_multiples",
        "category": "math",
        "technique": "Sum the arithmetic progression with a closed form instead of "
                     "iterating over every multiple.",
        "description": "Return the sum of all positive multiples of k that are strictly below n (k > 0).",
        "complexity_before": "O(n / k) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_multiples(n, k):
    total = 0
    for i in range(k, n, k):
        total += i
    return total
""".strip(),
        "optimized": """
def sum_of_multiples(n, k):
    count = (n - 1) // k
    return k * count * (count + 1) // 2
""".strip(),
        "tests": [
            {"args": [10, 3], "expected": 18},
            {"args": [20, 5], "expected": 30},
            {"args": [15, 5], "expected": 15},
            {"args": [1, 3], "expected": 0},
        ],
        "benchmark": {"args": [10000000, 7]},
    },
    {
        "name": "is_perfect_square",
        "category": "math",
        "technique": "Take the integer square root once with math.isqrt instead of "
                     "testing every integer up to sqrt(n).",
        "description": "Return True if n is a perfect square (negative inputs are False).",
        "complexity_before": "O(sqrt(n)) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def is_perfect_square(n):
    if n < 0:
        return False
    i = 0
    while i * i <= n:
        if i * i == n:
            return True
        i += 1
    return False
""".strip(),
        "optimized": """
def is_perfect_square(n):
    if n < 0:
        return False
    import math
    r = math.isqrt(n)
    return r * r == n
""".strip(),
        "tests": [
            {"args": [16], "expected": True},
            {"args": [17], "expected": False},
            {"args": [0], "expected": True},
            {"args": [1], "expected": True},
            {"args": [-4], "expected": False},
        ],
        "benchmark": {"args": [10**12]},
    },
    {
        "name": "sum_of_divisors",
        "category": "math",
        "technique": "Iterate only to sqrt(n) and add each complementary divisor pair "
                     "instead of testing every integer up to n.",
        "description": "Return the sum of all positive divisors of n (n >= 1).",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(sqrt(n)) time, O(1) space",
        "unoptimized": """
def sum_of_divisors(n):
    total = 0
    for i in range(1, n + 1):
        if n % i == 0:
            total += i
    return total
""".strip(),
        "optimized": """
def sum_of_divisors(n):
    total = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            total += i
            if i != n // i:
                total += n // i
        i += 1
    return total
""".strip(),
        "tests": [
            {"args": [6], "expected": 12},
            {"args": [12], "expected": 28},
            {"args": [1], "expected": 1},
            {"args": [28], "expected": 56},
            {"args": [16], "expected": 31},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "trailing_zeros_factorial",
        "category": "math",
        "technique": "Count factors of 5 with Legendre's formula (O(log n)) instead of "
                     "materializing the enormous factorial and repeatedly dividing it.",
        "description": "Return the number of trailing zeros in n! (n >= 0).",
        "complexity_before": "O(n log n!) time and huge big-int space",
        "complexity_after": "O(log n) time, O(1) space",
        "unoptimized": """
def trailing_zeros_factorial(n):
    import math
    f = math.factorial(n)
    count = 0
    while f > 0 and f % 10 == 0:
        count += 1
        f //= 10
    return count
""".strip(),
        "optimized": """
def trailing_zeros_factorial(n):
    count = 0
    power = 5
    while power <= n:
        count += n // power
        power *= 5
    return count
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [5], "expected": 1},
            {"args": [10], "expected": 2},
            {"args": [25], "expected": 6},
            {"args": [100], "expected": 24},
        ],
        "benchmark": {"args": [20000]},
    },
    {
        "name": "lcm",
        "category": "math",
        "technique": "Compute a*b/gcd(a,b) with the Euclidean algorithm instead of "
                     "stepping through multiples until one divides both inputs.",
        "description": "Return the least common multiple of integers a and b (0 if either is 0).",
        "complexity_before": "O(lcm / max(a, b)) time, O(1) space",
        "complexity_after": "O(log(min(a, b))) time, O(1) space",
        "unoptimized": """
def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    a, b = abs(a), abs(b)
    step = max(a, b)
    multiple = step
    while multiple % a != 0 or multiple % b != 0:
        multiple += step
    return multiple
""".strip(),
        "optimized": """
def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    a, b = abs(a), abs(b)

    def gcd(x, y):
        while y:
            x, y = y, x % y
        return x

    return a * b // gcd(a, b)
""".strip(),
        "tests": [
            {"args": [4, 6], "expected": 12},
            {"args": [7, 13], "expected": 91},
            {"args": [21, 6], "expected": 42},
            {"args": [1, 1], "expected": 1},
            {"args": [0, 5], "expected": 0},
        ],
        "benchmark": {"args": [1000003, 999983]},
    },
    {
        "name": "sum_of_primes_below",
        "category": "math",
        "technique": "Mark composites with a sieve of Eratosthenes instead of trial-dividing "
                     "every candidate from scratch.",
        "description": "Return the sum of all prime numbers strictly below n.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n log log n) time, O(n) space",
        "unoptimized": """
def sum_of_primes_below(n):
    total = 0
    for x in range(2, n):
        prime = True
        for d in range(2, x):
            if x % d == 0:
                prime = False
                break
        if prime:
            total += x
    return total
""".strip(),
        "optimized": """
def sum_of_primes_below(n):
    if n <= 2:
        return 0
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = False
    return sum(i for i in range(2, n) if sieve[i])
""".strip(),
        "tests": [
            {"args": [10], "expected": 17},
            {"args": [20], "expected": 77},
            {"args": [2], "expected": 0},
            {"args": [3], "expected": 2},
            {"args": [100], "expected": 1060},
        ],
        "benchmark": {"args": [3000]},
    },
    {
        "name": "sum_of_powers_of_two",
        "category": "math",
        "technique": "Use the identity 1 + 2 + ... + 2^(n-1) = 2^n - 1 instead of "
                     "accumulating every power in a loop.",
        "description": "Return 2^0 + 2^1 + ... + 2^(n-1).",
        "complexity_before": "O(n) big-int operations, O(n) space",
        "complexity_after": "O(1) big-int operations, O(1) space",
        "unoptimized": """
def sum_of_powers_of_two(n):
    total = 0
    power = 1
    for _ in range(n):
        total += power
        power *= 2
    return total
""".strip(),
        "optimized": """
def sum_of_powers_of_two(n):
    return (1 << n) - 1
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [5], "expected": 31},
            {"args": [10], "expected": 1023},
        ],
        "benchmark": {"args": [100000]},
    },
    {
        "name": "count_divisors",
        "category": "math",
        "technique": "Count divisor pairs up to sqrt(n) instead of testing every "
                     "integer up to n.",
        "description": "Return the number of positive divisors of n (n >= 1).",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(sqrt(n)) time, O(1) space",
        "unoptimized": """
def count_divisors(n):
    count = 0
    for i in range(1, n + 1):
        if n % i == 0:
            count += 1
    return count
""".strip(),
        "optimized": """
def count_divisors(n):
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
        i += 1
    return count
""".strip(),
        "tests": [
            {"args": [1], "expected": 1},
            {"args": [6], "expected": 4},
            {"args": [12], "expected": 6},
            {"args": [16], "expected": 5},
            {"args": [28], "expected": 6},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "catalan_number",
        "category": "math",
        "technique": "Use the closed form binom(2n, n) / (n + 1) with math.comb instead "
                     "of an O(n^2) dynamic-programming recurrence.",
        "description": "Return the n-th Catalan number.",
        "complexity_before": "O(n^2) big-int operations, O(n) space",
        "complexity_after": "O(n) big-int operations, O(1) space",
        "unoptimized": """
def catalan_number(n):
    catalan = [0] * (n + 1)
    catalan[0] = 1
    for i in range(n):
        for j in range(i + 1):
            catalan[i + 1] += catalan[j] * catalan[i - j]
    return catalan[n]
""".strip(),
        "optimized": """
def catalan_number(n):
    import math
    return math.comb(2 * n, n) // (n + 1)
""".strip(),
        "tests": [
            {"args": [0], "expected": 1},
            {"args": [1], "expected": 1},
            {"args": [5], "expected": 42},
            {"args": [10], "expected": 16796},
            {"args": [15], "expected": 9694845},
        ],
        "benchmark": {"args": [1000]},
    },
    {
        "name": "sum_of_odd_numbers",
        "category": "math",
        "technique": "Use the identity that the first n odd numbers sum to n^2 instead "
                     "of adding them in a loop.",
        "description": "Return 1 + 3 + 5 + ... + (2n - 1).",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_odd_numbers(n):
    total = 0
    for i in range(n):
        total += 2 * i + 1
    return total
""".strip(),
        "optimized": """
def sum_of_odd_numbers(n):
    return n * n
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [5], "expected": 25},
            {"args": [10], "expected": 100},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "geometric_series_sum",
        "category": "math",
        "technique": "Use the closed form (r^n - 1) / (r - 1) instead of accumulating "
                     "every power in a loop.",
        "description": "Return 1 + r + r^2 + ... + r^(n-1) for integer r and n >= 0.",
        "complexity_before": "O(n) big-int operations, O(1) space",
        "complexity_after": "O(log n) big-int operations, O(1) space",
        "unoptimized": """
def geometric_series_sum(r, n):
    total = 0
    power = 1
    for _ in range(n):
        total += power
        power *= r
    return total
""".strip(),
        "optimized": """
def geometric_series_sum(r, n):
    if n == 0:
        return 0
    if r == 1:
        return n
    return (r ** n - 1) // (r - 1)
""".strip(),
        "tests": [
            {"args": [2, 5], "expected": 31},
            {"args": [3, 4], "expected": 40},
            {"args": [1, 10], "expected": 10},
            {"args": [5, 0], "expected": 0},
            {"args": [0, 3], "expected": 1},
        ],
        "benchmark": {"args": [2, 100000]},
    },
    {
        "name": "binomial_coefficient",
        "category": "math",
        "technique": "Call math.comb (C implementation) instead of filling an "
                     "O(n * k) dynamic-programming table.",
        "description": "Return n choose k (0 when k is out of range).",
        "complexity_before": "O(n * k) big-int additions, O(k) space",
        "complexity_after": "O(n) big-int operations, O(1) space",
        "unoptimized": """
def binomial_coefficient(n, k):
    if k < 0 or k > n:
        return 0
    dp = [0] * (k + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        upper = min(i, k)
        for j in range(upper, 0, -1):
            dp[j] += dp[j - 1]
    return dp[k]
""".strip(),
        "optimized": """
def binomial_coefficient(n, k):
    if k < 0 or k > n:
        return 0
    import math
    return math.comb(n, k)
""".strip(),
        "tests": [
            {"args": [5, 2], "expected": 10},
            {"args": [10, 3], "expected": 120},
            {"args": [50, 0], "expected": 1},
            {"args": [50, 50], "expected": 1},
            {"args": [5, 6], "expected": 0},
        ],
        "benchmark": {"args": [2000, 1000]},
    },
    {
        "name": "sum_of_fourth_powers",
        "category": "math",
        "technique": "Use the closed form n(n+1)(2n+1)(3n^2+3n-1)/30 instead of adding "
                     "every fourth power in a loop.",
        "description": "Return 1^4 + 2^4 + ... + n^4.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_fourth_powers(n):
    total = 0
    for i in range(1, n + 1):
        total += i ** 4
    return total
""".strip(),
        "optimized": """
def sum_of_fourth_powers(n):
    return n * (n + 1) * (2 * n + 1) * (3 * n * n + 3 * n - 1) // 30
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 17},
            {"args": [3], "expected": 98},
            {"args": [10], "expected": 25333},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "euler_totient",
        "category": "math",
        "technique": "Factor n and apply phi(n) = n * product(1 - 1/p) in O(sqrt(n)) "
                     "instead of testing every integer for coprimality (O(n log n)).",
        "description": "Return Euler's totient phi(n): how many integers in 1..n are coprime to n.",
        "complexity_before": "O(n log n) time, O(1) space",
        "complexity_after": "O(sqrt(n)) time, O(1) space",
        "unoptimized": """
def euler_totient(n):
    count = 0
    for k in range(1, n + 1):
        a, b = k, n
        while b:
            a, b = b, a % b
        if a == 1:
            count += 1
    return count
""".strip(),
        "optimized": """
def euler_totient(n):
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result
""".strip(),
        "tests": [
            {"args": [1], "expected": 1},
            {"args": [7], "expected": 6},
            {"args": [9], "expected": 6},
            {"args": [10], "expected": 4},
            {"args": [36], "expected": 12},
        ],
        "benchmark": {"args": [1000000]},
    },
    {
        "name": "trailing_zeros_binary",
        "category": "math",
        "technique": "Extract the lowest set bit with n & -n and bit_length (O(1)) "
                     "instead of repeatedly dividing by two.",
        "description": "Return the number of trailing zero bits in the binary representation of n (0 for n = 0).",
        "complexity_before": "O(n) big-int divisions, O(1) space",
        "complexity_after": "O(1) big-int operations, O(1) space",
        "unoptimized": """
def trailing_zeros_binary(n):
    if n == 0:
        return 0
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    return count
""".strip(),
        "optimized": """
def trailing_zeros_binary(n):
    if n == 0:
        return 0
    return (n & -n).bit_length() - 1
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 0},
            {"args": [8], "expected": 3},
            {"args": [12], "expected": 2},
            {"args": [16], "expected": 4},
        ],
        "benchmark": {"args": [2 ** 10000]},
    },
    {
        "name": "sum_of_triangular_numbers",
        "category": "math",
        "technique": "Use the closed form n(n+1)(n+2)/6 instead of adding every "
                     "triangular number in a loop.",
        "description": "Return T(1) + T(2) + ... + T(n), where T(k) = k(k+1)/2.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_triangular_numbers(n):
    total = 0
    for i in range(1, n + 1):
        total += i * (i + 1) // 2
    return total
""".strip(),
        "optimized": """
def sum_of_triangular_numbers(n):
    return n * (n + 1) * (n + 2) // 6
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 4},
            {"args": [3], "expected": 10},
            {"args": [10], "expected": 220},
        ],
        "benchmark": {"args": [10000000]},
    },
    {
        "name": "is_power_of_two",
        "category": "math",
        "technique": "Test n & (n - 1) == 0 in O(1) instead of repeatedly dividing "
                     "by two.",
        "description": "Return True if n is a positive power of two.",
        "complexity_before": "O(log n) big-int divisions, O(1) space",
        "complexity_after": "O(1) big-int operations, O(1) space",
        "unoptimized": """
def is_power_of_two(n):
    if n <= 0:
        return False
    while n % 2 == 0:
        n //= 2
    return n == 1
""".strip(),
        "optimized": """
def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
""".strip(),
        "tests": [
            {"args": [1], "expected": True},
            {"args": [2], "expected": True},
            {"args": [16], "expected": True},
            {"args": [18], "expected": False},
            {"args": [0], "expected": False},
            {"args": [-8], "expected": False},
        ],
        "benchmark": {"args": [2 ** 10000]},
    },
    {
        "name": "sum_of_squares_of_odds",
        "category": "math",
        "technique": "Use the closed form n(2n-1)(2n+1)/3 instead of squaring every "
                     "odd number in a loop.",
        "description": "Return 1^2 + 3^2 + ... + (2n-1)^2.",
        "complexity_before": "O(n) time, O(1) space",
        "complexity_after": "O(1) time, O(1) space",
        "unoptimized": """
def sum_of_squares_of_odds(n):
    total = 0
    for i in range(n):
        odd = 2 * i + 1
        total += odd * odd
    return total
""".strip(),
        "optimized": """
def sum_of_squares_of_odds(n):
    return n * (2 * n - 1) * (2 * n + 1) // 3
""".strip(),
        "tests": [
            {"args": [0], "expected": 0},
            {"args": [1], "expected": 1},
            {"args": [2], "expected": 10},
            {"args": [3], "expected": 35},
            {"args": [10], "expected": 1330},
        ],
        "benchmark": {"args": [10000000]},
    },
]
