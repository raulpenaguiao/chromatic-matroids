#!/usr/bin/env bash
# One-time setup per machine: create .venv, install the package, register the Jupyter kernel.
set -euo pipefail
cd "$(dirname "$0")"

[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e package ipykernel jupyter
.venv/bin/python -m ipykernel install --user --name chromatic-matroids \
    --display-name "Python (chromatic-matroids .venv)"

echo "Done. Start Jupyter with: .venv/bin/jupyter lab notebooks/"
