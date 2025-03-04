# matroid_chromatic/chromatic.py
from typing import Dict
from matroid_chromatic import Matroid



def compute_chromatic_noncommutative_qsym_function(matroid: Matroid) -> dict:
    """
    Compute the non commutative qsym function as a dictionary that matches a 
    """



def compute_chromatic_polynomial(matroid: Matroid) -> list:
    """
    Compute the chromatic polynomial as a list of coefficients.
    
    Args:
        matroid: The matroid
    
    Returns:
        Value of chromatic polynomial at q
    """
    def mobius_function(X: frozenset, Y: frozenset) -> int:
        """Compute the Möbius function value."""
        if X == Y:
            return 1
        if not X.issubset(Y):
            return 0
        
        result = 0
        for Z in range_sets[len(X):len(Y)]:
            if X.issubset(Z) and Z.issubset(Y):
                result -= mobius_function(X, Z)
        return result
    
    # Generate all sets between empty set and ground set
    range_sets = []
    for i in range(len(matroid.ground_set) + 1):
        current_level = set()
        for ind_set in matroid.independent_sets():
            if len(ind_set) == i:
                current_level.add(ind_set)
        range_sets.append(current_level)
    
    # Compute chromatic polynomial using Möbius inversion
    result = [0 for _ in range(len(matroid.ground_set) + 1)]
    empty_set = frozenset()
    ground_set = frozenset(matroid.ground_set)
    
    for X in matroid.independent_sets():
        coeff = mobius_function(empty_set, X)
        result[len(X)] += coeff
    
    return result