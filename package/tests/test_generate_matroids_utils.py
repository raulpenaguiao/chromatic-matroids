import pytest
from math import comb
from chromatic_matroids import (
    uniform_matroid, schubert_matroid, nested_matroid, graphic_matroid,
    generate_schubert_matroids, generate_loopless_schubert_matroids,
    generate_loopless_nested_matroids, generate_nested_matroids_doublechains,
)


# --- uniform_matroid ---

@pytest.mark.parametrize("n,r", [(3, 0), (3, 1), (3, 2), (3, 3), (4, 2), (5, 3)])
def test_uniform_basis_count(n, r):
    m = uniform_matroid(n, r)
    assert len(m.bases_sets) == comb(n, r)


@pytest.mark.parametrize("n,r", [(3, 0), (3, 1), (3, 2), (3, 3)])
def test_uniform_ground_set(n, r):
    m = uniform_matroid(n, r)
    assert m.ground_set == frozenset(range(1, n + 1))


@pytest.mark.parametrize("n,r", [(3, 0), (3, 1), (3, 2), (3, 3)])
def test_uniform_rank(n, r):
    m = uniform_matroid(n, r)
    assert m.rank(m.ground_set) == r


@pytest.mark.parametrize("n,r", [(-1, 0), (3, 4), (3, -1)])
def test_uniform_invalid_raises(n, r):
    with pytest.raises(Exception):
        uniform_matroid(n, r)


# --- schubert_matroid ---

def test_schubert_bases():
    sch = schubert_matroid(4, frozenset([2, 3]))
    expected = {frozenset({1, 2}), frozenset({1, 3}), frozenset({2, 3})}
    assert sch.bases_sets == expected


def test_schubert_full_set():
    sch = schubert_matroid(3, frozenset([1, 2, 3]))
    assert sch.bases_sets == frozenset({frozenset({1, 2, 3})})


def test_schubert_rank():
    sch = schubert_matroid(4, frozenset([2, 3]))
    assert sch.rank(sch.ground_set) == 2


def test_generate_schubert_count():
    all_sch = generate_schubert_matroids(3)
    assert len(all_sch) == 2 ** 3


def test_generate_loopless_schubert_subset():
    loopless = generate_loopless_schubert_matroids(3)
    all_sch = generate_schubert_matroids(3)
    assert len(loopless) <= len(all_sch)
    assert len(loopless) > 0


def test_generate_loopless_schubert_no_loops():
    for m in generate_loopless_schubert_matroids(4):
        # a loopless matroid has rank({e}) >= 1 for all e
        for e in m.ground_set:
            assert m.rank(frozenset([e])) >= 1


# --- nested_matroid ---

def test_nested_single_level_is_uniform():
    m = nested_matroid(3, 2, (frozenset([1, 2, 3]),), (2,))
    expected = {frozenset({1, 2}), frozenset({1, 3}), frozenset({2, 3})}
    assert m.bases_sets == expected


def test_nested_two_levels():
    m = nested_matroid(4, 2, (frozenset([1, 2]), frozenset([1, 2, 3, 4])), (1, 2))
    for b in m.bases_sets:
        assert len(b & frozenset([1, 2])) <= 1


def test_generate_loopless_nested_count():
    assert len(generate_loopless_nested_matroids(3)) == 6


def test_generate_loopless_nested_no_loops():
    for m in generate_loopless_nested_matroids(4):
        for e in m.ground_set:
            assert m.rank(frozenset([e])) >= 1


def test_generate_nested_doublechains_type():
    chains = generate_nested_matroids_doublechains(3)
    assert isinstance(chains, list)
    assert len(chains) == len(generate_loopless_nested_matroids(3))


# --- graphic_matroid ---

def test_k3_rank(k3):
    assert k3.rank(k3.ground_set) == 2


def test_k3_spanning_trees(k3):
    assert len(k3.bases_sets) == 3


def test_path_p3():
    m = graphic_matroid([(1, 2), (2, 3)], {1, 2, 3})
    assert m.rank(m.ground_set) == 2
    assert len(m.bases_sets) == 1


def test_single_edge():
    m = graphic_matroid([(1, 2)], {1, 2})
    assert m.rank(m.ground_set) == 1
    assert len(m.bases_sets) == 1


def test_disconnected_graph():
    # Two isolated edges: no spanning tree covers both components — rank = |V| - components = 4 - 2 = 2
    m = graphic_matroid([(1, 2), (3, 4)], {1, 2, 3, 4})
    assert m.rank(m.ground_set) == 2
