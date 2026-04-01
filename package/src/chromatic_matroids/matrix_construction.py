from .generate_matroids_utils import schubert_matroid
from .setcompositions import SetComposition
from .stable_matroids_setcompositions import stable_matroids_setcompositions
from .generate_matroids_utils import generate_loopless_nested_matroids
from .generate_matroids_utils import generate_nested_matroids_doublechains

from itertools import chain, combinations, permutations

"""
This part of the package is dedicated to the construction of a matrix that 
establishes a mower bound for the rank of the chromatic function 
in the non commutative case
"""

def from_set_to_set_composition(input_set, d):
    """
    Converts a given set into a set composition based on construction from paper.

    This function takes an input set {s1 < s2 < ... < sk } and an integer `d`.
    Constructs the complement {t1 < ..  < tj } wrt the set {1, ..., d}
    output is the composition tj|...t2|t1 sk| ... |s1.

    Parameters:
    input_set (set): The input set to be converted. Contains integers from {1, ..., d}
    d (int): The integer defining the range [1, d] the set composition.

    Returns:
    SetComposition: The resulting set composition constructed from the input set and its complement.
    """
    complement_list = list(set(range(1, d + 1)) - set(input_set))
    complement_list.sort(reverse=True)
    input_list = list(input_set)
    input_list.sort(reverse=True)
    if not complement_list:
        return SetComposition([[a] for a in input_list])
    set_composition_constructor = [[a] for a in complement_list[:-1]] + [[complement_list[-1], input_list[0]]] + [[a] for a in input_list[1:]]
    return SetComposition(set_composition_constructor)


def generate_valid_subsets(d):
    """
    Generate collection of subsets of a given size `d` that are valid for the construction of a loopless Schubert matroid.

    This function generates all valid subsets of the set {1, 2, ..., d}.
    A subset is considered valid if it meets the following criteria:
    1. The full set {1, 2, ..., d} is always included.
    2. For any other subset, the maximum element in the subset is greater than the minimum element in its complement.

    Parameters:
    d (int): The size of the set to generate subsets from.

    Returns:
    list of tuples: A list of tuples, where each tuple is a valid subset of the set {1, 2, ..., d}.
    """
    answer = []
    for subset in combinations(range(1, d + 1), d):#We start by adding the full set
        answer.append(subset)
    for subset in chain.from_iterable(combinations(range(1, d + 1), r) for r in range(1, d)):
        maxSubset = max(subset)
        minComplement = min(set(range(1, d+1)) - set(subset))
        if minComplement < maxSubset:
            answer.append(subset)
    return answer


def generate_min_max_set_compositions(d):
    list_permutations = permutations(range(1, d + 1))
    return [min_max_set_composition(per) for per in list_permutations]


def min_max_set_composition(permutation):
    """
    Constructs a set composition from a given permutation of integers.

    This function takes a permutation of integers and constructs a set composition based on the construction 
    from the paper. The set composition is constructed by taking the first element of the permutation and 
    appending it to the first block, then taking the second element and appending it to the second block, and so on.
    This splits permutations on the descent positions.

    Parameters:
    permutation (tuple): The permutation of integers to construct the set composition from.

    Returns:
    SetComposition: The resulting set composition constructed from the given permutation.
    """
    set_composition_constructor = [[permutation[0]]]
    for i in range(1, len(permutation)):
        if permutation[i] > permutation[i - 1]:
            set_composition_constructor[-1].append(permutation[i])
        else:
            set_composition_constructor.append([permutation[i]])
    return SetComposition(set_composition_constructor)


def compute_conjecture_matrix(d):
    """
    Computes a matrix based on the conjecture involving set compositions and loopless nested matroids.
    Args:
        d (int): The dimension or parameter used to generate set compositions and loopless nested matroids.
    Returns:
        list of list of int: A matrix where each entry (i, j) is 1 if the j-th loopless nested matroid 
                             is stable with respect to the i-th set composition, otherwise 0.
    """
    set_list = generate_min_max_set_compositions(d)
    #for sc in set_list:
    #    print(sc)
    
    loopless_nested_matroids = generate_loopless_nested_matroids(d)
    #for M in loopless_nested_matroids:
    #    print(str(loopless_nested_matroids.index(M)) +  " - > " + str(M.bases_sets))
    
    matrix = [[0 for i in range(len(set_list))] for j in range(len(loopless_nested_matroids))]
    for j in range(len(loopless_nested_matroids)):
        M = loopless_nested_matroids[j]
        for i in range(len(set_list)):
            opi = set_list[i]
            #print("Checking if matroid is stable with respect to set composition ", opi) 
            #print(" Indices are " + str(i) + " and " + str(j))
            #print("Result is ", stable_matroids_setcompositions(M, opi))
            if stable_matroids_setcompositions(M, opi):
                matrix[j][i] = 1
    return matrix, set_list, generate_nested_matroids_doublechains(d)


