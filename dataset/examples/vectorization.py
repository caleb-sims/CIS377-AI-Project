"""Category: NumPy / vectorization.

Replace Python-level loops over numeric data with vectorized NumPy operations.
The optimized code is self-contained (it imports numpy itself) and returns plain
Python types (int/float/list) so both versions compare equal.
"""

EXAMPLES = [
    {
        "name": "matvec",
        "category": "vectorization",
        "technique": "Compute a matrix-vector product with the BLAS-backed np.dot instead of "
                     "a Python loop that re-dots every row against the vector.",
        "description": "Return the product of square matrix A (n x n) times column vector b (length n).",
        "complexity_before": "O(n^2) time (Python loop), O(n) space",
        "complexity_after": "O(n^2) time (BLAS), O(n) space",
        "unoptimized": """
def matvec(A, b):
    n = len(b)
    out = []
    for i in range(len(A)):
        s = 0
        for j in range(n):
            s += A[i][j] * b[j]
        out.append(s)
    return out
""".strip(),
        "optimized": """
import numpy as np

def matvec(A, b):
    return np.dot(np.asarray(A, dtype=float), np.asarray(b, dtype=float)).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3, 4]], [5, 6]], "expected": [17.0, 39.0]},
            {"args": [[[1]], [2]], "expected": [2.0]},
            {"args": [[[1, 0], [0, 1]], [2, 3]], "expected": [2.0, 3.0]},
            {"args": [[[2, 0], [0, 3]], [4, 5]], "expected": [8.0, 15.0]},
        ],
        "benchmark": {"args": [[[(i + j) % 7 for j in range(500)] for i in range(500)],
                              [j % 5 for j in range(500)]]},
    },
    {
        "name": "normalize",
        "category": "vectorization",
        "technique": "Scale to the [0, 1] range with one vectorized expression instead of "
                     "a per-element Python loop.",
        "description": "Return values scaled to [0, 1] via (v - min) / (max - min); all-equal values map to 0.0.",
        "complexity_before": "O(n) time (Python loop), O(n) space",
        "complexity_after": "O(n) time (vectorized), O(n) space",
        "unoptimized": """
def normalize(values):
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    out = []
    for v in values:
        if hi == lo:
            out.append(0.0)
        else:
            out.append((v - lo) / (hi - lo))
    return out
""".strip(),
        "optimized": """
import numpy as np

def normalize(values):
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return []
    lo, hi = float(arr.min()), float(arr.max())
    if hi == lo:
        return [0.0] * len(values)
    return ((arr - lo) / (hi - lo)).tolist()
""".strip(),
        "tests": [
            {"args": [[0, 5, 10]], "expected": [0.0, 0.5, 1.0]},
            {"args": [[7, 7, 7]], "expected": [0.0, 0.0, 0.0]},
            {"args": [[]], "expected": []},
            {"args": [[3, 1, 2]], "expected": [1.0, 0.0, 0.5]},
        ],
        "benchmark": {"args": [list(range(20000))]},
    },
    {
        "name": "moving_average",
        "category": "vectorization",
        "technique": "Maintain a running sum (O(1) per step) instead of re-summing the "
                     "whole window (O(k) per step).",
        "description": "Return the sliding window means of size k for values (length n-k+1).",
        "complexity_before": "O(n * k) time, O(n) space",
        "complexity_after": "O(n) time, O(n) space",
        "unoptimized": """
def moving_average(values, k):
    out = []
    for i in range(len(values) - k + 1):
        total = 0
        for j in range(i, i + k):
            total += values[j]
        out.append(total / k)
    return out
""".strip(),
        "optimized": """
def moving_average(values, k):
    if k <= 0 or k > len(values):
        return []
    out = []
    total = sum(values[:k])
    out.append(total / k)
    for i in range(k, len(values)):
        total += values[i] - values[i - k]
        out.append(total / k)
    return out
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4, 5], 3], "expected": [2.0, 3.0, 4.0]},
            {"args": [[1, 2, 3], 1], "expected": [1.0, 2.0, 3.0]},
            {"args": [[10], 1], "expected": [10.0]},
            {"args": [[1, 2], 5], "expected": []},
        ],
        "benchmark": {"args": [list(range(10000)), 100]},
    },
    {
        "name": "matmul",
        "category": "vectorization",
        "technique": "Multiply two matrices with the BLAS-backed np.dot instead of a Python "
                     "triple loop over every row, column, and inner index.",
        "description": "Return the matrix product A @ B of two equal-size square matrices.",
        "complexity_before": "O(n^3) time (Python loop), O(n^2) space",
        "complexity_after": "O(n^3) time (BLAS), O(n^2) space",
        "unoptimized": """
def matmul(A, B):
    n = len(A)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        for k in range(n):
            a = Ai[k]
            Bk = B[k]
            for j in range(n):
                out[i][j] += a * Bk[j]
    return out
""".strip(),
        "optimized": """
import numpy as np

def matmul(A, B):
    return np.dot(np.asarray(A, dtype=float), np.asarray(B, dtype=float)).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3, 4]], [[5, 6], [7, 8]]], "expected": [[19.0, 22.0], [43.0, 50.0]]},
            {"args": [[[1]], [[2]]], "expected": [[2.0]]},
            {"args": [[[1, 0], [0, 1]], [[2, 3], [4, 5]]], "expected": [[2.0, 3.0], [4.0, 5.0]]},
        ],
        "benchmark": {"args": [[[(i * j) % 11 for j in range(160)] for i in range(160)],
                              [[(i + j) % 13 for j in range(160)] for i in range(160)]]},
    },
    {
        "name": "z_scores",
        "category": "vectorization",
        "technique": "Compute the z-scores with vectorized mean/std and one expression "
                     "instead of three Python passes over the data.",
        "description": "Return the z-scores (x - mean) / population_std of values; all-equal values map to 0.0.",
        "complexity_before": "O(n) time (Python loops), O(n) space",
        "complexity_after": "O(n) time (vectorized), O(n) space",
        "unoptimized": """
def z_scores(values):
    n = len(values)
    if n == 0:
        return []
    mean = 0
    for v in values:
        mean += v
    mean /= n
    var = 0
    for v in values:
        var += (v - mean) ** 2
    var /= n
    sd = var ** 0.5
    out = []
    for v in values:
        if sd == 0:
            out.append(0.0)
        else:
            out.append((v - mean) / sd)
    return out
""".strip(),
        "optimized": """
import numpy as np

def z_scores(values):
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return []
    mean = float(arr.mean())
    sd = float(arr.std())
    if sd == 0:
        return [0.0] * len(values)
    return ((arr - mean) / sd).tolist()
""".strip(),
        "tests": [
            {"args": [[2, 2, 2]], "expected": [0.0, 0.0, 0.0]},
            {"args": [[]], "expected": []},
            {"args": [[1, 3]], "expected": [-1.0, 1.0]},
        ],
        "benchmark": {"args": [list(range(10000))]},
    },
    {
        "name": "pairwise_abs_sum",
        "category": "vectorization",
        "technique": "Sum all pairwise absolute differences with a vectorized broadcast "
                     "(O(n^2) in C) instead of a Python double loop (O(n^2) in Python).",
        "description": "Return the sum of |x[i] - x[j]| over all pairs with i < j.",
        "complexity_before": "O(n^2) time (Python loop), O(1) space",
        "complexity_after": "O(n^2) time (vectorized), O(n^2) space",
        "unoptimized": """
def pairwise_abs_sum(xs):
    total = 0.0
    n = len(xs)
    for i in range(n):
        xi = xs[i]
        for j in range(i + 1, n):
            d = xi - xs[j]
            total += d if d >= 0 else -d
    return total
""".strip(),
        "optimized": """
import numpy as np

def pairwise_abs_sum(xs):
    a = np.asarray(xs, dtype=float)
    return float(np.abs(a[:, None] - a[None, :]).sum()) / 2.0
""".strip(),
        "tests": [
            {"args": [[1, 2, 3]], "expected": 4.0},
            {"args": [[5]], "expected": 0.0},
            {"args": [[1.0, 4.0, 2.0]], "expected": 6.0},
            {"args": [[]], "expected": 0.0},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 / 10.0 for i in range(1200)]]},
    },
    {
        "name": "convolve_valid",
        "category": "vectorization",
        "technique": "Run the convolution with the C-implemented np.convolve instead of a "
                     "Python double loop over every window and kernel tap.",
        "description": "Return the valid-mode convolution of 1-D sequence a with kernel k (length len(a)-len(k)+1).",
        "complexity_before": "O(n * m) time (Python loop), O(n) space",
        "complexity_after": "O(n * m) time (vectorized), O(n) space",
        "unoptimized": """
def convolve_valid(a, kernel):
    n = len(a)
    m = len(kernel)
    out = []
    for i in range(n - m + 1):
        s = 0
        for j in range(m):
            s += a[i + j] * kernel[m - 1 - j]
        out.append(s)
    return out
""".strip(),
        "optimized": """
import numpy as np

def convolve_valid(a, kernel):
    return np.convolve(np.asarray(a, dtype=float),
                       np.asarray(kernel, dtype=float), mode="valid").tolist()
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4], [1, 1]], "expected": [3.0, 5.0, 7.0]},
            {"args": [[1, 2, 3, 4], [1, 2, 1]], "expected": [8.0, 12.0]},
            {"args": [[1, 2], [1]], "expected": [1.0, 2.0]},
            {"args": [[5], [2]], "expected": [10.0]},
        ],
        "benchmark": {"args": [[i % 10 for i in range(20000)], [1] * 51]},
    },
    {
        "name": "gram_matrix",
        "category": "vectorization",
        "technique": "Compute X @ X.T with one BLAS call instead of a Python triple loop "
                     "over every row pair and feature.",
        "description": "Return the Gram matrix G of row matrix X, where G[i][j] is the dot product of rows i and j.",
        "complexity_before": "O(n^2 * d) time (Python loop), O(n^2) space",
        "complexity_after": "O(n^2 * d) time (BLAS), O(n^2) space",
        "unoptimized": """
def gram_matrix(X):
    n = len(X)
    d = len(X[0]) if n else 0
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(d):
                s += X[i][k] * X[j][k]
            out[i][j] = s
    return out
""".strip(),
        "optimized": """
import numpy as np

def gram_matrix(X):
    A = np.asarray(X, dtype=float)
    return np.dot(A, A.T).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3, 4]]], "expected": [[5.0, 11.0], [11.0, 25.0]]},
            {"args": [[[1, 0], [0, 1]]], "expected": [[1.0, 0.0], [0.0, 1.0]]},
            {"args": [[[2]]], "expected": [[4.0]]},
        ],
        "benchmark": {"args": [[[(i * j) % 13 for j in range(30)] for i in range(300)]]},
    },
    {
        "name": "polynomial_features",
        "category": "vectorization",
        "technique": "Broadcast values against the power vector in one NumPy expression "
                     "instead of computing every power in a Python nested loop.",
        "description": "For each x in values return [x**1, x**2, ..., x**degree] as a row of the output matrix.",
        "complexity_before": "O(n * degree) time (Python loop), O(n * degree) space",
        "complexity_after": "O(n * degree) time (vectorized), O(n * degree) space",
        "unoptimized": """
def polynomial_features(values, degree):
    out = []
    for x in values:
        row = []
        for p in range(1, degree + 1):
            row.append(x ** p)
        out.append(row)
    return out
""".strip(),
        "optimized": """
import numpy as np

def polynomial_features(values, degree):
    x = np.asarray(values, dtype=float)
    powers = np.arange(1, degree + 1)
    return (x[:, None] ** powers[None, :]).tolist()
""".strip(),
        "tests": [
            {"args": [[1, 2, 3], 3], "expected": [[1.0, 1.0, 1.0], [2.0, 4.0, 8.0], [3.0, 9.0, 27.0]]},
            {"args": [[2], 1], "expected": [[2.0]]},
            {"args": [[2], 0], "expected": [[]]},
            {"args": [[], 3], "expected": []},
        ],
        "benchmark": {"args": [list(range(2000)), 50]},
    },
    {
        "name": "sliding_window_variance",
        "category": "vectorization",
        "technique": "Compute every window's variance with a vectorized sliding-window "
                     "view instead of re-slicing and re-summing each window in Python.",
        "description": "Return the population variance of every contiguous window of length k (length n-k+1).",
        "complexity_before": "O(n * k) time (Python loop), O(n) space",
        "complexity_after": "O(n * k) time (vectorized), O(n * k) space",
        "unoptimized": """
def sliding_window_variance(values, k):
    out = []
    for i in range(len(values) - k + 1):
        window = values[i:i + k]
        mean = sum(window) / k
        var = sum((x - mean) ** 2 for x in window) / k
        out.append(var)
    return out
""".strip(),
        "optimized": """
import numpy as np

def sliding_window_variance(values, k):
    if k <= 0 or k > len(values):
        return []
    arr = np.asarray(values, dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(arr, k)
    return windows.var(axis=1).tolist()
""".strip(),
        "tests": [
            {"args": [[1, 2, 3, 4, 5], 2], "expected": [0.25, 0.25, 0.25, 0.25]},
            {"args": [[1, 2, 3], 1], "expected": [0.0, 0.0, 0.0]},
            {"args": [[2, 2, 2], 2], "expected": [0.0, 0.0]},
            {"args": [[1, 2], 5], "expected": []},
        ],
        "benchmark": {"args": [list(range(20000)), 50]},
    },
    {
        "name": "pairwise_sq_distances",
        "category": "vectorization",
        "technique": "Broadcast points against each other and sum over the feature axis "
                     "in C instead of a Python triple loop.",
        "description": "Return matrix D where D[i][j] is the squared Euclidean distance between points[i] and points[j].",
        "complexity_before": "O(n^2 * d) time (Python loop), O(n^2) space",
        "complexity_after": "O(n^2 * d) time (vectorized), O(n^2 * d) space",
        "unoptimized": """
def pairwise_sq_distances(points):
    n = len(points)
    d = len(points[0]) if n else 0
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(d):
                diff = points[i][k] - points[j][k]
                s += diff * diff
            out[i][j] = s
    return out
""".strip(),
        "optimized": """
import numpy as np

def pairwise_sq_distances(points):
    X = np.asarray(points, dtype=float)
    return ((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=-1).tolist()
""".strip(),
        "tests": [
            {"args": [[[0, 0], [3, 4]]], "expected": [[0.0, 25.0], [25.0, 0.0]]},
            {"args": [[[1], [2], [4]]], "expected": [[0.0, 1.0, 9.0], [1.0, 0.0, 4.0], [9.0, 4.0, 0.0]]},
            {"args": [[[2]]], "expected": [[0.0]]},
        ],
        "benchmark": {"args": [[[(i * j) % 17 for j in range(3)] for i in range(250)]]},
    },
    {
        "name": "pairwise_manhattan_sum",
        "category": "vectorization",
        "technique": "Broadcast the values against each other and sum absolute "
                     "differences in C instead of a Python double loop.",
        "description": "Return the sum of absolute differences over all unordered pairs of values.",
        "complexity_before": "O(n^2) time (Python loop), O(1) space",
        "complexity_after": "O(n^2) time (vectorized), O(n^2) space",
        "unoptimized": """
def pairwise_manhattan_sum(values):
    total = 0
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            total += abs(values[i] - values[j])
    return total
""".strip(),
        "optimized": """
import numpy as np

def pairwise_manhattan_sum(values):
    x = np.asarray(values, dtype=float)
    diff = np.abs(x[:, None] - x[None, :])
    return float(diff.sum() / 2)
""".strip(),
        "tests": [
            {"args": [[1, 2, 3]], "expected": 4},
            {"args": [[5]], "expected": 0},
            {"args": [[1, 1]], "expected": 0},
            {"args": [[0, 2, 4]], "expected": 8},
        ],
        "benchmark": {"args": [[(i * 37) % 1000 for i in range(1500)]]},
    },
    {
        "name": "image_convolve_2d",
        "category": "vectorization",
        "technique": "Extract all sliding windows with a strided view and contract them "
                     "against the flipped kernel with einsum instead of four nested Python loops.",
        "description": "Return the valid 2-D convolution of image with a square kernel (no padding).",
        "complexity_before": "O(m * n * k^2) time (Python loops), O(m * n) space",
        "complexity_after": "O(m * n * k^2) time (vectorized), O(m * n * k^2) view space",
        "unoptimized": """
def image_convolve_2d(image, kernel):
    rows = len(image)
    cols = len(image[0])
    k = len(kernel)
    out_rows = rows - k + 1
    out_cols = cols - k + 1
    out = []
    for i in range(out_rows):
        row = []
        for j in range(out_cols):
            total = 0
            for ki in range(k):
                for kj in range(k):
                    total += image[i + ki][j + kj] * kernel[k - 1 - ki][k - 1 - kj]
            row.append(total)
        out.append(row)
    return out
""".strip(),
        "optimized": """
import numpy as np

def image_convolve_2d(image, kernel):
    img = np.asarray(image, dtype=float)
    ker = np.asarray(kernel, dtype=float)
    k = ker.shape[0]
    windows = np.lib.stride_tricks.sliding_window_view(img, (k, k))
    return np.einsum("ijkl,kl->ij", windows, ker[::-1, ::-1]).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3, 4]], [[1]]], "expected": [[1.0, 2.0], [3.0, 4.0]]},
            {"args": [[[1, 2], [3, 4]], [[1, 0], [0, 1]]], "expected": [[5.0]]},
            {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[1, 1], [1, 1]]], "expected": [[12.0, 16.0], [24.0, 28.0]]},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(300)] for i in range(300)],
                               [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6], [3, 4, 5, 6, 7], [4, 5, 6, 7, 8], [5, 6, 7, 8, 9]]]},
    },
    {
        "name": "k_means_assign",
        "category": "vectorization",
        "technique": "Broadcast every point against every center and take argmin in C "
                     "instead of a Python triple loop.",
        "description": "Return the index of the nearest center (squared Euclidean distance, ties to lowest index) for each point.",
        "complexity_before": "O(n * k * d) time (Python loop), O(1) space",
        "complexity_after": "O(n * k * d) time (vectorized), O(n * k) space",
        "unoptimized": """
def k_means_assign(points, centers):
    if not centers:
        return []
    assignments = []
    for point in points:
        best = None
        best_index = 0
        for c_index, center in enumerate(centers):
            dist = 0
            for k in range(len(point)):
                diff = point[k] - center[k]
                dist += diff * diff
            if best is None or dist < best:
                best = dist
                best_index = c_index
        assignments.append(best_index)
    return assignments
""".strip(),
        "optimized": """
import numpy as np

def k_means_assign(points, centers):
    if not points or not centers:
        return []
    X = np.asarray(points, dtype=float)
    C = np.asarray(centers, dtype=float)
    distances = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
    return distances.argmin(axis=1).tolist()
""".strip(),
        "tests": [
            {"args": [[[0, 0], [10, 10]], [[0, 0], [10, 10]]], "expected": [0, 1]},
            {"args": [[[1, 1], [9, 9], [5, 5]], [[0, 0], [10, 10]]], "expected": [0, 1, 0]},
            {"args": [[[2, 2]], [[0, 0], [1, 1], [3, 3]]], "expected": [1]},
            {"args": [[[1, 1]], []], "expected": []},
            {"args": [[], [[0, 0]]], "expected": []},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(3)] for i in range(3000)],
                               [[(c * 17 + j * 23) % 100 for j in range(3)] for c in range(12)]]},
    },
    {
        "name": "pairwise_cosine_similarity",
        "category": "vectorization",
        "technique": "Normalize rows once and multiply with BLAS instead of computing "
                     "every dot product in a Python triple loop.",
        "description": "Return the matrix of pairwise cosine similarities between the rows of X (zero rows have similarity 0).",
        "complexity_before": "O(n^2 * d) time (Python loop), O(n^2) space",
        "complexity_after": "O(n^2 * d) time (BLAS), O(n^2) space",
        "unoptimized": """
def pairwise_cosine_similarity(X):
    n = len(X)
    d = len(X[0]) if n else 0
    norms = []
    for i in range(n):
        s = 0
        for k in range(d):
            s += X[i][k] * X[i][k]
        norms.append(s ** 0.5)
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dot = 0
            for k in range(d):
                dot += X[i][k] * X[j][k]
            denom = norms[i] * norms[j]
            out[i][j] = dot / denom if denom else 0.0
    return out
""".strip(),
        "optimized": """
import numpy as np

def pairwise_cosine_similarity(X):
    if not X:
        return []
    A = np.asarray(X, dtype=float)
    norms = np.linalg.norm(A, axis=1, keepdims=True)
    safe = np.where(norms == 0, 1.0, norms)
    normalized = A / safe
    return (normalized @ normalized.T).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 0], [0, 1]]], "expected": [[1.0, 0.0], [0.0, 1.0]]},
            {"args": [[[1, 0], [1, 0]]], "expected": [[1.0, 1.0], [1.0, 1.0]]},
            {"args": [[[0, 0], [1, 0]]], "expected": [[0.0, 0.0], [0.0, 1.0]]},
            {"args": [[[2, 0], [0, 3]]], "expected": [[1.0, 0.0], [0.0, 1.0]]},
            {"args": [[[0, 0]]], "expected": [[0.0]]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(10)] for i in range(300)]]},
    },
    {
        "name": "covariance_matrix",
        "category": "vectorization",
        "technique": "Center the data and use a matrix product with BLAS instead of "
                     "accumulating every covariance entry in a Python triple loop.",
        "description": "Return the population covariance matrix of the rows of X (0 rows for empty input).",
        "complexity_before": "O(n * d^2) time (Python loop), O(d^2) space",
        "complexity_after": "O(n * d^2) time (BLAS), O(n * d) space",
        "unoptimized": """
def covariance_matrix(X):
    n = len(X)
    d = len(X[0]) if n else 0
    means = []
    for k in range(d):
        total = 0
        for i in range(n):
            total += X[i][k]
        means.append(total / n)
    cov = [[0.0] * d for _ in range(d)]
    for i in range(n):
        for a in range(d):
            for b in range(d):
                cov[a][b] += (X[i][a] - means[a]) * (X[i][b] - means[b])
    for a in range(d):
        for b in range(d):
            cov[a][b] /= n
    return cov
""".strip(),
        "optimized": """
import numpy as np

def covariance_matrix(X):
    if not X:
        return []
    A = np.asarray(X, dtype=float)
    centered = A - A.mean(axis=0)
    return (centered.T @ centered / A.shape[0]).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2], [3, 4]]], "expected": [[1.0, 1.0], [1.0, 1.0]]},
            {"args": [[[1, 1], [1, 1]]], "expected": [[0.0, 0.0], [0.0, 0.0]]},
            {"args": [[[1], [2], [3]]], "expected": [[2 / 3]]},
            {"args": [[[1, 2]]], "expected": [[0.0, 0.0], [0.0, 0.0]]},
            {"args": [[]], "expected": []},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(20)] for i in range(2000)]]},
    },
    {
        "name": "convolve_full",
        "category": "vectorization",
        "technique": "Run the full convolution with the C-implemented np.convolve instead "
                     "of a Python double loop over every input/kernel pair.",
        "description": "Return the full-mode convolution of 1-D sequence a with kernel k (length len(a)+len(k)-1).",
        "complexity_before": "O(n * m) time (Python loop), O(n + m) space",
        "complexity_after": "O(n * m) time (vectorized), O(n + m) space",
        "unoptimized": """
def convolve_full(a, kernel):
    n = len(a)
    m = len(kernel)
    out = [0] * (n + m - 1)
    for i in range(n):
        for j in range(m):
            out[i + j] += a[i] * kernel[j]
    return out
""".strip(),
        "optimized": """
import numpy as np

def convolve_full(a, kernel):
    return np.convolve(np.asarray(a, dtype=float),
                       np.asarray(kernel, dtype=float), mode="full").tolist()
""".strip(),
        "tests": [
            {"args": [[1, 2, 3], [1, 1]], "expected": [1.0, 3.0, 5.0, 3.0]},
            {"args": [[1, 2, 3], [1, 2]], "expected": [1.0, 4.0, 7.0, 6.0]},
            {"args": [[1, 2], [1]], "expected": [1.0, 2.0]},
            {"args": [[5], [2]], "expected": [10.0]},
        ],
        "benchmark": {"args": [[i % 10 for i in range(20000)], [1] * 51]},
    },
    {
        "name": "pairwise_chebyshev_sum",
        "category": "vectorization",
        "technique": "Broadcast points against each other and take the max absolute "
                     "coordinate difference in C instead of a Python triple loop.",
        "description": "Return the sum of Chebyshev distances (max absolute coordinate difference) over all unordered pairs of points.",
        "complexity_before": "O(n^2 * d) time (Python loop), O(1) space",
        "complexity_after": "O(n^2 * d) time (vectorized), O(n^2 * d) space",
        "unoptimized": """
def pairwise_chebyshev_sum(points):
    total = 0
    n = len(points)
    d = len(points[0]) if n else 0
    for i in range(n):
        for j in range(i + 1, n):
            best = 0
            for k in range(d):
                diff = abs(points[i][k] - points[j][k])
                if diff > best:
                    best = diff
            total += best
    return total
""".strip(),
        "optimized": """
import numpy as np

def pairwise_chebyshev_sum(points):
    if not points:
        return 0.0
    X = np.asarray(points, dtype=float)
    diff = np.abs(X[:, None, :] - X[None, :, :])
    return float(diff.max(axis=2).sum() / 2)
""".strip(),
        "tests": [
            {"args": [[[0, 0], [3, 4]]], "expected": 4},
            {"args": [[[1, 1], [2, 5], [0, 0]]], "expected": 10},
            {"args": [[[2, 2]]], "expected": 0},
            {"args": [[[1, 1], [1, 1]]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(3)] for i in range(800)]]},
    },
    {
        "name": "histogram_counts",
        "category": "vectorization",
        "technique": "Use np.bincount to tally every bin in C instead of scanning the "
                     "values once per bin (O(n * bins)).",
        "description": "Return counts for bins 0..num_bins-1 over integer values in that range.",
        "complexity_before": "O(n * bins) time, O(bins) space",
        "complexity_after": "O(n + bins) time, O(bins) space",
        "unoptimized": """
def histogram_counts(values, num_bins):
    counts = [0] * num_bins
    for b in range(num_bins):
        for x in values:
            if x == b:
                counts[b] += 1
    return counts
""".strip(),
        "optimized": """
import numpy as np

def histogram_counts(values, num_bins):
    arr = np.asarray(values, dtype=int)
    counts = np.bincount(arr, minlength=num_bins)
    return counts[:num_bins].tolist()
""".strip(),
        "tests": [
            {"args": [[1, 3, 3, 0, 2], 4], "expected": [1, 1, 1, 2]},
            {"args": [[0, 0], 2], "expected": [2, 0]},
            {"args": [[2], 3], "expected": [0, 0, 1]},
            {"args": [[], 3], "expected": [0, 0, 0]},
        ],
        "benchmark": {"args": [[i % 100 for i in range(20000)], 100]},
    },
    {
        "name": "max_pool_2d",
        "category": "vectorization",
        "technique": "Reshape the image into non-overlapping blocks and reduce with "
                     "NumPy instead of four nested Python loops.",
        "description": "Return 2-D max pooling with a k by k kernel and stride k (floor dimensions).",
        "complexity_before": "O(m * n * k^2) time (Python loops), O(m * n) space",
        "complexity_after": "O(m * n) time (vectorized), O(m * n) space",
        "unoptimized": """
def max_pool_2d(image, k):
    rows = len(image)
    cols = len(image[0])
    out_rows = rows // k
    out_cols = cols // k
    out = []
    for i in range(out_rows):
        row = []
        for j in range(out_cols):
            best = image[i * k][j * k]
            for r in range(i * k, i * k + k):
                for c in range(j * k, j * k + k):
                    if image[r][c] > best:
                        best = image[r][c]
            row.append(best)
        out.append(row)
    return out
""".strip(),
        "optimized": """
import numpy as np

def max_pool_2d(image, k):
    arr = np.asarray(image, dtype=float)
    rows = (arr.shape[0] // k) * k
    cols = (arr.shape[1] // k) * k
    trimmed = arr[:rows, :cols]
    pooled = trimmed.reshape(rows // k, k, cols // k, k).max(axis=(1, 3))
    return pooled.tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], 2],
             "expected": [[6.0, 8.0], [14.0, 16.0]]},
            {"args": [[[1, 2], [3, 4]], 1], "expected": [[1.0, 2.0], [3.0, 4.0]]},
            {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2], "expected": [[5.0]]},
            {"args": [[[5]], 1], "expected": [[5.0]]},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(600)] for i in range(600)], 5]},
    },
    {
        "name": "batch_affine_transform",
        "category": "vectorization",
        "technique": "Use one matrix product plus a broadcast bias (BLAS) instead of a "
                     "Python triple loop over rows, outputs, and features.",
        "description": "Return X @ W + b for a batch of row vectors X.",
        "complexity_before": "O(n * d * m) time (Python loop), O(n * m) space",
        "complexity_after": "O(n * d * m) time (BLAS), O(n * m) space",
        "unoptimized": """
def batch_affine_transform(X, W, b):
    n = len(X)
    d = len(X[0]) if n else 0
    m = len(W[0]) if d else 0
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            total = b[j]
            for k in range(d):
                total += X[i][k] * W[k][j]
            row.append(total)
        out.append(row)
    return out
""".strip(),
        "optimized": """
import numpy as np

def batch_affine_transform(X, W, b):
    x = np.asarray(X, dtype=float)
    w = np.asarray(W, dtype=float)
    bias = np.asarray(b, dtype=float)
    return (x @ w + bias).tolist()
""".strip(),
        "tests": [
            {"args": [[[1, 2]], [[1, 0], [0, 1]], [10, 20]], "expected": [[11.0, 22.0]]},
            {"args": [[[1, 2], [3, 4]], [[1], [1]], [0]], "expected": [[3.0], [7.0]]},
            {"args": [[[0, 0]], [[1, 2], [3, 4]], [5, 6]], "expected": [[5.0, 6.0]]},
            {"args": [[[1]], [[2]], [3]], "expected": [[5.0]]},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 100 for j in range(50)] for i in range(500)],
                               [[(i * 17 + j * 23) % 100 for j in range(50)] for i in range(50)],
                               [i % 10 for i in range(50)]]},
    },
    {
        "name": "pairwise_hamming_sum",
        "category": "vectorization",
        "technique": "Broadcast binary vectors against each other and count differences "
                     "in C instead of a Python triple loop.",
        "description": "Return the sum of Hamming distances over all unordered pairs of binary vectors.",
        "complexity_before": "O(n^2 * d) time (Python loop), O(1) space",
        "complexity_after": "O(n^2 * d) time (vectorized), O(n^2 * d) space",
        "unoptimized": """
def pairwise_hamming_sum(vectors):
    total = 0
    n = len(vectors)
    for i in range(n):
        for j in range(i + 1, n):
            distance = 0
            for a, b in zip(vectors[i], vectors[j]):
                if a != b:
                    distance += 1
            total += distance
    return total
""".strip(),
        "optimized": """
import numpy as np

def pairwise_hamming_sum(vectors):
    if not vectors:
        return 0
    X = np.asarray(vectors, dtype=float)
    diff = (X[:, None, :] != X[None, :, :]).sum(axis=2)
    return int(diff.sum() // 2)
""".strip(),
        "tests": [
            {"args": [[[1, 0], [0, 1]]], "expected": 2},
            {"args": [[[1, 1], [1, 1], [0, 0]]], "expected": 4},
            {"args": [[[1, 0, 1]]], "expected": 0},
            {"args": [[[1, 0], [1, 0]]], "expected": 0},
            {"args": [[]], "expected": 0},
        ],
        "benchmark": {"args": [[[(i * 37 + j * 11) % 2 for j in range(10)] for i in range(600)]]},
    },
]
