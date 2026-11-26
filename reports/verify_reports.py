"""Cross-check the final report and visual evidence against generated outputs."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "REPORT.md"
TABLES = ROOT / "outputs" / "tables"


def parse_markdown_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if line.strip().startswith("|") and not re.match(r"\|\s*:?-+", line.strip()):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and cells[0] not in {"Method", "Rank"}:
                rows.append(cells)
    return rows


def main() -> None:
    report = REPORT.read_text(encoding="utf-8")
    metrics = pd.read_csv(TABLES / "method_comparison.csv")
    rankings = pd.read_csv(TABLES / "full_rankings.csv")
    assert len(metrics) == 9 and not metrics.duplicated(["method", "k"]).any()

    metrics_section = report.split("## Evaluation results", 1)[1].split("\n## ", 1)[0]
    report_metrics = parse_markdown_rows(metrics_section)
    assert len(report_metrics) == 9, f"Expected 9 report metric rows; got {len(report_metrics)}"
    labels = {"Population": "population", "White-space": "white_space", "Ridge": "ridge"}
    for cells in report_metrics:
        label, k = cells[:2]
        source = metrics[(metrics.method == labels[label]) & (metrics.k == int(k))].iloc[0]
        expected = [
            f"{source.selected_net_additions:,.0f}",
            f"{source.hindsight_best_net_additions:,.0f}",
            f"{source.regret:,.0f}",
            f"{int(source.overlap_actual_top_k)}",
            f"{source.precision_at_k:.2f}",
            f"{source.ndcg_at_k_nonnegative_linear_gain:.3f}",
            f"{source.spearman_rho:.3f}",
        ]
        assert cells[2:] == expected, f"Report metrics differ for {label} K={k}: {cells[2:]} != {expected}"

    top_section = report.split("## Top five and observed outcomes", 1)[1].split("\n## ", 1)[0]
    report_top = parse_markdown_rows(top_section)
    assert len(report_top) == 5, f"Expected 5 top-five report rows; got {len(report_top)}"
    column_map = [("population", 1, 2), ("white_space", 3, 4), ("ridge", 5, 6)]
    for row in report_top:
        rank = int(row[0])
        for method, name_col, value_col in column_map:
            expected = rankings[(rankings.method == method) & (rankings["rank"] == rank)].iloc[0]
            report_name = row[name_col]
            assert expected.metro_name.split(",")[0] == report_name, f"Top-five name differs: {report_name}"
            assert int(row[value_col].replace(",", "")) == int(expected.net_additions)

    figure_links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", report)
    assert figure_links, "No report figure references found"
    for link in figure_links:
        assert (ROOT / link).is_file(), f"Report figure is missing: {link}"
    assert "COVID-19" in report and "causal" in report.lower() and "chain-level" in report
    assert (ROOT / "SOURCES.md").is_file() and (ROOT / "outputs" / "feasibility.md").is_file()

    screenshot_map = {
        "top_five_comparison.png": "top-five-market-comparison.png",
        "method_comparison.png": "method-comparison-k5-k10-k20.png",
        "white_space_markets.png": "white-space-market-ranking.png",
        "methodology_limitations.png": "methodology-and-limitations.png",
    }
    for source_name, screenshot_name in screenshot_map.items():
        source = ROOT / "presentation_assets" / source_name
        screenshot = ROOT / "reports" / "screenshots" / screenshot_name
        assert source.read_bytes() == screenshot.read_bytes(), f"Review image is not a copy of {source_name}"

    print("Report metrics: 9/9 match outputs/tables/method_comparison.csv")
    print("Top-five names and signed outcomes: 15/15 match outputs/tables/full_rankings.csv")
    print(f"Report figures: {len(figure_links)} linked files exist")
    print("Review images: 4/4 byte-identical to generated presentation charts")


if __name__ == "__main__":
    main()
