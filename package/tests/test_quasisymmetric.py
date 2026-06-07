import pytest
from chromatic_matroids import QSymFunction, Composition


# --- Construction ---

def test_from_composition():
    q = QSymFunction(monomial_basis=Composition([2, 1]))
    assert q.coefficients == {'(2,1)': 1}


def test_from_tuple():
    q = QSymFunction(monomial_basis=(Composition([1, 3, 2]), -3))
    assert q.coefficients == {'(1,3,2)': -3}


def test_from_dict():
    q = QSymFunction(monomial_basis={'(1,2)': 2, '(3,1)': -1})
    assert q.coefficients == {'(1,2)': 2, '(3,1)': -1}


def test_zero_no_arg():
    q = QSymFunction()
    assert q.coefficients == {}


def test_zero_none():
    q = QSymFunction(monomial_basis=None)
    assert q.coefficients == {}


# --- Addition ---

def test_addition():
    q1 = QSymFunction(monomial_basis=Composition([1, 2]))
    q2 = QSymFunction(monomial_basis=Composition([2, 1]))
    result = q1 + q2
    assert result.coefficients == {'(1,2)': 1, '(2,1)': 1}


def test_addition_immutability():
    q1 = QSymFunction(monomial_basis=Composition([1, 2]))
    q2 = QSymFunction(monomial_basis=Composition([2, 1]))
    _ = q1 + q2
    assert q1.coefficients == {'(1,2)': 1}
    assert q2.coefficients == {'(2,1)': 1}


def test_addition_same_term():
    q = QSymFunction(monomial_basis=Composition([1, 2]))
    result = q + q
    assert result.coefficients == {'(1,2)': 2}
    assert q.coefficients == {'(1,2)': 1}


def test_addition_cancellation():
    q = QSymFunction(monomial_basis={'(1,2)': 3})
    neg_q = QSymFunction(monomial_basis={'(1,2)': -3})
    result = q + neg_q
    assert result.coefficients.get('(1,2)', 0) == 0


def test_add_zero():
    q = QSymFunction(monomial_basis=Composition([1, 2]))
    zero = QSymFunction()
    assert (q + zero).coefficients == q.coefficients


# --- Scalar multiplication ---

def test_scalar_multiple():
    q = QSymFunction(monomial_basis=Composition([1, 2]))
    result = q._scalarMultiple(5)
    assert result.coefficients == {'(1,2)': 5}


def test_scalar_multiple_immutability():
    q = QSymFunction(monomial_basis=Composition([1, 2]))
    q._scalarMultiple(5)
    assert q.coefficients == {'(1,2)': 1}


def test_scalar_zero():
    q = QSymFunction(monomial_basis={'(1,2)': 3})
    result = q._scalarMultiple(0)
    assert result.coefficients.get('(1,2)', 0) == 0


# --- Multiplication (quasi-shuffle product) ---

def test_multiplication_commutes_total_degree():
    q1 = QSymFunction(monomial_basis=Composition([1]))
    q2 = QSymFunction(monomial_basis=Composition([2]))
    product = q1 * q2
    # All terms in the product should have n = 1 + 2 = 3
    for key in product.coefficients:
        c = Composition(key)
        assert c.n == 3


def test_multiplication_immutability():
    q1 = QSymFunction(monomial_basis=Composition([1]))
    q2 = QSymFunction(monomial_basis=Composition([2]))
    _ = q1 * q2
    assert q1.coefficients == {'(1)': 1}
    assert q2.coefficients == {'(2)': 1}


def test_multiply_by_zero():
    q = QSymFunction(monomial_basis=Composition([1, 2]))
    zero = QSymFunction()
    result = q * zero
    assert result.coefficients == {}
