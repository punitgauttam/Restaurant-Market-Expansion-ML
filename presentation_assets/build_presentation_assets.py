"""Build presentation visuals from the verified project CSV outputs."""
from __future__ import annotations

import base64
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"
COLORS = {"population": "#52677D", "white_space": "#087E75", "ridge": "#7656A5"}
LABELS = {"population": "Population", "white_space": "White-space", "ridge": "Ridge"}
SHORT_NAMES = {
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
BG = "#F3F6FA"
INK = "#14263D"
MUTED = "#56677D"
GRID = "#D7DFE8"


def style_axes(ax) -> None:
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)


def save(fig, name: str) -> Path:
    fig.savefig(OUT / name, dpi=240, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return OUT / name


def top_five_figure(rankings: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 7.4))
    fig.patch.set_facecolor(BG)
    for ax, method in zip(axes, ["population", "white_space", "ridge"]):
        group = rankings[rankings.method.eq(method)].sort_values("rank").head(5).sort_values("rank", ascending=False)
        names = [SHORT_NAMES.get(name, name) for name in group.metro_name]
        vals = group.net_additions.to_numpy(float)
        y = np.arange(len(vals))
        bars = ax.barh(y, vals, color=COLORS[method], height=0.62, zorder=3)
        ax.set_yticks(y, names)
        ax.axvline(0, color=INK, linewidth=1.0)
        ax.set_title(LABELS[method], loc="left", color=INK, fontweight="bold", fontsize=14, pad=14)
        ax.set_xlabel("Observed net additions, 2018–2021", color=MUTED, fontsize=9)
        style_axes(ax)
        lo, hi = min(0.0, vals.min()), max(0.0, vals.max())
        span = max(hi - lo, 1.0)
        ax.set_xlim(lo - span * 0.18, hi + span * 0.2)
        for bar, value in zip(bars, vals):
            ax.text(value + (span * 0.025 if value >= 0 else -span * 0.025), bar.get_y() + bar.get_height()/2,
                    f"{value:+,.0f}", ha="left" if value >= 0 else "right", va="center",
                    color=INK, fontsize=9, fontweight="bold")
        total = group.net_additions.sum()
        ax.text(0.0, -0.16, f"Top-five total: {total:+,.0f}", transform=ax.transAxes,
                color=COLORS[method], fontsize=11, fontweight="bold")
    fig.suptitle("Same 100 markets. Three ranking rules. Different observed outcomes.",
                 x=0.04, y=0.98, ha="left", color=INK, fontsize=19, fontweight="bold")
    fig.text(0.04, 0.91, "Industry-wide limited-service restaurant establishment net additions—not chain performance",
             color=MUTED, fontsize=10)
    fig.subplots_adjust(top=0.82, bottom=0.21, left=0.07, right=0.98, wspace=0.27)
    save(fig, "top_five_comparison.png")


