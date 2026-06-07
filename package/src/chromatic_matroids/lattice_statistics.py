"""
Lattice-theoretic statistics of the WQSym image of a collection of matroids.

Given matroids M_1, ..., M_k let
    M = Z-span{WQSym(M_1), ..., WQSym(M_k)} ⊆ Z^N
where N = |{WQSym basis elements that appear}|.

The Smith Normal Form of the (k × N) coefficient matrix A decomposes A as
    A = U D V
with U (k × k) and V (N × N) unimodular integer matrices and
    D = diag(d_1, d_2, ..., d_r, 0, ..., 0),  d_1 | d_2 | ... | d_r > 0.

This gives the complete Z-module structure:
    Z^N / M  ≅  Z^(N-r)  ⊕  Z/d_1  ⊕  ...  ⊕  Z/d_r

Key quantities exported here:
    z_rank(matroids)         — r, the rank of M as a free abelian group
    invariant_factors(matroids) — [d_1, ..., d_r] from the SNF
    z_index(matroids)        — d_1 · d_2 · ... · d_r = [sat(M) : M]

The saturation sat(M) = {x ∈ Z^N : cx ∈ M for some c > 0} is the largest
subgroup of Z^N containing M with finite index; z_index = 1 iff M is saturated.
"""

import numpy as np
from .chromatic_statistics_matorids import chromatic_non_commutative_quasisymmetric_function


def smith_normal_form_factors(A):
    """Nonzero invariant factors of the Smith Normal Form of integer matrix A.

    A may be a list of lists or a 2-D numpy integer array.
    Returns a list [d_1, ..., d_r] sorted so that d_1 | d_2 | ... | d_r,
    all positive.  Their product equals the index [sat(M) : M] where M is
    the Z-span of the rows of A.

    The algorithm applies alternating integer row / column Euclidean reductions
    (no division, no floating point) until the matrix is diagonal, then checks
    the divisibility condition and repairs it if needed by absorbing rows.
    """
    if hasattr(A, "tolist"):
        rows = [list(map(int, row)) for row in A.tolist()]
    else:
        rows = [list(map(int, row)) for row in A]
    m = len(rows)
    if not m:
        return []
    n = len(rows[0])
    factors = []
    pivot = 0
    while pivot < min(m, n):
        # Find the minimum nonzero |entry| in the active sub-matrix
        best_val, best_pos = None, None
        for i in range(pivot, m):
            for j in range(pivot, n):
                v = rows[i][j]
                if v and (best_val is None or abs(v) < abs(best_val)):
                    best_val, best_pos = v, (i, j)
        if best_pos is None:
            break
        pi, pj = best_pos
        # Move the smallest entry to the (pivot, pivot) position
        rows[pivot], rows[pi] = rows[pi], rows[pivot]
        for row in rows:
            row[pivot], row[pj] = row[pj], row[pivot]
        while True:
            # Euclidean-reduce the pivot column (entries below pivot row → 0)
            changed = True
            while changed:
                changed = False
                for i in range(pivot + 1, m):
                    if rows[i][pivot] == 0:
                        continue
                    q = rows[i][pivot] // rows[pivot][pivot]
                    rows[i] = [rows[i][k] - q * rows[pivot][k] for k in range(n)]
                    if rows[i][pivot]:          # remainder is a new smaller pivot
                        rows[pivot], rows[i] = rows[i], rows[pivot]
                    changed = True
                    break                       # restart with updated pivot row
            # Euclidean-reduce the pivot row (entries right of pivot col → 0)
            changed = True
            while changed:
                changed = False
                for j in range(pivot + 1, n):
                    if rows[pivot][j] == 0:
                        continue
                    q = rows[pivot][j] // rows[pivot][pivot]
                    for i in range(m):
                        rows[i][j] -= q * rows[i][pivot]
                    if rows[pivot][j]:          # remainder is a new smaller pivot
                        for i in range(m):
                            rows[i][pivot], rows[i][j] = rows[i][j], rows[i][pivot]
                    changed = True
                    break
            # Verify: the pivot must divide every entry in the remaining sub-matrix.
            # If not, absorb the offending row into the pivot row and repeat.
            p = rows[pivot][pivot]
            bad = next(
                ((i, j) for i in range(pivot + 1, m)
                 for j in range(pivot + 1, n)
                 if rows[i][j] % p),
                None,
            )
            if bad is None:
                break
            bi, _ = bad
            rows[pivot] = [rows[pivot][k] + rows[bi][k] for k in range(n)]
        if rows[pivot][pivot]:
            factors.append(abs(rows[pivot][pivot]))
        pivot += 1
    return sorted(factors)


def _wqsym_coefficient_matrix(matroids):
    """Build the (k × N) WQSym coefficient matrix for a list of matroids."""
    funcs = [chromatic_non_commutative_quasisymmetric_function(m) for m in matroids]
    keys = sorted({k for f in funcs for k in f.coefficients})
    mat = [[f.coefficients.get(k, 0) for k in keys] for f in funcs]
    return mat, keys


def z_rank(matroids):
    """Z-rank of the WQSym span of a list of matroids.

    Equals the Q-dimension of span_Q{WQSym(M) : M in matroids}, computed as
    the rank of the integer coefficient matrix over Q (via numpy).
    """
    mat, _ = _wqsym_coefficient_matrix(matroids)
    if not mat:
        return 0
    return int(np.linalg.matrix_rank(np.array(mat, dtype=float)))


def invariant_factors(matroids):
    """Invariant factors [d_1, ..., d_r] of the Smith Normal Form of the
    WQSym coefficient matrix, sorted so that d_1 | d_2 | ... | d_r > 0.

    The number of factors r equals the Z-rank.
    Their product equals the Z-index (index of the span in its saturation).
    """
    mat, _ = _wqsym_coefficient_matrix(matroids)
    return smith_normal_form_factors(mat)


def z_index(matroids):
    """Index [sat(M) : M] where M = Z-span{WQSym(M_i)}.

    sat(M) = { x ∈ Z^N : c·x ∈ M for some positive integer c }.
    Equals the product of the Smith Normal Form invariant factors.
    z_index = 1 iff the Z-span is already saturated.
    """
    result = 1
    for d in invariant_factors(matroids):
        result *= d
    return result
