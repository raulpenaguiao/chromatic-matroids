import pytest
from chromatic_matroids import NCQSymFunction, QSymFunction, SetComposition, Composition


# --- Construction ---

def test_from_setcomposition():
    sc = SetComposition([[1, 2], [3]])
    nc = NCQSymFunction(monomial_basis=sc)
    assert nc.coefficients == {'(1,2|3)': 1}


def test_from_string():
    nc = NCQSymFunction(monomial_basis="(1,2|3)")
    assert nc.coefficients == {'(1,2|3)': 1}


def test_from_dict():
    nc = NCQSymFunction(monomial_basis={'(1,2|3)': 2, '(1|2,3)': -1})
    assert nc.coefficients == {'(1,2|3)': 2, '(1|2,3)': -1}


def test_zero():
    nc = NCQSymFunction()
    assert nc.coefficients == {}



# --- Addition ---

def test_addition():
    nc1 = NCQSymFunction(monomial_basis="(1|2)")
    nc2 = NCQSymFunction(monomial_basis="(1,2)")
    result = nc1 + nc2
    assert result.coefficients == {'(1|2)': 1, '(1,2)': 1}


def test_addition_immutability():
    nc1 = NCQSymFunction(monomial_basis="(1|2)")
    nc2 = NCQSymFunction(monomial_basis="(1,2)")
    _ = nc1 + nc2
    assert nc1.coefficients == {'(1|2)': 1}
    assert nc2.coefficients == {'(1,2)': 1}


def test_addition_self_doubles():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    result = nc + nc
    assert result.coefficients == {'(1|2)': 2}
    assert nc.coefficients == {'(1|2)': 1}


def test_add_zero():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    result = nc + NCQSymFunction()
    assert result.coefficients == nc.coefficients


# --- Scalar multiplication ---

def test_scalar_multiple():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    result = nc._scalarMultiple(5)
    assert result.coefficients == {'(1|2)': 5}


def test_scalar_multiple_immutability():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    nc._scalarMultiple(5)
    assert nc.coefficients == {'(1|2)': 1}


# --- Multiplication ---

def test_product_quasi_shuffle():
    nc_a = NCQSymFunction(monomial_basis=SetComposition([[1]]))
    nc_b = NCQSymFunction(monomial_basis=SetComposition([[2]]))
    prod = nc_a * nc_b
    assert prod.coefficients.get('(1|2)', 0) == 1
    assert prod.coefficients.get('(2|1)', 0) == 1
    assert prod.coefficients.get('(1,2)', 0) == 1


def test_product_immutability():
    nc_a = NCQSymFunction(monomial_basis=SetComposition([[1]]))
    nc_b = NCQSymFunction(monomial_basis=SetComposition([[2]]))
    _ = nc_a * nc_b
    assert nc_a.coefficients == {'(1)': 1}
    assert nc_b.coefficients == {'(2)': 1}


def test_multiply_by_zero():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    result = nc * NCQSymFunction()
    assert result.coefficients == {}


# --- comu (forgetful map to QSym) ---

def test_comu_basic():
    nc = NCQSymFunction(monomial_basis=SetComposition([[1, 2], [3]]))
    q = nc.comu()
    assert isinstance(q, QSymFunction)
    # (1,2|3) maps to alpha = (2,1)
    assert q.coefficients.get('(2,1)', 0) == 1


def test_comu_two_terms():
    nc = NCQSymFunction(monomial_basis={'(2|1)': 1, '(1|2)': 1})
    q = nc.comu()
    # both map to alpha (1,1)
    assert q.coefficients.get('(1,1)', 0) == 2


def test_comu_immutability():
    nc = NCQSymFunction(monomial_basis="(1|2)")
    nc.comu()
    assert nc.coefficients == {'(1|2)': 1}
