# matroid_chromatic/compositions.py
from typing import Set, List, Tuple

class Composition:
    """
    A class representing compositions of integers as an imutable class. This means no methods change self.
    A composition of n is a way of writing n as a sum of positive integers.
    For example, [2,1,3] is a composition of 6.

    This class implements quasi-shuffles of compositions
    """
    # Class variables for memoization of quasi-shuffle computations
    _PREGEN = 4
    _all_generated_compositions_size = 0  # Limit for precomputation
    _all_generated_compositions_list = [] # Cache for precomputed results
    _qshuffle_precomputation_dictionary = {}  # Cache for precomputed results
    
    def __init__(self, *args, **kwargs):
        """
        Initialize a composition of integers
        
        Args:
            *args: Variable length argument list. Can be a list or a tuple of positive integers
            **kwargs: Arbitrary keyword arguments (reserved for future use)
            
        Raises:
            TypeError: If any argument is not an integer
            ValueError: If any integer is not positive
        """
        # Check if args is a single list/tuple
        if len(args) == 0:#Composition() = [] the unique composition of 0
            self.parts = []
        elif len(args) == 1:
            if isinstance(args[0], (list, tuple)):
                self.parts = list(args[0]) # Convert to list to ensure mutability
            elif isinstance(args[0], str):
                if args[0] == "()":
                    self.parts = []#Composition('()') = [] the unique composition of 0
                else:
                    try:
                        self.parts = [int(i) for i in args[0][1:-1].split(",")]#Composition('(2,1,3)') = [2,1,3]
                    except:
                        raise Exception(f"Composition input malformed, expected a string of the form '(2,1,3)', got {args[0]}")
            else:
                raise Exception("")
        else:
            raise Exception("")
        # Validate all arguments are positive integers
        for part in self.parts:
            if not isinstance(part, int):
                raise TypeError(f"All parts must be integers, got {type(part)}")
            if part <= 0:
                raise ValueError(f"All parts must be positive integers, got {part}")
        
        self.nparts = len(self.parts)  # Number of parts in the composition
        self.n = sum(self.parts)  # Total sum of all parts
    
    def __str__(self) -> str:
        """
        String representation of the composition using | as separator
        
        Returns:
            str: Composition parts joined by '|' character
        """
        return "(" + ",".join([str(i) for i in self.parts]) + ")"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not self.n == other.n:
            return False
        if not self.nparts == other.nparts:
            return False
        for a, b in zip(self.parts, other.parts):
            if not a == b:
                return False
        return True

    def rest(self) -> 'Composition':
        """
        Returns a new Composition object containing all but the first part
        of this composition.
        
        Returns:
            Composition: A new composition without the first part
        """
        if len(self.parts) == 0:
            raise Exception("Empty composition cannot be rest-ed")
        return Composition(self.parts[1:])
        
    def prepend(self, a: int) -> 'Composition':
        """
        Computes a new composition with a prepend element
        Does not change self

        Args:
            self (Composition): a composition
            a (int): term to prepend
        
        Returns:
            Composition: A new composition with a prepend element
        """
        return Composition([a] + self.parts)

    @staticmethod
    def generate_all_composition(n: int) -> list['Composition']:
        """
        Computes all compositions of a given size iteratively with memoization
        
        Args:
            n (int): The positive integer to generate compositions for
        
        Returns:
            list: A list of all compositions of n, ordered lexicographically
                 For example, generate_all_composition(3) returns:
                 [[3], [2,1], [1,2], [1,1,1]]
        
        Note:
            Uses memoization to avoid recomputing previously generated compositions.
            Results are stored in _all_generated_compositions_list for future use.
        """
        # Check if these compositions were already generated
        if n < Composition._all_generated_compositions_size:
            if n < 0:
                return []  # No compositions for negative numbers
            return Composition._all_generated_compositions_list[n]
        
        # Start with the trivial composition [n]
        answer = [Composition([n])]

        # Generate all compositions by breaking off initial parts
        for k in range(1, n):
            # For each k from 1 to n-1:
            # Take each composition of k and prepend (n-k) to it
            # This systematically generates all possible compositions
            smaller_compositions = Composition.generate_all_composition(k)
            for alpha in smaller_compositions:
                answer.append(alpha.prepend(n-k))
        
        # Update the memoization cache
        Composition._all_generated_compositions_size = n + 1
        Composition._all_generated_compositions_list += [answer]
        return answer

    @staticmethod
    def quasi_shuffles(q: 'Composition', t: 'Composition') -> dict[str:int]:
        """
        Compute all possible quasi-shuffles of two compositions.
        A quasi-shuffle combines two compositions allowing both interleaving and addition 
        of corresponding terms.
        
        For example, quasi-shuffling [1,2] and [3,1] could give:
        - [1,3,2,1] (interleaving)
        - [4,2,1] (adding first terms)
        - [1,5,1] (adding first and second terms)
        And other combinations...
        
        Args:
            q (Composition): First composition
            t (Composition): Second composition
            
        Returns:
            dict: Dictionary mapping resulting compositions to their coefficients.
                 The coefficients track how many ways that composition can be formed.
        
        Note:
            Uses the recursive formula:
            qs(a·q, b·t) = a·qs(q, bt) + b·qs(aq, t) + (a+b)·qs(q, t)
            where a·q means composition q with 'a' prepended
        """
        # Check memoization cache
        if str(q) in Composition._qshuffle_precomputation_dictionary:
            if str(t) in Composition._qshuffle_precomputation_dictionary[str(q)]:
                return Composition._qshuffle_precomputation_dictionary[str(q)][str(t)]
        
        # Base cases: if either composition is empty, return the other
        if q.n == 0:
            return {str(t): 1}
        if t.n == 0:
            return {str(q): 1}

        # Get the first terms and rest of each composition
        a = q.parts[0]
        b = t.parts[0]
        qrest = q.rest()
        trest = t.rest()

        answer = {}
        
        # Case 1: Take 'a' from first composition > a·qs(q, bt) 
        qsh1 = Composition.quasi_shuffles(qrest, t)
        for alphas in qsh1:
            newqs = str(Composition(alphas).prepend(a))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh1[alphas]
        
        # Case 2: Take 'b' from second composition > + b·qs(aq, t)
        qsh2 = Composition.quasi_shuffles(q, trest)
        for alphas in qsh2:
            newqs = str(Composition(alphas).prepend(b))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh2[alphas]
        
        # Case 3: Take both first terms and add them together > (a+b)·qs(q, t)
        qsh3 = Composition.quasi_shuffles(qrest, trest)
        for alphas in qsh3:
            newqs = str(Composition(alphas).prepend(a + b))
            if not(newqs in answer):
                answer[newqs] = 0
            answer[newqs] += qsh3[alphas]

        
        if not str(q) in Composition._qshuffle_precomputation_dictionary:
            Composition._qshuffle_precomputation_dictionary[str(q)] = {}
        Composition._qshuffle_precomputation_dictionary[str(q)][str(t)] = answer
        return answer


Composition._all_generated_compositions_list = [[Composition()]]
# Pregenerate all compositions and qshuffles up to size PREGEN
Composition.generate_all_composition(Composition._PREGEN)
for comp_list1 in Composition._all_generated_compositions_list:
    for comp1 in comp_list1:        
        for comp_list2 in Composition._all_generated_compositions_list:
            for comp2 in comp_list2:
                Composition.quasi_shuffles(comp1, comp2)
