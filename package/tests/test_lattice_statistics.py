import pytest
from math import factorial
from chromatic_matroids import (
    uniform_matroid,
    generate_loopless_nested_matroids,
    smith_normal_form_factors,
    z_rank,
    z_index,
    invariant_factors,
)


# ── smith_normal_form_factors (raw SNF on integer matrices) ───────────────────

def test_snf_empty():
    assert smith_normal_form_factors([]) == []


def test_snf_identity_2x2():
    assert smith_normal_form_factors([[1, 0], [0, 1]]) == [1, 1]


def test_snf_diagonal_coprime():
    # [[2,0],[0,3]]: D_1 = gcd(2,0,0,3) = 1, D_2 = det = 6 → factors [1, 6]
    assert smith_normal_form_factors([[2, 0], [0, 3]]) == [1, 6]


def test_snf_rank_deficient_row():
    # [[2,3],[4,6]]: second row = 2 × first; rank 1; gcd of entries = 1 → [1]
    assert smith_normal_form_factors([[2, 3], [4, 6]]) == [1]


def test_snf_single_row_01():
    # A single 0/1 row always has gcd 1 → index 1
    assert smith_normal_form_factors([[1, 0, 1, 0, 1]]) == [1]


def test_snf_single_row_scaled():
    # Scaled row: gcd of entries = k
    assert smith_normal_form_factors([[6, 4]]) == [2]


def test_snf_product_equals_det_for_square():
    # For a square full-rank matrix, product of SNF factors = |det|
    A = [[3, 1], [2, 5]]
    # det = 15 - 2 = 13
    factors = smith_normal_form_factors(A)
    product = 1
    for f in factors:
        product *= f
    assert product == 13


def test_snf_factors_divide_each_other():
    # Invariant factors must satisfy d_1 | d_2 | ... | d_r
    A = [[6, 0, 0], [0, 10, 0], [0, 0, 15]]
    factors = smith_normal_form_factors(A)
    for i in range(len(factors) - 1):
        assert factors[i + 1] % factors[i] == 0


def test_snf_numpy_array_input():
    import numpy as np
    A = np.array([[2, 0], [0, 3]])
    assert smith_normal_form_factors(A) == [1, 6]


# ── z_rank ────────────────────────────────────────────────────────────────────

def test_z_rank_empty():
    assert z_rank([]) == 0


def test_z_rank_single_matroid():
    assert z_rank([uniform_matroid(2, 1)]) == 1


@pytest.mark.parametrize("d", [2, 3, 4])
def test_z_rank_loopless_nested_equals_factorial(d):
    matroids = generate_loopless_nested_matroids(d)
    assert z_rank(matroids) == factorial(d)


def test_z_rank_repeated_matroid():
    m = uniform_matroid(3, 2)
    # Two copies of the same matroid span only 1 dimension
    assert z_rank([m, m]) == 1


# ── invariant_factors ─────────────────────────────────────────────────────────

def test_invariant_factors_length_equals_z_rank():
    matroids = generate_loopless_nested_matroids(3)
    assert len(invariant_factors(matroids)) == z_rank(matroids)


def test_invariant_factors_all_positive():
    matroids = generate_loopless_nested_matroids(3)
    for d in invariant_factors(matroids):
        assert d > 0


def test_invariant_factors_divide_each_other():
    matroids = generate_loopless_nested_matroids(3)
    fs = invariant_factors(matroids)
    for i in range(len(fs) - 1):
        assert fs[i + 1] % fs[i] == 0


def test_invariant_factors_single_matroid_is_one():
    # WQSym of a single matroid is a 0/1 vector; gcd of entries = 1
    assert invariant_factors([uniform_matroid(3, 2)]) == [1]


# ── z_index ───────────────────────────────────────────────────────────────────

def test_z_index_empty():
    assert z_index([]) == 1


def test_z_index_single_matroid():
    # Single 0/1 WQSym vector is always saturated
    assert z_index([uniform_matroid(3, 2)]) == 1


def test_z_index_at_least_one():
    matroids = generate_loopless_nested_matroids(3)
    assert z_index(matroids) >= 1


def test_z_index_equals_product_of_invariant_factors():
    matroids = generate_loopless_nested_matroids(3)
    fs = invariant_factors(matroids)
    expected = 1
    for f in fs:
        expected *= f
    assert z_index(matroids) == expected
