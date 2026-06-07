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
    # Matroid characteristic polynomial of M(K_3): χ(M, q) = (q-1)(q-2) = q^2 - 3q + 2
    # (The graph chromatic polynomial P(K_3, q) = q·χ(M,q) = q(q-1)(q-2), which differs by a factor of q.)
    m = graphic_matroid([(1, 2), (1, 3), (2, 3)], {1, 2, 3})
    poly = compute_chromatic_polynomial(m)
    assert poly == [2, -3, 1]


def test_returns_list():
    p = compute_chromatic_polynomial(uniform_matroid(2, 1))
    assert isinstance(p, list)


def test_free_matroid_polynomial():
    # U(3,3): all subsets are independent, so r(A) = |A| for all A.
    # χ(q) = Σ_{A} (-1)^|A| q^{3-|A|} = (q-1)^3 = q^3 - 3q^2 + 3q - 1
    m = uniform_matroid(3, 3)
    poly = compute_chromatic_polynomial(m)
    assert poly == [-1, 3, -3, 1]
