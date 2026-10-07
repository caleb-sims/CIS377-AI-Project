from datasets import load_dataset

ds = load_dataset("google-research-datasets/mbpp", "sanitized")
print(ds)

example = ds["train"][0]
for key, value in example.items():
    print(f"--- {key} ---")
    print(value)