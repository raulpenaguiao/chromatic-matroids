# chromatic-matroids

A self-contained Python library for computing chromatic invariants of matroids.
No CAS required; the only runtime dependency is NumPy.

```bash
pip install chromatic-matroids
```

---

## Table of contents

1. [Quick start](#quick-start)
2. [Matroids](#matroids)
3. [Compositions and set compositions](#compositions-and-set-compositions)
4. [Quasi-symmetric functions](#quasi-symmetric-functions)
5. [Word quasi-symmetric functions (WQSym / NCQSym)](#word-quasi-symmetric-functions)
6. [Chromatic invariants](#chromatic-invariants)
7. [Lattice statistics](#lattice-statistics)
8. [Running the tests](#running-the-tests)

---

## Quick start

```python
from chromatic_matroids import (
    uniform_matroid,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    compute_chromatic_polynomial,
    z_rank, z_index,
)

m = uniform_matroid(3, 2)                         # U(3,2)
print(compute_chromatic_polynomial(m))            # [2, -3, 1]  →  (q-1)(q-2)
print(chromatic_quasisymmetric_function(m).coefficients)
# {'(1,1,1)': 6, '(1,2)': 3}
print(chromatic_non_commutative_quasisymmetric_function(m).coefficients)
# {'(1|2|3)': 1, '(1|3|2)': 1, ...}  (9 terms, all coefficient 1)
```

---

## Matroids

### Constructors

```python
from chromatic_matroids import (
    Matroid,
    uniform_matroid, schubert_matroid, nested_matroid, graphic_matroid,
)

# Explicit bases
m = Matroid(frozenset([1, 2, 3]), {frozenset([1, 2]), frozenset([1, 3]), frozenset([2, 3])})

# U(n, r): all r-subsets of {1, …, n} are bases
u = uniform_matroid(4, 2)

# Schubert matroid sh({1,…,n}, A): B = {b₁<…<bᵣ} is a basis iff bᵢ ≤ aᵢ for all i
s = schubert_matroid(4, frozenset([2, 3]))

# Nested matroid: chain of flats X₁ ⊂ X₂ ⊂ … with rank bounds
ne = nested_matroid(4, 2,
    (frozenset({1, 2}), frozenset({1, 2, 3, 4})),
    (1, 2))

# Graphic matroid: ground set = edges, bases = spanning forests
K3 = graphic_matroid([(1, 2), (1, 3), (2, 3)], {1, 2, 3})
```

The `Matroid` constructor validates the basis exchange axiom and raises if the input is invalid.

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `m.rank(S)` | `int` | Rank of a subset S |
| `m.independent_sets()` | `set[frozenset]` | All independent sets |
| `m.is_nested()` | `bool` | True if m is a nested matroid |
| `m.extend(e)` | `Matroid` | Add e as a coloop |
| `m.relabel(bij)` | `Matroid` | Relabel ground set via bijection dict |

### Generators

```python
from chromatic_matroids import (
    generate_schubert_matroids,            # all 2^n Schubert matroids on {1,…,n}
    generate_loopless_schubert_matroids,   # loopless subset
    generate_loopless_nested_matroids,     # all n! loopless nested matroids on {1,…,n}
    generate_nested_matroids_doublechains, # nested matroids from double chains
)

matroids = generate_loopless_nested_matroids(4)  # 24 matroids
```

---

## Compositions and set compositions

### Composition

A composition of n is an ordered list of positive integers summing to n.

```python
from chromatic_matroids import Composition

c = Composition([2, 1, 3])   # parts=[2,1,3], n=6
c = Composition("(2,1,3)")   # from string repr

c.rest()        # Composition([1, 3])
c.prepend(4)    # Composition([4, 2, 1, 3])

Composition.generate_all_composition(4)  # all 2^(n-1) compositions, cached
Composition.quasi_shuffles(Composition([1]), Composition([1]))
# {'(2)': 1, '(1,1)': 2}
```

### SetComposition

An ordered partition of a finite set of integers.

```python
from chromatic_matroids import SetComposition

sc = SetComposition([[1, 2], [3, 4], [5]])  # (1,2|3,4|5)
sc = SetComposition("(1,2|3,4|5)")          # from string repr

sc.first()    # frozenset({1, 2})
sc.rest()     # SetComposition([[3, 4], [5]])
sc.alpha()    # Composition([2, 2, 1])   — block sizes
sc.relabel({1: 10, 2: 20, 3: 30, 4: 40, 5: 50})
sc.relabel(None)  # standardise to {1, 2, …, n}

SetComposition.generate_all_setcompositions(3)  # 13 set compositions on {1,2,3}
SetComposition.quasi_shuffles(sc1, sc2)         # dict[str, int]
```

---

## Quasi-symmetric functions

`QSymFunction` represents an element of QSym in the monomial basis M_α.

```python
from chromatic_matroids import QSymFunction, Composition

f = QSymFunction(monomial_basis=Composition([1, 2]))       # M_{(1,2)}
g = QSymFunction(monomial_basis={"(1,2)": 2, "(3,)": -1})
zero = QSymFunction()

h = f + g            # addition
h = f * g            # quasi-shuffle product
h = f._scalarMultiple(3)

f.coefficients       # dict[str, int]
```

---

## Word quasi-symmetric functions

`NCQSymFunction` represents an element of WQSym in the monomial basis M_σ
indexed by set compositions.

```python
from chromatic_matroids import NCQSymFunction, SetComposition

sc = SetComposition([[1, 2], [3]])
f = NCQSymFunction(monomial_basis=sc)          # M_{(1,2|3)}
g = NCQSymFunction(monomial_basis="(1|2,3)")
h = NCQSymFunction(monomial_basis={"(1|2)": 2, "(2|1)": -1})

f + g                # addition
f * g                # quasi-shuffle product
f._scalarMultiple(3)
f.comu()             # forgetful map to QSym: M_σ ↦ M_{α(σ)}

f.coefficients       # dict[str, int]
```

---

## Chromatic invariants

```python
from chromatic_matroids import (
    compute_chromatic_polynomial,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    stable_matroids_setcompositions,
)

m = uniform_matroid(3, 2)

# Characteristic polynomial χ(M, q) = Σ_{A⊆E} (-1)^|A| q^{r(E)-r(A)}
# Returns [c₀, c₁, …, cᵣ] so that χ = c₀ + c₁q + … + cᵣqʳ
poly = compute_chromatic_polynomial(m)   # [2, -3, 1] → (q-1)(q-2)

# Chromatic QSym (commutative)
q = chromatic_quasisymmetric_function(m)
print(q.coefficients)   # {'(1,1,1)': 6, '(1,2)': 3}

# Chromatic WQSym (non-commutative lift)
nc = chromatic_non_commutative_quasisymmetric_function(m)
print(nc.coefficients)  # 9 terms, each coefficient 1

# Stability check: σ is stable for M if the greedy scoring has a unique maximiser
sc = SetComposition([[2], [1]])
stable_matroids_setcompositions(uniform_matroid(2, 1), sc)  # True
```

The chromatic WQSym is the sum of M_σ over all set compositions σ that are
*stable* for M (i.e. the score function Σᵢ |B ∩ Sᵢ| · i has a unique maximising
basis B). The QSym image is the forgetful map M_σ ↦ M_{α(σ)}.

---

## Lattice statistics

These functions analyse the integer lattice structure of the WQSym coefficient
matrix via the Smith Normal Form (SNF).

```python
from chromatic_matroids import (
    smith_normal_form_factors,
    z_rank,
    invariant_factors,
    z_index,
    generate_loopless_nested_matroids,
)

# SNF of an arbitrary integer matrix
smith_normal_form_factors([[2, 0], [0, 3]])   # [1, 6]
smith_normal_form_factors([[6, 4]])            # [2]

matroids = generate_loopless_nested_matroids(3)

z_rank(matroids)             # 6  (= 3!)
invariant_factors(matroids)  # [d₁, …, d₆] with d₁ | d₂ | … | d₆
z_index(matroids)            # d₁ · … · d₆ = [sat(M) : M]
```

**Z-index**: given the ℤ-module M spanned by the WQSym coefficient vectors,
its saturation is sat(M) = {x ∈ ℤᴺ : cx ∈ M for some c > 0}. The Z-index is
[sat(M) : M]; it equals 1 if and only if M is saturated.

---

## Running the tests

```bash
python3 -m venv venv && source venv/bin/activate
pip install -e "package[test]"
pytest package/tests/ -v
```

224 tests covering all modules, including parametrised rank theorems:
`z_rank = d!` and `QSym rank = 2^(d−1)` for loopless nested matroids of size d.

---

## License

MIT — see [LICENSE](LICENSE).
