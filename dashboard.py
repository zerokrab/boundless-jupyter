"""
Boundless Prover Profitability Dashboard

Visualization-only — no model logic. All computation lives in the notebook.

Usage:
  Notebook:   from dashboard import build_dashboard; build_dashboard(revenue_df)
  Local dev:  panel serve dashboard.py  (requires results.csv)
  Static:     panel convert dashboard.py --to pyodide-worker --out dist/
"""

import matplotlib.pyplot as plt
import pandas as pd
import panel as pn

pn.extension()


def build_dashboard(df: pd.DataFrame | None = None) -> pn.viewable.Viewable:
    """
    Build the Panel dashboard.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Pre-computed revenue_df from the notebook. If None, loads results.csv.

    Expected columns: scenario, zkc_price_usd, market_order_util,
                       profit_per_epoch, povw_revenue, market_revenue,
                       cost_per_epoch, label
    """
    if df is None:
        df = pd.read_csv("results.csv")

    # Derive available discrete values directly from the data
    zkc_prices = sorted(df["zkc_price_usd"].unique())
    util_values = sorted(df["market_order_util"].unique())

    # ── Widgets ───────────────────────────────────────────────────────────────

    zkc_slider = pn.widgets.DiscreteSlider(
        name="ZKC Price (USD)", options=zkc_prices, value=zkc_prices[len(zkc_prices) // 2]
    )
    util_select = pn.widgets.Select(
        name="Market Utilization",
        options={f"{int(u * 100)}%": u for u in util_values},
        value=util_values[len(util_values) // 2],
    )

    # ── Tab 1: Profit Explorer ────────────────────────────────────────────────

    @pn.depends(zkc_slider, util_select)
    def profit_chart(zkc_price, market_util):
        sub = df[(df["zkc_price_usd"] == zkc_price) & (df["market_order_util"] == market_util)]

        labels = sub["label"].tolist()
        profits = sub["profit_per_epoch"].tolist()
        povw_revs = sub["povw_revenue"].tolist()
        mkt_revs = sub["market_revenue"].tolist()
        costs = sub["cost_per_epoch"].tolist()

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

    # ── Tab 2: Break-even ─────────────────────────────────────────────────────

    @pn.depends(util_select)
    def breakeven_chart(market_util):
        sub = df[df["market_order_util"] == market_util]
        # Find minimum ZKC price where profit >= 0, per GPU config
        breakevens = {}
        for label, group in sub.groupby("label"):
            profitable = group[group["profit_per_epoch"] >= 0]
            if profitable.empty:
                breakevens[label] = group["zkc_price_usd"].max()  # not reached
            else:
                breakevens[label] = profitable["zkc_price_usd"].min()

        labels = list(breakevens.keys())
        values = list(breakevens.values())

        fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 1.2 + 1)))
        colors = ["#2ecc71" if v <= 0.5 else "#f39c12" if v <= 1.0 else "#e74c3c" for v in values]
        bars = ax.barh(labels, values, color=colors)
        ax.set_xlabel("Break-even ZKC price (USD)")
        ax.set_title("Minimum ZKC price to break even")
        ax.axvline(0.1, color="#3498db", linestyle=":", linewidth=1.5, label="$0.10 reference")
        ax.axvline(0.5, color="#9b59b6", linestyle=":", linewidth=1.5, label="$0.50 reference")
        ax.legend(fontsize=8)
        span = max(values) or 1
        for bar, v in zip(bars, values):
            ax.text(
                bar.get_width() + span * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"${v:.3f}", va="center", fontsize=9,
            )
        plt.tight_layout()
        plt.close(fig)
        return fig

    # ── Layout ────────────────────────────────────────────────────────────────

    sidebar = pn.Column(
        "### Controls",
        zkc_slider,
        util_select,
        width=240,
    )

    tabs = pn.Tabs(
        ("Profit Explorer", pn.pane.Matplotlib(profit_chart, tight=True)),
        ("Break-even",      pn.pane.Matplotlib(breakeven_chart, tight=True)),
    )

    return pn.Row(sidebar, tabs)


# Standalone entry point (panel serve / panel convert)
if __name__ == "__main__" or pn.state.served:
    build_dashboard().servable()
