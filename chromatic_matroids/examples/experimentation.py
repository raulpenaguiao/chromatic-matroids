# example.py
from matroid_chromatic import Matroid, compute_chromatic_polynomial
from matroid_chromatic import uniform_matroid, schubert_matroid, nested_matroid
from matroid_chromatic import generate_schubert_matroids, generate_loopless_schubert_matroids, generate_loopless_nested_matroids
from matroid_chromatic import graphic_matroid, Composition, QSymFunction, SetComposition, NCQSymFunction
from matroid_chromatic import chromatic_quasisymmetric_function, chromatic_non_commutative_quasisymmetric_function
from matroid_chromatic import stable_matroids_setcompositions
import numpy as np

i = 4

loopless_nested_i = generate_loopless_nested_matroids(i)
wqsym = [chromatic_non_commutative_quasisymmetric_function(matroid) for matroid in loopless_nested_i]

set_coefs = set()
for symfuncy in wqsym:
    for key in symfuncy.coefficients:
        set_coefs.add(key)
mat_coeffs = [[0 for _ in set_coefs] for _ in wqsym]
for i, symfuncy in enumerate(wqsym):
    for j, key in enumerate(set_coefs):
        mat_coeffs[i][j] = symfuncy.coefficients.get(key, 0)

print( np.linalg.matrix_rank(mat_coeffs))
"""
for i in range(24):
    print(loopless_nested_i[i].bases_sets)
    print("i = ", i, " has rank = ",  np.linalg.matrix_rank(mat_coeffs[i:]))"""