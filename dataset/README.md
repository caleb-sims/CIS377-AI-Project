# Code Performance Optimization Dataset

Synthetic **slow → fast Python function pairs** for training and evaluating code-optimization
models (e.g. a CodeT5-style seq2seq model, compared with small decoder-only LLMs).
Each pair keeps the same signature and behavior while the optimized version improves
**time and/or memory**.

Default dataset: **1000 examples** — 800 train / 100 validation / 100 test
(10% validation, 10% test). The pool combines 200 hand-curated pairs with 40
parameterized generator families. The CLI can build **any requested number**; above
1000 it expands the families to additional unique variants.

## Layout

```
code_performance_dataset/
├── examples/              # Example sources, one module per category
│   ├── __init__.py        # build_all(n): curated + dynamically expanded generated pool
│   ├── hashing.py         # set/dict lookups instead of nested scans
│   ├── sorting.py         # sorting, binary search, merge techniques
│   ├── dp.py              # memoization / dynamic programming
│   ├── strings.py         # join, translate, str built-ins instead of O(n^2) concat
│   ├── memory.py          # lazy generators, avoiding intermediate collections
│   ├── vectorization.py   # NumPy / BLAS instead of Python loops
│   ├── stdlib.py          # closed-form math and efficient stdlib algorithms (category "math")
│   ├── loops.py           # sliding windows, two pointers, prefix sums
│   ├── gen_common.py      # Shared helpers for generated families
│   └── gen_*.py           # 40 parameterized families; build(variants) expands any count
├── generate_dataset.py    # CLI: count + train/val/test fractions + seed -> JSONL
├── validate_dataset.py    # Correctness tests + timing/memory benchmarks
├── data/
│   ├── all.jsonl          # every record
│   ├── train.jsonl        # default 80%
│   ├── val.jsonl          # default 10%
│   ├── test.jsonl         # default 10%
│   └── meta.json          # counts, fractions, seed, categories
└── reports/
    └── validation_report.json
```

## Record schema

Each line of `data/*.jsonl` is a JSON object:

| Field | Meaning |
|---|---|
| `id` | Stable id, e.g. `codeopt_0000` |
| `name` | Function name (unique) |
| `category` | One of `hashing`, `sorting`, `dynamic-programming`, `strings`, `memory`, `vectorization`, `math`, `loops` |
| `technique` | Human-readable explanation of the optimization |
| `description` | Precise statement of the function's behavior |
| `complexity_before`, `complexity_after` | Claimed time/space complexity |
| `unoptimized` | Source code of the slow function (string) |
| `optimized` | Source code of the fast function, self-contained (includes imports) |
| `prompt` | Decoder-only prompt embedding the unoptimized code |
| `tests` | List of correctness tests: `{"args": [...], "expected": value}` |
| `benchmark` | `{"args": [...]}` larger input used for agreement + timing + memory |
| `materialize_output` | Optional; `true` means the result is a generator and is compared via `list(result)` |

Test details:

- `args` is a **list of positional arguments**. A single list argument therefore needs an
  extra wrapper: `{"args": [[1, 2, 3]]}`. A matrix argument is `{"args": [[[1, 2], [3, 4]]]}`.
- `tests[].expected` is one expected value.
- `tests[].acceptable` (optional) replaces `expected` with a list of acceptable values when
  the correct answer is not unique (e.g. `two_sum` may return any valid index pair).
- NumPy-based optimized functions return native Python types (`.tolist()`, `float`) so the
  two versions compare equal. The harness compares floats with `math.isclose` (tol 1e-9).

## Generate

From this directory, inside the `cis377` conda environment:

```bash
source /home/hinson/anaconda3/etc/profile.d/conda.sh
conda activate cis377

python generate_dataset.py
```

### CLI options

| Option | Default | Meaning |
|---|---:|---|
| `--num-examples N` | `1000` | Total number of examples to generate. Any integer ≥ 1. |
| `--val-fraction F` | `0.1` | Fraction reserved for validation. |
| `--test-fraction F` | `0.1` | Fraction reserved for test. |
| `--seed S` | `42` | Seed for family expansion order and split shuffling. |
| `--out-dir DIR` | `data` | Output directory for `all/train/val/test.jsonl` and `meta.json`. |

`--val-fraction + --test-fraction` must be less than 1. The splitter keeps at least one
training row; for very small datasets a fraction may round to zero, in which case the
corresponding file is still written but empty.

### Examples

```bash
# Default: 1000 examples -> 800 train / 100 val / 100 test
python generate_dataset.py

# Scale up; families expand to unique variants as needed
python generate_dataset.py --num-examples 5000

# Custom split and seed
python generate_dataset.py --num-examples 2500 --val-fraction 0.05 --test-fraction 0.05 --seed 7

# Small reproducible dataset in a separate directory
python generate_dataset.py --num-examples 500 --out-dir data_500
```

How arbitrary counts work:

- `N <= 200`: sampled deterministically from the hand-curated pool.
- `N > 200`: all curated examples plus generated variants. Each of the 40 families is
  expanded to `ceil((N - 200) / 40)` variants, then the generated pool is trimmed to the
  exact request. Names stay unique, and benchmark sizes cycle (bounded) so large
  requests remain practical.
- Every generated snippet is compiled at generation time, and duplicate names abort the run.

## Validate

```bash
python validate_dataset.py            # tests + benchmark agreement + median time + peak memory
# options: --in data/all.jsonl --out reports/validation_report.json --runs 3 --cap 6
```

For every example the harness executes both versions in isolated namespaces, runs all
correctness tests, checks that both versions agree on the benchmark input, then measures
median wall time (`--runs`, default 3) and peak memory (`tracemalloc`).

Latest default run: **1000/1000 correct and agreeing, 100% of optimized versions faster,
median speedup ≈133x** (timing is machine-dependent). Full per-example numbers are in
`reports/validation_report.json`.

## Use for training

- **Seq2seq (CodeT5-style):** source = `unoptimized`, target = `optimized`.
- **Decoder-only:** prompt = `prompt`, completion = `optimized` (train on the completion,
  or on prompt+completion depending on your setup).
- Train on `data/train.jsonl`.
- Tune/select on `data/val.jsonl`.
- Report final numbers on `data/test.jsonl`; never train on val or test.

## Add more examples

1. Append a new dict to `EXAMPLES` in the appropriate curated `examples/*.py` module, or
   add a parameterized family to `examples/gen_*.py`. A generated family should expose its
   variants through the module's `build(variants)` function.
2. Prefer optimizations with a clear algorithmic win (hashing, DP, sliding window,
   closed-form math) or a clear vectorization win (BLAS, broadcasting). Pure
   `O(n)` Python-loop → `O(n)` NumPy conversions often show only ~1x speedup because
   `np.asarray` conversion dominates.
3. Run `python generate_dataset.py --num-examples <N> && python validate_dataset.py`
   and fix any reported correctness failures or benchmarks where the optimized version
   is not faster.
