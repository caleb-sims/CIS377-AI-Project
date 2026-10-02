# Code Performance Improvement Plan

**Idea:** Train a small **seq2seq** model (and compare to small decoder-only models) that turns a Python function into a faster version. Beat a large LLM on **latency** while staying competitive on **quality**.

## Models

- [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)
- [Gemma 4 E2B](https://huggingface.co/google/gemma-4-E2B)
- [SmolLM3-3B](https://huggingface.co/HuggingFaceTB/SmolLM3-3B)
- Train a small **seq2seq** ([CodeT5-small](https://huggingface.co/Salesforce/codet5-small) ~60M, [CodeT5-base](https://huggingface.co/Salesforce/codet5-base) ~220M, [CodeT5-large](https://huggingface.co/Salesforce/codet5-large) ~770M) as the main model; the three above are comparison points.

## Steps

1. Make slow→fast Python function pairs from MBPP or generate synthetically and test.
2. Build a testing harness: run tests, then time original vs new (median of several runs).
3. Train the small seq2seq on the pairs.
4. Prompt the LLMs on the same set as the baseline.
5. Measure per model: inference latency, percentage tests passed, median speedup, percentage correct and faster.
6. Plot latency vs quality for all four.
7. Create a Gradio GUI to demo your model vs the LLMs
