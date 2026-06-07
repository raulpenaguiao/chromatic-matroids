#!/usr/bin/env bash
set -euo pipefail

VENV=".venv"

# --- Setup ---
if [ ! -d "$VENV" ]; then
    echo "[run.sh] Creating virtual environment..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

echo "[run.sh] Installing package..."
pip install -e package --quiet
pip install pytest numpy --quiet

# --- Unit tests ---
echo ""
echo "========================================"
echo "  Running unit tests"
echo "========================================"
pytest package/tests/ -v
echo ""

# --- Matrix computations ---
echo "========================================"
echo "  Matrix computations (sizes 2–5)"
echo "========================================"
python3 - <<'PYEOF'
import numpy as np
from chromatic_matroids import (
    compute_conjecture_matrix,
    compute_lowerbound_matrix,
    generate_loopless_nested_matroids,
    generate_min_max_set_compositions,
)

for d in range(2, 6):
    print(f"\n--- d = {d} ---")

    lb = compute_lowerbound_matrix(d)
    lb_arr = np.array(lb, dtype=float)
    print(f"  Lower-bound matrix:  {len(lb)} x {len(lb[0])},  rank = {int(np.linalg.matrix_rank(lb_arr))}")

    mat, set_list, chains = compute_conjecture_matrix(d)
    mat_arr = np.array(mat, dtype=float)
    n_matroids = len(generate_loopless_nested_matroids(d))
    n_comps = len(generate_min_max_set_compositions(d))
    print(f"  Conjecture matrix:   {n_matroids} x {n_comps},  rank = {int(np.linalg.matrix_rank(mat_arr))}")
PYEOF

echo ""
echo "Done. All checks passed."
echo ""
echo "To launch the web interface:"
echo "  source .venv/bin/activate"
echo "  pip install flask --quiet"
echo "  python3 -m frontend.app"
echo "  Then open http://localhost:5001/chromatic-matroids/"
