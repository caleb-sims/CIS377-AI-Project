"""
WORK IN PROGRESS

mbpp_data.py - turn MBPP rows into (a) harness problems and (b) model inputs.
"""
import ast
import re


def load_mbpp(split="test"):
    from datasets import load_dataset
    # "sanitized" is the cleaner subset; use "full" for more rows
    return load_dataset("Muennighoff/mbpp", "sanitized", split=split)


def find_func_name(code, tests):
    """The function the tests call (MBPP code can contain helper functions)."""
    names = [n.name for n in ast.walk(ast.parse(code)) if isinstance(n, ast.FunctionDef)]
    for name in names:
        if name in tests[0]:
            return name
    return names[0] if names else None


def row_to_problem(row, bench_setup="", bench_stmt=""):
    """Build the dict that harness.evaluate()/compare() expects.
    MBPP has no big benchmark input, so you supply bench_setup/bench_stmt."""
    setup = "\n".join(row.get("test_imports") or []) or row.get("test_setup_code", "")
    return {
        "tests": row["test_list"],
        "test_setup": setup,
        "bench_setup": bench_setup,
        "bench_stmt": bench_stmt,
        "func_name": find_func_name(row["code"], row["test_list"]),
    }


# ---------- Decoder-only LLMs (Qwen, Gemma, SmolLM3) ----------
def build_llm_messages(code):
    return [{
        "role": "user",
        "content": (
            "Rewrite this Python function so it runs faster. Keep the same function "
            "name and signature and the same behavior. Reply with only the code in a "
            "```python block.\n\n```python\n" + code + "\n```"
        ),
    }]


def extract_code(text):
    """Pull code out of an LLM reply (handles ```python fences)."""
    m = re.findall(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m[0] if m else text).strip()


# ---------- CodeT5 (seq2seq) ----------
T5_PREFIX = "optimize: "

def build_t5_input(code):
    return T5_PREFIX + code
