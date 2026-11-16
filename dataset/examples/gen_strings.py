"""Generated string families: 5 proven patterns x 20 data variants each."""

from __future__ import annotations

from .gen_common import make, rng

EXAMPLES = []


def _ref_count_substring(s, sub):
    count = 0
    i = 0
    while i <= len(s) - len(sub):
        if s[i:i + len(sub)] == sub:
            count += 1
            i += len(sub)
        else:
            i += 1
    return count


def _reverse_string(variants):
    unopt = """
def __NAME__(s):
    out = ""
    for c in s:
        out = c + out
    return out
"""
    opt = """
def __NAME__(s):
    return s[::-1]
"""
    for i in range(variants):
        r = rng(600 + i)
        sample = "".join(r.choice("abcdef") for _ in range(6))
        length = 1000 + (i % 20) * 100
        text = ("abcdefghij" * ((length // 10) + 1))[:length]
        EXAMPLES.append(make(
            f"gen_reverse_string_{i:02d}", "strings",
            "Use the C-level slice s[::-1] instead of prepending characters one by "
            "one (O(n^2)).",
            "Return the reverse of s.",
            "O(n^2) time, O(n) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": sample[::-1]},
                {"args": ["abc"], "expected": "cba"},
                {"args": ["hello"], "expected": "olleh"},
                {"args": [""], "expected": ""},
            ],
            {"args": [text]},
        ))


def _is_palindrome(variants):
    unopt = """
def __NAME__(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True
"""
    opt = """
def __NAME__(s):
    return s == s[::-1]
"""
    for i in range(variants):
        sample = "a" * (5 + i % 5)
        n = 3000 + (i % 20) * 100
        EXAMPLES.append(make(
            f"gen_is_palindrome_{i:02d}", "strings",
            "Compare the string with its reversed slice in C instead of a "
            "character-by-character Python loop.",
            "Return True if s reads the same forwards and backwards.",
            "O(n) time (Python loop), O(1) space", "O(n) time (C), O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": True},
                {"args": ["abba"], "expected": True},
                {"args": ["abc"], "expected": False},
                {"args": [""], "expected": True},
                {"args": ["abca"], "expected": False},
            ],
            {"args": ["a" * n]},
        ))


def _remove_spaces(variants):
    unopt = """
def __NAME__(s):
    out = ""
    for c in s:
        if c != " ":
            out = out + c
    return out
"""
    opt = """
def __NAME__(s):
    return s.replace(" ", "")
"""
    for i in range(variants):
        r = rng(700 + i)
        sample = "".join(r.choice("abc ") for _ in range(8))
        length = 2000 + (i % 20) * 100
        text = ("a b c " * ((length // 6) + 1))[:length]
        EXAMPLES.append(make(
            f"gen_remove_spaces_{i:02d}", "strings",
            "Use the C-implemented str.replace instead of building the result with "
            "repeated concatenation (O(n^2)).",
            "Return s with every space character removed.",
            "O(n^2) time, O(n) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample], "expected": sample.replace(" ", "")},
                {"args": ["a b c"], "expected": "abc"},
                {"args": ["   "], "expected": ""},
                {"args": [""], "expected": ""},
            ],
            {"args": [text]},
        ))


def _count_substring(variants):
    unopt = """
def __NAME__(s, sub):
    count = 0
    i = 0
    while i <= len(s) - len(sub):
        if s[i:i + len(sub)] == sub:
            count += 1
            i += len(sub)
        else:
            i += 1
    return count
"""
    opt = """
def __NAME__(s, sub):
    return s.count(sub)
"""
    for i in range(variants):
        reps = 1000 + (i % 20) * 50
        text = "abc" * reps
        EXAMPLES.append(make(
            f"gen_count_substring_{i:02d}", "strings",
            "Use the C-implemented str.count instead of slicing and comparing "
            "candidate windows in Python.",
            "Return the number of non-overlapping occurrences of sub in s.",
            "O(n * m) time, O(m) space", "O(n) time (C), O(1) space",
            unopt, opt,
            [
                {"args": ["aaaa", "aa"], "expected": 2},
                {"args": ["abcabc", "abc"], "expected": 2},
                {"args": ["abc", "d"], "expected": 0},
                {"args": ["a", "a"], "expected": 1},
                {"args": [text, "abc"], "expected": reps},
            ],
            {"args": [text, "abc"]},
        ))


def _is_anagram(variants):
    unopt = """
def __NAME__(a, b):
    if len(a) != len(b):
        return False
    chars = list(b)
    for c in a:
        found = False
        for i, d in enumerate(chars):
            if c == d:
                chars.pop(i)
                found = True
                break
        if not found:
            return False
    return True
"""
    opt = """
def __NAME__(a, b):
    from collections import Counter
    return Counter(a) == Counter(b)
"""
    for i in range(variants):
        length = 1000 + (i % 20) * 50
        a = ("abcdefghij" * ((length // 10) + 1))[:length]
        b = a[::-1]
        sample = ("abcdefghij" * (1 + i % 3))
        EXAMPLES.append(make(
            f"gen_is_anagram_{i:02d}", "strings",
            "Compare character counts with Counter (O(n)) instead of removing each "
            "character from a list (O(n^2)).",
            "Return True if a and b are anagrams of each other.",
            "O(n^2) time, O(n) space", "O(n) time, O(n) space",
            unopt, opt,
            [
                {"args": [sample, sample[::-1]], "expected": True},
                {"args": ["listen", "silent"], "expected": True},
                {"args": ["abc", "abd"], "expected": False},
                {"args": ["", ""], "expected": True},
                {"args": ["a", "aa"], "expected": False},
            ],
            {"args": [a, b]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _reverse_string(variants)
    _is_palindrome(variants)
    _remove_spaces(variants)
    _count_substring(variants)
    _is_anagram(variants)
    return EXAMPLES


EXAMPLES = build(20)
