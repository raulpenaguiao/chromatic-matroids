# chromatic-matroids

A self-contained Python library for computing chromatic invariants of matroids — chromatic polynomial, chromatic quasisymmetric function (QSym), and chromatic non-commutative quasisymmetric function (WQSym/NCQSym).
No external CAS required; the only runtime dependency is NumPy.

---

## Contents

1. [Getting started](#1-getting-started)
   - [Install](#install)
   - [Quick-start examples](#quick-start-examples)
   - [Web UI](#web-ui)
   - [Notebooks](#notebooks)
2. [API reference](#2-api-reference)
   - [Composition](#composition)
   - [SetComposition](#setcomposition)
   - [QSymFunction](#qsymfunction)
   - [NCQSymFunction](#ncqsymfunction)
   - [Matroid](#matroid)
   - [Matroid generators](#matroid-generators)
   - [Chromatic invariants](#chromatic-invariants)
   - [Matrix construction (research)](#matrix-construction-research)
3. [Developer guide](#3-developer-guide)
   - [Running tests](#running-tests)
   - [Repo structure](#repo-structure)
   - [Releasing to PyPI](#releasing-to-pypi)
   - [Deploying the frontend](#deploying-the-frontend)
   - [CI/CD overview](#cicd-overview)

---

## 1. Getting started

### Install

**From PyPI:**

```bash
pip install chromatic-matroids
```

**Local development install** (changes to source take effect immediately):

```bash
python3 -m venv venv && source venv/bin/activate
pip install -e package
```

> **Note:** On systems with an externally-managed Python (PEP 668, e.g. Ubuntu 23+) always use a virtual environment.

### Quick-start examples

```python
from chromatic_matroids import (
    uniform_matroid,
    nested_matroid,
    graphic_matroid,
    generate_loopless_nested_matroids,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    compute_chromatic_polynomial,
)

# ── Build matroids ────────────────────────────────────────────────────────────
u = uniform_matroid(3, 2)               # U(3,2): all pairs of {1,2,3} are bases
K3 = graphic_matroid([(1,2),(1,3),(2,3)], {1,2,3})  # graphic matroid of K₃
# Note: K3.ground_set = {(1,2),(1,3),(2,3)} — edge tuples, not integers.
# Relabel to integers before computing chromatic functions:
K3 = K3.relabel({e: i+1 for i, e in enumerate(sorted(K3.ground_set))})

# Nested matroid: ground set {1,2,3,4}, rank 2, chain X₁={1,2} ⊂ X₂={1,2,3,4},
# rank bounds R=(1,2)
ne = nested_matroid(4, 2,
    (frozenset({1,2}), frozenset({1,2,3,4})),
    (1, 2))

# ── Chromatic polynomial ──────────────────────────────────────────────────────
poly = compute_chromatic_polynomial(u)
# [2, -3, 1]  →  q² - 3q + 2 = (q-1)(q-2)

# ── Chromatic QSym (commutative) ──────────────────────────────────────────────
q = chromatic_quasisymmetric_function(uniform_matroid(2, 1))
print(q.coefficients)   # {'(1,1)': 2}  →  2 M_{(1,1)}

# ── Chromatic WQSym (non-commutative) ────────────────────────────────────────
nc = chromatic_non_commutative_quasisymmetric_function(uniform_matroid(2, 1))
print(nc.coefficients)  # {'(2|1)': 1, '(1|2)': 1}

# ── Sweep over a family ───────────────────────────────────────────────────────
for m in generate_loopless_nested_matroids(4):
    f = chromatic_non_commutative_quasisymmetric_function(m)
    print(m.rank(m.ground_set), f.coefficients)
```

---

### Web UI

The repository ships with a Flask frontend for interactive exploration.

**Launch:**

```bash
./run_frontend.sh
```

This creates a virtual environment, installs all dependencies, runs the test suite, and starts a gunicorn server at:

```
http://localhost:5001/chromatic-matroids/
```

**What you can do in the UI:**

| Feature | How |
|---|---|
| Add a uniform matroid U(n, r) | **+ Add → Uniform** tab |
| Add a nested matroid | **+ Add → Nested** tab — enter layers and rank bounds |
| Add all loopless nested matroids of size n | **+ Add → Nested → Add all loopless (size n)** |
| Add a graphic matroid | **+ Add → Graphic** tab — click to place vertices, drag to add edges |
| Add a matroid by listing its bases | **+ Add → Custom bases** tab |
| Inspect the bases of a matroid | **Inspect bases** button on the matroid card |
| Delete elements / contract | **Delete elems** or **Contract** buttons on the card |
| Direct sum of two matroids | **⊕ Direct sum** button on the card |
| Compute QSym or WQSym | Check matroids, click **QSym** or **WQSym** in the toolbar |
| Compute Z-rank of the WQSym span | Check matroids, click **Z-rank** |

The matroids panel is on the left; computation results appear on the right.

---

### Notebooks

```bash
pip install -e package jupyter
jupyter notebook notebooks/
```

Each notebook auto-installs the package in its first cell, so you can also just open and run.

| Notebook | Purpose |
|---|---|
| `00_unit_tests.ipynb` | Full test suite with verbose output |
| `01_comprehensive_api_guide.ipynb` | Usage examples for every public function |
| `02_matrix_computation_examples.ipynb` | Research: rank computations, dimension sweeps, conjecture matrices |
| `03_min_max_conjecture_testing.ipynb` | Research: conjecture 1 and 2 (min-max matrix non-singularity) |

---

## 2. API reference

### `Composition`

An ordered tuple of positive integers.

```python
from chromatic_matroids import Composition

Composition([2, 1, 3])    # from list   → (2,1,3)
Composition("(2,1,3)")    # from string
Composition()             # empty composition of 0
```

**Attributes:** `parts: list[int]`, `n: int`, `nparts: int`

| Method | Returns | Description |
|---|---|---|
| `rest()` | `Composition` | Drop the first part |
| `prepend(a)` | `Composition` | Prepend integer `a` |
| `generate_all_composition(n)` | `list[Composition]` | All compositions of n (memoized) |
| `quasi_shuffles(q, t)` | `dict[str, int]` | Quasi-shuffles of self with multiplicities; `q`, `t` are `Composition` |

Compositions of size ≤ 4 and their quasi-shuffles are precomputed at import time.

---

### `SetComposition`

An ordered partition of a finite set of positive integers.

```python
from chromatic_matroids import SetComposition

SetComposition([[1, 4], [2], [3]])   # from list of lists → (1,4|2|3)
SetComposition("(1,4|2|3)")          # from string
SetComposition()                     # empty
```

**Attributes:** `parts: list[list[int]]`, `ground_set: list[int]`

| Method | Returns | Description |
|---|---|---|
| `first()` | `frozenset` | First part |
| `rest()` | `SetComposition` | Drop the first part |
| `prepend(a)` | `SetComposition` | Prepend frozenset `a` |
| `alpha()` | `Composition` | Underlying composition of part sizes |
| `relabel(map)` | `SetComposition` | `map` can be a `dict`, `list`, or `None` (→ canonical {1,…,n}) |
| `generate_all_setcompositions(n)` | `list[SetComposition]` | All set compositions of {1,…,n} (memoized) |
| `quasi_shuffles(q, t)` | `dict[str, int]` | Quasi-shuffles; `q`, `t` must be disjoint `SetComposition` |

Set compositions of size ≤ 3 and their quasi-shuffles are precomputed at import time.

---

### `QSymFunction`

A quasisymmetric function in the monomial basis M_α.

```python
from chromatic_matroids import QSymFunction, Composition

QSymFunction(monomial_basis=Composition([2, 1]))        # M_{(2,1)}
QSymFunction(monomial_basis=(Composition([1,3]), -2))   # -2 M_{(1,3)}
QSymFunction(monomial_basis={'(1,2)': 3, '(2,1)': -1}) # 3 M_{(1,2)} - M_{(2,1)}
QSymFunction()                                          # zero
```

**Attribute:** `coefficients: dict[str, int]`

**Operations:** `f + g`, `f * g` (quasi-shuffle product), `f._scalarMultiple(c)`

All operations return new objects; operands are not mutated.

---

### `NCQSymFunction`

A non-commutative quasisymmetric function in the monomial basis M_π.

```python
from chromatic_matroids import NCQSymFunction, SetComposition

NCQSymFunction(monomial_basis=SetComposition([[1,2],[3]]))    # M_{(1,2|3)}
NCQSymFunction(monomial_basis="(1,2|3)")                     # same
NCQSymFunction(monomial_basis={'(1,2|3)': 2, '(1|2,3)': -1})
NCQSymFunction()                                             # zero
```

**Attribute:** `coefficients: dict[str, int]`

**Operations:** `f + g`, `f * g` (quasi-shuffle product), `f._scalarMultiple(c)`, `f.comu()` (→ `QSymFunction`)

---

### `Matroid`

Core matroid class. The basis exchange axiom is validated on construction.

```python
from chromatic_matroids import Matroid

Matroid(ground_set=frozenset({1,2,3}), bases_sets={frozenset({1,2}), frozenset({1,3}), frozenset({2,3})})
```

**Attributes:** `ground_set: frozenset`, `bases_sets: set[frozenset]`

| Method | Returns | Description |
|---|---|---|
| `rank(subset)` | `int` | Max size of `subset ∩ B` over all bases `B` |
| `independent_sets()` | `set[frozenset]` | All subsets of all bases |
| `is_nested()` | `bool` | True iff flats are totally ordered by inclusion (Bonin–de Mier) |
| `extend(element)` | `Matroid` | Coloop extension: adds `element` to every basis (rank +1) |
| `relabel(bijection)` | `Matroid` | Relabelled copy; `bijection` is a `dict` |

**Notes:**
- `is_nested` uses brute-force flat enumeration — suitable for |E| ≤ ~12.
- `independent_sets()` recomputes on every call; cache it yourself if you call it repeatedly.

---

### Matroid generators

```python
from chromatic_matroids import (
    uniform_matroid, schubert_matroid, nested_matroid, graphic_matroid,
    generate_schubert_matroids, generate_loopless_schubert_matroids,
    generate_loopless_nested_matroids, generate_nested_matroids_doublechains,
)

uniform_matroid(n, r)
# U(n,r): ground set {1,...,n}, all r-element subsets are bases

schubert_matroid(n, A)
# sh({1,...,n}, A): B = {b₁ < ... < bᵣ} is a basis iff bᵢ ≤ aᵢ for all i

nested_matroid(n, rank, X, R)
# X = tuple of frozensets forming a chain, R = tuple of rank bounds
# B is a basis iff |B ∩ Xᵢ| ≤ Rᵢ for all i and |B| = rank

graphic_matroid(edges, vertex_set)
# Ground set = edges (as (u,v) tuples), bases = edge-sets of spanning forests

generate_schubert_matroids(n)            # all Schubert matroids on {1,...,n}
generate_loopless_schubert_matroids(n)   # loopless subset
generate_loopless_nested_matroids(d)     # all loopless nested matroids of size d
generate_nested_matroids_doublechains(d) # (n, rank, X, R) tuples for the above
```

---

### Chromatic invariants

```python
from chromatic_matroids import (
    compute_chromatic_polynomial,
    chromatic_quasisymmetric_function,
    chromatic_non_commutative_quasisymmetric_function,
    stable_matroids_setcompositions,
)

compute_chromatic_polynomial(matroid)
# Returns list [c₀, c₁, ..., cᵣ] where χ(M,q) = Σ cₖ qᵏ
# Uses inclusion-exclusion: χ(M,q) = Σ_{A⊆E} (-1)^|A| q^{r(E)−r(A)}

chromatic_non_commutative_quasisymmetric_function(matroid)
# Returns NCQSymFunction: Σ_{π stable} M_π

chromatic_quasisymmetric_function(matroid)
# Returns QSymFunction: commutative image of the WQSym function

stable_matroids_setcompositions(matroid, set_composition)
# Returns True if set_composition is stable for matroid
# (unique basis maximising the score Σᵢ i·|B ∩ πᵢ|)
```

---

### Matrix construction (research)

```python
from chromatic_matroids import (
    compute_lowerbound_matrix,
    compute_conjecture_matrix,
    compute_conjecture_big_matrix,
    compute_conjecture_alternatingsum_matrix,
    from_set_to_set_composition,
    generate_valid_subsets,
    min_max_set_composition,
    generate_min_max_set_compositions,
)

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

generate_valid_subsets(d)
# Subsets of {1,...,d} indexing loopless Schubert matroids

min_max_set_composition(permutation)
# Splits a permutation at descent positions into a set composition

generate_min_max_set_compositions(d)
# All d! min-max set compositions of {1,...,d}
```

---

## 3. Developer guide

### Running tests

The test suite lives in `package/tests/` and uses pytest.

```bash
# Quickest path (reuses any existing venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -e "package[test]"
pytest package/tests/ -v
```

Or just run the all-in-one script that also starts the frontend afterward:

```bash
./run_frontend.sh
```

---

### Repo structure

```
chromatic-matroids/
├── package/
│   ├── src/chromatic_matroids/   ← source (10 modules)
│   ├── tests/                    ← pytest suite (~200 tests)
│   └── pyproject.toml            ← hatchling build, version x.x.x
├── frontend/
│   ├── app.py                    ← Flask app factory
│   ├── routes.py                 ← stateless Blueprint: /api/create/*, /api/ops/*, /api/compute/*
│   ├── operations.py             ← delete / contract / direct-sum helpers
│   ├── templates/index.html
│   └── static/                   ← style.css, app.js, graph_editor.js
├── notebooks/                    ← 4 Jupyter notebooks (00–03)
├── .github/workflows/
│   ├── ci.yml                    ← pytest on every push to main
│   ├── release.yml               ← PyPI publish on tag release-x.x.x
│   └── deploy-frontend.yml       ← VPS deploy on tag frontend
├── run.sh                        ← run tests + print research output
├── run_frontend.sh               ← run tests + launch gunicorn
└── requirements.txt              ← numpy (runtime)
```

---

### Releasing to PyPI

1. Bump `version` in `package/pyproject.toml`.
2. Commit and push to `main`.
3. Push a tag matching `release-x.x.x`:

```bash
git tag release-0.1.0
git push origin release-0.1.0
```

The `release.yml` workflow will: run tests, verify the tag version matches `pyproject.toml`, build the wheel + sdist, and publish via PyPI Trusted Publishing (no API token required — configure the publisher once on PyPI under the project's Publishing settings).

---

### Deploying the frontend

The frontend runs as a gunicorn service behind nginx on a VPS.

**nginx config** (add inside your `server {}` block):

```nginx
location /chromatic-matroids {
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**systemd unit** (`/etc/systemd/system/chromatic-matroids.service`):

```ini
[Unit]
Description=Chromatic Matroids frontend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/chromatic-matroids
ExecStart=/var/www/chromatic-matroids/.venv/bin/gunicorn \
    --bind 127.0.0.1:5001 --workers 1 \
    "frontend.app:create_app()"
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now chromatic-matroids
```

> **Architecture note:** the server is fully stateless — all matroid state lives in the browser's `localStorage`. Multiple gunicorn workers are safe. Computations are guarded: n ≤ 9 and a 15 s timeout per request.

**Automated deploy:** push the tag `frontend` and the `deploy-frontend.yml` workflow SSHes into the VPS, pulls the latest code, reinstalls the package, and restarts the service. Configure these secrets in GitHub → Settings → Secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_SSH_PORT`.

---

### CI/CD overview

| Trigger | Workflow | What it does |
|---|---|---|
| Push / PR to `main` | `ci.yml` | Installs package + pytest deps, runs full test suite |
| Tag `release-x.x.x` | `release.yml` | Tests → version check → build → PyPI publish |
| Tag `frontend` | `deploy-frontend.yml` | SSH to VPS → git pull → pip install → systemctl restart |
