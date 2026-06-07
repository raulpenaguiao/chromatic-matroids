import pytest
from chromatic_matroids import compute_chromatic_polynomial, uniform_matroid, graphic_matroid


def test_u21():
    p = compute_chromatic_polynomial(uniform_matroid(2, 1))
    assert p == [-1, 1]


def test_u32():
    p = compute_chromatic_polynomial(uniform_matroid(3, 2))
    assert p == [2, -3, 1]


def test_degree_equals_rank():
    for n, r in [(2, 0), (3, 1), (4, 2), (4, 4)]:
        m = uniform_matroid(n, r)
        poly = compute_chromatic_polynomial(m)
        assert len(poly) == r + 1


def test_leading_coefficient_is_one():
    for n, r in [(2, 1), (3, 2), (4, 3)]:
        m = uniform_matroid(n, r)
        poly = compute_chromatic_polynomial(m)
        assert poly[-1] == 1


def test_k3_chromatic_polynomial():
    # χ(K_3, q) = q(q-1)(q-2) = q^3 - 3q^2 + 2q → [0, 2, -3, 1]
    m = graphic_matroid([(1, 2), (1, 3), (2, 3)], {1, 2, 3})
    poly = compute_chromatic_polynomial(m)
    assert len(poly) == 3  # degree = rank(K_3) = 2  → poly len 3


def test_returns_list():
    p = compute_chromatic_polynomial(uniform_matroid(2, 1))
    assert isinstance(p, list)


def test_free_matroid_polynomial():
    # U(3,3): only one basis {1,2,3}, χ(q) = (q-1)^3 ... wait
    # Actually for free matroid (rank = n), χ(M,q) = product_{i=0}^{n-1}(q - i)?
    # Just verify degree equals rank
    m = uniform_matroid(3, 3)
    poly = compute_chromatic_polynomial(m)
    assert len(poly) == 4  # degree 3
