# boundless-jupyter

A collection of jupyter notebooks exploring the cost/revenue/profit of running Boundless provers.

## Notebooks

- [boundless_profitability.ipynb](/boundless_profitability.ipynb) - Models various scenarios to determine profitability.

## Usage

### Option 1 — Hosted (no setup)

Visit **[jupyter.zerokrab.com](https://jupyter.zerokrab.com)** — JupyterLite runs entirely in your browser, no installation required.

---

### Option 2 — JupyterLite Locally

Run the same browser-based JupyterLite environment on your machine. All notebooks work identically to the hosted version.

**Requirements:** Python 3.9+, `pip`

```bash
# Install dependencies
pip install -r requirements.txt
pip install jupyterlite-core jupyterlite-pyodide-kernel

# Build the JupyterLite site
jupyter lite build \
  --contents boundless_profitability.ipynb \
  --contents epochs.csv \
  --contents dashboard.py \
  --output-dir _site

# Serve locally
jupyter lite serve --output-dir _site
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Option 3 — IDE

Most Python compatible IDEs have support for running Jupyter Notebooks.