def method_comparison_figure(metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor(BG)
    ks = [5, 10, 20]
    x = np.arange(len(ks))
    width = 0.23

    ax = axes[0, 0]
    for i, method in enumerate(["population", "white_space", "ridge"]):
        g = metrics[metrics.method.eq(method)].set_index("k").reindex(ks)
        b = ax.bar(x + (i-1)*width, g.selected_net_additions, width, color=COLORS[method], label=LABELS[method])
        ax.bar_label(b, fmt="%.0f", fontsize=8, padding=2, color=INK)
    ax.axhline(0, color=INK, linewidth=0.9)
    ax.set_xticks(x, [f"K={k}" for k in ks])
    ax.set_title("Observed additions captured", color=INK, loc="left", fontweight="bold")
    ax.set_ylabel("Sum among selected markets", color=MUTED)
    ax.legend(frameon=False, ncols=3, fontsize=8, loc="upper left")
    style_axes(ax)
    ax.grid(axis="y", color=GRID, linewidth=0.7)

    ax = axes[0, 1]
    for i, method in enumerate(["population", "white_space", "ridge"]):
        g = metrics[metrics.method.eq(method)].set_index("k").reindex(ks)
        b = ax.bar(x + (i-1)*width, g.regret, width, color=COLORS[method], label=LABELS[method])
        ax.bar_label(b, fmt="%.0f", fontsize=8, padding=2, color=INK)
    ax.set_xticks(x, [f"K={k}" for k in ks])
    ax.set_title("Regret vs hindsight reference", color=INK, loc="left", fontweight="bold")
    ax.set_ylabel("Hindsight best minus selected", color=MUTED)
    style_axes(ax)

    ax = axes[1, 0]
    for method in ["population", "white_space", "ridge"]:
        g = metrics[metrics.method.eq(method)].sort_values("k")
        ax.plot(g.k, g.precision_at_k, color=COLORS[method], marker="o", linewidth=2.5,
                markersize=7, label=LABELS[method])
        for r in g.itertuples():
            ax.annotate(f"{int(r.overlap_actual_top_k)}/{int(r.k)}", (r.k, r.precision_at_k),
                        xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8, color=INK)
    ax.set_xticks(ks, [f"K={k}" for k in ks])
    ax.set_ylim(0, 0.72)
    ax.set_title("Precision@K (overlap count labeled)", color=INK, loc="left", fontweight="bold")
    ax.set_ylabel("Share of selected markets in actual top K", color=MUTED)
    ax.legend(frameon=False, ncols=3, fontsize=8, loc="lower right")
    style_axes(ax)

    ax = axes[1, 1]
    for method in ["population", "white_space", "ridge"]:
        g = metrics[metrics.method.eq(method)].sort_values("k")
        ax.plot(g.k, g.ndcg_at_k_nonnegative_linear_gain, color=COLORS[method], marker="o",
                linewidth=2.5, markersize=7, label=LABELS[method])
    ax.set_xticks(ks, [f"K={k}" for k in ks])
    ax.set_ylim(0, 0.68)
    ax.set_title("NDCG@K (nonnegative linear gain)", color=INK, loc="left", fontweight="bold")
    ax.set_ylabel("Normalized discounted gain", color=MUTED)
    ax.legend(frameon=False, ncols=3, fontsize=8, loc="lower right")
    style_axes(ax)
    fig.suptitle("White-space leads this held-out window; weaker results remain visible",
                 x=0.04, y=0.98, ha="left", color=INK, fontsize=19, fontweight="bold")
    fig.text(0.04, 0.92, "Hindsight is an evaluation reference only. The outcome includes the COVID-19 period.",
             color=MUTED, fontsize=10)
    fig.subplots_adjust(top=0.83, bottom=0.09, left=0.08, right=0.98, hspace=0.34, wspace=0.18)
    save(fig, "method_comparison.png")


def white_space_figure(explanations: pd.DataFrame) -> None:
    group = explanations[explanations.white_space_rank.le(5)].sort_values("white_space_rank")
    labels = [SHORT_NAMES.get(n, n) for n in group.metro_name]
    score = group.white_space_score.to_numpy(float)
    actual = group.net_additions.to_numpy(float)
    y = np.arange(len(group))
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
    fig.patch.set_facecolor(BG)
    for ax, vals, title, color, xlabel in [
        (axes[0], score, "White-space score", COLORS["white_space"], "Score (population × national density − current establishments)"),
        (axes[1], actual, "Observed outcome", "#3973A8", "Net additions, 2018–2021"),
    ]:
        bars = ax.barh(y, vals, color=color, height=0.62)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_title(title, color=INK, loc="left", fontweight="bold", fontsize=14)
        ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
        style_axes(ax)
        hi = max(vals.max(), 1.0)
        ax.set_xlim(0, hi*1.23)
        ax.bar_label(bars, fmt="%.0f", padding=4, fontsize=9, color=INK, fontweight="bold")
    fig.suptitle("White-space shortlist: score and later outcome are different quantities",
                 x=0.04, y=0.98, ha="left", color=INK, fontsize=17, fontweight="bold")
    fig.text(0.04, 0.91, "The score measures estimated capacity relative to existing supply; bars at right show actual industry net additions.",
             color=MUTED, fontsize=10)
    fig.subplots_adjust(top=0.80, bottom=0.18, left=0.11, right=0.98, wspace=0.40)
    save(fig, "white_space_markets.png")


def methodology_figure() -> None:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.text(0.03, 0.94, "What this backtest does—and what it cannot say", transform=ax.transAxes,
            color=INK, fontsize=20, fontweight="bold", va="top")

    def card(x, y, w, h, title, body, accent):
        rect = plt.Rectangle((x, y), w, h, transform=ax.transAxes, facecolor="white",
                             edgecolor=GRID, linewidth=1.0, zorder=1)
        ax.add_patch(rect)
        ax.add_patch(plt.Rectangle((x, y), 0.012, h, transform=ax.transAxes,
                                   facecolor=accent, edgecolor="none", zorder=2))
        title_lines = textwrap.fill(title, width=max(14, int(w*48)), break_long_words=False)
        body_lines = "\n".join(textwrap.fill(part, width=max(27, int(w*90)), break_long_words=False) for part in body.split("\n"))
        title_n = title_lines.count("\n") + 1
        ax.text(x+0.03, y+h-0.03, title_lines, transform=ax.transAxes, color=accent,
                fontsize=10, fontweight="bold", va="top", linespacing=1.05, zorder=3)
        ax.text(x+0.03, y+h-0.07-0.035*title_n, body_lines, transform=ax.transAxes, color=INK,
                fontsize=8.5, va="top", linespacing=1.15, zorder=3)

    card(0.03, 0.59, 0.44, 0.27, "TRAINING ROW", "Cutoff: 2010-01-01\nCBP 2007 + PEP 2008 features\nLabel: CBP 2013 − CBP 2010", "#3973A8")
    card(0.53, 0.59, 0.44, 0.27, "HELD-OUT EVALUATION", "Cutoff: 2018-02-01\nTop 100 by 2016 population\nLabel: CBP 2021 MSA − CBP 2018 MSA", COLORS["white_space"])
    card(0.03, 0.23, 0.29, 0.29, "COVID-19 WINDOW", "2018–2021 includes pandemic shocks. A single window cannot establish general performance.", "#C67A21")
    card(0.355, 0.23, 0.29, 0.29, "RETROSPECTIVE MAP", "2017 OMB counties are applied to history. This fixed-boundary map was not known in 2010.", "#7656A5")
    card(0.68, 0.23, 0.29, 0.29, "BUSINESS INTERPRETATION", "Outcome is industry net additions, not chain profit, revenue, survival, or causal returns.", "#B14D62")
    ax.text(0.03, 0.12, "CBP suppression: post-2017 absent small cells are unknown, not zero. Candidates without both outcome endpoints are rejected.",
            transform=ax.transAxes, color=MUTED, fontsize=10, va="center")
    ax.text(0.03, 0.055, "Sources and evidence: SOURCES.md • outputs/feasibility.md • outputs/dataset_qa.json",
            transform=ax.transAxes, color=MUTED, fontsize=9)
    save(fig, "methodology_limitations.png")


def dashboard_html(rankings: pd.DataFrame, metrics: pd.DataFrame, explanations: pd.DataFrame) -> None:
    top_tables=[]
    for method in ["population", "white_space", "ridge"]:
        top=rankings[rankings.method.eq(method)].sort_values("rank").head(5)
        total=int(top.net_additions.sum())
        rows="".join(f"<tr><td>{int(r.rank)}</td><td>{r.metro_name}</td><td class='num'>{int(r.net_additions):+,}</td></tr>" for r in top.itertuples())
        top_tables.append(f"<section class='method-card'><div class='method-head'><h3>{LABELS[method]}</h3><span class='pill' style='--pill:{COLORS[method]}'>{total:+,} observed additions</span></div><table><thead><tr><th>Rank</th><th>Selected MSA</th><th>Observed</th></tr></thead><tbody>{rows}</tbody></table></section>")
    metrics=metrics.copy()
    metric_rows=[]
    for r in metrics.sort_values(["k","method"]).itertuples():
        metric_rows.append(f"<tr><td>{LABELS[r.method]}</td><td>{r.k}</td><td>{r.selected_net_additions:,.0f}</td><td>{r.regret:,.0f}</td><td>{int(r.overlap_actual_top_k)}/{r.k} ({r.precision_at_k:.0%})</td><td>{r.ndcg_at_k_nonnegative_linear_gain:.3f}</td></tr>")
    best=rankings[rankings.method.eq('white_space')].sort_values('rank').head(5)
    best_names=", ".join(SHORT_NAMES.get(x,x) for x in best.metro_name)
    img_sections=[]
    for fname,alt in [("top_five_comparison.png","Top-five market comparison"),("method_comparison.png","Method metrics at K 5, 10 and 20"),("white_space_markets.png","White-space scores and observed outcomes"),("methodology_limitations.png","Methodology and limitations")]:
        encoded=base64.b64encode((OUT/fname).read_bytes()).decode('ascii')
        img_sections.append(f"<section class='visual'><img src='data:image/png;base64,{encoded}' alt='{alt}'></section>")
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Restaurant Expansion | Market Evidence</title>
<style>
:root{{--ink:#14263d;--muted:#56677d;--line:#d7dfe8;--bg:#f3f6fa;--teal:#087e75;--blue:#3973a8;--amber:#c67a21}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 'Segoe UI',Arial,sans-serif}}
.wrap{{max-width:1320px;margin:auto;padding:42px 28px 70px}}header{{padding:34px 38px;border-radius:20px;background:#14263d;color:white;box-shadow:0 12px 36px #14263d20}}
.eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-weight:700;font-size:12px;color:#9bd5cd}}h1{{font-size:38px;line-height:1.1;margin:10px 0 12px}}header p{{max-width:890px;color:#d4deea;margin:0}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0 34px}}.stat{{background:white;border:1px solid var(--line);border-radius:14px;padding:18px 20px}}
.stat b{{display:block;font-size:27px;line-height:1.2;color:var(--teal)}}.stat span{{font-size:12px;color:var(--muted)}}section.block{{margin-top:32px}}h2{{font-size:23px;margin:0 0 6px}}.sub{{color:var(--muted);margin:0 0 18px}}
.methods{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.method-card,.table-wrap,.visual{{background:white;border:1px solid var(--line);border-radius:14px;overflow:hidden}}
.method-card{{padding:18px}}.method-head{{display:flex;justify-content:space-between;align-items:start;gap:8px}}h3{{margin:0 0 12px;font-size:18px}}.pill{{border-radius:20px;color:white;background:var(--pill);padding:5px 9px;font-size:11px;font-weight:700;white-space:nowrap}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th{{text-align:left;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.04em;background:#f6f8fb}}td,th{{padding:8px 7px;border-bottom:1px solid #e8edf2}}tr:last-child td{{border-bottom:0}}.num{{text-align:right;font-variant-numeric:tabular-nums}}
.table-wrap{{padding:8px 14px;overflow:auto}}.table-wrap table{{min-width:700px;font-size:13px}}.highlight{{color:var(--teal);font-weight:700}}
.visual{{padding:10px;margin:18px 0}}.visual img{{display:block;width:100%;height:auto}}.note{{padding:17px 20px;border-left:4px solid var(--amber);background:#fff8ec;border-radius:8px;color:#503b20}}
footer{{margin-top:38px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12px}}a{{color:var(--blue)}}@media(max-width:900px){{.cards{{grid-template-columns:repeat(2,1fr)}}.methods{{grid-template-columns:1fr}}h1{{font-size:30px}}.wrap{{padding:20px 14px 50px}}header{{padding:25px}}}}
</style></head><body><main class="wrap">
<header><div class="eyebrow">Historical market selection backtest</div><h1>Restaurant Expansion<br>Market Evidence</h1><p>Three ranking rules evaluated on the same 100 largest eligible US metropolitan areas at the 2018-02-01 cutoff. The held-out outcome is industry-wide limited-service restaurant establishment net additions from 2018 to 2021.</p></header>
<div class="cards"><div class="stat"><b>+838</b><span>White-space top-five observed additions</span></div><div class="stat"><b>−8</b><span>Population and Ridge top-five observed additions</span></div><div class="stat"><b>383</b><span>Historical training MSAs</span></div><div class="stat"><b>100</b><span>Shared evaluation candidates</span></div></div>
<section class="block"><h2>Top-five market choices</h2><p class="sub">Observed net additions are kept signed; negative outcomes are shown.</p><div class="methods">{''.join(top_tables)}</div></section>
<section class="block"><h2>Method comparison</h2><p class="sub">Regret compares with the hindsight-best K markets in this held-out sample; it is an evaluation reference, not a forecast.</p><div class="table-wrap"><table><thead><tr><th>Method</th><th>K</th><th>Selected additions</th><th>Regret</th><th>Actual top-K overlap / precision</th><th>NDCG</th></tr></thead><tbody>{''.join(metric_rows)}</tbody></table></div>{img_sections[1]}</section>
<section class="block"><h2>White-space score versus observed outcome</h2><p class="sub">Shortlist: {best_names}. The score and later observed additions are distinct quantities.</p>{img_sections[2]}<div class="note"><b>Score definition:</b> 2016 population × national CBP restaurant density − existing CBP 2015 establishments. It estimates capacity relative to observed supply; it is not predicted profit or the 2018–2021 outcome.</div></section>
<section class="block"><h2>Selection comparison and research boundaries</h2>{img_sections[0]}{img_sections[3]}</section>
<footer><b>Limitations:</b> the 2018–2021 outcome includes COVID-19 and is the only evaluation window. OMB 2017 geography is applied retrospectively. The label is industry-wide net establishment additions, not chain-specific profit, revenue, survival, or causal entry returns. Missing post-2017 CBP small cells remain unknown, not zero.<br><br>Source register: <code>SOURCES.md</code> · Feasibility evidence: <code>outputs/feasibility.md</code> · Full report: <code>REPORT.md</code></footer>
</main></body></html>'''
    (OUT/"dashboard.html").write_text(html,encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rankings=pd.read_csv(TABLES/"full_rankings.csv")
    metrics=pd.read_csv(TABLES/"method_comparison.csv")
    explanations=pd.read_csv(TABLES/"metro_explanations.csv")
    top_five_figure(rankings)
    method_comparison_figure(metrics)
    white_space_figure(explanations)
    methodology_figure()
    dashboard_html(rankings,metrics,explanations)
    top5={m:rankings[rankings.method.eq(m)].sort_values("rank").head(5) for m in LABELS}
    lines=["# Presentation summary: restaurant market expansion", "",
           "## Finding", "",
           "In the single 2018–2021 held-out evaluation, white-space captured 838 industry-wide net additions at K=5, compared with -8 for population and Ridge. At K=10 and K=20, white-space captured 1,081 and 1,359 additions. This is a historical proxy result, not a chain-level return estimate.", "",
           "## Top-five selections", ""]
    for method in LABELS:
        g=top5[method]
        lines.append(f"### {LABELS[method]} — total observed net additions: {g.net_additions.sum():+,.0f}")
        lines.extend(f"{int(r.rank)}. {r.metro_name} — {r.net_additions:+,.0f}" for r in g.itertuples())
        lines.append("")
    lines += ["## Method and evaluation", "",
              "The evaluation universe is the 100 largest eligible MSAs by 2016 PEP population. The training set contains 383 MSAs. The target is CBP 2021 MSA establishments minus CBP 2018 MSA establishments. Ridge uses alpha=1.0. Every method ranks the same evaluation candidates.", "",
              "| Method | K | Selected additions | Regret | Overlap | Precision@K | NDCG@K |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in metrics.sort_values(["k","method"]).itertuples():
        lines.append(f"| {LABELS[r.method]} | {r.k} | {r.selected_net_additions:,.0f} | {r.regret:,.0f} | {int(r.overlap_actual_top_k)}/{r.k} | {r.precision_at_k:.2f} | {r.ndcg_at_k_nonnegative_linear_gain:.3f} |")
    lines += ["", "## Boundaries", "",
              "- Evaluation spans 2018–2021, includes COVID-19, and is the only evaluation window.",
              "- OMB 2017 county assignments are applied retrospectively.",
              "- The target is industry-wide net establishment additions, not chain revenue, profit, survival, or causal entry returns.",
              "- Post-2017 suppressed small CBP cells are unknown, not zero.",
              "- White-space score and observed outcome are different quantities.", "",
              "Generated PNGs and the self-contained dashboard use the verified outputs under `outputs/tables/`."]
    (OUT/"presentation_summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("Generated dashboard and four presentation PNGs in presentation_assets/")


if __name__ == "__main__":
    main()
