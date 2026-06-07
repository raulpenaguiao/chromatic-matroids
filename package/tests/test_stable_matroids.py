import pytest
from chromatic_matroids import stable_matroids_setcompositions, uniform_matroid, SetComposition, schubert_matroid


def test_u21_stable_21():
    m = uniform_matroid(2, 1)
    sc = SetComposition([[2], [1]])
    assert stable_matroids_setcompositions(m, sc) == True


def test_u21_stable_12():
    m = uniform_matroid(2, 1)
    sc = SetComposition([[1], [2]])
    assert stable_matroids_setcompositions(m, sc) == True


def test_u21_not_stable_single_block():
    m = uniform_matroid(2, 1)
    sc = SetComposition([[1, 2]])
    # single block: all bases get score 0, not unique
    assert stable_matroids_setcompositions(m, sc) == False


def test_u32_not_stable_single_block():
    m = uniform_matroid(3, 2)
    sc = SetComposition([[1, 2, 3]])
    assert stable_matroids_setcompositions(m, sc) == False


def test_stable_gives_bool():
    m = uniform_matroid(2, 1)
    sc = SetComposition([[1], [2]])
    result = stable_matroids_setcompositions(m, sc)
    assert isinstance(result, bool)


def test_u11_stable_for_its_single_element():
    m = uniform_matroid(1, 1)
    sc = SetComposition([[1]])
    # Only one basis {1}, score is always 0, unique maximizer → stable
    assert stable_matroids_setcompositions(m, sc) == True


def test_schubert_stability():
    # sh(3, {1,2,3}) = free matroid with unique basis {1,2,3}
    m = schubert_matroid(3, frozenset([1, 2, 3]))
    # Any set composition on {1,2,3} is stable (unique basis always wins)
    for sc in [SetComposition([[1], [2], [3]]),
               SetComposition([[1, 2], [3]]),
               SetComposition([[1, 2, 3]])]:
        assert stable_matroids_setcompositions(m, sc) == True


def test_rank0_matroid():
    from chromatic_matroids import Matroid
    m = Matroid(frozenset([1, 2]), {frozenset()})
    sc = SetComposition([[1], [2]])
    # Only basis is {}, always unique maximizer
    assert stable_matroids_setcompositions(m, sc) == True
