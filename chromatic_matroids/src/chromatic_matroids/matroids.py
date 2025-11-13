# matroid_chromatic/matroid.py
from typing import Set, List, Tuple

class Matroid:
    def __init__(self, ground_set: frozenset[int], bases_sets: Set[frozenset]):
        """
        Initialize a matroid with its ground set and bases sets.
        
        Args:
            ground_set (frozenset[int]): The ground set of the matroid
            bases_sets (Set[frozenset]): Collection of bases sets that define the matroid
            
        Raises:
            Exception: If the given sets do not satisfy matroid axioms
        """
        self.ground_set = ground_set
        self.bases_sets = bases_sets
        self._validate_matroid()
    
    def _validate_matroid(self) -> None:
        """
        Validate that the given sets satisfy matroid axioms.
        
        Checks:
        1. Basis existence property - at least one basis exists
        2. Exchange property - for any two bases B1, B2 and element i in B2-B1,
           there exists j in B1-B2 such that (B2 + j - i) is also a basis
        
        Raises:
            Exception: If either matroid axiom is not satisfied
        """
        #Basis existance property
        found_basis = False
        for basis_set in self.bases_sets:
            found_basis = True
            break
        if not found_basis:
            raise Exception("Matroid not well defined: Basis axiom 1 not verified")
        
        # Exchange property
        for B1 in self.bases_sets:
            for B2 in self.bases_sets:
                    if(B1 == B2):
                        continue
                    exchange_exists = False
                    for i in B2:
                        if not(i in B1):
                            for j in B1:
                                if not(j in B2):
                                    #Check if B2 + j - i is a basis
                                    B = frozenset(B2 | {i} - {j})
                                    if B in self.bases_sets:#Check condition
                                        exchange_exists = True
                                if exchange_exists:
                                    break
                        if exchange_exists:
                            break
                    if not exchange_exists:
                        raise Exception("Matroid not well defined: Basis axiom 2 not verified")
    

    def _get_all_subsets(self, s: frozenset) -> Set[frozenset]:
        """
        Return all subsets of a given set.
        
        Args:
            s (frozenset): The set to find subsets of
            
        Returns:
            Set[frozenset]: All possible subsets of the input set
        """
        result = {frozenset()}
        for elem in s:
            new_sets = set()
            for subset in result:
                new_sets.add(subset | {elem})
            result.update(new_sets)
        return result
    
    def rank(self, subset: Set[int]) -> int:
        """
        Compute the rank of a subset.
        
        The rank is the size of the largest independent set contained in the subset.
        
        Args:
            subset (Set[int]): The subset to compute rank for
            
        Returns:
            int: The rank of the subset
        """
        return max([len([i for i in basis_set if i in subset]) for basis_set in self.bases_sets])
    
    def independent_sets(self) -> Set[frozenset]:
        """
        Return all independent sets of the matroid.
        
        An independent set is any subset of a basis set.
        
        Returns:
            Set[frozenset]: All independent sets of the matroid
        """
        independent_sets = set()
        for subset in self._get_all_subsets(self.ground_set):
            for basis_set in self.bases_sets:
                flag = True
                for i in subset:
                    if not(i in basis_set):
                        flag = False
                        break
                if flag:
                    independent_sets.add(subset)
        return independent_sets
    
    def is_nested(self) -> bool:
        """
        Check if the matroid is nested.
        
        A matroid is nested if ***condition form Anna de Mier and Joseph Bonin***.
        That is, if this matroid arises as a sequence of creating coloops and extensions.
        
        Returns:
            bool: True if the matroid is nested, False otherwise
        """
        #TODO
        return False
    
    def extend(self, elements: List[int]) -> 'Matroid':
        """
        Extend the matroid by adding a collection of elements.
        """
        new_ground_set = frozenset(self.ground_set)
        new_bases_sets = set(self.bases_sets)
        
        for element in elements:
            if element in new_ground_set:
                raise Exception("Element already in ground set")
            new_ground_set = new_ground_set | {element}
            for basis_set in new_bases_sets:
                for i in basis_set: 
                    if i in self.ground_set:
                        new_bases_sets.add(frozenset(basis_set - {i} | {element}))
        return Matroid(new_ground_set, new_bases_sets)
    


    def relabel(self, bijection: dict[int, int]) -> 'Matroid':
        """
        Returns a relabeled version of the matroid.
        
        Args:
            bijection (dict[int, int]): A bijective mapping between old and new labels
            
        Returns:
            Matroid: A new matroid with elements relabeled according to the bijection
        """
        ground_set = frozenset(bijection[i] for i in self.ground_set)
        bases_sets = {frozenset(bijection[i] for i in basis_set) for basis_set in self.bases_sets}
        return Matroid(ground_set, bases_sets)
