# boundless-jupyter

A collection of jupyter notebooks exploring the cost/revenue/profit of running Boundless provers.

Visit [jupyter.zerokrab.com](https://jupyter.zerokrab.com) for a live hosted version of the notebooks.

## Notebooks

- [boundless_profitability.ipynb](/boundless_profitability.ipynb) - Models various scenarios to determine profitability.

## Usage

- **Online** - visit [jupyter.zerokrab.com](https://jupyter.zerokrab.com)
- **Local** - Requires Python 3.11+

See `How to run` at the top of the notebook.

## Local Development

### Prerequisites

Python 3.11+ is required.

### Install dependencies

```bash
pip install \
  jupyterlite-core \
  jupyterlite-pyodide-kernel \
  jupyter-server \
  panel \
  pandas numpy matplotlib nbconvert ipykernel
```

### Run the notebook

```bash
jupyter notebook
```

This opens the browser UI where you can run `boundless_profitability.ipynb` interactively.

### Build the full site (JupyterLite + Panel dashboard)

This replicates the CI/CD pipeline locally:

```bash
# 1. Execute the notebook to generate results.csv
jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.timeout=120 \
  boundless_profitability.ipynb \
  --output boundless_profitability.ipynb

# 2. Build JupyterLite static site
jupyter lite build \
  --contents boundless_profitability.ipynb \
  --contents epochs.csv \
  --contents dashboard.py \
  --output-dir _site

# 3. Build Panel standalone dashboard
panel convert dashboard.py \
  --to pyodide-worker \
  --out _site/dashboard/
cp results.csv _site/dashboard/results.csv

# 4. Copy CORS headers (needed for SharedArrayBuffer / Pyodide)
cp _headers _site/_headers
```

### Serve the built site locally

```bash
cd _site
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

> **Note:** Some browsers require CORS headers (`Cross-Origin-Opener-Policy` / `Cross-Origin-Embedder-Policy`) for Pyodide to work. The `_headers` file handles this on Cloudflare Pages. For local dev, you may need a server that sets these headers, or use the `jupyter notebook` workflow above instead.
