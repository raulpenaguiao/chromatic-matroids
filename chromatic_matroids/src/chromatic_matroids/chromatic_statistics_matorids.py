# matroid_chromatic/chromatic_statistics_matorids.py
from .matroids import Matroid
from .setcompositions import SetComposition
from .compositions import Composition
from .quasisymmetric import QSymFunction
from .ncquasisymmetric import NCQSymFunction
from .stable_matroids_setcompositions import stable_matroids_setcompositions

def chromatic_quasisymmetric_function(matroid: Matroid) -> QSymFunction:
    """
    Compute the chromatic quasisymmetric function of a matroid
    """
    return NCQSymFunction.comu(chromatic_non_commutative_quasisymmetric_function(matroid))


def chromatic_non_commutative_quasisymmetric_function(matroid: Matroid) -> NCQSymFunction:
    """
    Compute the chromatic non-commutative quasisymmetric function of a matroid
    """
    ground_list = list(matroid.ground_set)
    relabeling_map = {i+1: ground_list[i] for i in range(len(ground_list))}
    all_set_compositions = [opi.relabel(relabeling_map) for opi in SetComposition.generate_all_setcompositions(len(ground_list))]
    coeffs = {str(opi): 1 for opi in all_set_compositions
                if stable_matroids_setcompositions(matroid, opi)}
    return NCQSymFunction(monomial_basis=coeffs)


