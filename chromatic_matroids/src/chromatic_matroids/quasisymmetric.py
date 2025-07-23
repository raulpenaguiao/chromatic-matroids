# matroid_chromatic/quasisymmetric.py
from typing import Set, List, Tuple
from matroid_chromatic import Composition

class QSymFunction:
    def __init__(self, *args, **kwargs):
        """
        Initialize a quasi symmetric function, it is the zero term by default
        
        Args:
            monomial_basis: 
                A dictionary of compositions to integers, or
                A tuple of a composition and an integer, or 
                A single composition.
        """
        if "monomial_basis" in kwargs:
            item = kwargs["monomial_basis"]
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], int):
                #QSym(monomial_basis=(Composition([1,3,2]), -3)
                self.coefficients = {str(item[0]):item[1]}
            elif isinstance(item, Composition):
                #QSym(monomial_basis={Composition([1, 3, 2]))
                self.coefficients = {str(item):1}
            elif isinstance(item, dict):
                #QSym(monomial_basis={"(1, 3, 2)":1,"(2, 1)":1})
                self.coefficients = {i:item[i] for i in item}
            elif item == None:
                self.coefficients = {}
            else:
                raise Exception(f"QSym input malformed, expected {type(Composition())} or dictionary, got {item} of type {type(item)}")
        else:
            # no initialization happened
            self.coefficients = {}

        #Check if the list of coefficients makes sense as a monomial basis
        for key, item in self.coefficients.items():
            if not isinstance(key, str):
                raise TypeError("Monomial basis indexed by compositions")
            # Check if we can build a composition from this
            # This will raise an exception if the string is malformed or does not correspond to a composition
            Composition(key)

            # Check if the coefficient is an integer
            if not isinstance(item, int):
                raise TypeError("Quasisymmetric functions must integer coefficients")

    def _addTo(self, g: 'QSymFunction') -> None:
        for tstr in g.coefficients:
            if not tstr in self.coefficients:
                self.coefficients[tstr] = 0
            self.coefficients[tstr] += g.coefficients[tstr]
        return

    def __add__(self, g: 'QSymFunction'):
        answer = QSymFunction(monomial_basis = self.coefficients)
        answer._addTo(g)
        return answer
    
    def _scalarMultiple(self, scalar):
        answer = QSymFunction(monomial_basis = self.coefficients)
        for tstr in self.coefficients:
            answer.coefficients[tstr] *= scalar
        return answer
    
    def __mul__(self, g: 'QSymFunction'):
        answer = QSymFunction()
        for tstr in self.coefficients:
            t = Composition(tstr)
            for qstr in g.coefficients:
                q = Composition(qstr)
                coeff = g.coefficients[qstr] * self.coefficients[tstr]
                answer._addTo(QSymFunction(monomial_basis = Composition.quasi_shuffles(t, q))._scalarMultiple(coeff))
        return answer

    def __repr__(self) -> str:
        return f"QSymFunction({self.coefficients})"


