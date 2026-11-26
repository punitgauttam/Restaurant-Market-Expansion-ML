"""Presentation figures generated from held-out ranking results."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

METHOD_ORDER = ["population", "white_space", "ridge"]
METHOD_LABELS = {
    "population": "Population",
    "white_space": "White-space",
    "ridge": "Ridge",
}
METHOD_COLORS = {
    "population": "#4C78A8",
    "white_space": "#F58518",
    "ridge": "#54A24B",
}
SHORT_METRO_NAMES = {
    "New York-Newark-Jersey City, NY-NJ-PA": "New York",
    "Los Angeles-Long Beach-Anaheim, CA": "Los Angeles",
    "Chicago-Naperville-Elgin, IL-IN-WI": "Chicago",
    "Dallas-Fort Worth-Arlington, TX": "Dallas-Fort Worth",
    "Houston-The Woodlands-Sugar Land, TX": "Houston",
    "Miami-Fort Lauderdale-West Palm Beach, FL": "Miami",
    "Tampa-St. Petersburg-Clearwater, FL": "Tampa",
    "Phoenix-Mesa-Scottsdale, AZ": "Phoenix",
    "Riverside-San Bernardino-Ontario, CA": "Riverside",
}


def generate_figures(rankings: pd.DataFrame, metrics: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Write a K sensitivity chart and a top-five outcome comparison chart."""
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ks = sorted(metrics.k.unique())
    x = np.arange(len(ks), dtype=float)
    width = 0.24
    for i, method in enumerate(METHOD_ORDER):
        group = metrics[metrics.method.eq(method)].set_index("k").reindex(ks)
        positions = x + (i - 1) * width
        bars = ax.bar(positions, group.selected_net_additions, width,
                      color=METHOD_COLORS[method], label=METHOD_LABELS[method])
        ax.bar_label(bars, padding=2, fontsize=8, fmt="%.0f")
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xticks(x, [f"K={k}" for k in ks])
    ax.set_ylabel("Observed industry net additions")
    ax.set_title("Observed net additions captured by each ranking")
    ax.legend(frameon=False, ncols=3, loc="best")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    path = output_dir / "captured_net_additions_by_k.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)

    top = rankings[rankings["rank"].le(5)].copy()
    if "net_additions" not in top:
        raise ValueError("Top-five figure requires observed held-out net_additions.")
    if "metro_name" not in top:
        top["metro_name"] = top.metro_id
    fig, axes = plt.subplots(1, 3, figsize=(15, 7), sharex=False)
    for ax, method in zip(axes, METHOD_ORDER):
        group = top[top.method.eq(method)].sort_values("rank", kind="mergesort")
        labels = [SHORT_METRO_NAMES.get(r.metro_name, r.metro_name) for r in group.itertuples()]
        values = group.net_additions.to_numpy(dtype=float)
        y = np.arange(len(group))
        bars = ax.barh(y, values, color=METHOD_COLORS[method], alpha=0.9)
        ax.set_yticks(y, labels, fontsize=7)
        ax.invert_yaxis()
        ax.axvline(0, color="#444444", linewidth=0.8)
        ax.set_title(METHOD_LABELS[method])
        ax.set_xlabel("Observed net additions")
        ax.grid(axis="x", alpha=0.2)
        ax.bar_label(bars, padding=2, fontsize=7, fmt="%.0f")
        low, high = float(values.min()), float(values.max())
        span = max(high - low, abs(high), abs(low), 1.0)
        ax.set_xlim(min(0.0, low) - 0.18 * span, max(0.0, high) + 0.18 * span)
    fig.suptitle("Top-five markets selected and their observed outcomes", y=1.01)
    fig.tight_layout()
    path = output_dir / "top5_markets_observed_outcomes.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)
    return outputs
