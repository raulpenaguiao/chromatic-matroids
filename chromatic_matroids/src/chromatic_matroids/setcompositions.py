# matroid_chromatic/setcompositions.py
from typing import Set, List, Tuple
from itertools import combinations
from matroid_chromatic.compositions import Composition

class SetComposition:
    """
    A class representing set compositions as an imutable class. This means no methods change self.
    A set composition of a frozenset E is a way of writing E as a disjoint union of subsets.
    For example, [{1, 4},{2},{3, 5, 6}] is a composition of {1, 2, 3, 4, 5, 6}.

    This class implements quasi-shuffles of set compositions
    """
    # Class variables for memoization of set compositions and quasi-shuffles
    _PREGEN = 3
    _all_generated_setcompositions_size = 1  # Limit for precomputation
    _all_generated_setcompositions_list = [] # Cache for precomputed results
    _qshuffle_precomputation_dictionary = {}  # Cache for precomputed results
    
    def __init__(self, *args, **kwargs):
        """
        Initialize a set composition of a set.
        The set has to be a collection of positive integers
        
        Args:
            *args: Variable length argument list. Can be a list or a tuple of positive integers
            **kwargs: Arbitrary keyword arguments (reserved for future use)
            
        Raises:
            TypeError: If any argument is not an integer
            ValueError: If any integer is not positive
        """
        # Check if args is a single list/tuple
        if len(args) == 0:#SetComposition() is the unique set composition on 1 element
            self.parts = []
        elif len(args) == 1:
            if isinstance(args[0], (list, tuple, frozenset)):#SetComposition([[2, 4], [1], [3, 5, 6]])
                for part in args[0]:
                    if not isinstance(part, (list, tuple, frozenset)):
                        raise TypeError(f"All parts must be lists, tuples, or frozensets, got {type(part)}")
                self.parts = [list(part) for part in args[0]] # Convert to list to ensure mutability
            elif isinstance(args[0], str):#SetComposition("(2,4|1|3,5,6)")
                if args[0] == "()":
                    self.parts = []
                else:
                    self.parts = [[int(i) for i in part.split(",")] for part in args[0][1:-1].split("|")]
            else:
                self.parts = []
        else:#any invalid input will raise an exception
            raise Exception(f"Invalid collection of inputs on SetComposition class with args = {args} and kwards = {kwargs}")
        
        # Validate all parts are disjoint and elements are positive integers
        self.ground_set = set()
        for part in self.parts:
            for p in part:
                if not isinstance(p, int):
                    raise TypeError(f"All elements must be integers, got {type(p)}")
                if p <= 0:
                    raise ValueError(f"All parts must be positive integers, got {p}")
                if p in self.ground_set:
                    raise ValueError(f"Not all parts are disjoint, specifically {part} in {self.parts}")
                self.ground_set.add(p)
        
        # Sort all parts to make sure all set compositions hash to the same string
        for part in self.parts:
            part.sort()
        
        #make ground set an ordered list
        self.ground_set = list(self.ground_set)
        
    def __str__(self) -> str:
        """
        String representation of the composition using | as separator
        
        Returns:
            str: Composition parts joined by '|' character
        """
        return "(" + "|".join([",".join([str(i) for i in part]) for part in self.parts]) + ")"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'SetComposition') -> bool:
        if not self.ground_set == other.ground_set:
            return False
        if not len(self.parts) == len(other.parts):
            return False
        for part1, part2 in zip(self.parts, other.parts):
            if not part1 == part1:
                return False
        return True

    def rest(self) -> 'SetComposition':
        """
        Returns a new Composition object containing all but the first part
        of this composition.
        
        Returns:
            Composition: A new composition without the first part
        """
        if self.ground_set == frozenset():
            raise Exception("Empty set composition cannot be rest-ed")
        return SetComposition(self.parts[1:])
        
    def prepend(self, a: frozenset[int]) -> 'SetComposition':
        """
        Computes a new composition with a prepend element
        Does not change 

        Args:
            self (Composition): a composition
            a (int): term to prepend
        
        Returns:
            Composition: A new composition with a prepend set
        """
        return SetComposition([a] + self.parts)

    def relabel(self, relabeling_map: (None, list, tuple, dict[int:int])) -> 'SetComposition':
        """
        Computes a new composition where each element is relabeled
        Does not change previous set composition
        If no relabeling map was given, we relabel it to range(1, n+1)

        Args:
            self (SetComposition): a composition
            relabeling_map (None, list, tuple, dict[int:int]): relabeling map
        
        Returns:
            Composition: A relabeled composition. Ground set and number of parts will still be the same
        """
        if isinstance(relabeling_map, (list, tuple)):
            if not len(relabeling_map) == len(self.ground_set):
                raise Exception("Attempting to relabel with incorrect label set")
            relabeling_map_build = {}
            for element, new_element in zip(self.ground_set, relabeling_map):
                relabeling_map_build[element] = new_element
            relabeling_map = relabeling_map_build
        elif relabeling_map == None:
            relabeling_map = {}
            for index, element in enumerate(self.ground_set):
                relabeling_map[element] = index+1
        elif not isinstance(relabeling_map, dict):
            raise Exception(f"Attempting to relabel with incorrect label type {type(relabeling_map)}, using {relabeling_map}.")
        return SetComposition([[relabeling_map[p] for p in part] for part in self.parts])

    def alpha(self) -> Composition:
        return Composition([len(part) for part in self.parts])
    
    @staticmethod
    def generate_all_setcompositions(n: int):
        """
        Computes all set compositions of a given size iteratively with memoization
        
        Args:
            n (int): A positive integer, we generate compositions for list(range(1, n+1))
        
        Returns:
            list: A list of all set compositions of range(1, n+1), ordered lexicographically by size then larger terms
                 For example, generate_all_composition(3) returns:
                 [[[1,2,3]], [[2, 3], [1]], [[1, 3], [2]], [[1, 2], [3]], [[3], [1, 2]], [[2], [1, 3]], [[1], [2, 3]], 
                    [[3], [2], [1]], [[3], [1], [2]], [[2], [3], [1]], [[2], [1], [3]], [[1], [3], [2]], [[1], [2], [3]]]
        
        Note:
            Uses memoization to avoid recomputing previously generated set compositions.
            Results are stored in _all_generated_setcompositions_list for future use.
        """
        # Check if these compositions were already generated
        if n < SetComposition._all_generated_setcompositions_size:
            if n < 0:
                return []  # No set compositions for negative numbers
            return SetComposition._all_generated_setcompositions_list[n]
        
        # Initialize answer with one-block composition
        ground_set = list(range(1, n+1))
        answer = [SetComposition([ground_set])]

        # Generate all setcompositions by breaking off initial part
        for size_rest in range(1, n):#rest has size < n
            smaller_setcompositions = SetComposition.generate_all_setcompositions(size_rest)#get smaller compositions
            for rest in combinations(ground_set, size_rest):
                
                #create first set
                first = frozenset([k for k in ground_set if not k in rest])
                
                #add each constructed set compositions prepended by first set to answer
                for smaller_setcomposition in smaller_setcompositions:
                    answer.append(smaller_setcomposition.relabel(rest).prepend(first))

        # Update the memoization cache
        SetComposition._all_generated_setcompositions_size = n + 1
        SetComposition._all_generated_setcompositions_list += [answer]
        return answer

    @staticmethod
    def quasi_shuffles_add_to_cache(q_in: 'SetComposition', t_in: 'SetComposition', qs_in: dict[str:int]) -> None:
        lq = len(q_in.ground_set)
        lt = len(t_in.ground_set)
        
        q = q_in.relabel(None)
        t = t_in.relabel(list(range(lq+1, lq+lt+1)))

        #build unrelabel map
        relabel_map = {}
        for i in range(lq+lt):#We need to be careful with the one-index issue here
            if i < lq:
                relabel_map[i+1] = q_in.ground_set[i]
            else:
                relabel_map[i+1] = t_in.ground_set[i - lq]
        
        #unrelabel quasi-shuffle
        qs = {str(SetComposition(set_composition_string).relabel(relabel_map)):coeff 
                    for set_composition_string, coeff in qs_in.items()}
        
        # Update memoization cache
        if not str(q) in SetComposition._qshuffle_precomputation_dictionary:
            SetComposition._qshuffle_precomputation_dictionary[str(q)] = {}
        SetComposition._qshuffle_precomputation_dictionary[str(q)][str(t)] = qs

    @staticmethod
    def quasi_shuffles_fetch_from_cache(q_in: 'SetComposition', t_in: 'SetComposition') -> tuple[bool, dict]:
        lq = len(q_in.ground_set)
        lt = len(t_in.ground_set)

        #get relabelled versions to consult memoization cache
        q = q_in.relabel(None)
        t = t_in.relabel(list(range(lq+1, lq+lt+1)))

        # Check memoization cache
        if str(q) in SetComposition._qshuffle_precomputation_dictionary:
            if str(t) in SetComposition._qshuffle_precomputation_dictionary[str(q)]:
                #unrelable map
                relabel_map = {}
                for i in range(lq+lt):
                    if i < lq:
                        relabel_map[i+1] = q_in.ground_set[i]
                    else:
                        relabel_map[i+1] = t_in.ground_set[i - lq]
                return True, { str(SetComposition(opistr).relabel(relabel_map)):coeff 
                    for opistr, coeff in SetComposition._qshuffle_precomputation_dictionary[str(q)][str(t)].items() }
        return False, {}

    @staticmethod
    def quasi_shuffles(q: 'SetComposition', t: 'SetComposition'):
        """
        Compute all possible quasi-shuffles of two set compositions.
        A quasi-shuffle combines two set compositions allowing both interleaving and union 
        of corresponding terms.

        For example, quasi-shuffling [[2], [1,3]] and [[2], [1]] would give:
        - [[2], [5], [4], [1,3]] (interleaving)
        - [[2], [1,3], [5], [4]] (interleaving)
        - [[2, 5], [1, 3], [4]] (adding first terms)
        - [[2], [1, 3, 5], [4]] (adding first and second terms)
        And other combinations...
        
        Args:
            q (SetComposition): First set composition
            t (SetComposition): Second set composition
            
        Returns:
            dict: Dictionary mapping resulting set compositions in string format to their coefficients.
                 The coefficients track how many ways that set composition can be formed.
        
        Note:
            Uses the recursive formula:
            qs(a·q, b·t) = a·qs(q, bt) + b·qs(aq, t) + (a+b)·qs(q, t)
            where a·q means set composition q with 'a' prepended
        """
        
        #No qausi-shuffles of non-disjoint sets
        for q_el in q.ground_set:
            if q_el in t.ground_set:
                raise("Exception")
        for t_el in t.ground_set:
            if t_el in q.ground_set:
                raise("Exception")
        
        # Base cases: if either composition is empty, return the other
        if len(q.ground_set) == 0:
            return {str(t): 1}
        if len(t.ground_set) == 0:
            return {str(q): 1}
        
        #fetch from cache
        found_in_cache, qs = SetComposition.quasi_shuffles_fetch_from_cache(q, t)
        if found_in_cache:
            return qs
        
        # Get the first terms and rest of each composition
        a = q.parts[0]
        b = t.parts[0]
        qrest = q.rest()
        trest = t.rest()

        answer = {}
        
        # Case 1: Take 'a' from first set composition > a·qs(q, bt) 
        qsh1 = SetComposition.quasi_shuffles(qrest, t)
        for opistr in qsh1:
            newqs = str(SetComposition(opistr).prepend(a))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh1[opistr]
        
        # Case 2: Take 'b' from second set composition > + b·qs(aq, t)
        qsh2 = SetComposition.quasi_shuffles(q, trest)
        for opistr in qsh2:
            newqs = str(SetComposition(opistr).prepend(b))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh2[opistr]
        
        # Case 3: Take both first terms and union them together > (a+b)·qs(q, t)
        qsh3 = SetComposition.quasi_shuffles(qrest, trest)
        for opistr in qsh3:
            newqs = str(SetComposition(opistr).prepend(a + b))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh3[opistr]
        
        #add to cache after relabel
        SetComposition.quasi_shuffles_add_to_cache(q, t, answer)
        return answer


SetComposition._all_generated_setcompositions_list = [[SetComposition()]]
# Pregenerate all set compositions and qshuffles up to size PREGEN
SetComposition.generate_all_setcompositions(SetComposition._PREGEN)
for scomp_list1 in SetComposition._all_generated_setcompositions_list:
    l1 = len(scomp_list1[0].ground_set)
    for scomp1 in scomp_list1:        
        for scomp_list2 in SetComposition._all_generated_setcompositions_list:
            l2 = len(scomp_list2[0].ground_set)
            for scomp2 in scomp_list2:
                SetComposition.quasi_shuffles(scomp1, scomp2.relabel({i:i+l1 for i in range(1, l2+1)}))
