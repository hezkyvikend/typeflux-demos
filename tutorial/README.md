# Tutorial

This folder is meant to be self-contained. The notebook installs the published
Typeflux dependencies through this folder's own `pyproject.toml`, so you can
work entirely from inside `tutorial/`.

The notebook reads its prompt from `prompts/explain.txt` and then loads that
text into an `InlineResolver`.

From inside `tutorial/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e .
```

After that, start Jupyter and open the notebook:

```bash
jupyter notebook
```
