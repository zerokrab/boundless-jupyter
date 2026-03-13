"""
Boundless Prover Profitability Dashboard

Self-contained Panel app. Can be:
  - Imported in the notebook:  from dashboard import dashboard
  - Served standalone:         panel serve dashboard.py
  - Converted to static HTML:  panel convert dashboard.py --to pyodide-worker --out dist/
"""

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import panel as pn

pn.extension()

# ── Model Parameters (mirrors notebook section 1.1) ───────────────────────────

MARKET_REWARD_USD_PER_MHZ = 0.00007
FIXED_COST_MONTHLY_USD = 0

gpu_configs = pd.DataFrame([
    {"label": "RTX5090 x 8", "num_gpus": 8, "usd_per_hour": 0.50, "mhz": 1.1},
    {"label": "RTX5090 x 4", "num_gpus": 4, "usd_per_hour": 0.55, "mhz": 1.1},
    {"label": "RTX4090 x 8", "num_gpus": 8, "usd_per_hour": 0.40, "mhz": 0.9},
])

# ── Constants ─────────────────────────────────────────────────────────────────

HOURS_PER_EPOCH = 48
SECONDS_PER_EPOCH = HOURS_PER_EPOCH * 3600
EPOCHS_PER_MONTH = 30 * 24 / HOURS_PER_EPOCH
EPOCH_LOOKBACK_COUNT = 10

# ── Derived calculations ───────────────────────────────────────────────────────

gpu_configs["rental_per_epoch_usd"] = (
    gpu_configs["usd_per_hour"] * gpu_configs["num_gpus"] * HOURS_PER_EPOCH
)
gpu_configs["mhz_per_epoch"] = (
    gpu_configs["mhz"] * gpu_configs["num_gpus"] * SECONDS_PER_EPOCH
)

# ── POVW reward from epochs.csv ───────────────────────────────────────────────

def _parse_cycles(s):
    s = str(s).strip().upper().replace(",", "")
    if not s or s == "0":
        return 0.0
    m = re.match(r"^([\d.]+)\s*([TGMK]?)$", s)
    if not m:
        return np.nan
    val, suffix = float(m.group(1)), m.group(2) or ""
    return val * {"T": 1e12, "G": 1e9, "M": 1e6, "K": 1e3}.get(suffix, 1)


def _parse_zkc(s):
    s = str(s).strip().replace(",", "").replace(" ZKC", "").upper()
    if not s or s == "0":
        return 0.0
    m = re.match(r"^([\d.]+)\s*([KMB]?)$", s)
    if not m:
        return np.nan
    val, suffix = float(m.group(1)), m.group(2) or ""
    return val * {"B": 1e9, "M": 1e6, "K": 1e3}.get(suffix, 1)


epochs = pd.read_csv("epochs.csv")
epochs_complete = epochs.iloc[1:].copy()
epochs_complete["total_cycles"] = epochs_complete["Total Cycles"].map(_parse_cycles)
epochs_complete["mining_rewards_zkc"] = epochs_complete["Mining Rewards (ZKC)"].map(_parse_zkc)
epochs_complete["mhz"] = epochs_complete["total_cycles"] / 1e6
epochs_complete["zkc_per_mhz"] = np.where(
    epochs_complete["mhz"] > 0,
    epochs_complete["mining_rewards_zkc"] / epochs_complete["mhz"],
    np.nan,
)
POVW_ZKC_PER_MHZ_PER_EPOCH = epochs_complete.head(EPOCH_LOOKBACK_COUNT)["zkc_per_mhz"].mean()

# ── Widgets ───────────────────────────────────────────────────────────────────

zkc_slider = pn.widgets.FloatSlider(
    name="ZKC Price (USD)", start=0.01, end=2.0, step=0.01, value=0.1
)
util_select = pn.widgets.Select(
    name="Market Utilization",
    options={"25%": 0.25, "50%": 0.50, "75%": 0.75, "100%": 1.0},
    value=0.5,
)
market_reward_slider = pn.widgets.FloatSlider(
    name="Market Reward ($/MHz)",
    start=0.00001, end=0.0005, step=0.000005,
    value=MARKET_REWARD_USD_PER_MHZ, format="0.00000",
)
fixed_cost_slider = pn.widgets.FloatSlider(
    name="Fixed Cost ($/mo)", start=0, end=500, step=10, value=FIXED_COST_MONTHLY_USD
)

