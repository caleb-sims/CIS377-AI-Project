"""Fine-tune CodeT5-small to turn slow Python functions into faster ones.

Each JSONL record provides a ``unoptimized`` source function and an
``optimized`` target function. The model is trained as a seq2seq model and
validated on ``data/val.jsonl``; the best checkpoint is written to
``checkpoints/best`` and the final checkpoint to ``checkpoints/final``.

Examples:
    python pytorch_train.py
    python pytorch_train.py --limit 200 --val-limit 50 --num-epochs 1
    python pytorch_train.py --device cuda --batch-size 16 --num-epochs 3
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer,
    T5ForConditionalGeneration,
    get_linear_schedule_with_warmup,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "Salesforce/codet5-small"
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_CHECKPOINT_DIR = BASE_DIR / "checkpoints"


class CodeOptimizationDataset(Dataset):
    """Pairs of (unoptimized, optimized) Python functions from a JSONL file."""

    def __init__(self, path: Path, limit: int = 0) -> None:
        self.sources: list[str] = []
        self.targets: list[str] = []

        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue

                record = json.loads(line)
                source = record.get("unoptimized") or record.get("prompt")
                target = record.get("optimized")
                if not source or not target:
                    continue

                self.sources.append(source)
                self.targets.append(target)
                if limit and len(self.sources) >= limit:
                    break

        if not self.sources:
            raise ValueError(f"No usable training records found in {path}")

    def __len__(self) -> int:
        return len(self.sources)

    def __getitem__(self, index: int) -> tuple[str, str]:
        return self.sources[index], self.targets[index]


class Seq2SeqCollator:
    """Tokenize and pad a batch of (source, target) string pairs."""

    def __init__(
        self,
        tokenizer: AutoTokenizer,
        max_source_length: int,
        max_target_length: int,
    ) -> None:
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __call__(self, features: list[tuple[str, str]]) -> dict[str, torch.Tensor]:
        sources, targets = zip(*features)

        batch = self.tokenizer(
            list(sources),
            max_length=self.max_source_length,
            truncation=True,
            padding=True,
            return_tensors="pt",
        )
        labels = self.tokenizer(
            text_target=list(targets),
            max_length=self.max_target_length,
            truncation=True,
            padding=True,
            return_tensors="pt",
        )["input_ids"]

        # -100 tells the loss function to ignore padding tokens.
        labels = labels.masked_fill(labels == self.tokenizer.pad_token_id, -100)
        batch["labels"] = labels
        return batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune CodeT5-small on slow-to-fast Python function pairs."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Hugging Face model name.")
    parser.add_argument(
        "--train-file",
        type=Path,
        default=DEFAULT_DATA_DIR / "train.jsonl",
        help="Training JSONL file.",
    )
    parser.add_argument(
        "--val-file",
        type=Path,
        default=DEFAULT_DATA_DIR / "val.jsonl",
        help="Validation JSONL file. Ignored if it does not exist.",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=DEFAULT_CHECKPOINT_DIR,
        help="Directory where best/ and final/ checkpoints are written.",
    )
    parser.add_argument("--num-epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=1,
        help="Accumulate gradients over this many batches.",
    )
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.05)
    parser.add_argument("--max-grad-norm", type=float, default=1.0)
    parser.add_argument("--max-source-length", type=int, default=256)
    parser.add_argument("--max-target-length", type=int, default=256)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Use only the first N training examples (0 = all).",
    )
    parser.add_argument(
        "--val-limit",
        type=int,
        default=0,
        help="Use only the first N validation examples (0 = all).",
    )
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=50)
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Device to train on.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def pick_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def make_scaler(device: torch.device, enabled: bool):
    try:
        return torch.amp.GradScaler(device.type, enabled=enabled)
    except (AttributeError, TypeError):
        return torch.cuda.amp.GradScaler(enabled=enabled)


def train_one_epoch(
    model: T5ForConditionalGeneration,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler,
    scaler,
    device: torch.device,
    epoch: int,
    args: argparse.Namespace,
    use_amp: bool,
) -> float:
    model.train()
    accumulation_steps = args.gradient_accumulation_steps
    total_loss = 0.0
    total_examples = 0
    epoch_start = time.time()
    optimizer.zero_grad(set_to_none=True)

    for step, batch in enumerate(loader, start=1):
        batch = {key: value.to(device) for key, value in batch.items()}
        batch_size = batch["input_ids"].size(0)

        with torch.autocast(
            device_type=device.type,
            dtype=torch.float16,
            enabled=use_amp,
        ):
            loss = model(**batch).loss

        scaler.scale(loss / accumulation_steps).backward()

        total_loss += loss.item() * batch_size
        total_examples += batch_size

        should_step = step % accumulation_steps == 0 or step == len(loader)
        if not should_step:
            continue

        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        optimizer.zero_grad(set_to_none=True)

        if step % args.log_every == 0 or step == len(loader):
            average_loss = total_loss / total_examples
            elapsed = time.time() - epoch_start
            examples_per_second = total_examples / elapsed if elapsed > 0 else 0.0
            current_lr = scheduler.get_last_lr()[0]
            print(
                f"epoch {epoch} | step {step}/{len(loader)} | "
                f"loss {average_loss:.4f} | lr {current_lr:.2e} | "
                f"{examples_per_second:.1f} examples/s",
                flush=True,
            )

    return total_loss / max(total_examples, 1)


@torch.no_grad()
def evaluate(
    model: T5ForConditionalGeneration,
    loader: DataLoader,
    device: torch.device,
    use_amp: bool,
) -> float:
    model.eval()
    total_loss = 0.0
    total_examples = 0

    for batch in loader:
        batch = {key: value.to(device) for key, value in batch.items()}
        with torch.autocast(
            device_type=device.type,
            dtype=torch.float16,
            enabled=use_amp,
        ):
            loss = model(**batch).loss
        total_loss += loss.item() * batch["input_ids"].size(0)
        total_examples += batch["input_ids"].size(0)

    return total_loss / max(total_examples, 1)


def save_checkpoint(
    model: T5ForConditionalGeneration,
    tokenizer: AutoTokenizer,
    directory: Path,
    epoch: int,
    val_loss: float,
    args: argparse.Namespace,
    history: list[dict[str, float]],
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(directory)
    tokenizer.save_pretrained(directory)

    state = {
        "epoch": epoch,
        "val_loss": val_loss,
        "args": vars(args),
        "history": history,
    }
    torch.save(state, directory / "training_state.pt")
    (directory / "training_state.json").write_text(
        json.dumps(state, indent=2, default=str),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    if args.gradient_accumulation_steps < 1:
        raise ValueError("--gradient-accumulation-steps must be at least 1")
    if not args.train_file.exists():
        raise FileNotFoundError(f"Training file not found: {args.train_file}")

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    device = pick_device(args.device)
    use_amp = device.type == "cuda"
    print(f"device: {device} | mixed precision: {use_amp}", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = T5ForConditionalGeneration.from_pretrained(args.model)
    model.to(device)

    train_dataset = CodeOptimizationDataset(args.train_file, limit=args.limit)
    val_dataset = None
    if args.val_file.exists():
        val_dataset = CodeOptimizationDataset(args.val_file, limit=args.val_limit)

    collator = Seq2SeqCollator(
        tokenizer,
        max_source_length=args.max_source_length,
        max_target_length=args.max_target_length,
    )
    generator = torch.Generator().manual_seed(args.seed)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
        generator=generator,
    )
    val_loader = None
    if val_dataset is not None:
        val_loader = DataLoader(
            val_dataset,
            batch_size=args.batch_size,
            shuffle=False,
            collate_fn=collator,
            num_workers=args.num_workers,
            pin_memory=device.type == "cuda",
        )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    steps_per_epoch = math.ceil(
        len(train_loader) / args.gradient_accumulation_steps
    )
    total_steps = max(steps_per_epoch * args.num_epochs, 1)
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )
    scaler = make_scaler(device, enabled=use_amp)

    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    print(
        f"train examples: {len(train_dataset)} | "
        f"val examples: {len(val_dataset) if val_dataset else 0} | "
        f"parameters: {parameter_count:,}",
        flush=True,
    )
    print(
        f"batches per epoch: {len(train_loader)} | "
        f"optimizer steps: {total_steps} | warmup steps: {warmup_steps}",
        flush=True,
    )

    best_val_loss = float("inf")
    history: list[dict[str, float]] = []

    for epoch in range(1, args.num_epochs + 1):
        train_loss = train_one_epoch(
            model,
            train_loader,
            optimizer,
            scheduler,
            scaler,
            device,
            epoch,
            args,
            use_amp,
        )

        if val_loader is not None:
            val_loss = evaluate(model, val_loader, device, use_amp)
        else:
            val_loss = train_loss

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
            }
        )
        print(
            f"epoch {epoch} complete | train loss {train_loss:.4f} | "
            f"val loss {val_loss:.4f} | perplexity {math.exp(min(val_loss, 20)):.2f}",
            flush=True,
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_checkpoint(
                model,
                tokenizer,
                args.checkpoint_dir / "best",
                epoch,
                val_loss,
                args,
                history,
            )
            print(f"saved new best checkpoint to {args.checkpoint_dir / 'best'}", flush=True)

    save_checkpoint(
        model,
        tokenizer,
        args.checkpoint_dir / "final",
        args.num_epochs,
        history[-1]["val_loss"],
        args,
        history,
    )
    print(
        f"training complete | best val loss {best_val_loss:.4f} | "
        f"checkpoints: {args.checkpoint_dir}",
        flush=True,
    )


if __name__ == "__main__":
    main()