def compute_lowerbound_matrix(d):
    """
    Computes a matrix representing the coefficient of Schubert matroids for some terms of the monomial basis.

    The function generates all valid subsets of the set {1, 2, ..., d}, sorts them according to 
    specific order described in the paper.
    To each valid subset corresponds a 
     - loopless Schubert matroid (indexing the row of the matrid) 
     - a set composition (indexing the column of the matrix)
    This function constructs a matrix where each entry (i, j) is 1 if the corresponding schubert matroid
    is stable with respect to the set composition corresponding to j.

    Args:
        d (int): The size of the set {1, 2, ..., d} from which subsets are generated.

    Returns:
        list of list of int: A square matrix where each entry (i, j) is 1 if the matroid corresponding 
                             to subset i is stable with respect to the set composition of subset j, 
                             and 0 otherwise.
    """
    set_list = generate_valid_subsets(d)
    set_list.sort(key=lambda x: (len(x), [a for a in sorted(x)]))
    matrix = [[0 for i in range(len(set_list))] for j in range(len(set_list))]
    for A in set_list:
        matroid = schubert_matroid(d, A)
        for B in set_list:
            set_composition = from_set_to_set_composition(B, d)
            if stable_matroids_setcompositions(matroid, set_composition):
                matrix[set_list.index(A)][set_list.index(B)] = 1
    return matrix




def compute_conjecture_alternatingsum_matrix(d):
    """
    Computes a matrix based on the conjecture involving alternating sums of set compositions and loopless nested matroids.
    Args:
        d (int): The dimension or parameter used to generate set compositions and loopless nested matroids.
    Returns:
        list of list of int: A matrix where each entry (i, j) is 1 if the j-th loopless nested matroid 
                             is stable with respect to the i-th set composition, otherwise 0.
    """
    perm_list = list(permutations(range(1, d + 1)))
    
    generate_set_composition_list_from_permutation_precompute = {perm: generate_set_composition_list_from_permutation(perm) for perm in perm_list}
    loopless_nested_matroids = generate_loopless_nested_matroids(d)
    
    matrix = [[0 for i in range(len(perm_list))] for j in range(len(loopless_nested_matroids))]
    for j in range(len(loopless_nested_matroids)):
        M = loopless_nested_matroids[j]
        for i in range(len(perm_list)):
            perm = perm_list[i]
            for opi, rk in generate_set_composition_list_from_permutation_precompute[perm]:
                if stable_matroids_setcompositions(M, opi):
                    matrix[j][i] += (-1)**rk
    return matrix, perm_list, generate_nested_matroids_doublechains(d)


def compute_conjecture_big_matrix(d):
    """
    Computes a matrix involving all set compositions and loopless nested matroids. This is conjectured to have full rank.
    Args:
        d (int): The dimension or parameter used to generate set compositions and loopless nested matroids.
    Returns:
        list of list of int: A matrix where each entry (i, j) is 1 if the j-th loopless nested matroid 
                             is stable with respect to the i-th set composition, otherwise 0.
    """
    set_list = SetComposition.generate_all_setcompositions(d)
    loopless_nested_matroids = generate_loopless_nested_matroids(d)
    
    matrix = [[0 for i in range(len(set_list))] for j in range(len(loopless_nested_matroids))]
    for j in range(len(loopless_nested_matroids)):
        M = loopless_nested_matroids[j]
        for i in range(len(set_list)):
            opi = set_list[i]
            if stable_matroids_setcompositions(M, opi):
                matrix[j][i] = 1
    return matrix, set_list, generate_nested_matroids_doublechains(d)

def generate_set_composition_list_from_permutation(perm):
    """
    Generates set composition list from a given permutation.

    This function generates set compositions from a given permutation of integers.
    The set compositions are constructed by taking the first element of the permutation and 
    appending it to the first block, then taking the second element and appending it to the second block, and so on.
    This splits permutations on the descent positions.

    Parameters:
    perm (tuple): The permutation of integers to generate set compositions from.

    Returns:
    list of tuple: A list of tuples, where each tuple is a set composition constructed from the given permutation.
    """
    if len(perm) == 0:
        return []
    result_blocks = [[[perm[0]]]]
    for i in range(1, len(perm)):
        new_result_blocks = []
        for blocks in result_blocks:
            new_result_blocks.append(blocks + [[perm[i]]])
            new_result_blocks.append(blocks[:-1] + [blocks[-1] + [perm[i]]])
        result_blocks = new_result_blocks[:]
    return [(SetComposition(blocks), len(blocks)) for blocks in result_blocks]
