# matroid_chromatic/utils.py
from typing import Set, List, Tuple
from matroid_chromatic import Matroid
from itertools import combinations
from matroid_chromatic.setcompositions import SetComposition

"""
Utility functions for creating various types of matroids.

This module provides functions to create uniform matroids, Schubert matroids,
nested matroids, and graphic matroids. Each function includes validation checks
to ensure the input parameters create valid matroids.
"""

def uniform_matroid(n: int, r: int) -> Matroid:
    """
    Create a uniform matroid U(n,r).

    A uniform matroid U(n,r) has ground set of size n and all subsets of size r
    as its bases.

    Args:
        n (int): Size of the ground set
        r (int): Rank of the matroid

    Returns:
        Matroid: A uniform matroid U(n,r)

    Raises:
        Exception: If n < 0, r < 0, or r > n
    """
    if n < 0 or r < 0 or r > n:
        raise Exception("Uniform matroid malformed: size or rank are not valid")
    ground_set = set(range(1, n+1))#make sure it is 1-indexed
    bases_sets = set([frozenset(comb) for comb in combinations(range(1,n+1), r)])
    return Matroid(ground_set, bases_sets)

def schubert_matroid(n: int, A: frozenset[int]) -> Matroid:
    """
    Create a Schubert matroid sh({1, ..., n}, A).

    A Schubert matroid is defined by a ground set {1, ..., n} and a subset A = {a1 < ... < ar}.
    A set B = {b1 < ... < br} is a basis if and only if bi ≤ ai for all i.

    Args:
        n (int): Size of the ground set
        A (frozenset[int]): Defining subset A = {a1 < ... < ar}

    Returns:
        Matroid: A Schubert matroid

    Raises:
        Exception: If any element of A is not in {1, ..., n}
    """
    ground_set = set(range(1, n+1))
    rank = len(A)
    
    for a in A:
        if a <= 0 or a > n:
            raise Exception("Schubert matroid is malformed")

    #make sure A is sorted
    Asorted = list(A)
    Asorted.sort()

    bases_sets = set()
    for B in combinations(range(1,n+1), rank):
        flag_B_smaller_than_A = True
        for a, b in zip(Asorted, B):
            if a < b:
                flag_B_smaller_than_A = False
                break
        if flag_B_smaller_than_A:
            bases_sets.add(frozenset(B))
    
    return Matroid(ground_set, bases_sets)

def generate_schubert_matroids(n: int) -> List[Matroid]:
    """
    Generate all Schubert matroids of rank n.
    """
    if n < 0:
        raise Exception("Invalid input")
    if n == 0:
        return [schubert_matroid(0, frozenset([]))]
    result = []
    for rank in range(0, n+1):
        for A in combinations(range(1,n+1), rank):
            result.append(schubert_matroid(n, frozenset(A)))
    return result

def generate_loopless_schubert_matroids(n: int) -> List[Matroid]:
    result = []
    for rank in range(0, n+1):
        for A in combinations(range(1,n), rank):
            result.append(schubert_matroid(n, frozenset(list(A) + [n])))
    return result

