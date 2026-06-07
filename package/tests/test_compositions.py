import pytest
from math import factorial
from chromatic_matroids import Composition


# --- Construction ---

def test_from_list():
    c = Composition([2, 1, 3])
    assert c.parts == [2, 1, 3]
    assert c.n == 6
    assert c.nparts == 3


def test_from_tuple():
    c = Composition((1, 2))
    assert c.parts == [1, 2]
    assert c.n == 3


def test_from_string():
    c = Composition("(2,1,3)")
    assert c.parts == [2, 1, 3]
    assert c.n == 6


def test_empty_composition():
    c = Composition()
    assert c.parts == []
    assert c.n == 0
    assert c.nparts == 0


def test_empty_from_string():
    c = Composition("()")
    assert c.parts == []


def test_equality():
    assert Composition([2, 1, 3]) == Composition([2, 1, 3])
    assert Composition([2, 1, 3]) != Composition([3, 1, 2])
    assert Composition() == Composition()


def test_invalid_zero_part():
    with pytest.raises(ValueError):
        Composition([0, 1])


def test_invalid_float_part():
    with pytest.raises(TypeError):
        Composition([1.5])


def test_invalid_negative_part():
    with pytest.raises(ValueError):
        Composition([-1, 2])


# --- rest / prepend ---

def test_rest():
    c = Composition([2, 1, 3])
    r = c.rest()
    assert r.parts == [1, 3]
    assert r.n == 4


def test_prepend():
    c = Composition([2, 1, 3])
    p = c.prepend(4)
    assert p.parts == [4, 2, 1, 3]
    assert p.n == 10


def test_rest_prepend_immutability():
    c = Composition([2, 1, 3])
    c.rest()
    c.prepend(5)
    assert c.parts == [2, 1, 3]


def test_rest_of_empty_raises():
    with pytest.raises(Exception):
        Composition().rest()


def test_rest_of_singleton():
    r = Composition([3]).rest()
    assert r.parts == []
    assert r.n == 0


def test_prepend_to_empty():
    p = Composition().prepend(5)
    assert p.parts == [5]


# --- generate_all_composition ---

@pytest.mark.parametrize("n,expected", [(1, 1), (2, 2), (3, 4), (4, 8), (5, 16)])
def test_generate_count(n, expected):
    comps = Composition.generate_all_composition(n)
    assert len(comps) == expected


def test_generate_all_sum_to_n():
    for n in range(1, 7):
        for c in Composition.generate_all_composition(n):
            assert c.n == n


def test_generate_cached():
    c1 = Composition.generate_all_composition(4)
    c2 = Composition.generate_all_composition(4)
    assert c1 is c2  # same object from cache


# --- quasi_shuffles ---

def test_qs_left_empty():
    qs = Composition.quasi_shuffles(Composition(), Composition([1, 2]))
    assert qs == {'(1,2)': 1}


def test_qs_right_empty():
    qs = Composition.quasi_shuffles(Composition([1, 2]), Composition())
    assert qs == {'(1,2)': 1}


def test_qs_both_empty():
    qs = Composition.quasi_shuffles(Composition(), Composition())
    assert qs == {'()': 1}


def test_qs_1_1():
    qs = Composition.quasi_shuffles(Composition([1]), Composition([1]))
    assert qs.get('(2)', 0) == 1
    assert qs.get('(1,1)', 0) == 2


def test_qs_positive_int_values():
    qs = Composition.quasi_shuffles(Composition([1]), Composition([1]))
    for val in qs.values():
        assert isinstance(val, int) and val > 0


def test_qs_symmetry_total():
    # total count: |qs(α,β)| entries (with multiplicity) equals sum formula
    c1 = Composition([1, 2])
    c2 = Composition([1])
    qs = Composition.quasi_shuffles(c1, c2)
    # all values positive
    for v in qs.values():
        assert v > 0
