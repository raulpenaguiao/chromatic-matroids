# Chromatic matroids Package

To install the package
```bash
pip install chromatic-matroids
```

Running the following should work:
```python3
from chromatic_matroids.compositions import Composition
comp1 = Composition([1, 2, 1])
```

# Overview
This package is part of a matroid library that provides tools for working with matroids and their chromatic invariants.
It includes various combinatorial structures and operations for the study of matroids, such as compositions, set compositions, quasi-symmetric functions, word quasi-symmetric functions, graphs, and chromatic functions on matroids.

This is done in a self-contained way so that it can be used independently of typical libraries like sagemath or sympy.
I also allows for building up examples of matroids and its corresponding chromatic invariants without the need for external libraries.

## Classes and objects

### Compositions - file compositions.py

This package implements a construction of compositions.
Accessible is the constructor `Composition` and the method `generate_all_composition`.
There are also methods for manipulating compositions, such as `rest` and `prepend`.
These objects can be printed with a user-friendly representation.
For a construction example, run the following:

```python3
from chromatic_matroids.compositions import Composition
comp1 = Composition([1, 2, 1])
comp2 = Composition([2, 1])
print(f"Basic compositions: {comp1}, {comp2}")
print("")

print("Composition Operations")
print(f"Rest of {comp1}: {comp1.rest()}")
print(f"Prepending 3 to {comp2}: {comp2.prepend(3)}")
print("")

print("Generate all compositions of size 4")
comps = Composition.generate_all_composition(4)
print(f"All compositions of 4: {comps}")
```


### Set compositions - file setcompositions.py

This package implements a construction of set compositions.
Accessible is the constructor `SetComposition` and the method `generate_all_set_composition`.
There are also methods for manipulating set compositions, such as `rest(self) -> 'SetComposition'` and `prepend(self, a: frozenset[int]) -> 'SetComposition'`.
It exposes a method `first(self) -> frozenset[int]` that returns the first part of the set composition, if it exists, raising an error if it does not exist (_i.e._ the original set composition is empty).
It exposes a method `relabel(self, relabeling_map: (None, list, tuple, dict[int:int])) -> 'SetComposition'` that allows for changing the basis set of a set composition.
It exposes a method `alpha(self) -> Composition` that allows for computing the underlying composition.
Finally, this package exposes a static method `def quasi_shuffles(q: 'SetComposition', t: 'SetComposition') -> dict[str:int]`, that computes the quasi-shuffles of two set compositions.
These objects can be printed with a user-friendly representation.
For an example, run the following:

```python3
from chromatic_matroids.setcompositions import SetComposition
print("Example 13: SetComposition Operations")
set_comp1 = SetComposition([[1, 2], [3, 4], [5]])
set_comp2 = SetComposition([[6], [7, 8]])
print(f"Set Compositions: {set_comp1}, {set_comp2}")
print(f"Quasi-shuffles: {SetComposition.quasi_shuffles(set_comp1, set_comp2)}")
```


### Quasi-symmetric functions

This package implements a construction of quasi-symmetric functions.
Accessible is the constructor `QSymFunction` with keyword argument `monomial_basis`, that takes a dictionary `dict[Composition:int]` or a tuple `(str, Composition)` or a single `Composition` or no argument at all.
It also exposes basic arithmetic operations such as addition and multiplication.
It allows for printing the coefficients in a user-friendly way.

For a construction example, run the following:
```python3
from chromatic_matroids.quasisymmetric import QSymFunction
from chromatic_matroids.compositions import Composition
print("Construct QSymFunction from a dictionary of monomial bases")
qsym_from_dict = QSymFunction(monomial_basis={"(1,2,1)": 2, "(2,1)": -1})
qsym_from_tuple = QSymFunction(monomial_basis=(Composition([1,2,1]), 2))
qsym_empty = QSymFunction()
print("QSymFunction from dictionary:")
print(f"Dictionary coefficients: {qsym_from_dict.coefficients}")
print(f"Tuple coefficients: {qsym_from_tuple.coefficients}")
print(f"Empty coefficients: {qsym_empty.coefficients}")
print(f"Product coefficients: {(qsym_from_tuple * qsym_from_dict).coefficients}")
```

