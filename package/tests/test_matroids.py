import pytest
from chromatic_matroids import Matroid, uniform_matroid


# --- Construction & validation ---

def test_u32_constructs():
    m = Matroid(frozenset([1, 2, 3]), {frozenset([1, 2]), frozenset([1, 3]), frozenset([2, 3])})
    assert m.ground_set == frozenset({1, 2, 3})
    assert len(m.bases_sets) == 3


def test_rank0_empty_matroid():
    m = Matroid(frozenset(), {frozenset()})
    assert m.ground_set == frozenset()


def test_exchange_axiom_violation_raises():
    with pytest.raises(Exception):
        Matroid(frozenset([1, 2, 3]), {frozenset([1, 2]), frozenset([3])})


def test_empty_bases_raises():
    with pytest.raises(Exception):
        Matroid(frozenset([1]), set())


def test_single_basis():
    m = Matroid(frozenset([1, 2, 3]), {frozenset([1, 2, 3])})
    assert len(m.bases_sets) == 1
    assert m.rank(m.ground_set) == 3


# --- rank ---

def test_rank_ground_set(u32):
    assert u32.rank(u32.ground_set) == 2


def test_rank_basis(u32):
    assert u32.rank(frozenset([1, 2])) == 2


def test_rank_singleton(u32):
    assert u32.rank(frozenset([1])) == 1


def test_rank_empty(u32):
    assert u32.rank(frozenset()) == 0


def test_rank_zero_matroid():
    m = Matroid(frozenset([1, 2]), {frozenset()})
    assert m.rank(frozenset([1, 2])) == 0


def test_rank_monotone(u32):
    assert u32.rank(frozenset([1])) <= u32.rank(frozenset([1, 2]))
    assert u32.rank(frozenset([1, 2])) <= u32.rank(u32.ground_set)


# --- independent_sets ---

def test_empty_set_is_independent(u32):
    assert frozenset() in u32.independent_sets()


def test_singletons_independent(u32):
    for i in [1, 2, 3]:
        assert frozenset([i]) in u32.independent_sets()


def test_bases_are_independent(u32):
    ind = u32.independent_sets()
    for b in u32.bases_sets:
        assert b in ind


def test_ground_set_not_independent(u32):
    assert u32.ground_set not in u32.independent_sets()


def test_total_independent_sets_u32(u32):
    # U(3,2): {} + 3 singletons + 3 pairs = 7
    assert len(u32.independent_sets()) == 7


def test_independent_sets_u31():
    m = uniform_matroid(3, 1)
    ind = m.independent_sets()
    # U(3,1): {} + 3 singletons = 4
    assert len(ind) == 4


# --- is_nested ---

def test_u32_not_nested(u32):
    assert u32.is_nested() == False


def test_u31_is_nested():
    assert uniform_matroid(3, 1).is_nested() == True


def test_u11_is_nested():
    assert uniform_matroid(1, 1).is_nested() == True


def test_rank0_is_nested():
    m = Matroid(frozenset([1, 2]), {frozenset()})
    assert m.is_nested() == True


# --- extend (coloop) ---

def test_extend_adds_coloop(u21):
    ext = u21.extend(3)
    assert ext.ground_set == frozenset({1, 2, 3})
    assert ext.rank(ext.ground_set) == 2
    for b in ext.bases_sets:
        assert 3 in b


def test_extend_immutability(u21):
    u21.extend(3)
    assert u21.ground_set == frozenset({1, 2})


def test_extend_existing_element_raises(u21):
    with pytest.raises(Exception):
        u21.extend(1)


def test_extend_produces_valid_matroid(u21):
    ext = u21.extend(3)
    # constructor validates — if we get here it's valid
    assert len(ext.bases_sets) > 0


# --- relabel ---

def test_relabel_ground_set(u32):
    bij = {1: 10, 2: 20, 3: 30}
    m2 = u32.relabel(bij)
    assert m2.ground_set == frozenset({10, 20, 30})


def test_relabel_bases(u32):
    bij = {1: 10, 2: 20, 3: 30}
    m2 = u32.relabel(bij)
    assert frozenset({10, 20}) in m2.bases_sets
    assert frozenset({10, 30}) in m2.bases_sets
    assert frozenset({20, 30}) in m2.bases_sets


def test_relabel_immutability(u32):
    u32.relabel({1: 10, 2: 20, 3: 30})
    assert u32.ground_set == frozenset({1, 2, 3})