def nested_matroid(n: int, rank: int, X: tuple[frozenset[int]], R: tuple[int]) -> Matroid:
    """
    Create a nested matroid ne(n, r, X, R).

    A nested matroid is defined by:
    - A ground set of size n
    - A total rank r
    - A chain of sets X = (X₁ ⊂ X₂ ⊂ ... ⊂ Xₖ = {1,...,n})
    - A sequence of ranks R = (r₁ < r₂ < ... < rₖ = r)

    Args:
        n (int): Size of the ground set
        rank (int): Total rank of the matroid
        X (tuple[frozenset[int]]): Chain of nested sets
        R (tuple[int]): Corresponding ranks for each set in the chain

    Returns:
        Matroid: A nested matroid

    Raises:
        Exception: If:
            - The chain X is not strictly increasing
            - The last set in X is not equal to {1,...,n}
            - The ranks R are not strictly increasing
            - The lengths of X and R don't match
            - The last rank is not equal to the total rank
            - Any element in any set is not in {1,...,n}
    """
    ground_set = set(range(1,n+1))
    #Validate input
    if not ground_set == X[-1]:
        raise Exception("Nested matroid malformed: given chain is not valid")

    if rank > n or n < 0 or rank < 0:
        raise Exception("Nested matroid malformed: size or rank are not valid")

    if len(X) == 0 or len(X[0]) == 0:
        raise Exception("Nested matroid malformed: given chain does not have a valid first term")
    
    if not len(R) == len(X):
        raise Exception("Nested matroid malformed: given chains size don't match")
    k = len(X)

    if not R[-1] == rank:
        raise Exception("Nested matroid malformed: given ranks are not valid")

    for Xi, Xip1 in zip(X, list(X)[1:]):
        for xi in Xi:
            if not(xi in Xip1):
                raise Exception("Nested matroid malformed: given tuple is not a chain")
            if xi <= 0 or xi > n:
                raise Exception("Nested matroid malformed: element is not valid")
        
        #Strict inclusion at level i
        flag_inclusion_is_strict = False
        for xip1 in Xip1:
            if not xip1 in Xi:
                flag_inclusion_is_strict = True
                break
        if not flag_inclusion_is_strict:
            raise Exception("Nested matroid malformed: inclusion is not strict")

    for ri, rip1 in zip(R, list(R)[1:]):
        if ri < 0 or ri > n or rip1<= ri:
            raise Exception("Nested matroid malformed: rank chain is not valid")

    #Compatibility check
    X0 = X[0]
    r0 = R[0]
    if not 0 < len(X0) - r0:
        if k > 1:
            raise Exception("Nested matroid malformed: rank chain is not compatible with chain on level 0")
    for i, (Xi, ri, Xip1, rip1) in enumerate(zip(X[:-1], R[:-1], X[1:-1], R[1:-1])):
        if not len(Xi) - ri < len(Xip1) - rip1:
            raise Exception("Nested matroid malformed: rank chain is not compatible with chain on level " + str(i))
    if len(X) >= 2:
        Xm1 = X[-1]
        rm1 = R[-1]
        Xm2 = X[-2]
        rm2 = R[-2]
        if len(Xm2) - rm2 > len(Xm1) - rm1:
            raise Exception("Nested matroid malformed: rank chain is not compatible with chain on last level")
    
    #Create bases
    bases_sets = set()
    for B in combinations(range(1,n+1), rank):
        flag_has_B_right_rank = True
        frozenB = frozenset(B)
        for Xi, ri in zip(X, R):
            intersection_number = 0
            for i in B:
                if i in Xi:
                    intersection_number += 1
            if not intersection_number <= ri:
                flag_has_B_right_rank = False
                break
        if flag_has_B_right_rank:
            bases_sets.add(frozenB)
    return Matroid(ground_set, bases_sets)

def generate_nested_matroids_doublechains(d: int) -> List[tuple]:
    """
    Generate all balanced double chains of rank d.
    
    Args:
        d (int): The size of the matroids to generate
        
    Returns:
        List[tuple]: A list of all double chains of rank d
    """
    if d == 0 :
        return [tuple(0, 0, tuple([frozenset([])]), tuple([0]))]
    result = []

    for opi in SetComposition.generate_all_setcompositions(d):
        #Check if the set composition is valid
        #We also require that the first set is not a singleton because of the no loops property
        flag_valid_set_composition = True
        for pi in opi.parts[:-1]:
            if len(pi) == 1:
                flag_valid_set_composition = False
                break
        if len(opi.parts)%2 == 1 and len(opi.parts[-1]) == 1 and len(opi.parts[1]) == 1:
            flag_valid_set_composition = False
        if not flag_valid_set_composition:
            continue
        
        #generate corresponding chain of X
        k = len(opi.parts)
        X = [set(opi.parts[i]) for i in range(k)]
        for i in range(1, k):
            X[i] = X[i].union(X[i-1])

        #Generate bounds for ranks, recall r1 cannot be 0 because of the no loops property
        #For practical reasons, we generate the rank row with a starting 0
        possible_R = [[0]]
        previous_possible_R = []
        for i in range(k):
            previous_possible_R = possible_R[:]
            possible_R = []
            for R in previous_possible_R:
                for r in range(R[-1] + 1, len(opi.parts[i]) + R[-1]):
                    possible_R.append(R + [r])
        #add all the rank chains that allow for no coloops, these are the ones that have a 
        #specific equality in the last level
        for R in previous_possible_R:
            possible_R.append(R + [len(opi.parts[-1]) + R[-1]])

        #append double chain to result
        for R in possible_R:
            result.append(tuple([d, R[-1], tuple(X), tuple(R[1:])]))
    return result
        

