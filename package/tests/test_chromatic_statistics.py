import pytest
import numpy as np
from math import factorial
from chromatic_matroids import (
    uniform_matroid, generate_loopless_nested_matroids,
    chromatic_quasisymmetric_function, chromatic_non_commutative_quasisymmetric_function,
    NCQSymFunction, QSymFunction,
    z_rank,
)


# --- chromatic_non_commutative_quasisymmetric_function ---

def test_u21_ncqsym_terms(u21):
    nc = chromatic_non_commutative_quasisymmetric_function(u21)
    assert set(nc.coefficients.keys()) == {'(2|1)', '(1|2)'}
    assert nc.coefficients['(2|1)'] == 1
    assert nc.coefficients['(1|2)'] == 1


def test_u21_ncqsym_returns_ncqsym(u21):
    nc = chromatic_non_commutative_quasisymmetric_function(u21)
    assert isinstance(nc, NCQSymFunction)


def test_u11_ncqsym():
    m = uniform_matroid(1, 1)
    nc = chromatic_non_commutative_quasisymmetric_function(m)
    assert isinstance(nc, NCQSymFunction)
    assert len(nc.coefficients) >= 1


def test_ncqsym_coefficients_positive(u21):
    nc = chromatic_non_commutative_quasisymmetric_function(u21)
    for v in nc.coefficients.values():
        assert v > 0


def test_u32_ncqsym_terms(u32):
    # U(3,2): 9 stable set compositions, all with coefficient 1.
    # Each total order on {1,2,3} is stable (unique max-weight basis); the three
    # two-block set compositions with a singleton first block are also stable.
    nc = chromatic_non_commutative_quasisymmetric_function(u32)
    expected = {
        '(1|2|3)', '(1|3|2)', '(2|1|3)', '(2|3|1)', '(3|1|2)', '(3|2|1)',
        '(1|2,3)', '(2|1,3)', '(3|1,2)',
    }
    assert set(nc.coefficients.keys()) == expected
    for v in nc.coefficients.values():
        assert v == 1


# --- chromatic_quasisymmetric_function ---

def test_u21_qsym(u21):
    c = chromatic_quasisymmetric_function(u21)
    assert c.coefficients == {'(1,1)': 2}


def test_u32_qsym(u32):
    # U(3,2) QSym: 6 total orders (all stable) collapse under comu to (1,1,1) with coeff 6;
    # 3 two-block compositions collapse to (1,2) with coeff 3.
    c = chromatic_quasisymmetric_function(u32)
    assert c.coefficients == {'(1,1,1)': 6, '(1,2)': 3}


def test_u21_qsym_returns_qsym(u21):
    c = chromatic_quasisymmetric_function(u21)
    assert isinstance(c, QSymFunction)


def test_qsym_is_comu_of_ncqsym(u21):
    nc = chromatic_non_commutative_quasisymmetric_function(u21)
    qsym_via_comu = nc.comu()
    qsym_direct = chromatic_quasisymmetric_function(u21)
    assert qsym_via_comu.coefficients == qsym_direct.coefficients


# --- rank of chromatic map on loopless nested matroids ---

def _qsym_rank(matroids):
    """Local helper for QSym rank (z_rank covers WQSym; QSym needs its own matrix)."""
    funcs = [chromatic_quasisymmetric_function(m) for m in matroids]
    keys = sorted({k for f in funcs for k in f.coefficients})
    mat = [[f.coefficients.get(k, 0) for k in keys] for f in funcs]
    return int(np.linalg.matrix_rank(np.array(mat, dtype=float)))


@pytest.mark.parametrize("d", [2, 3, 4])
def test_ncqsym_rank_equals_factorial(d):
    matroids = generate_loopless_nested_matroids(d)
    assert z_rank(matroids) == factorial(d)


@pytest.mark.parametrize("d", [2, 3, 4])
def test_qsym_rank_equals_2_pow_d_minus_1(d):
    matroids = generate_loopless_nested_matroids(d)
    assert _qsym_rank(matroids) == 2 ** (d - 1)
