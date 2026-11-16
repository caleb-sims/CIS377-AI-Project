#!/usr/bin/env python3
"""Generate the synthetic slow->fast Python function dataset as JSONL.

Usage examples:
    python generate_dataset.py
    python generate_dataset.py --num-examples 5000
    python generate_dataset.py --num-examples 1000 --val-fraction 0.1 --test-fraction 0.1

The example pool combines 200 hand-curated pairs with 40 parameterized generator
families. Counts above the curated set are satisfied by expanding each family to
as many unique variants as needed; benchmark sizes cycle so large requests stay
usable.

Writes:
    <out-dir>/all.jsonl      every record
    <out-dir>/train.jsonl    training split
    <out-dir>/val.jsonl      validation split
    <out-dir>/test.jsonl     test split
    <out-dir>/meta.json      dataset statistics and split configuration

Train/val/test are disjoint and deterministically shuffled from the same seed.
"""

from __future__ import annotations

import argparse
import json
import os
import random

from examples import CURATED, FAMILY_COUNT, build_all

DEFAULT_SEED = 42
DEFAULT_NUM_EXAMPLES = 1000
DEFAULT_VAL_FRACTION = 0.1
DEFAULT_TEST_FRACTION = 0.1

SYSTEM_PROMPT = (
    "You are an expert Python performance engineer. Rewrite the following function "
    "so it runs as fast and uses as little memory as possible, while keeping its "
    "exact signature and behavior. Return only the optimized function code, including "
    "any imports it needs."
)


def build_prompt(example: dict) -> str:
    return (
        SYSTEM_PROMPT
        + "\n\n"
        + "Original function:\n```python\n"
        + example["unoptimized"]
        + "\n```\n\nOptimized function:"
    )


def build_record(example: dict, index: int) -> dict:
    record = {
        "id": f"codeopt_{index:04d}",
        "name": example["name"],
        "category": example["category"],
        "technique": example["technique"],
        "description": example["description"],
        "complexity_before": example["complexity_before"],
        "complexity_after": example["complexity_after"],
        "unoptimized": example["unoptimized"],
        "optimized": example["optimized"],
        "prompt": build_prompt(example),
        "tests": example["tests"],
        "benchmark": example["benchmark"],
    }
    if example.get("materialize_output"):
        record["materialize_output"] = True
    return record


def split_counts(total: int, val_fraction: float, test_fraction: float) -> tuple[int, int, int]:
    """Return (n_train, n_val, n_test) totaling ``total`` with at least 1 train row."""
    n_val = int(round(total * val_fraction))
    n_test = int(round(total * test_fraction))
    n_val = max(0, min(n_val, total))
    n_test = max(0, min(n_test, total - n_val))

    n_train = total - n_val - n_test
    # Keep at least one training row when fractions would consume everything.
    deficit = 1 - n_train
    if deficit > 0:
        take = min(deficit, n_val)
        n_val -= take
        deficit -= take
        if deficit > 0:
            n_test -= min(deficit, n_test)
        n_train = total - n_val - n_test
    return n_train, n_val, n_test


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate slow->fast Python training data as JSONL splits.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--num-examples", type=int, default=DEFAULT_NUM_EXAMPLES, metavar="N",
        help="total number of examples to generate (any integer >= 1)",
    )
    parser.add_argument(
        "--val-fraction", type=float, default=DEFAULT_VAL_FRACTION,
        help="fraction of examples reserved for validation",
    )
    parser.add_argument(
        "--test-fraction", type=float, default=DEFAULT_TEST_FRACTION,
        help="fraction of examples reserved for test",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help="seed for dataset expansion order and split shuffling",
    )
    parser.add_argument(
        "--out-dir", default="data",
        help="output directory for all.jsonl, train.jsonl, val.jsonl, test.jsonl, meta.json",
    )
    args = parser.parse_args()

    if args.num_examples < 1:
        parser.error("--num-examples must be at least 1")
    if not 0.0 <= args.val_fraction < 1.0:
        parser.error("--val-fraction must be in [0, 1)")
    if not 0.0 <= args.test_fraction < 1.0:
        parser.error("--test-fraction must be in [0, 1)")
    if args.val_fraction + args.test_fraction >= 1.0:
        parser.error("--val-fraction + --test-fraction must be less than 1")

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    examples = build_all(args.num_examples, seed=args.seed)

    # Sanity: unique names and well-formed code.
    names = [e["name"] for e in examples]
    if len(names) != len(set(names)):
        dupes = sorted({n for n in names if names.count(n) > 1})
        raise SystemExit(f"duplicate example names: {dupes[:20]}")

    for e in examples:
        compile(e["unoptimized"], f"{e['name']}.unopt", "exec")
        compile(e["optimized"], f"{e['name']}.opt", "exec")

    records = [build_record(e, i) for i, e in enumerate(examples)]

    n_train, n_val, n_test = split_counts(
        len(records), args.val_fraction, args.test_fraction
    )
    order = list(range(len(records)))
    random.Random(args.seed).shuffle(order)
    val_idx = set(order[:n_val])
    test_idx = set(order[n_val:n_val + n_test])

    train = [r for i, r in enumerate(records) if i not in val_idx and i not in test_idx]
    val = [r for i, r in enumerate(records) if i in val_idx]
    test = [r for i, r in enumerate(records) if i in test_idx]

    def dump(path: str, rows: list[dict]) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    dump(os.path.join(out_dir, "all.jsonl"), records)
    dump(os.path.join(out_dir, "train.jsonl"), train)
    dump(os.path.join(out_dir, "val.jsonl"), val)
    dump(os.path.join(out_dir, "test.jsonl"), test)

    categories = {}
    for r in records:
        categories[r["category"]] = categories.get(r["category"], 0) + 1

    meta = {
        "name": "code-performance-optimization-synthetic",
        "description": "Synthetic slow->fast Python function pairs (time and memory) "
                       "for training a small seq2seq / decoder-only code model.",
        "num_examples": len(records),
        "num_train": len(train),
        "num_val": len(val),
        "num_test": len(test),
        "seed": args.seed,
        "val_fraction": args.val_fraction,
        "test_fraction": args.test_fraction,
        "curated_examples": len(CURATED),
        "generator_families": FAMILY_COUNT,
        "categories": categories,
        "fields": [
            "id", "name", "category", "technique", "description",
            "complexity_before", "complexity_after",
            "unoptimized", "optimized", "prompt",
            "tests", "benchmark",
        ],
        "notes": [
            "seq2seq training: source=unoptimized, target=optimized.",
            "decoder-only training: system=user=prompt, assistant=optimized.",
            "train/val/test are disjoint and deterministically shuffled from meta.seed.",
            "tests[].expected is a single value; tests[].acceptable (optional) lists "
            "multiple acceptable values when the answer is non-unique.",
            "benchmark.args is a larger input used by the validation harness to "
            "measure original vs optimized speed and memory.",
            "materialize_output=True means the result is a generator; compare list(result).",
        ],
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"wrote {len(records)} examples to {out_dir}")
    print(f"  train: {len(train)}  val: {len(val)}  test: {len(test)}")
    print(f"  categories: {json.dumps(categories, sort_keys=True)}")


if __name__ == "__main__":
    main()
