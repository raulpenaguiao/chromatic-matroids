# chromatic-matroids

A self-contained Python library for computing chromatic invariants of matroids in both the commutative and non-commutative settings.
No external CAS (SageMath, SymPy) is required — the library depends only on NumPy (and optionally SciPy/pandas for the research notebooks).

---

## Mathematical background

Given a matroid M on ground set E, this library computes:

| Invariant | Symbol | Space |
|---|---|---|
| Chromatic polynomial | χ(M, q) | ℤ[q] |
| Chromatic quasisymmetric function | Ψ(M) | QSym |
| Chromatic non-commutative quasisymmetric function | Ψ̃(M) | NCQSym |

The chromatic NCQSym function is defined via **stable set compositions**: a set composition π = (π₁ | π₂ | … | πₖ) of E is *stable* for M if there is a unique basis B that maximises the score Σᵢ i·|B ∩ πᵢ|. Then

    Ψ̃(M) = Σ_{π stable} M_π

where M_π is the monomial basis element of NCQSym indexed by π.
The commutative version is obtained by the forgetful map π ↦ (|π₁|, |π₂|, …, |πₖ|).

The main research conjecture implemented here concerns the **rank of the chromatic NCQSym map** on families of nested matroids; see `writeout/SM_Qsym_Draft.pdf` for the full statement.

---

## Package structure

```
chromatic_matroids/
├── src/
│   └── chromatic_matroids/
│       ├── __init__.py                        # public API
│       ├── compositions.py                    # Composition class
│       ├── setcompositions.py                 # SetComposition class
│       ├── quasisymmetric.py                  # QSymFunction class
│       ├── ncquasisymmetric.py                # NCQSymFunction class
│       ├── matroids.py                        # Matroid class
│       ├── generate_matroids_utils.py         # matroid generators
│       ├── stable_matroids_setcompositions.py # stability check
│       ├── chromatic_statistics_matorids.py   # chromatic functions
│       ├── chromatic.py                       # chromatic polynomial
│       └── matrix_construction.py            # conjecture matrices
├── notebooks/
│   ├── 00_unit_tests.ipynb                   # full test suite (verbose)
│   ├── 01_comprehensive_api_guide.ipynb      # usage guide for every function
│   └── 02_matrix_computation_examples.ipynb  # research computations
└── pyproject.toml
```

---

## Installation

### From PyPI

```bash
pip install chromatic-matroids
```

### Local development install

```bash
cd chromatic_matroids
python3 -m venv venv
# Windows:  .\venv\Scripts\activate
source venv/bin/activate
pip install numpy
pip install . --force-reinstall
pip install jupyter          # to run notebooks
```

### Build and upload to PyPI

```bash
cd chromatic_matroids
source venv/bin/activate
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload dist/*
```

Before uploading: bump the version in `pyproject.toml` and delete stale files from `dist/`.

---

## Running the notebooks

```bash
cd chromatic_matroids
source venv/bin/activate    # or .\venv\Scripts\activate on Windows
jupyter notebook
```

Open `notebooks/00_unit_tests.ipynb` for the test suite, or `notebooks/01_comprehensive_api_guide.ipynb` for usage examples.

---

## Quick-start examples

```python
from chromatic_matroids import (
    uniform_matroid, schubert_matroid, nested_matroid,
    generate_loopless_nested_matroids,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    compute_chromatic_polynomial,
    Composition, SetComposition, QSymFunction, NCQSymFunction,
)

# --- Matroids ---
m = uniform_matroid(3, 2)          # U(3,2): all pairs from {1,2,3} are bases
m2 = schubert_matroid(4, frozenset([2, 3]))  # sh({1,2,3,4}, {2,3})

# --- Chromatic polynomial ---
poly = compute_chromatic_polynomial(m)
# poly = [2, -3, 1]  →  q² - 3q + 2 = (q-1)(q-2)

# --- Chromatic NCQSym function ---
nc = chromatic_non_commutative_quasisymmetric_function(uniform_matroid(2, 1))
# nc.coefficients = {'(2|1)': 1, '(1|2)': 1}  →  M_{(2|1)} + M_{(1|2)}

# --- Chromatic QSym function ---
c = chromatic_quasisymmetric_function(uniform_matroid(2, 1))
# c.coefficients = {'(1,1)': 2}  →  2 M_{(1,1)}
```

