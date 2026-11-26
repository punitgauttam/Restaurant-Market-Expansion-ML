# Reports and review artifacts

`../REPORT.md` is the authoritative final report. This folder indexes the verified source documents and review images without duplicating the report, result tables, or original generated figures.

## Method, provenance, and results

- Approved methodology: [`../docs/revised_design_proposal.md`](../docs/revised_design_proposal.md) and [`../CURRENT_PLAN.md`](../CURRENT_PLAN.md)
- Feasibility gate and source-by-source evidence: [`../outputs/feasibility.md`](../outputs/feasibility.md)
- Official sources and provenance: [`../SOURCES.md`](../SOURCES.md) and [`../data/raw/download_manifest.csv`](../data/raw/download_manifest.csv)
- Final audit: [`../FINAL_AUDIT.md`](../FINAL_AUDIT.md)
- Main results table: [`../outputs/tables/method_comparison.csv`](../outputs/tables/method_comparison.csv)
- Full rankings and metro explanations: [`../outputs/tables/full_rankings.csv`](../outputs/tables/full_rankings.csv) and [`../outputs/tables/metro_explanations.csv`](../outputs/tables/metro_explanations.csv)
- Original pipeline figures: [`../outputs/figures/`](../outputs/figures/)
- Presentation dashboard and figures: [`../presentation_assets/`](../presentation_assets/)

## Visual evidence

The PNGs under `screenshots/` are high-resolution copies of the actual static charts generated from the verified project CSVs. They are not browser screenshots. A screenshot of `presentation_assets/dashboard.html` could not be captured because the available browser/UI connector was unavailable during this audit. The dashboard itself is self-contained and embeds the same generated chart images.

- [`top-five-market-comparison.png`](screenshots/top-five-market-comparison.png)
- [`method-comparison-k5-k10-k20.png`](screenshots/method-comparison-k5-k10-k20.png)
- [`white-space-market-ranking.png`](screenshots/white-space-market-ranking.png)
- [`methodology-and-limitations.png`](screenshots/methodology-and-limitations.png)

## Reproduction

From the project root, install `requirements.txt`, download/validate the official sources with `python -m src.fetch_data`, rebuild the panel with `python -m src.build_dataset`, then run `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01`. Run tests with `python -m pytest -q`.

Run `python reports/verify_reports.py` to compare all nine report metric rows and all fifteen top-five name/outcome cells with the generated CSVs, confirm report figure links, and confirm the review PNGs match the generated charts byte-for-byte.
