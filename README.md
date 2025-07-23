This is a repo for all matroid related packages that are needed for research in algebraic combinatorics.


# Creation of packate


To create a package run

```bash
cd chromatic_matroids
python3 -m venv myenv
source myenv/bin/activate # On Windows, use `myenv\Scripts\activate`
python3 -m pip install --upgrade build
python3 -m pip install twine
python3 -m build
python3 -m twine upload dist/*
```

