# matroid_chromatic/chromatic.py
from itertools import combinations
from .matroids import Matroid


def compute_chromatic_polynomial(matroid: Matroid) -> list:
    """
    Compute the characteristic (chromatic) polynomial of a matroid.

    Uses the subset-expansion formula:

        χ(M, q) = Σ_{A ⊆ E} (-1)^|A| · q^(r(E) - r(A))

    where E is the ground set, r is the rank function of M, and the sum
    ranges over all subsets A of E (including the empty set).

    The result is returned as a list of integer coefficients ``[c_0, c_1, ..., c_r]``
    such that χ(M, q) = c_0 + c_1·q + c_2·q² + ... + c_r·q^r, where r = rank(M).

    Examples
    --------
    For the uniform matroid U(2,1) the polynomial is q − 1::

        compute_chromatic_polynomial(uniform_matroid(2, 1)) == [-1, 1]

    For U(3,2) the polynomial is q² − 3q + 2 = (q−1)(q−2)::

        compute_chromatic_polynomial(uniform_matroid(3, 2)) == [2, -3, 1]

    Args:
        matroid (Matroid): A valid matroid object.

    Returns:
        list[int]: Coefficient list ``[c_0, ..., c_r]`` where ``c_k`` is the
                   coefficient of ``q^k`` in χ(M, q).
    """
    ground_list = list(matroid.ground_set)
    n = len(ground_list)
    rank = matroid.rank(matroid.ground_set)

    result = [0] * (rank + 1)

    for size in range(n + 1):
        sign = (-1) ** size
        for subset_tuple in combinations(ground_list, size):
            subset = frozenset(subset_tuple)
            exponent = rank - matroid.rank(subset)
            result[exponent] += sign

    return result
