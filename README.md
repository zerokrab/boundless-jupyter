# boundless-jupyter

This repo contains a Jupyter Notebook ([boundless_profitability.ipynb](/boundless_profitability.ipynb)) which models various scenarios to determine profitability.

Hosted at [jupyter.zerokrab.com](https://jupyter.zerokrab.com).

## Prerequisites

This repo can be run as-is, but some inputs require additional steps for best results.

### Epoch Data (`epochs.csv`)
To fetch the most up-to-date epoch data:
1. Goto https://explorer.boundless.network/epochs
2. In the top right click "Export CSV"
3. Replace the existing `epochs.csv` 

### Market Utilization
To calculate the average market utilization (% of PoVW from market orders) for a specific prover see [boundless-market-util](https://github.com/zerokrab/boundless-market-util). 

This is used as an input for modeling in the notebook (see 1.1 Model Parameters).

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

Most Python IDEs have support for running Jupyter Notebooks.