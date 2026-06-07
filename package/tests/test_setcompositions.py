import pytest
from chromatic_matroids import SetComposition, Composition


# --- Construction ---

def test_from_list_of_lists():
    sc = SetComposition([[1, 4], [2], [3, 5, 6]])
    assert sc.parts == [[1, 4], [2], [3, 5, 6]]
    assert set(sc.ground_set) == {1, 2, 3, 4, 5, 6}


def test_from_string():
    sc = SetComposition("(1,4|2|3,5,6)")
    assert sc.parts == [[1, 4], [2], [3, 5, 6]]


def test_empty():
    sc = SetComposition()
    assert sc.parts == []


def test_non_disjoint_raises():
    with pytest.raises(Exception):
        SetComposition([[1, 2], [2, 3]])


def test_single_part():
    sc = SetComposition([[1, 2, 3]])
    assert len(sc.parts) == 1
    assert set(sc.ground_set) == {1, 2, 3}


# --- Equality ---

def test_equality():
    sc1 = SetComposition([[1, 2], [3]])
    sc2 = SetComposition([[1, 2], [3]])
    assert sc1 == sc2


def test_inequality_different_order():
    sc1 = SetComposition([[1, 2], [3]])
    sc2 = SetComposition([[3], [1, 2]])
    assert sc1 != sc2


def test_inequality_different_parts():
    sc1 = SetComposition([[1], [2, 3]])
    sc2 = SetComposition([[1, 2], [3]])
    assert sc1 != sc2


# --- first / rest / prepend / alpha ---

def test_first():
    sc = SetComposition([[1, 4], [2], [3]])
    assert sc.first() == frozenset([1, 4])


def test_first_empty_raises():
    with pytest.raises(Exception):
        SetComposition().first()


def test_rest():
    sc = SetComposition([[1, 4], [2], [3]])
    r = sc.rest()
    assert r.parts == [[2], [3]]


def test_rest_immutability():
    sc = SetComposition([[1], [2], [3]])
    sc.rest()
    assert sc.parts == [[1], [2], [3]]


def test_prepend():
    sc = SetComposition([[2], [3]])
    p = sc.prepend(frozenset([10, 11]))
    assert p.parts[0] == [10, 11] or set(p.parts[0]) == {10, 11}


def test_alpha():
    sc = SetComposition([[1, 4], [2], [3, 5, 6]])
    alpha = sc.alpha()
    assert isinstance(alpha, Composition)
    assert alpha.parts == [2, 1, 3]


def test_alpha_empty():
    assert SetComposition().alpha() == Composition()


# --- relabel ---

def test_relabel_dict():
    sc = SetComposition([[1, 2], [3]])
    sc2 = sc.relabel({1: 10, 2: 20, 3: 30})
    assert set(sc2.ground_set) == {10, 20, 30}


def test_relabel_none_standardises():
    sc = SetComposition([[3, 5], [1]])
    sc2 = sc.relabel(None)
    assert set(sc2.ground_set) == {1, 2, 3}


def test_relabel_immutability():
    sc = SetComposition([[1, 2], [3]])
    sc.relabel({1: 10, 2: 20, 3: 30})
    assert sc.parts == [[1, 2], [3]]


# --- generate_all_setcompositions ---

@pytest.mark.parametrize("n,expected", [(1, 1), (2, 3), (3, 13)])
def test_generate_count(n, expected):
    scs = SetComposition.generate_all_setcompositions(n)
    assert len(scs) == expected


def test_generate_ground_sets():
    for sc in SetComposition.generate_all_setcompositions(3):
        assert set(sc.ground_set) == {1, 2, 3}


def test_generate_cached():
    c1 = SetComposition.generate_all_setcompositions(3)
    c2 = SetComposition.generate_all_setcompositions(3)
    assert c1 is c2


# --- quasi_shuffles ---

def test_qs_disjoint():
    sc1 = SetComposition([[1, 2], [3, 4], [5]])
    sc2 = SetComposition([[31], [32, 33]])
    qs = SetComposition.quasi_shuffles(sc1, sc2)
    assert isinstance(qs, dict)
    assert len(qs) > 0
    for v in qs.values():
        assert isinstance(v, int) and v > 0


def test_qs_left_empty():
    sc = SetComposition([[1], [2]])
    qs = SetComposition.quasi_shuffles(SetComposition(), sc)
    assert len(qs) == 1


def test_qs_right_empty():
    sc = SetComposition([[1], [2]])
    qs = SetComposition.quasi_shuffles(sc, SetComposition())
    assert len(qs) == 1


def test_qs_ground_sets_in_result():
    sc1 = SetComposition([[1]])
    sc2 = SetComposition([[2]])
    qs = SetComposition.quasi_shuffles(sc1, sc2)
    # each result key's ground set must be {1,2}
    for key in qs:
        parsed = SetComposition(key)
        assert set(parsed.ground_set) == {1, 2}
