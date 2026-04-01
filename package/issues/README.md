# Issues

For bugs and feedback, send an e-mail or open a GitHub issue.

---

## Open issues

### Issue: Formal test suite

Create a `package/tests/` directory with pytest-based unit tests, one file per source module:

```
package/tests/
├── __init__.py
├── test_compositions.py
├── test_setcompositions.py
├── test_quasisymmetric.py
├── test_ncquasisymmetric.py
├── test_matroids.py
├── test_generate_matroids_utils.py
├── test_stable_matroids_setcompositions.py
├── test_chromatic_statistics_matroids.py
├── test_chromatic.py
└── test_matrix_construction.py
```

Tests should cover all public functions exported in `__init__.py`.
Currently, tests live in `notebooks/00_unit_tests.ipynb` as assertion cells — these can serve as a reference.
The goal is to be able to run `pytest package/tests/` from the repo root.

---

### Issue: Browser UI

Build a web interface (Flask or Django) for interactive matroid creation and chromatic invariant display.

Requirements (from `goals.txt`):
- Input a matroid in several ways: Schubert matroid (select the Schubert set from a list), graphical matroid (click nodes and drag edges)
- Maintain a list of matroids being analysed; click "Calculate" to compute chromatic invariants
- Display chromatic QSym and NCQSym functions for each matroid
- Each matroid card shows: size, rank, number of bases, number of circuits; hover to see the full list of bases and circuits
- Host as a local server accessible from a browser