---

## API reference

### `Composition`

Represents an ordered tuple of positive integers (a composition of n).

```python
Composition([2, 1, 3])   # from list      → (2,1,3)
Composition((1, 2))       # from tuple
Composition("(2,1,3)")   # from string
Composition()             # empty composition of 0
```

**Attributes:** `parts: list[int]`, `n: int` (total), `nparts: int`

**Methods:**

| Method | Description |
|---|---|
| `rest()` | New composition without the first part |
| `prepend(a)` | New composition with `a` prepended |
| `generate_all_composition(n)` | All compositions of n (memoized) |
| `quasi_shuffles(q, t)` | Dict of quasi-shuffles with multiplicities |

Compositions of size ≤ 4 and all their quasi-shuffles are precomputed at import time.

---

### `SetComposition`

Represents an ordered partition of a finite subset of ℤ₊.

```python
SetComposition([[1, 4], [2], [3, 5, 6]])  # from list of lists
SetComposition("(1,4|2|3,5,6)")            # from string
SetComposition()                            # empty
```

**Attributes:** `parts: list[list[int]]`, `ground_set: list[int]`

**Methods:**

| Method | Description |
|---|---|
| `first()` | First part as `frozenset` |
| `rest()` | New set composition without the first part |
| `prepend(a)` | New set composition with frozenset `a` prepended |
| `alpha()` | Underlying `Composition` of part sizes |
| `relabel(map)` | Relabeled copy. `map` can be a `dict`, `list`, or `None` (→ {1,…,n}) |
| `generate_all_setcompositions(n)` | All set compositions of {1,…,n} (memoized) |
| `quasi_shuffles(q, t)` | Dict-of-strings quasi-shuffles; q and t must be disjoint |

Set compositions of size ≤ 3 and all their quasi-shuffles are precomputed at import time.

---

### `QSymFunction`

A quasisymmetric function represented in the monomial basis M_α.

```python
QSymFunction(monomial_basis=Composition([2, 1]))           # M_{(2,1)}
QSymFunction(monomial_basis=(Composition([1, 3]), -2))     # -2 M_{(1,3)}
QSymFunction(monomial_basis={'(1,2)': 3, '(2,1)': -1})    # 3 M_{(1,2)} - M_{(2,1)}
QSymFunction()                                              # zero
```

**Attribute:** `coefficients: dict[str, int]`

**Operations:** `f + g`, `f * g` (quasi-shuffle product), `f._scalarMultiple(c)`

All operations return new objects and **do not mutate** the operands.

---

### `NCQSymFunction`

A non-commutative quasisymmetric function in the monomial basis M_π.

```python
NCQSymFunction(monomial_basis=SetComposition([[1, 2], [3]]))  # M_{(1,2|3)}
NCQSymFunction(monomial_basis="(1,2|3)")                       # same
NCQSymFunction(monomial_basis={'(1,2|3)': 2, '(1|2,3)': -1}) # 2 M_{(1,2|3)} - M_{(1|2,3)}
NCQSymFunction()                                               # zero
```

**Attribute:** `coefficients: dict[str, int]`

**Operations:** `f + g`, `f * g` (quasi-shuffle product), `f._scalarMultiple(c)`, `f.comu()` (→ QSymFunction)

All operations return new objects and **do not mutate** the operands.

---

### `Matroid`

Core matroid class validated on construction against the basis exchange axiom.

```python
Matroid(ground_set: frozenset[int], bases_sets: set[frozenset])
```

**Attributes:** `ground_set`, `bases_sets`

**Methods:**

| Method | Description |
|---|---|
| `rank(subset)` | Rank of a subset (max intersection with any basis) |
| `independent_sets()` | All subsets of all bases |
| `is_nested()` | True iff the lattice of flats is a chain |
| `extend(element)` | Coloop extension: adds `element` to every basis (rank +1) |
| `relabel(bijection)` | Returns a relabeled copy |

