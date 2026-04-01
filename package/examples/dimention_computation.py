# dimension_computation.py
import time
now = time.time()


from matroid_chromatic import generate_loopless_schubert_matroids, generate_loopless_nested_matroids
from matroid_chromatic import chromatic_quasisymmetric_function, chromatic_non_commutative_quasisymmetric_function
import numpy as np
import itertools
from math import factorial
from matroid_chromatic import SetComposition
from matroid_chromatic import Composition
from matroid_chromatic import NCQSymFunction, QSymFunction

def rank(list_of_symfuncy):
    set_coefs = set()
    for symfuncy in list_of_symfuncy:
        for key in symfuncy.coefficients:
            if not key in set_coefs:
                set_coefs.add(key)
    mat_coeffs = [[0 for _ in set_coefs] for _ in list_of_symfuncy]
    for i, symfuncy in enumerate(list_of_symfuncy):
        for j, key in enumerate(set_coefs):
            mat_coeffs[i][j] = symfuncy.coefficients.get(key, 0)
    return np.linalg.matrix_rank(mat_coeffs)


for d in range(2, 15):
    print("    creating loopless nested matroids")
    loopless_nested_d = generate_loopless_nested_matroids(d)
    
    print("    creating set compositions")
    setcompositions_d = SetComposition.generate_all_setcompositions(d)
    
    print("    creating possible bases")
    possible_bases = []
    for r in range(d+1):
        possible_bases += [frozenset(base) for base in itertools.combinations(range(1, d+1), r)]
    print("    initializing score table")
    scores = {base:[0 for _ in setcompositions_d] for base in possible_bases}

    print("    calculating scores")
    for sc_index, sc in enumerate(setcompositions_d):
        ground_set_score = {i:0 for i in range(1, d+1)}
        for index, part in enumerate(sc.parts):
            for i in part:
                ground_set_score[i] += index
        for base in possible_bases:
            score = 0
            for i in base:
                score += ground_set_score[i]
            scores[base][sc_index] = score
    
    print("    computing stable sc")
    ncqsym = [NCQSymFunction() for _ in loopless_nested_d]
    for matroid_index, matroid in enumerate(loopless_nested_d):
        matroid_basified = [frozenset(base) for base in matroid.bases_sets]
        #for base in matroid.bases_sets:

        #[base for base in possible_bases if base in matroid.bases_sets]
        for sc_index, sc in enumerate(setcompositions_d):
            if len(sc.alpha().parts) == d:
                ncqsym[matroid_index] += NCQSymFunction(monomial_basis = sc)
                continue
            scores_matroid = [scores[base][sc_index] for base in matroid_basified]
            m = max(scores_matroid)
            if scores_matroid.count(m) == 1:
                ncqsym[matroid_index] += NCQSymFunction(monomial_basis = sc)
    
    print(f"    computing ranks of matrices of size {len(setcompositions_d)}x{len(loopless_nested_d)}")
    qsym = [ncqsym_func.comu() for ncqsym_func in ncqsym]
    r = rank(qsym)
    print(f"rank of  qsym map for dimension {d}: {r} vs {2**(d-1)}")
    r = rank(ncqsym)
    print(f"rank of wqsym map for dimension {d}: {r} vs {factorial(d)}")
    print(f"time elapsed: {round(1000*(time.time() - now))/1000} seconds")
