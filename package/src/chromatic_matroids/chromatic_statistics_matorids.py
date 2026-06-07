# matroid_chromatic/chromatic_statistics_matorids.py
import numpy as np
from .matroids import Matroid
from .setcompositions import SetComposition
from .compositions import Composition
from .quasisymmetric import QSymFunction
from .ncquasisymmetric import NCQSymFunction
from .stable_matroids_setcompositions import stable_matroids_setcompositions


def chromatic_quasisymmetric_function(matroid: Matroid) -> QSymFunction:
    return NCQSymFunction.comu(chromatic_non_commutative_quasisymmetric_function(matroid))


def chromatic_non_commutative_quasisymmetric_function(matroid: Matroid) -> NCQSymFunction:
    """
    Vectorised computation via numpy.

    Score of basis B under set-composition π is  Σ_{e∈B} π_index(e).
    Build:
      A  (|bases| × n) – indicator: A[i,j] = 1 iff ground[j] ∈ basis_i
      C  (Bell(n) × n) – coloring:  C[k,j] = part-index of canonical element j+1 in sc_k
    Then  scores = A @ C.T  and sc_k is stable iff its column has a unique maximum.
    """
    ground = sorted(matroid.ground_set)
    n = len(ground)
    if n == 0:
        return NCQSymFunction()

    elem_col = {e: i for i, e in enumerate(ground)}   # ground element → column index

    # ── Basis matrix A ────────────────────────────────────────────────────────
    bases_list = list(matroid.bases_sets)
    nb = len(bases_list)
    if nb == 0:
        return NCQSymFunction()

    A = np.zeros((nb, n), dtype=np.int32)
    for i, basis in enumerate(bases_list):
        for e in basis:
            A[i, elem_col[e]] = 1

    # ── Coloring matrix C ────────────────────────────────────────────────────
    # generate_all_setcompositions(n) returns scs on canonical labels {1,...,n}
    all_scs = SetComposition.generate_all_setcompositions(n)
    K = len(all_scs)

    C = np.zeros((K, n), dtype=np.int32)
    for k, sc in enumerate(all_scs):
        for idx, part in enumerate(sc.parts):
            for canon_elem in part:          # canon_elem ∈ {1,...,n}
                C[k, canon_elem - 1] = idx

    # ── Batch scores and stability check ────────────────────────────────────
    scores = A @ C.T                                  # (nb, K)
    col_max = scores.max(axis=0, keepdims=True)       # (1,  K)
    stable_mask = (scores == col_max).sum(axis=0) == 1  # (K,)

    # ── Build NCQSym function ─────────────────────────────────────────────
    relabeling = {i + 1: ground[i] for i in range(n)}
    coeffs = {
        str(all_scs[k].relabel(relabeling)): 1
        for k in np.where(stable_mask)[0]
    }
    return NCQSymFunction(monomial_basis=coeffs)
