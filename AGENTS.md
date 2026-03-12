# Agent guide: boundless-jupyter

Instructions for AI agents working on this project.

## Project purpose

**Core objective:** Assess the profitability of running a Boundless Prover by modeling scenarios that vary ZKC price and GPU configurations (e.g. 4090s/5090s, 4–8 GPUs).

- **README.md** – Domain background, costs, revenue (POVW + market). Read first for context.
- **boundless_profitability.ipynb** – Single Jupyter notebook: config → cost → revenue → profit → break-even → scenario tables/charts. All figures are **per epoch**. Inputs live under `## 1. Inputs`:
  - **1.1 Model Parameters**: `ZKC_PRICES_USD`, `MARKET_ORDER_UTIL`, `MARKET_REWARD_USD_PER_MHZ`, `FIXED_COST_MONTHLY_USD`, and `gpu_configs` (with `label`, `num_gpus`, `hourly_cost_usd`, `mhz`).
  - **1.2 Constants**: `HOURS_PER_EPOCH`, `SECONDS_PER_EPOCH`, `EPOCHS_PER_MONTH`.
  - **1.3 POVW Reward Data**: parsing logic that derives `POVW_ZKC_PER_MHZ_PER_EPOCH` from `epochs.csv`.
- **epochs.csv** – Data export: Total Cycles (all provers) and Mining Rewards (ZKC) per epoch. Used to compute **ZKC per mhz per epoch** for POVW. Updated as new data becomes available. The notebook excludes the **latest epoch** (row 1) as it may still be ongoing.
- **requirements.txt** – Python deps (jupyter, pandas, numpy, matplotlib, seaborn).

## Timeframe and units

- **Epoch** = 48 hours. This is the standard timeframe and the POVW reward cadence.
- All costs, revenue, and profit in the notebook are **per epoch**.
- ~15 epochs per 30-day month (`EPOCHS_PER_MONTH = 15`).
- **mhz** = million cycles per second (rate). In `gpu_configs` the column is `mhz`; million cycles per epoch is derived as `mhz * SECONDS_PER_EPOCH`.

## Domain terms

| Term | Meaning |
|------|--------|
| POVW rewards | ZKC distributed every epoch based on cycles proven; modeled as ZKC per mhz per epoch. |
| Market rewards | Per-proof payouts; modeled as average USD per mhz, scaled by **market order utilization** (share of capacity fulfilling market orders; e.g. 50%, 75%, 100%). POVW is unchanged by utilization. |
| ZKC | Cryptocurrency used in Boundless; price in USD is a key input. |
| GPU config | A labeled GPU setup (e.g. `Mock 5090 0.2 5090 x8`) with `label`, `num_gpus`, `mhz` (million cycles/sec), and `hourly_cost_usd`. |

## Conventions

- **Config in one place:** Inputs (ZKC prices, GPU table, POVW/market assumptions, fixed cost) live in the first code section of the notebook. Keep them easy to edit without changing the rest of the pipeline.
- **POVW from data:** `POVW_ZKC_PER_MHZ_PER_EPOCH` is computed from **epochs.csv** (Total Cycles and Mining Rewards); the latest epoch is always excluded. Do not replace this with a literal placeholder.
- **Placeholders:** Other inputs may use placeholders (e.g. `MARKET_REWARD_USD_PER_MHZ`, sample GPU rows). Preserve the structure; replace values with real data when available. Label placeholders in comments or markdown.
- **Cost conversion:** GPU rental is stored **per hour** (`hourly_cost_usd`) and converted to per-epoch as `rental_per_epoch_usd`. Fixed cost is monthly, converted to per-epoch with `EPOCHS_PER_MONTH`, and added **separately** when computing total cost (profit / break-even).
- **Market order utilization:** Configurable (e.g. 50%, 75%, 100%); market revenue = mhz × reward_per_mhz × util. POVW revenue is not scaled by utilization.

## What to change vs preserve

- **Safe to change:** Config values, extra GPU rows, ZKC price list, chart styling, extra sensitivity sections, adding cells for new scenarios or plots.
- **Preserve:** Epoch-based accounting (all flows per epoch), the split between POVW and market revenue, market revenue scaled by utilization, and the overall flow: config → cost → revenue → profit → scenario results.

## Plan reference

A detailed project plan exists (Boundless Prover Profitability Model); it specifies epoch as the standard timeframe, per-epoch costs/revenue, and the break-even formulation. Align structural changes with that plan.
