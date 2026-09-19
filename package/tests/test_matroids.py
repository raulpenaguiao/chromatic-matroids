import pytest
from chromatic_matroids import Matroid, uniform_matroid, schubert_matroid


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
#
# Nestedness is defined via *cyclic* flats forming a chain, not via *all*
# flats forming a chain (an earlier version of is_nested() checked the
# latter, stricter condition, which is false in general for nested
# matroids -- see the module docstring of is_nested and the cyclic_flats /
# flats tests below).

def test_u32_is_nested(u32):
    # All uniform matroids are nested (they are exactly the k=1 double chains);
    # U(3,2)'s only cyclic flats are {} and the ground set.
    assert u32.is_nested() == True


def test_u31_is_nested():
    assert uniform_matroid(3, 1).is_nested() == True


def test_u11_is_nested():
    assert uniform_matroid(1, 1).is_nested() == True


def test_rank0_is_nested():
    m = Matroid(frozenset([1, 2]), {frozenset()})
    assert m.is_nested() == True


def test_schubert_sm24_is_nested():
    # SM({2,4}) on [4]: cyclic flats {}, {3,4}, {1,2,3,4} form a chain, so it
    # is nested, even though its flats {1} and {2} are incomparable.
    m = schubert_matroid(4, frozenset([2, 4]))
    assert m.is_nested() == True


# --- flats / cyclic_flats / loops ---

def test_flats_u32(u32):
    flats = {frozenset(f) for f in u32.flats()}
    assert flats == {frozenset(), frozenset([1]), frozenset([2]), frozenset([3]),
                      frozenset([1, 2, 3])}


def test_cyclic_flats_u32(u32):
    cflats = {frozenset(f) for f in u32.cyclic_flats()}
    assert cflats == {frozenset(), frozenset([1, 2, 3])}


def test_flats_and_cyclic_flats_sm24():
    m = schubert_matroid(4, frozenset([2, 4]))
    flats = {frozenset(f) for f in m.flats()}
    assert flats == {frozenset(), frozenset([1]), frozenset([2]),
                      frozenset([3, 4]), frozenset([1, 2, 3, 4])}
    cflats = {frozenset(f) for f in m.cyclic_flats()}
    assert cflats == {frozenset(), frozenset([3, 4]), frozenset([1, 2, 3, 4])}


def test_loops_of_loopless_matroid(u32):
    assert u32.loops() == frozenset()


def test_loops_of_schubert_matroid_with_loops():
    # SM({1}) on [3]: only 1 can be in a basis, so 2 and 3 are loops.
    m = schubert_matroid(3, frozenset([1]))
    assert m.loops() == frozenset([2, 3])


def test_loops_rank0_matroid():
    m = Matroid(frozenset([1, 2]), {frozenset()})
    assert m.loops() == frozenset([1, 2])


# --- restriction / contraction / minor ---

def test_restriction_bases():
    # SM({2,4}) on [4] restricted to {3,4} should be U(1,2) (rank 1, both bases size 1)
    m = schubert_matroid(4, frozenset([2, 4]))
    r = m.restriction(frozenset([3, 4]))
    assert r.ground_set == frozenset([3, 4])
    assert r.bases_sets == {frozenset([3]), frozenset([4])}


def test_restriction_uses_maximum_size_intersections():
    # U(1,2) on {1,2} restricted to {1}: bases are {1} and {2}; only the
    # maximum-size intersection with {1} (namely {1} itself) should survive,
    # not the size-0 intersection {2} \\cap {1} = {}.
    m = uniform_matroid(2, 1)
    r = m.restriction(frozenset([1]))
    assert r.bases_sets == {frozenset([1])}


def test_contraction_rank():
    m = schubert_matroid(4, frozenset([2, 4]))
    c = m.contraction(frozenset([1]))
    assert c.ground_set == frozenset([2, 3, 4])
    assert c.rank(c.ground_set) == m.rank(m.ground_set) - m.rank(frozenset([1]))


def test_minor_matches_restriction_then_contraction():
    m = schubert_matroid(4, frozenset([2, 4]))
    Fi, Fim1 = frozenset([1, 2, 3]), frozenset([1])
    minor = m.minor(Fi, Fim1)
    expected = m.restriction(Fi).contraction(Fim1)
    assert minor.ground_set == expected.ground_set
    assert minor.bases_sets == expected.bases_sets


def test_minor_along_complete_flag_of_flats_is_loopless_rank1():
    # For SM({2,4}) on [4], the flag {} < {1} < [4] is a complete flag of
    # flats (rank 2), so both successive minors should be loopless of rank 1.
    m = schubert_matroid(4, frozenset([2, 4]))
    n1 = m.minor(frozenset([1]), frozenset())
    n2 = m.minor(frozenset([1, 2, 3, 4]), frozenset([1]))
    assert n1.rank(n1.ground_set) == 1 and n1.loops() == frozenset()
    assert n2.rank(n2.ground_set) == 1 and n2.loops() == frozenset()


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
