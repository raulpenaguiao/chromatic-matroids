# Matroid Package


This is a simple matroid package that contains constructor functions for basic combinatorial structures like set compositions, complext structures like matroids and algebraic structure like word quasisymmetric functions.
This builds up for the construction of chromatic invariants on matroids.

This abstracts away all the intricacies of matroid operations in order to compute the chromatic invariants.


## Packages

### Compositions

This package implements a construction of compositions:

```
print("Composition Construction")
comp1 = Composition([1, 2, 1])
comp2 = Composition([2, 1])
print(f"Example 5: Basic compositions: {comp1}, {comp2}")
print("\n")

print("Composition Operations")
print(f"Rest of {comp1}: {comp1.rest()}")
print(f"Prepending 3 to {comp2}: {comp2.prepend(3)}")
print("\n")

print("Generate All Compositions")
comps3 = Composition.generate_all_composition(3)
print(f"All compositions of 3: {comps3}\n")
print("\n")
```


### Set compositions

This package implements a construction of set compositions.
For a construction example, run the following:

```
print("Example 13: SetComposition Operations")
set_comp1 = SetComposition([[1, 2], [3, 4], [5]])
set_comp2 = SetComposition([[1], [2, 3]])
print(f"\nSet Compositions: {set_comp1}, {set_comp2}")
```


### Quasi-symmetric functions

This package implements a construction of quasi-symmetric functions.
For a construction example, run the following:
```
print("Construct QSymFunction from a dictionary of monomial bases")
qsym_from_dict = QSymFunction(monomial_basis={"(1,2,1)": 2, "(2,1)": -1})
print("QSymFunction from dictionary:")
print(f"coefficients: {qsym_from_dict.coefficients}")
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



# To do

## Test cases

We are still building up our unit test library

## Efficiency

We are improving the construction of some methods related to computing stability of some set compositions with memorization.