def generate_loopless_nested_matroids(d: int) -> List[Matroid]:
    """
    Generate all loopless nested matroids of rank d.
    We do this by generating first all balanced double chains and then creating the matroids from them.
    
    Args:
        d (int): The size of the matroids to generate
        
    Returns:
        List[Matroid]: A list of all loopless nested matroids of rank d
    """
    return [nested_matroid(a1, a2, a3, a4) for a1, a2, a3, a4 in generate_nested_matroids_doublechains(d)]


def graphic_matroid(edges: List[Tuple[int, int]], vertex_set: Set[int]) -> Matroid:#can also be strings instead of ints
    """
    Create a graphic matroid from a graph.

    A graphic matroid represents the cycle structure of a graph. The ground set
    consists of the edges, and basis sets are spanning forests (contain no cycles).

    Args:
        edges (List[Tuple[int, int]]): List of edges, each represented as (vertex1, vertex2)
        vertex_set (Set[int]): Set of vertices in the graph

    Returns:
        Matroid: A graphic matroid represented by the given graph
    """
    
    def is_cycle_free(edge_subset: List[Tuple[int, int]], vertex_set: Set[int]) -> bool:
        """
        Check if a subset of edges forms a forest (contains no cycles).

        Args:
            edge_subset (Set[int]): Set of edge indices to check

        Returns:
            bool: True if the edges form a forest, False if they contain a cycle
        """
        print("Checking if edges", edge_subset, "form a forest")
        # Initialize parent array for union-find
        parent = {}
        rank = {}
        
        # Initialize each vertex as its own parent
        for edge in edge_subset:
            v1, v2 = edge
            if v1 not in parent:
                parent[v1] = v1
                rank[v1] = 0
            if v2 not in parent:
                parent[v2] = v2 
                rank[v2] = 0
                
        def find(x):
            # Find root parent with path compression
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
            
        def union(x, y):
            # Union by rank
            px, py = find(x), find(y)
            if px == py:
                return False
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            if rank[px] == rank[py]:
                rank[px] += 1
            return True
            
        # Check each edge - if vertices already connected, edge creates cycle
        for edge in edge_subset:
            v1, v2 = edge
            if not union(v1, v2):
                return False

        return True
    
    def count_connected_components(vertex_set: List[int], edges: List[Tuple[int, int]]):
        """
        Compute the number of connected components in a graph with arbitrary vertex labels.
        
        Args:
            vertex_set (Set[int]): Set of vertices in the graph
            edges (List[Tuple[int, int]]): List of tuples representing edges, e.g. [(0,1), (1,2)]
        Returns:
            int: Number of connected components
        """
        # Create adjacency list
        adj_list = {}
        for u, v in edges:
            if u not in adj_list:
                adj_list[u] = []
            if v not in adj_list:
                adj_list[v] = []
            adj_list[u].append(v)
            adj_list[v].append(u)
        
        # Keep track of visited vertices
        visited = set()
        
        def dfs(vertex):
            visited.add(vertex)
            for neighbor in adj_list[vertex]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        # Count components
        components = 0
        for vertex in vertex_set:
            if vertex not in visited:
                dfs(vertex)
                components += 1
                
        return components
    
    ground_set = set(edges)
    bases_sets = set()
    size = len(vertex_set) - count_connected_components(vertex_set, edges)
    for edge_subset in combinations(ground_set, size):
        if is_cycle_free(edge_subset, ground_set):
            bases_sets.add(frozenset(edge_subset))
    print("Defined graphic matroid with ground set", ground_set, "and bases", bases_sets)
    return Matroid(ground_set, bases_sets)