**`is_nested` characterisation:** A matroid is nested (Bonin–de Mier) if and only if its flats are totally ordered by inclusion. This is checked directly by computing all flats and verifying the chain condition.

**`extend` semantics:** Adding a *coloop* — an element that belongs to every basis. If M has bases B(M), then `M.extend(e)` has bases {B ∪ {e} : B ∈ B(M)} and rank r(M)+1.

---

### Matroid generators

```python
uniform_matroid(n, r)
# U(n,r): ground set {1,...,n}, all r-subsets are bases

schubert_matroid(n, A)
# sh({1,...,n}, A): B={b₁<…<bᵣ} is a basis iff bᵢ ≤ aᵢ for all i

nested_matroid(n, rank, X, R)
# X = chain of sets, R = chain of ranks
# B is a basis iff |B ∩ Xᵢ| ≤ Rᵢ for all i and |B| = rank

graphic_matroid(edges, vertex_set)
# Ground set = edges, bases = spanning forests

generate_schubert_matroids(n)            # all Schubert matroids on {1,...,n}
generate_loopless_schubert_matroids(n)   # loopless subset
generate_loopless_nested_matroids(d)     # all loopless nested matroids of size d
generate_nested_matroids_doublechains(d) # double-chain data for the above
```

---

### Chromatic invariants

```python
compute_chromatic_polynomial(matroid)
# Returns list [c₀, c₁, ..., cᵣ] where χ(M,q) = Σ cₖ qᵏ
# Formula: χ(M,q) = Σ_{A⊆E} (-1)^|A| q^{r(E)-r(A)}

chromatic_non_commutative_quasisymmetric_function(matroid)
# Returns NCQSymFunction: Σ_{π stable} M_π

chromatic_quasisymmetric_function(matroid)
# Returns QSymFunction: commutative image of the above

stable_matroids_setcompositions(matroid, set_composition)
# Returns True if set_composition is stable for matroid
```

---

### Matrix construction utilities (research)

These implement the matrices from the main paper.

```python
compute_lowerbound_matrix(d)
# Square matrix indexed by valid subsets of {1,...,d}
# Entry (A,B) = 1 iff sh({1,...,d}, A) is stable for the set composition of B

compute_conjecture_matrix(d)
# Rows = loopless nested matroids of size d
# Columns = min-max set compositions (from permutations of {1,...,d})

compute_conjecture_big_matrix(d)
# Same rows, columns = all set compositions of {1,...,d}

compute_conjecture_alternatingsum_matrix(d)
# Alternating-sign version of the conjecture matrix

from_set_to_set_composition(input_set, d)
# Converts a subset of {1,...,d} to a set composition

generate_valid_subsets(d)
# Subsets of {1,...,d} that index loopless Schubert matroids

min_max_set_composition(permutation)
# Splits a permutation at descent positions into a set composition

generate_min_max_set_compositions(d)
# All d! min-max set compositions
```

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `notebooks/00_unit_tests.ipynb` | Full test suite. Run top-to-bottom: every cell uses `assert` and prints verbose output. A clean run means all tests pass. |
| `notebooks/01_comprehensive_api_guide.ipynb` | Usage guide for every public function with printed output. |
| `notebooks/02_matrix_computation_examples.ipynb` | Research: rank computations, dimension sweeps, conjecture matrices. |
| `notebooks/03_min_max_conjecture_testing.ipynb` *(outer `notebooks/`)* | Research: conjecture 1 and 2 (min-max matrix non-singularity). |

---

## Known limitations / future work

- `Matroid.is_nested` uses brute-force flat enumeration (exponential in |E|). Suitable for |E| ≤ 12.
- `Matroid._validate_matroid` checks the exchange axiom in O(|B|² · |E|) time. For large matroids, construction can be slow.
- The browser interface described in `goals.txt` is not yet implemented.
- `Matroid.independent_sets()` recomputes on every call (no caching). For repeated access, cache the result yourself: `ind = m.independent_sets()`.

---

## Contributing

Contributions and issue reports are welcome at the project repository.

## License

MIT License — see `chromatic_matroids/LICENSE`.
