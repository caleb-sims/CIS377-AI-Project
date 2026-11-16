"""Shared helpers for programmatically generated example families."""

from __future__ import annotations

import math
import random


def make(name, category, technique, description, before, after,
         unoptimized, optimized, tests, benchmark, materialize=False):
    """Build one example dict in the curated format."""
    example = {
        "name": name,
        "category": category,
        "technique": technique,
        "description": description,
        "complexity_before": before,
        "complexity_after": after,
        "unoptimized": unoptimized.replace("__NAME__", name).strip(),
        "optimized": optimized.replace("__NAME__", name).strip(),
        "tests": tests,
        "benchmark": benchmark,
    }
    if materialize:
        example["materialize_output"] = True
    return example


def next_prime(n):
    """Smallest prime >= n (used to build genuinely slow primality benchmarks)."""
    if n <= 2:
        return 2
    candidate = n if n % 2 else n + 1
    while True:
        limit = math.isqrt(candidate)
        is_prime = True
        d = 3
        while d <= limit:
            if candidate % d == 0:
                is_prime = False
                break
            d += 2
        if is_prime:
            return candidate
        candidate += 2


def rng(seed):
    return random.Random(seed)