# ── Tab 1: Profit Explorer ────────────────────────────────────────────────────

@pn.depends(zkc_slider, util_select, market_reward_slider, fixed_cost_slider)
def profit_chart(zkc_price, market_util, market_reward, fixed_monthly):
    fixed_epoch = fixed_monthly / EPOCHS_PER_MONTH
    labels, profits, povw_revs, mkt_revs, costs = [], [], [], [], []
    for _, row in gpu_configs.iterrows():
        mhz = row["mhz_per_epoch"]
        cost = row["rental_per_epoch_usd"] + fixed_epoch
        povw = mhz * POVW_ZKC_PER_MHZ_PER_EPOCH * zkc_price
        mkt = mhz * market_reward * market_util
        profit = povw + mkt - cost
        labels.append(row["label"])
        profits.append(profit)
        povw_revs.append(povw)
        mkt_revs.append(mkt)
        costs.append(cost)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, max(3, len(labels) * 1.2 + 1)))

    colors = ["#2ecc71" if p >= 0 else "#e74c3c" for p in profits]
    bars = ax1.barh(labels, profits, color=colors)
    ax1.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax1.set_xlabel("Profit per epoch (USD)")
    ax1.set_title("Profit per epoch")
    span = max(abs(p) for p in profits) or 1
    for bar, p in zip(bars, profits):
        ax1.text(
            bar.get_width() + span * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"${p:+.2f}", va="center", fontsize=9,
        )

    x = range(len(labels))
    ax2.bar(x, povw_revs, label="POVW", color="#3498db")
    ax2.bar(x, mkt_revs, bottom=povw_revs, label="Market", color="#9b59b6")
    ax2.bar(x, [-c for c in costs], label="Cost", color="#e67e22", alpha=0.8)
    ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(labels, rotation=15, ha="right")
    ax2.set_ylabel("USD per epoch")
    ax2.set_title("Revenue & cost breakdown")
    ax2.legend(fontsize=8)

    plt.tight_layout()
    plt.close(fig)
    return fig


# ── Tab 2: Break-even ─────────────────────────────────────────────────────────

@pn.depends(util_select, market_reward_slider, fixed_cost_slider)
def breakeven_chart(market_util, market_reward, fixed_monthly):
    fixed_epoch = fixed_monthly / EPOCHS_PER_MONTH
    labels, breakevens = [], []
    for _, row in gpu_configs.iterrows():
        mhz = row["mhz_per_epoch"]
        cost = row["rental_per_epoch_usd"] + fixed_epoch
        mkt_rev = mhz * market_reward * market_util
        denom = mhz * POVW_ZKC_PER_MHZ_PER_EPOCH
        be = (cost - mkt_rev) / denom if denom > 0 else float("inf")
        labels.append(row["label"])
        breakevens.append(max(be, 0))

    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 1.2 + 1)))
    colors = ["#2ecc71" if b <= 0.5 else "#f39c12" if b <= 1.0 else "#e74c3c" for b in breakevens]
    bars = ax.barh(labels, breakevens, color=colors)
    ax.set_xlabel("Break-even ZKC price (USD)")
    ax.set_title("Minimum ZKC price to break even")
    ax.axvline(0.1, color="#3498db", linestyle=":", linewidth=1.5, label="$0.10 reference")
    ax.axvline(0.5, color="#9b59b6", linestyle=":", linewidth=1.5, label="$0.50 reference")
    ax.legend(fontsize=8)
    span = max(breakevens) or 1
    for bar, be in zip(bars, breakevens):
        ax.text(
            bar.get_width() + span * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"${be:.3f}", va="center", fontsize=9,
        )
    plt.tight_layout()
    plt.close(fig)
    return fig


# ── Layout ────────────────────────────────────────────────────────────────────

sidebar = pn.Column(
    "### Controls",
    zkc_slider,
    util_select,
    market_reward_slider,
    fixed_cost_slider,
    width=240,
)

tabs = pn.Tabs(
    ("Profit Explorer", pn.pane.Matplotlib(profit_chart, tight=True)),
    ("Break-even",      pn.pane.Matplotlib(breakeven_chart, tight=True)),
)

dashboard = pn.Row(sidebar, tabs)
dashboard.servable()
