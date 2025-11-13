This is a repo for all matroid related packages that are needed for research in algebraic combinatorics.


# Package description

This package implements functions to compute the chromatic functions of a matroids. 
It works for both the commutative and non-commutative versions.

1. Matroid Classes & Utilities
- Matroid class for representing and validating matroids
- Generators for specific matroid types: uniform_matroid, graphic_matroid, schubert_matroid, nested_matroid
- Functions to generate families of matroids: generate_schubert_matroids, generate_loopless_nested_matroids,

2. Quasisymmetric Functions
- QSymFunction - Commutative quasi-symmetric functions
- NCQSymFunction - Non-commutative quasi-symmetric functions
- Operations on quasisymmetric functions

3. Combinatorial Structures
- Composition - Ordered partitions of integers
- SetComposition - Set compositions with quasi-shuffle operations

4. Chromatic Polynomials & Functions for Matroids
- compute_chromatic_polynomial() - Computes chromatic polynomial using Möbius inversion
- chromatic_quasisymmetric_function() - Chromatic QSym functions for matroids
- chromatic_non_commutative_quasisymmetric_function() - Chromatic NCQSym functions

5. Matrix Computations
- Functions for computing various matrices: compute_lowerbound_matrix, compute_conjecture_matrix, etc.
- Set composition conversion utilities


# Package creation
## Creation of package and upload to PyPI

To create a package run

```bash
cd chromatic_matroids
python3 -m venv venv
pip install numpy
source venv/bin/activate # On Windows, use `.\venv\Scripts\activate` -- do not type `source`
python3 -m pip install --upgrade build
python3 -m pip install twine
python3 -m build
python3 -m twine upload dist/*
```

Before uploading to PyPI, make sure to update the version in `pyproject.toml`, delete old versions from dist/ folder, and use the API key from your PyPI account.


## To install the local package for test

Make sure to force the install of the local package even if the version number did not change:
```bash
cd chromatic_matroids
python3 -m venv venv
source venv/bin/activate # On Windows, use `.\venv\Scripts\activate` -- do not type `source`
pip install numpy
pip install . --force-reinstall
pip install jupyter
```



# Run exploratory Jupyter notebooks

To run the Jupyter notebooks for exploration, first install the package locally as described above. Then, navigate to the `notebooks/` directory and start Jupyter Notebook or JupyterLab:

```bash
jupyter notebook
```