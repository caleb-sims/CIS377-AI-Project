"""Synthetic slow->fast Python function pairs.

Each example module exposes an ``EXAMPLES`` list. Every example is a dict with:
  name, category, technique, description,
  complexity_before, complexity_after,
  unoptimized (str), optimized (str),
  tests (list of {"args": [...], "expected": ...}),
  benchmark ({"args": [...]}),
  materialize_output (bool, optional).

Each test normally uses ``expected`` for the single expected value. When a correct
answer is not unique (e.g. two_sum may return any valid pair), the test instead
uses ``acceptable``: a list of values, any one of which is accepted.

The package combines 200 hand-curated examples with 40 parameterized generator
families. ``build_all(n)`` can build any non-negative number of examples: beyond
the curated set it expands each family to as many unique variants as needed.
"""

from __future__ import annotations

import math
import random

from .hashing import EXAMPLES as _hashing
from .sorting import EXAMPLES as _sorting
from .dp import EXAMPLES as _dp
from .strings import EXAMPLES as _strings
from .memory import EXAMPLES as _memory
from .vectorization import EXAMPLES as _vectorization
from .stdlib import EXAMPLES as _stdlib
from .loops import EXAMPLES as _loops

from . import gen_hashing as _gen_hashing
from . import gen_sorting as _gen_sorting
from . import gen_dp as _gen_dp
from . import gen_strings as _gen_strings
from . import gen_memory as _gen_memory
from . import gen_vectorization as _gen_vectorization
from . import gen_math as _gen_math
from . import gen_loops as _gen_loops

SEED = 42

#: Hand-curated examples (always included first when the requested count allows).
CURATED = (
    _hashing
    + _sorting
    + _dp
    + _strings
    + _memory
    + _vectorization
    + _stdlib
    + _loops
)

#: Modules whose ``build(variants)`` returns 5 families worth of examples.
GEN_MODULES = (
    _gen_hashing,
    _gen_sorting,
    _gen_dp,
    _gen_strings,
    _gen_memory,
    _gen_vectorization,
    _gen_math,
    _gen_loops,
)

#: Five generator families per module.
FAMILY_COUNT = len(GEN_MODULES) * 5


def build_all(num_examples: int, seed: int = SEED) -> list[dict]:
    """Return exactly ``num_examples`` examples (deterministic for a given seed).

    For counts above ``len(CURATED)`` the generator families are expanded to
    enough unique variants, then trimmed to the exact request. Benchmark sizes
    are bounded by cycling their parameters, so very large requests stay usable.
    """
    if num_examples < 0:
        raise ValueError("num_examples must be non-negative")

    curated = list(CURATED)
    if num_examples <= len(curated):
        if num_examples == len(curated):
            return curated
        return random.Random(seed).sample(curated, num_examples)

    needed = num_examples - len(curated)
    variants = max(1, math.ceil(needed / FAMILY_COUNT))

    generated: list[dict] = []
    for module in GEN_MODULES:
        generated.extend(module.build(variants))

    rng = random.Random(seed)
    rng.shuffle(generated)
    return curated + generated[:needed]


# Default in-process pool (the historical 1000-example dataset).
ALL = build_all(1000)

__all__ = ["ALL", "CURATED", "FAMILY_COUNT", "GEN_MODULES", "SEED", "build_all"]
