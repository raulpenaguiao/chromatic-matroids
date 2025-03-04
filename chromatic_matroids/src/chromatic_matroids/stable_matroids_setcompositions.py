# matroid_chromatic/stable_matroids_setcompositions.py
from matroid_chromatic import Matroid
from matroid_chromatic import SetComposition

def stable_matroids_setcompositions(matroid: Matroid, opi: SetComposition) -> bool:
    """
    Check if a set composition is stable with respect to a matroid
    """
    scores = [sum([len([i for i in pi if i in base])*index for index, pi in enumerate(opi.parts)]) for base in matroid.bases_sets]
    return scores.count(max(scores)) == 1


