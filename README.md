# boundless-jupyter

A collection of Jupyter notebooks exploring the cost, revenue, and performance of running Boundless provers.

Visit [jupyter.zerokrab.com](https://jupyter.zerokrab.com) for a live hosted version.

## Notebooks

| Notebook | Description |
|----------|-------------|
| [boundless_profitability.ipynb](boundless_profitability.ipynb) | Models profitability across ZKC prices, GPU configs, and market reward rates |
| [prover_stats.ipynb](prover_stats.ipynb) | Fetches and visualizes your prover's order history and market vs mining cycle breakdown |

---

## Running the Notebooks

### Option 1 — Hosted (no setup)

Visit **[jupyter.zerokrab.com](https://jupyter.zerokrab.com)** — JupyterLite runs entirely in your browser, no installation required.

---

### Option 2 — JupyterLite Locally

Run the same browser-based JupyterLite environment on your machine.

> ⚠️ **Note:** `prover_stats.ipynb` **will not work** with local JupyterLite. The hosted version at `jupyter.zerokrab.com` works fine because it routes API calls through a CORS proxy at `proxy.jupyter.zerokrab.com`. When running JupyterLite from `localhost`, the browser origin is not in the proxy's allowed list, so requests are still blocked. Use [Option 3](#option-3--standard-jupyter-jupyterlab--classic-notebook) for local development with that notebook.

`boundless_profitability.ipynb` works fine with local JupyterLite as it doesn't make external API calls.

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
  --contents prover_stats.ipynb \
  --output-dir _site

# Serve locally
jupyter lite serve --output-dir _site
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Option 3 — Standard Jupyter (JupyterLab / Classic Notebook)

Most notebooks run fine with a standard Jupyter install. The one exception is **`prover_stats.ipynb`**, which uses `pyodide.http` for HTTP requests (a Pyodide-only API). To run it outside JupyterLite, replace the fetch helper in **Cell 4** with the `requests` equivalent:

```python
# Replace this (Pyodide only):
import pyodide.http
def fetch_json(url):
    return json.loads(pyodide.http.open_url(url).read())

# With this (standard Python):
import requests
def fetch_json(url):
    return requests.get(url).json()
```

You'll also need to install `requests` if it isn't already available:

```bash
pip install requests
```

**Install and run:**

```bash
pip install -r requirements.txt
jupyter lab
# or: jupyter notebook
```

Then open the notebook file directly from the JupyterLab file browser.
