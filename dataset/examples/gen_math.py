"""Generated math families: 5 closed-form/stdlib patterns x 20 variants."""

from __future__ import annotations

import math

from .gen_common import make, next_prime

EXAMPLES = []


def _sum_to_n(variants):
    unopt = """
def __NAME__(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total
"""
    opt = """
def __NAME__(n):
    return n * (n + 1) // 2
"""
    for i in range(variants):
        n = 1000000 + (i % 20) * 50000
        check = 5 + i % 10
        EXAMPLES.append(make(
            f"gen_sum_to_n_{i:02d}", "math",
            "Use the arithmetic-series closed form instead of adding every integer.",
            "Return 1 + 2 + ... + n.",
            "O(n) time, O(1) space", "O(1) time, O(1) space",
            unopt, opt,
            [
                {"args": [check], "expected": check * (check + 1) // 2},
                {"args": [0], "expected": 0},
                {"args": [1], "expected": 1},
                {"args": [10], "expected": 55},
            ],
            {"args": [n]},
        ))


def _sum_of_squares(variants):
    unopt = """
def __NAME__(n):
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total
"""
    opt = """
def __NAME__(n):
    return n * (n + 1) * (2 * n + 1) // 6
"""
    for i in range(variants):
        n = 800000 + (i % 20) * 40000
        check = 5 + i % 10
        EXAMPLES.append(make(
            f"gen_sum_of_squares_{i:02d}", "math",
            "Use the closed form n(n+1)(2n+1)/6 instead of adding every square.",
            "Return 1^2 + 2^2 + ... + n^2.",
            "O(n) time, O(1) space", "O(1) time, O(1) space",
            unopt, opt,
            [
                {"args": [check],
                 "expected": check * (check + 1) * (2 * check + 1) // 6},
                {"args": [0], "expected": 0},
                {"args": [4], "expected": 30},
                {"args": [10], "expected": 385},
            ],
            {"args": [n]},
        ))


def _factorial(variants):
    unopt = """
def __NAME__(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
"""
    opt = """
def __NAME__(n):
    import math
    return math.factorial(n)
"""
    for i in range(variants):
        n = 2000 + (i % 20) * 100
        check = 5 + i % 5
        EXAMPLES.append(make(
            f"gen_factorial_{i:02d}", "math",
            "Use the C-implemented math.factorial instead of a Python multiplication loop.",
            "Return n! (0! = 1).",
            "O(n) big-int multiplications, O(1) space",
            "O(n) big-int operations in C, O(1) space",
            unopt, opt,
            [
                {"args": [check], "expected": math.factorial(check)},
                {"args": [0], "expected": 1},
                {"args": [1], "expected": 1},
                {"args": [10], "expected": 3628800},
            ],
            {"args": [n]},
        ))


def _is_prime(variants):
    unopt = """
def __NAME__(n):
    if n < 2:
        return False
    for d in range(2, n):
        if n % d == 0:
            return False
    return True
"""
    opt = """
def __NAME__(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True
"""
    for i in range(variants):
        n = next_prime(100000 + (i % 20) * 3000)
        check = next_prime(20 + i % 10)
        EXAMPLES.append(make(
            f"gen_is_prime_{i:02d}", "math",
            "Test divisors only up to sqrt(n) instead of scanning every integer below n.",
            "Return True if n is prime.",
            "O(n) time, O(1) space", "O(sqrt(n)) time, O(1) space",
            unopt, opt,
            [
                {"args": [check], "expected": True},
                {"args": [2], "expected": True},
                {"args": [3], "expected": True},
                {"args": [4], "expected": False},
                {"args": [25], "expected": False},
                {"args": [1], "expected": False},
            ],
            {"args": [n]},
        ))


def _pow_mod(variants):
    unopt = """
def __NAME__(base, exp, mod):
    result = 1
    for _ in range(exp):
        result = (result * base) % mod
    return result
"""
    opt = """
def __NAME__(base, exp, mod):
    return pow(base, exp, mod)
"""
    for i in range(variants):
        exp = 150000 + (i % 20) * 5000
        base = 3 + i % 5
        mod = 1000000007
        tbase = 2 + i % 4
        texp = 5 + i % 5
        tmod = 97
        EXAMPLES.append(make(
            f"gen_pow_mod_{i:02d}", "math",
            "Use the built-in three-argument pow (C modular exponentiation) instead "
            "of multiplying in a Python loop.",
            "Return (base ** exp) mod mod.",
            "O(exp) time, O(1) space", "O(log exp) time, O(1) space",
            unopt, opt,
            [
                {"args": [tbase, texp, tmod],
                 "expected": pow(tbase, texp, tmod)},
                {"args": [2, 10, 1000], "expected": 24},
                {"args": [3, 5, 7], "expected": 5},
                {"args": [5, 0, 13], "expected": 1},
            ],
            {"args": [base, exp, mod]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _sum_to_n(variants)
    _sum_of_squares(variants)
    _factorial(variants)
    _is_prime(variants)
    _pow_mod(variants)
    return EXAMPLES


EXAMPLES = build(20)
