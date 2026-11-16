"""Category: string operations.

Replace repeated string concatenation (O(n^2) due to reallocation) with ``join``/
comprehensions, and use built-ins like ``str.count`` or ``str.translate`` where they
are faster.
"""

EXAMPLES = [
    {
        "name": "join_words",
        "category": "strings",
        "technique": "Join with str.join (single O(total) allocation) instead of "
                     "repeatedly concatenating a growing string (O(n^2)).",
        "description": "Return the words joined together with the separator sep.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def join_words(words, sep=" "):
    out = ""
    first = True
    for w in words:
        if first:
            out = w
            first = False
        else:
            out = out + sep + w
    return out
""".strip(),
        "optimized": """
def join_words(words, sep=" "):
    return sep.join(words)
""".strip(),
        "tests": [
            {"args": [["a", "b", "c"], " "], "expected": "a b c"},
            {"args": [["x"], ","], "expected": "x"},
            {"args": [[], " "], "expected": ""},
            {"args": [["a"], ""], "expected": "a"},
        ],
        "benchmark": {"args": [["w%d" % i for i in range(1500)], "-"]},
    },
    {
        "name": "most_frequent_char",
        "category": "strings",
        "technique": "Count characters with collections.Counter (O(n)) instead of "
                     "rescanning the whole string for each candidate (O(n^2)).",
        "description": "Return the most frequent character in s (ties: the earliest in scan order), or '' for empty s.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def most_frequent_char(s):
    best = ""
    best_count = -1
    for c in s:
        count = 0
        for ch in s:
            if ch == c:
                count += 1
        if count > best_count:
            best = c
            best_count = count
    return best
""".strip(),
        "optimized": """
def most_frequent_char(s):
    from collections import Counter
    if not s:
        return ""
    return Counter(s).most_common(1)[0][0]
""".strip(),
        "tests": [
            {"args": ["aabbcc"], "expected": "a"},
            {"args": ["aabbc"], "expected": "a"},
            {"args": ["xyz"], "expected": "x"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["".join(chr(97 + i % 5) for i in range(1500))]},
    },
    {
        "name": "remove_chars",
        "category": "strings",
        "technique": "Filter characters with a set lookup and a single join (O(n)) "
                     "instead of per-character membership tests plus concatenation.",
        "description": "Return s with every character that appears in chars removed.",
        "complexity_before": "O(n * m) time, O(n) space",
        "complexity_after": "O(n + m) time, O(n) space",
        "unoptimized": """
def remove_chars(s, chars):
    out = ""
    for c in s:
        if c in chars:
            continue
        out = out + c
    return out
""".strip(),
        "optimized": """
def remove_chars(s, chars):
    keep = set(chars)
    return "".join(c for c in s if c not in keep)
""".strip(),
        "tests": [
            {"args": ["abcabc", "ac"], "expected": "bb"},
            {"args": ["hello", "l"], "expected": "heo"},
            {"args": ["abc", ""], "expected": "abc"},
            {"args": ["aaa", "a"], "expected": ""},
        ],
        "benchmark": {"args": ["ab" * 10000, "b"]},
    },
    {
        "name": "is_palindrome",
        "category": "strings",
        "technique": "Compare from both ends inward (O(n)) instead of building the "
                     "reversed string one prepended character at a time (O(n^2)).",
        "description": "Return True if s reads the same forwards and backwards.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def is_palindrome(s):
    rev = ""
    for c in s:
        rev = c + rev
    return rev == s
""".strip(),
        "optimized": """
def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True
""".strip(),
        "tests": [
            {"args": ["racecar"], "expected": True},
            {"args": ["hello"], "expected": False},
            {"args": [""], "expected": True},
            {"args": ["a"], "expected": True},
            {"args": ["abba"], "expected": True},
        ],
        "benchmark": {"args": ["a" * 1200 + "b"]},
    },
    {
        "name": "count_substring",
        "category": "strings",
        "technique": "Count non-overlapping occurrences with the C-implemented str.count "
                     "instead of a Python double loop that re-scans every start position.",
        "description": "Return the number of non-overlapping occurrences of sub in text.",
        "complexity_before": "O(n * m) time, O(1) space",
        "complexity_after": "O(n) time (C-optimized), O(1) space",
        "unoptimized": """
def count_substring(text, sub):
    if not sub:
        return 0
    count = 0
    i = 0
    n = len(text)
    m = len(sub)
    while i <= n - m:
        j = 0
        while j < m and text[i + j] == sub[j]:
            j += 1
        if j == m:
            count += 1
            i += m
        else:
            i += 1
    return count
""".strip(),
        "optimized": """
def count_substring(text, sub):
    if not sub:
        return 0
    return text.count(sub)
""".strip(),
        "tests": [
            {"args": ["abababab", "ab"], "expected": 4},
            {"args": ["aaaa", "aa"], "expected": 2},
            {"args": ["abcabc", "abc"], "expected": 2},
            {"args": ["xyz", "q"], "expected": 0},
        ],
        "benchmark": {"args": ["ab" * 2500, "ab" * 25]},
    },
    {
        "name": "caesar",
        "category": "strings",
        "technique": "Shift with a single C-implemented str.translate built once (O(n)) "
                     "instead of per-character chr/concat building a string (O(n^2)).",
        "description": "Return text with each lowercase letter shifted forward by shift (mod 26); other characters are unchanged.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(1) extra space",
        "unoptimized": """
def caesar(text, shift):
    out = ""
    for c in text:
        if c.islower():
            out = out + chr((ord(c) - 97 + shift) % 26 + 97)
        else:
            out = out + c
    return out
""".strip(),
        "optimized": """
def caesar(text, shift):
    import string
    shift = shift % 26
    lower = string.ascii_lowercase
    table = str.maketrans(lower, lower[shift:] + lower[:shift])
    return text.translate(table)
""".strip(),
        "tests": [
            {"args": ["hello", 1], "expected": "ifmmp"},
            {"args": ["abc", 3], "expected": "def"},
            {"args": ["xyz", 3], "expected": "abc"},
            {"args": ["Hello", 1], "expected": "Hfmmp"},
            {"args": ["abc", 26], "expected": "abc"},
        ],
        "benchmark": {"args": ["ab" * 1500, 13]},
    },
    {
        "name": "reverse_words",
        "category": "strings",
        "technique": "Reverse the word list and join once (O(n)) instead of prepending "
                     "each word to a growing string (O(n^2)).",
        "description": "Return the whitespace-separated words of s in reverse order, joined by single spaces.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def reverse_words(s):
    out = ""
    for w in s.split():
        if out:
            out = w + " " + out
        else:
            out = w
    return out
""".strip(),
        "optimized": """
def reverse_words(s):
    return " ".join(reversed(s.split()))
""".strip(),
        "tests": [
            {"args": ["the sky is blue"], "expected": "blue is sky the"},
            {"args": ["  hello world  "], "expected": "world hello"},
            {"args": ["a"], "expected": "a"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": [" ".join("w%d" % i for i in range(3000))]},
    },
    {
        "name": "capitalize_words",
        "category": "strings",
        "technique": "Capitalize with a generator and one join (O(n)) instead of repeated "
                     "concatenation of a growing string (O(n^2)).",
        "description": "Return s with each whitespace-separated word capitalized, joined by single spaces.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def capitalize_words(s):
    out = ""
    first = True
    for w in s.split():
        cap = w[:1].upper() + w[1:].lower()
        if first:
            out = cap
            first = False
        else:
            out = out + " " + cap
    return out
""".strip(),
        "optimized": """
def capitalize_words(s):
    return " ".join(w.capitalize() for w in s.split())
""".strip(),
        "tests": [
            {"args": ["hello world"], "expected": "Hello World"},
            {"args": ["  multiple   spaces "], "expected": "Multiple Spaces"},
            {"args": ["hELLO"], "expected": "Hello"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": [" ".join("word%d" % i for i in range(3000))]},
    },
    {
        "name": "run_length_encode",
        "category": "strings",
        "technique": "Accumulate pieces in a list and join once (O(n)) instead of "
                     "concatenating each run onto a growing string (O(n^2)).",
        "description": "Return the run-length encoding of s as character followed by run length for each run.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def run_length_encode(s):
    out = ""
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        out = out + s[i] + str(j - i)
        i = j
    return out
""".strip(),
        "optimized": """
def run_length_encode(s):
    parts = []
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        parts.append(s[i])
        parts.append(str(j - i))
        i = j
    return "".join(parts)
""".strip(),
        "tests": [
            {"args": ["aaabb"], "expected": "a3b2"},
            {"args": ["abc"], "expected": "a1b1c1"},
            {"args": ["aaaa"], "expected": "a4"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["ab" * 3000]},
    },
    {
        "name": "is_rotation",
        "category": "strings",
        "technique": "Test b in a + a (linear-time C substring search) instead of building "
                     "and comparing every rotation (O(n^2)).",
        "description": "Return True if b is a rotation of a.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time (C search), O(n) space",
        "unoptimized": """
def is_rotation(a, b):
    if len(a) != len(b):
        return False
    if not a:
        return True
    for i in range(len(a)):
        if a[i:] + a[:i] == b:
            return True
    return False
""".strip(),
        "optimized": """
def is_rotation(a, b):
    return len(a) == len(b) and b in a + a
""".strip(),
        "tests": [
            {"args": ["abcde", "cdeab"], "expected": True},
            {"args": ["abcde", "abced"], "expected": False},
            {"args": ["", ""], "expected": True},
            {"args": ["a", "a"], "expected": True},
            {"args": ["abc", "abcd"], "expected": False},
        ],
        "benchmark": {"args": ["a" * 2000 + "b", "b" + "a" * 2000]},
    },
    {
        "name": "swap_case",
        "category": "strings",
        "technique": "Use the C-implemented str.swapcase (O(n)) instead of per-character "
                     "branching and concatenation (O(n^2)).",
        "description": "Return s with uppercase letters lowercased and lowercase letters uppercased.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def swap_case(s):
    out = ""
    for c in s:
        if c.isupper():
            out = out + c.lower()
        elif c.islower():
            out = out + c.upper()
        else:
            out = out + c
    return out
""".strip(),
        "optimized": """
def swap_case(s):
    return s.swapcase()
""".strip(),
        "tests": [
            {"args": ["Hello World"], "expected": "hELLO wORLD"},
            {"args": ["Python3"], "expected": "pYTHON3"},
            {"args": ["abc"], "expected": "ABC"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["Ab3" * 3000]},
    },
    {
        "name": "repeat_string",
        "category": "strings",
        "technique": "Use C-level string repetition (O(n)) instead of appending the same "
                     "string in a loop with repeated reallocation (O(n^2)).",
        "description": "Return the string s repeated n times.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def repeat_string(s, n):
    out = ""
    for _ in range(n):
        out = out + s
    return out
""".strip(),
        "optimized": """
def repeat_string(s, n):
    return s * n
""".strip(),
        "tests": [
            {"args": ["ab", 3], "expected": "ababab"},
            {"args": ["x", 0], "expected": ""},
            {"args": ["a", 5], "expected": "aaaaa"},
            {"args": ["", 4], "expected": ""},
        ],
        "benchmark": {"args": ["ab", 5000]},
    },
    {
        "name": "compress_spaces",
        "category": "strings",
        "technique": "Split and join once (O(n)) instead of concatenating each word onto "
                     "a growing output string (O(n^2)).",
        "description": "Collapse every run of whitespace to a single space and strip leading/trailing whitespace.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def compress_spaces(s):
    out = ""
    for w in s.split():
        if out:
            out = out + " " + w
        else:
            out = w
    return out
""".strip(),
        "optimized": """
def compress_spaces(s):
    return " ".join(s.split())
""".strip(),
        "tests": [
            {"args": ["  a   b  c "], "expected": "a b c"},
            {"args": ["hello"], "expected": "hello"},
            {"args": ["one  two"], "expected": "one two"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["  ".join("w%d" % i for i in range(4000))]},
    },
    {
        "name": "remove_adjacent_duplicates",
        "category": "strings",
        "technique": "Use a stack with O(1) pushes/pops instead of repeatedly rebuilding "
                     "the whole string after every removed pair (O(n^2)).",
        "description": "Repeatedly remove adjacent duplicate character pairs until no such pair remains, and return the result.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def remove_adjacent_duplicates(s):
    changed = True
    while changed:
        changed = False
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]
                changed = True
                break
    return s
""".strip(),
        "optimized": """
def remove_adjacent_duplicates(s):
    stack = []
    for c in s:
        if stack and stack[-1] == c:
            stack.pop()
        else:
            stack.append(c)
    return "".join(stack)
""".strip(),
        "tests": [
            {"args": ["abbaca"], "expected": "ca"},
            {"args": ["azxxzy"], "expected": "ay"},
            {"args": ["aaaa"], "expected": ""},
            {"args": ["a"], "expected": "a"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["aabb" * 1000]},
    },
    {
        "name": "first_unique_char",
        "category": "strings",
        "technique": "Count characters once with a Counter (O(n)) instead of rescanning the "
                     "string for every character (O(n^2)).",
        "description": "Return the index of the first character that appears exactly once, or -1 if none.",
        "complexity_before": "O(n^2) time, O(1) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def first_unique_char(s):
    for i, c in enumerate(s):
        count = 0
        for d in s:
            if d == c:
                count += 1
        if count == 1:
            return i
    return -1
""".strip(),
        "optimized": """
def first_unique_char(s):
    from collections import Counter
    counts = Counter(s)
    for i, c in enumerate(s):
        if counts[c] == 1:
            return i
    return -1
""".strip(),
        "tests": [
            {"args": ["leetcode"], "expected": 0},
            {"args": ["loveleetcode"], "expected": 2},
            {"args": ["aabb"], "expected": -1},
            {"args": ["z"], "expected": 0},
            {"args": [""], "expected": -1},
        ],
        "benchmark": {"args": ["ab" * 2000 + "c"]},
    },
    {
        "name": "valid_parentheses",
        "category": "strings",
        "technique": "Validate with a stack in one pass (O(n)) instead of repeatedly "
                     "rewriting the string to strip adjacent pairs (O(n^2)).",
        "description": "Return True if the brackets in s are correctly matched and nested.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def valid_parentheses(s):
    while "()" in s or "[]" in s or "{}" in s:
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""
""".strip(),
        "optimized": """
def valid_parentheses(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for c in s:
        if c in "([{":
            stack.append(c)
        elif c in pairs:
            if not stack or stack.pop() != pairs[c]:
                return False
        else:
            return False
    return not stack
""".strip(),
        "tests": [
            {"args": ["()"], "expected": True},
            {"args": ["()[]{}"], "expected": True},
            {"args": ["(]"], "expected": False},
            {"args": ["([)]"], "expected": False},
            {"args": ["{[]}"], "expected": True},
            {"args": [""], "expected": True},
        ],
        "benchmark": {"args": ["(" * 3000 + ")" * 3000]},
    },
    {
        "name": "count_segments",
        "category": "strings",
        "technique": "Use the C-implemented str.split to count words instead of a "
                     "character-by-character Python state machine.",
        "description": "Return the number of whitespace-separated words in s.",
        "complexity_before": "O(n) time (Python loop), O(1) space",
        "complexity_after": "O(n) time (C split), O(n) space",
        "unoptimized": """
def count_segments(s):
    count = 0
    in_word = False
    for c in s:
        if c != " ":
            if not in_word:
                count += 1
                in_word = True
        else:
            in_word = False
    return count
""".strip(),
        "optimized": """
def count_segments(s):
    return len(s.split())
""".strip(),
        "tests": [
            {"args": ["Hello, my name is John"], "expected": 5},
            {"args": [" "], "expected": 0},
            {"args": [""], "expected": 0},
            {"args": ["a"], "expected": 1},
            {"args": ["  a  b "], "expected": 2},
        ],
        "benchmark": {"args": [" ".join("word%d" % i for i in range(4000))]},
    },
    {
        "name": "add_binary",
        "category": "strings",
        "technique": "Convert to int, add, and format back with bin (C-level) instead of "
                     "prepending one character at a time (O(n^2)).",
        "description": "Return the binary string sum of binary strings a and b.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def add_binary(a, b):
    i, j = len(a) - 1, len(b) - 1
    carry = 0
    out = ""
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        out = str(total % 2) + out
        carry = total // 2
    return out or "0"
""".strip(),
        "optimized": """
def add_binary(a, b):
    return bin(int(a, 2) + int(b, 2))[2:]
""".strip(),
        "tests": [
            {"args": ["11", "1"], "expected": "100"},
            {"args": ["1010", "1011"], "expected": "10101"},
            {"args": ["0", "0"], "expected": "0"},
            {"args": ["1", "111"], "expected": "1000"},
            {"args": ["0", "1"], "expected": "1"},
        ],
        "benchmark": {"args": ["1" * 3000, "1" * 3000]},
    },
    {
        "name": "reverse_vowels",
        "category": "strings",
        "technique": "Swap vowels in a mutable list (O(n)) instead of rebuilding the "
                     "whole string on every swap (O(n^2)).",
        "description": "Return s with only its vowels reversed.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def reverse_vowels(s):
    vowels = "aeiouAEIOU"
    i, j = 0, len(s) - 1
    chars = s
    while i < j:
        while i < j and chars[i] not in vowels:
            i += 1
        while i < j and chars[j] not in vowels:
            j -= 1
        if i < j:
            chars = chars[:i] + chars[j] + chars[i + 1:j] + chars[i] + chars[j + 1:]
            i += 1
            j -= 1
    return chars
""".strip(),
        "optimized": """
def reverse_vowels(s):
    vowels = set("aeiouAEIOU")
    chars = list(s)
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and chars[i] not in vowels:
            i += 1
        while i < j and chars[j] not in vowels:
            j -= 1
        if i < j:
            chars[i], chars[j] = chars[j], chars[i]
            i += 1
            j -= 1
    return "".join(chars)
""".strip(),
        "tests": [
            {"args": ["hello"], "expected": "holle"},
            {"args": ["leetcode"], "expected": "leotcede"},
            {"args": ["aA"], "expected": "Aa"},
            {"args": ["racecar"], "expected": "racecar"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["aeiou" * 1000]},
    },
    {
        "name": "count_palindromic_substrings",
        "category": "strings",
        "technique": "Expand around every center (O(n^2)) instead of slicing and reversing "
                     "every substring (O(n^3)).",
        "description": "Return the number of palindromic contiguous substrings of s.",
        "complexity_before": "O(n^3) time, O(n) space",
        "complexity_after": "O(n^2) time, O(1) space",
        "unoptimized": """
def count_palindromic_substrings(s):
    count = 0
    n = len(s)
    for i in range(n):
        for j in range(i, n):
            sub = s[i:j + 1]
            if sub == sub[::-1]:
                count += 1
    return count
""".strip(),
        "optimized": """
def count_palindromic_substrings(s):
    count = 0
    n = len(s)
    for center in range(n):
        left, right = center, center
        while left >= 0 and right < n and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
        left, right = center, center + 1
        while left >= 0 and right < n and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
    return count
""".strip(),
        "tests": [
            {"args": ["abc"], "expected": 3},
            {"args": ["aaa"], "expected": 6},
            {"args": ["abba"], "expected": 6},
            {"args": ["a"], "expected": 1},
            {"args": [""], "expected": 0},
        ],
        "benchmark": {"args": ["ab" * 150]},
    },
    {
        "name": "word_frequency",
        "category": "strings",
        "technique": "Count words with a Counter (O(n)) instead of searching a list of "
                     "counts for every word (O(n^2)).",
        "description": "Return a dict mapping each whitespace-separated word to its frequency.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def word_frequency(text):
    pairs = []
    for w in text.split():
        found = False
        for item in pairs:
            if item[0] == w:
                item[1] += 1
                found = True
                break
        if not found:
            pairs.append([w, 1])
    return {w: c for w, c in pairs}
""".strip(),
        "optimized": """
def word_frequency(text):
    from collections import Counter
    return dict(Counter(text.split()))
""".strip(),
        "tests": [
            {"args": ["the cat the dog"], "expected": {"the": 2, "cat": 1, "dog": 1}},
            {"args": ["a a a"], "expected": {"a": 3}},
            {"args": ["x y x"], "expected": {"x": 2, "y": 1}},
            {"args": ["one"], "expected": {"one": 1}},
            {"args": [""], "expected": {}},
        ],
        "benchmark": {"args": [" ".join("w%d" % (i % 500) for i in range(5000))]},
    },
    {
        "name": "count_char_occurrences",
        "category": "strings",
        "technique": "Use the C-implemented str.count instead of a character-by-character "
                     "Python loop.",
        "description": "Return how many times the character ch occurs in s.",
        "complexity_before": "O(n) time (Python loop), O(1) space",
        "complexity_after": "O(n) time (C scan), O(1) space",
        "unoptimized": """
def count_char_occurrences(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
    return count
""".strip(),
        "optimized": """
def count_char_occurrences(s, ch):
    return s.count(ch)
""".strip(),
        "tests": [
            {"args": ["hello", "l"], "expected": 2},
            {"args": ["aaaa", "a"], "expected": 4},
            {"args": ["abc", "z"], "expected": 0},
            {"args": ["", "a"], "expected": 0},
        ],
        "benchmark": {"args": ["ab" * 50000, "a"]},
    },
    {
        "name": "replace_all",
        "category": "strings",
        "technique": "Use the C-implemented str.replace instead of building the result "
                     "with repeated string concatenation (O(n^2)).",
        "description": "Return s with every non-overlapping occurrence of old replaced by new.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def replace_all(s, old, new):
    if old == "":
        return s
    out = ""
    i = 0
    while i < len(s):
        if s.startswith(old, i):
            out = out + new
            i += len(old)
        else:
            out = out + s[i]
            i += 1
    return out
""".strip(),
        "optimized": """
def replace_all(s, old, new):
    return s.replace(old, new)
""".strip(),
        "tests": [
            {"args": ["hello world", "o", "0"], "expected": "hell0 w0rld"},
            {"args": ["aaaa", "aa", "b"], "expected": "bb"},
            {"args": ["abc", "x", "y"], "expected": "abc"},
            {"args": ["aaa", "a", ""], "expected": ""},
            {"args": ["", "a", "b"], "expected": ""},
        ],
        "benchmark": {"args": ["ab" * 5000, "a", "xy"]},
    },
    {
        "name": "valid_palindrome_ii",
        "category": "strings",
        "technique": "Check at most two mismatching substrings with two pointers (O(n)) "
                     "instead of trying every single-character deletion (O(n^2)).",
        "description": "Return True if s can become a palindrome after deleting at most one character.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(1) space",
        "unoptimized": """
def valid_palindrome_ii(s):
    def is_pal(t):
        return t == t[::-1]

    if is_pal(s):
        return True
    for i in range(len(s)):
        if is_pal(s[:i] + s[i + 1:]):
            return True
    return False
""".strip(),
        "optimized": """
def valid_palindrome_ii(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            def is_pal(a, b):
                while a < b:
                    if s[a] != s[b]:
                        return False
                    a += 1
                    b -= 1
                return True

            return is_pal(i + 1, j) or is_pal(i, j - 1)
        i += 1
        j -= 1
    return True
""".strip(),
        "tests": [
            {"args": ["aba"], "expected": True},
            {"args": ["abca"], "expected": True},
            {"args": ["abc"], "expected": False},
            {"args": ["abccba"], "expected": True},
            {"args": [""], "expected": True},
        ],
        "benchmark": {"args": ["".join(chr(97 + (i * 37) % 26) for i in range(5000))]},
    },
    {
        "name": "reverse_string",
        "category": "strings",
        "technique": "Use the C-level slice s[::-1] instead of prepending each character "
                     "to a growing string (O(n^2)).",
        "description": "Return the reverse of s.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def reverse_string(s):
    out = ""
    for c in s:
        out = c + out
    return out
""".strip(),
        "optimized": """
def reverse_string(s):
    return s[::-1]
""".strip(),
        "tests": [
            {"args": ["abc"], "expected": "cba"},
            {"args": ["hello"], "expected": "olleh"},
            {"args": ["a"], "expected": "a"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["abcdefghij" * 1000]},
    },
    {
        "name": "remove_char_set",
        "category": "strings",
        "technique": "Use str.translate with a delete table (C-level) instead of "
                     "concatenating surviving characters one by one (O(n^2)).",
        "description": "Return s with every character contained in remove_chars deleted.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def remove_char_set(s, remove_chars):
    out = ""
    for c in s:
        if c not in remove_chars:
            out = out + c
    return out
""".strip(),
        "optimized": """
def remove_char_set(s, remove_chars):
    return s.translate(str.maketrans("", "", remove_chars))
""".strip(),
        "tests": [
            {"args": ["hello, world!", ",!"], "expected": "hello world"},
            {"args": ["a.b,c", ".,"], "expected": "abc"},
            {"args": ["abc", ""], "expected": "abc"},
            {"args": ["aeiou", "aeiou"], "expected": ""},
            {"args": ["", "!"], "expected": ""},
        ],
        "benchmark": {"args": ["abcdefghij" * 1000, "aeiou"]},
    },
    {
        "name": "swap_adjacent_pairs",
        "category": "strings",
        "technique": "Swap characters in a list and join once (O(n)) instead of building "
                     "the output with repeated concatenation (O(n^2)).",
        "description": "Return s with each adjacent character pair swapped, leaving a final unpaired character in place.",
        "complexity_before": "O(n^2) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def swap_adjacent_pairs(s):
    out = ""
    i = 0
    while i < len(s):
        if i + 1 < len(s):
            out = out + s[i + 1] + s[i]
            i += 2
        else:
            out = out + s[i]
            i += 1
    return out
""".strip(),
        "optimized": """
def swap_adjacent_pairs(s):
    chars = list(s)
    for i in range(0, len(chars) - 1, 2):
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)
""".strip(),
        "tests": [
            {"args": ["abcdef"], "expected": "badcfe"},
            {"args": ["abc"], "expected": "bac"},
            {"args": ["a"], "expected": "a"},
            {"args": [""], "expected": ""},
        ],
        "benchmark": {"args": ["abcdefghij" * 1000]},
    },
]
