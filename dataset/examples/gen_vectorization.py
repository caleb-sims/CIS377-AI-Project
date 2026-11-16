"""Generated vectorization families: 5 NumPy patterns x 20 variants."""

from __future__ import annotations

from .gen_common import make

EXAMPLES = []


def _ref_pairwise_abs(values):
    total = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            total += abs(values[i] - values[j])
    return total


def _ref_matmul(A, B):
    n = len(A)
    p = len(B)
    m = len(B[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            total = 0
            for k in range(p):
                total += A[i][k] * B[k][j]
            out[i][j] = total
    return out


def _ref_convolve_valid(a, kernel):
    n = len(a)
    m = len(kernel)
    out = []
    for i in range(n - m + 1):
        total = 0
        for j in range(m):
            total += a[i + j] * kernel[m - 1 - j]
        out.append(total)
    return out


def _ref_gram(X):
    n = len(X)
    d = len(X[0])
    return [[sum(X[i][k] * X[j][k] for k in range(d)) for j in range(n)]
            for i in range(n)]


def _ref_max_pool(image, k):
    rows = len(image)
    cols = len(image[0])
    out = []
    for i in range(rows // k):
        row = []
        for j in range(cols // k):
            best = image[i * k][j * k]
            for r in range(i * k, i * k + k):
                for c in range(j * k, j * k + k):
                    if image[r][c] > best:
                        best = image[r][c]
            row.append(best)
        out.append(row)
    return out


def _pairwise_abs(variants):
    unopt = """
def __NAME__(values):
    total = 0
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            total += abs(values[i] - values[j])
    return total
"""
    opt = """
import numpy as np

def __NAME__(values):
    x = np.asarray(values, dtype=float)
    diff = np.abs(x[:, None] - x[None, :])
    return float(diff.sum() / 2)
"""
    for i in range(variants):
        n = 250 + (i % 20) * 10
        sample = [(j * 37 + i * 11) % 100 for j in range(6 + i % 4)]
        EXAMPLES.append(make(
            f"gen_pairwise_abs_{i:02d}", "vectorization",
            "Broadcast the values and sum absolute differences in C instead of a "
            "Python double loop.",
            "Return the sum of absolute differences over all unordered pairs.",
            "O(n^2) time (Python loop), O(1) space",
            "O(n^2) time (vectorized), O(n^2) space",
            unopt, opt,
            [
                {"args": [sample], "expected": _ref_pairwise_abs(sample)},
                {"args": [[1, 2, 3]], "expected": 4},
                {"args": [[5]], "expected": 0},
                {"args": [[1, 1]], "expected": 0},
            ],
            {"args": [[(j * 37 + i * 11) % 1000 for j in range(n)]]},
        ))


def _matrix_multiply(variants):
    unopt = """
def __NAME__(A, B):
    n = len(A)
    p = len(B)
    m = len(B[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            total = 0
            for k in range(p):
                total += A[i][k] * B[k][j]
            out[i][j] = total
    return out
"""
    opt = """
import numpy as np

def __NAME__(A, B):
    return (np.asarray(A, dtype=float) @ np.asarray(B, dtype=float)).tolist()
"""
    for i in range(variants):
        size = 20 + i % 5
        A = [[(r * 7 + c * 11 + i) % 10 for c in range(size)] for r in range(size)]
        B = [[(r * 13 + c * 5 + i) % 10 for c in range(size)] for r in range(size)]
        tsize = 2 + i % 3
        tA = [[(r + c + i) % 7 for c in range(tsize)] for r in range(tsize)]
        tB = [[(r * 2 + c + i) % 7 for c in range(tsize)] for r in range(tsize)]
        EXAMPLES.append(make(
            f"gen_matrix_multiply_{i:02d}", "vectorization",
            "Use a single NumPy matrix product (BLAS) instead of a Python triple loop.",
            "Return the matrix product A @ B.",
            "O(n^3) time (Python loop), O(n^2) space",
            "O(n^3) time (BLAS), O(n^2) space",
            unopt, opt,
            [
                {"args": [tA, tB], "expected": _ref_matmul(tA, tB)},
                {"args": [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
                 "expected": [[19, 22], [43, 50]]},
                {"args": [[[2]], [[3]]], "expected": [[6]]},
            ],
            {"args": [A, B]},
        ))


def _convolve_valid(variants):
    unopt = """
def __NAME__(a, kernel):
    n = len(a)
    m = len(kernel)
    out = []
    for i in range(n - m + 1):
        total = 0
        for j in range(m):
            total += a[i + j] * kernel[m - 1 - j]
        out.append(total)
    return out
"""
    opt = """
import numpy as np

def __NAME__(a, kernel):
    return np.convolve(np.asarray(a, dtype=float),
                       np.asarray(kernel, dtype=float), mode="valid").tolist()
"""
    for i in range(variants):
        n = 4000 + (i % 20) * 200
        klen = 21 + i % 10
        sample = [(j * 3 + i) % 10 for j in range(6 + i % 4)]
        kernel = [(j * 2 + i) % 5 for j in range(3 + i % 3)]
        EXAMPLES.append(make(
            f"gen_convolve_valid_{i:02d}", "vectorization",
            "Run the valid convolution with C-implemented np.convolve instead of a "
            "Python double loop.",
            "Return the valid-mode convolution of a with kernel.",
            "O(n * m) time (Python loop), O(n) space",
            "O(n * m) time (C), O(n) space",
            unopt, opt,
            [
                {"args": [sample, kernel],
                 "expected": _ref_convolve_valid(sample, kernel)},
                {"args": [[1, 2, 3, 4], [1, 1]], "expected": [3, 5, 7]},
                {"args": [[5], [2]], "expected": [10]},
            ],
            {"args": [[j % 10 for j in range(n)], [1] * klen]},
        ))


def _gram_matrix(variants):
    unopt = """
def __NAME__(X):
    n = len(X)
    d = len(X[0]) if n else 0
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(d):
                total += X[i][k] * X[j][k]
            out[i][j] = total
    return out
"""
    opt = """
import numpy as np

def __NAME__(X):
    A = np.asarray(X, dtype=float)
    return np.dot(A, A.T).tolist()
"""
    for i in range(variants):
        n = 120 + (i % 20) * 5
        d = 8
        X = [[(r * 37 + c * 11 + i) % 100 for c in range(d)] for r in range(n)]
        tX = [[(r * 5 + c * 3 + i) % 9 for c in range(3)] for r in range(4)]
        EXAMPLES.append(make(
            f"gen_gram_matrix_{i:02d}", "vectorization",
            "Compute X @ X.T with one BLAS call instead of a Python triple loop.",
            "Return the Gram matrix G with G[i][j] equal to the dot product of rows i and j.",
            "O(n^2 * d) time (Python loop), O(n^2) space",
            "O(n^2 * d) time (BLAS), O(n^2) space",
            unopt, opt,
            [
                {"args": [tX], "expected": _ref_gram(tX)},
                {"args": [[[1, 2], [3, 4]]], "expected": [[5, 11], [11, 25]]},
                {"args": [[[2]]], "expected": [[4]]},
            ],
            {"args": [X]},
        ))


def _max_pool_2d(variants):
    unopt = """
def __NAME__(image, k):
    rows = len(image)
    cols = len(image[0])
    out = []
    for i in range(rows // k):
        row = []
        for j in range(cols // k):
            best = image[i * k][j * k]
            for r in range(i * k, i * k + k):
                for c in range(j * k, j * k + k):
                    if image[r][c] > best:
                        best = image[r][c]
            row.append(best)
        out.append(row)
    return out
"""
    opt = """
import numpy as np

def __NAME__(image, k):
    arr = np.asarray(image, dtype=float)
    rows = (arr.shape[0] // k) * k
    cols = (arr.shape[1] // k) * k
    trimmed = arr[:rows, :cols]
    pooled = trimmed.reshape(rows // k, k, cols // k, k).max(axis=(1, 3))
    return pooled.tolist()
"""
    for i in range(variants):
        size = 400 + (i % 20) * 5
        k = 5 + i % 2
        image = [[(r * 37 + c * 11 + i) % 100 for c in range(size)]
                 for r in range(size)]
        tsize = 4 + i % 2
        timage = [[(r * 5 + c * 3 + i) % 20 for c in range(tsize)]
                  for r in range(tsize)]
        EXAMPLES.append(make(
            f"gen_max_pool_2d_{i:02d}", "vectorization",
            "Reshape the image into non-overlapping blocks and reduce with NumPy "
            "instead of four nested Python loops.",
            "Return 2-D max pooling with a k by k kernel and stride k.",
            "O(m * n * k^2) time (Python loops), O(m * n) space",
            "O(m * n) time (vectorized), O(m * n) space",
            unopt, opt,
            [
                {"args": [timage, 2], "expected": _ref_max_pool(timage, 2)},
                {"args": [[[1, 2, 3, 4], [5, 6, 7, 8],
                           [9, 10, 11, 12], [13, 14, 15, 16]], 2],
                 "expected": [[6, 8], [14, 16]]},
                {"args": [[[5]], 1], "expected": [[5]]},
            ],
            {"args": [image, k]},
        ))


def build(variants=20):
    EXAMPLES.clear()
    _pairwise_abs(variants)
    _matrix_multiply(variants)
    _convolve_valid(variants)
    _gram_matrix(variants)
    _max_pool_2d(variants)
    return EXAMPLES


EXAMPLES = build(20)
