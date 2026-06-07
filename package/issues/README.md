# Issues

For bugs and feedback, send an e-mail or open a GitHub issue.

---

## Open issues

### Pyodide (zero server compute)

Move all matroid computations (QSym, WQSym, Z-rank, deduplication) to the browser via
[Pyodide](https://pyodide.org), eliminating the compute load on the VPS entirely.
The Flask server would serve only static files; the Python package would ship as a wheel
loaded in the browser worker.
Blocked on: stable Pyodide numpy support and acceptable load time for the wheel.

---

## Closed issues

### ✅ Formal test suite

**Resolved.** A full pytest suite lives in `package/tests/` (~200 tests, one file per source module). Run with:

```bash
pytest package/tests/ -v
```

or via `./run_frontend.sh` / `./run.sh` which run tests automatically before launching.

---

### ✅ Frontend UX polish

**Resolved.**
- Rename a matroid label: double-click the label on any card; press Enter or click away to save, Escape to cancel.
- Export list to JSON: "Export JSON" button in the matroid panel downloads `matroids.json`.
- "Clear duplicates" feedback: button is disabled and shows "Clearing…" while the server call is in flight.

---

### ✅ Browser UI

**Resolved.** A Flask frontend is in `frontend/`. Launch with:

```bash
./run_frontend.sh
```

Features implemented:
- Add matroids: Uniform, Nested, Schubert, Graphic (canvas editor), Matrix (column matroid), Custom bases
- Add entire families: all loopless nested of size n, all loopless nested of size n and rank r, all Schubert of size n and rank r
- Operations: delete elements, contract, direct sum (including with self)
- Inspect bases, select all, clear isomorphic duplicates
- Compute: QSym, WQSym, Z-rank
- Guard: n ≤ 9; 15 s computation timeout
- State stored in browser localStorage — multi-user safe, survives server restarts
