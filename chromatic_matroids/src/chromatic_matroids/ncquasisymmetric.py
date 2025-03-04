# matroid_chromatic/ncquasisymmetric.py
from typing import Set, List, Tuple
from matroid_chromatic import SetComposition
from matroid_chromatic import QSymFunction

class NCQSymFunction:
    def __init__(self, *args, **kwargs):
        """
        Initialize a non commutative quasi symmetric function, it is the zero term by default
        
        Args:
            coefficients: the dictionary of coefficients: keys are compositions and 
        """
        if "monomial_basis" in kwargs:
            item = kwargs["monomial_basis"]
            if isinstance(item, (str, SetComposition)):
                #NCQSymFunction(monomial_basis = "3|1,5|2,4,6") = M_{3|1,5|2,4,6}
                #NCQSymFunction(monomial_basis = SetComposition("3|1,5|2,4,6")) = M_{3|1,5|2,4,6}
                self.coefficients = {str(item) : 1}
            elif isinstance(item, dict):
                #NCQSymFunction(monomial_basis = {"3|1,5|2,4,6":2, "4|1,2|3":-1}) = 2 M_{3|1,5|2,4,6} - M_{4|1,2|3}
                self.coefficients = item
            else:
                raise Exception("NCQSymFunction not correctly initialized")
        else:#NCQSymFunction() = 0
            self.coefficients = {}

    def _addTo(self, g: 'NCQSymFunction') -> None:
        #changes underlying term
        for tstr in g.coefficients:
            if not tstr in self.coefficients:
                self.coefficients[tstr] = 0
            self.coefficients[tstr] += g.coefficients[tstr]

    def __add__(self, g: 'NCQSymFunction') -> 'NCQSymFunction':
        answer = NCQSymFunction(monomial_basis = self.coefficients)
        answer._addTo(g)
        return answer
    
    def _scalarMultiple(self, scalar: int) -> 'NCQSymFunction':
        answer = NCQSymFunction(monomial_basis = self.coefficients)
        for tstr in self.coefficients:
            answer.coefficients[tstr] *= scalar
        return answer
    
    def __mul__(self, g: 'NCQSymFunction') -> 'NCQSymFunction':
        answer = NCQSymFunction()
        for tstr, tcoeff in self.coefficients.items():
            for qstr, qcoeff in g.coefficients.items():
                coeff = qcoeff * tcoeff
                answer._addTo(NCQSymFunction(monomial_basis = SetComposition.quasi_shuffles(t, q))._scalarMultiple(coeff))
        return answer
    
    def comu(self) -> QSymFunction:
        """
        Compute the commutative quasisymmetric function of a non-commutative quasisymmetric function
        """
        answer = QSymFunction()
        for tstr, tcoeff in self.coefficients.items():
            answer._addTo(QSymFunction(monomial_basis = {str(SetComposition(tstr).alpha()): tcoeff}))
        return answer

    def __repr__(self) -> str:
        return f"NCQSymFunction({self.coefficients})"


