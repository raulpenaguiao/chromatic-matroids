import pytest
import numpy as np
from math import factorial
from chromatic_matroids import (
    from_set_to_set_composition, generate_valid_subsets,
    compute_lowerbound_matrix, compute_conjecture_matrix,
    min_max_set_composition, generate_min_max_set_compositions,
    SetComposition,
)


# --- from_set_to_set_composition ---

def test_output_is_setcomposition():
    sc = from_set_to_set_composition({1, 3}, 4)
    assert isinstance(sc, SetComposition)


def test_ground_set_is_full():
    for d in [3, 4, 5]:
        sc = from_set_to_set_composition({1, 2}, d)
        assert set(sc.ground_set) == set(range(1, d + 1))


def test_full_set_input():
    sc = from_set_to_set_composition({1, 2, 3, 4}, 4)
    assert set(sc.ground_set) == {1, 2, 3, 4}


def test_singleton_input():
    sc = from_set_to_set_composition({3}, 4)
    assert set(sc.ground_set) == {1, 2, 3, 4}


# --- generate_valid_subsets ---

def test_valid_subsets_d3():
    vs = generate_valid_subsets(3)
    assert len(vs) == 5


def test_valid_subsets_full_set_included():
    for d in [2, 3, 4]:
        vs = generate_valid_subsets(d)
        full = tuple(range(1, d + 1))
        assert full in vs


def test_valid_subsets_d2():
    vs = generate_valid_subsets(2)
    assert len(vs) == 2  # {1,2} and {2}


# --- min_max_set_composition ---

def test_identity_permutation_single_block():
    sc = min_max_set_composition((1, 2, 3))
    assert len(sc.parts) == 1
    assert set(sc.ground_set) == {1, 2, 3}


def test_reverse_permutation_all_singletons():
    sc = min_max_set_composition((3, 2, 1))
    assert len(sc.parts) == 3


def test_one_descent():
    sc = min_max_set_composition((1, 3, 2))
    assert len(sc.parts) == 2
    assert set(sc.parts[0]) == {1, 3}
    assert sc.parts[1] == [2]


def test_returns_setcomposition():
    sc = min_max_set_composition((1, 2, 3))
    assert isinstance(sc, SetComposition)


# --- generate_min_max_set_compositions ---

@pytest.mark.parametrize("d", [2, 3, 4])
def test_count_equals_factorial(d):
    comps = generate_min_max_set_compositions(d)
    assert len(comps) == factorial(d)


def test_all_ground_sets_correct():
    for d in [2, 3]:
        for sc in generate_min_max_set_compositions(d):
            assert set(sc.ground_set) == set(range(1, d + 1))


# --- compute_lowerbound_matrix ---

@pytest.mark.parametrize("d", [2, 3, 4])
def test_lowerbound_matrix_is_square(d):
    m = compute_lowerbound_matrix(d)
    n = len(m)
    assert all(len(row) == n for row in m)


@pytest.mark.parametrize("d", [2, 3, 4])
def test_lowerbound_matrix_full_rank(d):
    m = compute_lowerbound_matrix(d)
    rank = np.linalg.matrix_rank(np.array(m, dtype=float))
    assert rank == len(m)


def test_lowerbound_entries_binary():
    m = compute_lowerbound_matrix(3)
    for row in m:
        for val in row:
            assert val in (0, 1)


# --- compute_conjecture_matrix ---

def test_conjecture_matrix_d3():
    matrix, set_list, chains = compute_conjecture_matrix(3)
    assert isinstance(matrix, list)
    assert len(matrix) > 0
    assert len(matrix[0]) == factorial(3)


def test_conjecture_matrix_entries_binary():
    matrix, _, _ = compute_conjecture_matrix(3)
    for row in matrix:
        for val in row:
            assert val in (0, 1)


def test_conjecture_matrix_row_count():
    from chromatic_matroids import generate_loopless_nested_matroids
    matrix, _, _ = compute_conjecture_matrix(3)
    assert len(matrix) == len(generate_loopless_nested_matroids(3))