### Word quasi-symmetric functions

This package implements a construction of word quasi-symmetric functions.
For a construction example, run the following:
```
print("Construct NCQSymFunctions from a dictionary of monomial bases")
nc_f = NCQSymFunction(monomial_basis=set_comp1)
nc_g = NCQSymFunction(monomial_basis=set_comp2)
nc_sum = nc_f + nc_g
print("Sum of NCQSymFunctions:")
print(f"nc_f: {nc_f.coefficients}")
print(f"nc_g: {nc_g.coefficients}")
print(f"nc_f + nc_g: {nc_sum.coefficients}")
```

### Graphs
This package implements a construction of graphs from edge list.

### Matroids

This package implements a construction of matroids from base list.
It also implements construction of *Schubert matroids*, *graphical matroids*, *uniform matroids*, and *nested matroids.


### Chromatic functions on matroids

This package implements a construction of chromatic invariants on matroids.


## Features


### Compositions

This subpackage exposes the following classes and methods:
- `Composition`: A class representing a composition of integers.
- `generate_all_composition`: A method to generate all compositions of a given size.
- `rest`: A method to get the rest of a composition.
- `prepend`: A method to prepend an integer to a composition.

The method `generate_all_composition` precomputes compositions of size 4 and saves any computed compositions in a cache for efficiency.
For instance running the following code one notes that the second time the method is called, it returns the cached value:

```python3
from chromatic_matroids.compositions import Composition
import time
# Get current time
start_time = time.time()

# Generate compositions of size 22
N = 22
comps = Composition.generate_all_composition(N)
# Get time after first call
end_time = time.time()
print(f"Time taken for first call: {(end_time - start_time)*1000} miliseconds\n")# 5482.729434967041 miliseconds

comps2 = Composition.generate_all_composition(N)
# Get time after second call
end_time2 = time.time()
print(f"Time taken for second call: {(end_time2 - end_time)*1000} miliseconds\n")# 0.5552768707275391 miliseconds
```

### Set compositions

This subpackage exposes the following classes and methods:
- `SetComposition`: A class representing a set composition.
- `generate_all_set_composition`: A method to generate all set compositions of a given size.
- `rest`: A method to get the rest of a set composition.
- `prepend`: A method to prepend a set to a set composition.
- `first`: A method to get the first part of a set composition.
- `relabel`: A method to relabel the basis set of a set composition.
- `alpha`: A method to compute the underlying composition of a set composition.
- `quasi_shuffles`: A static method to compute the quasi-shuffles of two set compositions.

This subpackage also implements a method to compute the quasi-shuffles of two set compositions, which is useful in combinatorial applications.
Here is an example of a quasi-shuffle computation:

```python3
from chromatic_matroids.setcompositions import SetComposition
set_comp1 = SetComposition([[1, 2], [3, 4], [5]])
set_comp2 = SetComposition([[31], [32, 33]])
print(f"Quasi-shuffles: {SetComposition.quasi_shuffles(set_comp1, set_comp2)}")
```


### Quasi-symmetric functions

### Word quasi-symmetric functions

### Graphs

### Matroids

### Chromatic functions on matroids


# To do

## Documentation

- Readme file
    - Set up documentation for each subpackage and its classes.
        - Word QSym
        - Graphs
        - Matroids
        - Chromatic functions on matroids
    - Display examples of usage for each class and method.
        - QSym
        - Word QSym
        - Graphs
        - Matroids
        - Chromatic functions on matroids
- Documentation for each class and method.
    - Add docstrings to all classes and methods.
    - Add type hints to all classes and methods.

    
## Test cases

- We are still building up our unit test library

## Efficiency

- We are improving the construction of some methods related to computing stability of some set compositions with memorization.

# Contributing
We welcome contributions to this package. If you have suggestions for improvements or new features, please open an issue or submit a pull request.

# License
This package is licensed under the MIT License. See the LICENSE file for more details.