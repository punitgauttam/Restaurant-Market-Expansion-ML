# Restaurant Market Expansion: Reproducible Analysis

This repository contains the approved retrospective analysis of US limited-service restaurant market opportunity. The final comparison ranks the 100 largest eligible US metropolitan areas at the 2018-02-01 cutoff using population, a white-space score, and Ridge regression. The held-out target is industry-wide establishment net additions from CBP 2018 to CBP 2021.

**Current result:** white-space performed best in the single 2018-2021 evaluation: its top five recorded 838 net additions, compared with -8 for both population and Ridge. See [REPORT.md](REPORT.md) for rankings, metrics, interpretation, and limitations. This outcome is not a chain-level profit or causal estimate.

## Design

| Stage | Cutoff | Features | Outcome |
|---|---|---|---|
| Training | 2010-01-01 | CBP 2007 county restaurants (NAICS 722211); PEP 2008 county population | CBP 2013 minus CBP 2010 establishments |
| Evaluation | 2018-02-01 | CBP 2015 county restaurants (NAICS 722513); PEP 2016 county population | CBP 2021 MSA minus CBP 2018 MSA establishments |

The 2017 OMB Bulletin 17-01 MSA county geography is applied retrospectively. Census List 1 is filtered to metropolitan statistical areas. The historical training sample uses all eligible MSAs; evaluation candidates are chosen separately as the 100 largest by 2016 population. Ridge alpha is fixed at 1.0. The evaluation includes COVID-19 and is one unusual historical regime. Full design and caveats are in `docs/revised_design_proposal.md` and `outputs/feasibility.md`.

## Data sources and method

The project uses official US Census County Business Patterns (CBP) establishment counts, Population Estimates Program (PEP) county population files, and the Census/OMB 2017 List 1 county-to-MSA delineation. CBP county and MSA geography reference files support coverage checks. Exact source URLs, reference years, retrieval metadata, file sizes, HTTP status, and SHA-256 hashes are documented in `SOURCES.md` and `data/raw/download_manifest.csv`.

The business question is which five eligible metropolitan markets should be prioritized under a constrained expansion shortlist. It compares a 2016 population baseline, the approved white-space score (`population × national establishment density − current establishments`), and a Ridge model with fixed alpha 1.0. The outcome is industry-wide limited-service restaurant establishment net additions; it is not chain-specific profit or causal returns. Training uses the 2010-01-01 cutoff and 2010–2013 label; evaluation uses the 2018-02-01 cutoff and 2018–2021 label. All three methods use the same top 100 evaluation candidates, selected by 2016 population.

## Install in a clean environment

Use Python 3.11.9. From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The pinned requirements cover data processing, modeling, plotting, and tests. The raw source payloads are not stored in Git; `python -m src.fetch_data` retrieves and validates them from the official sources. A clean reproduction therefore needs network access to those Census/OMB endpoints.

## Environment and execution

The validated local interpreter is Python 3.11.9 with project dependencies already installed. On this machine the Windows Store Python executable is registered under the current user's Python 3.11 registry key but is absent from PATH. In PowerShell, if `python` is not recognized, locate the existing interpreter with:

```powershell
$pythonExe = (Get-ItemProperty 'HKCU:\Software\Python\PythonCore\3.11\InstallPath').ExecutablePath
& $pythonExe --version
```

No packages need to be reinstalled on the validated machine. To rerun the project from a normal environment where Python is on PATH:

```powershell
python -m pytest -q
python -m src.fetch_data
python -m src.build_dataset
python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01
python reports/verify_reports.py
python -m compileall -q src run_all.py tests
```

The downloader validates cached files and records source URL, HTTP status, size, SHA-256, retrieval time, and local validation status in `data/raw/download_manifest.csv`. It does not extract archives. Keep the raw downloads unchanged. The analysis tables are generated under `outputs/tables/`, figures under `outputs/figures/`, processed data under `data/processed/`, and dataset checks in `outputs/dataset_qa.json`.

## Project map

- `REPORT.md`: results and decision interpretation.
- `CURRENT_PLAN.md`: approved timing and business design.
- `SOURCES.md`: official provenance and source facts.
- `outputs/feasibility.md`: current `PASS_WITH_LIMITATIONS` evidence gate.
- `data/raw/download_manifest.csv`: verified source file inventory and hashes.
- `data/processed/metro_panel.csv`: analytical panel.
- `outputs/tables/`: candidate list, complete rankings, shortlists, metrics, definitions, and explanations.
- `outputs/figures/`: generated evaluation figures.
- `reports/README.md`: index to the authoritative report, feasibility evidence, result tables, figures, and review images.
- `reports/screenshots/`: high-resolution PNG copies of the actual generated result visualizations. The interactive HTML dashboard was not available to the UI screenshot connector during this audit.
- `presentation_assets/`: self-contained HTML dashboard, four 240-DPI presentation PNGs, a reproducible builder, and a concise result summary.
- `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip`: latest verified archive, including the presentation assets.
- `dist/Restaurant_Market_Expansion_Submission.zip` and `dist/Restaurant_Market_Expansion_Submission_Audited_2026-11-26.zip`: earlier preserved packages.
- `IMPLEMENTATION_STATUS.md` and `PROJECT_JOURNEY.md`: execution evidence and chronological record.
- `FINAL_AUDIT.md`: pre-submission quality audit, command results, limitations, and Git-review outcome.
- `README_ORIGINAL.md`: preserved original proposal; the approved design is in `CURRENT_PLAN.md`.
- `README_MLB_PROJECT_SETUP.md`: the original README from the remote repository's initial setup commit, retained because that commit is labeled for an MLB project.

## Presentation assets

Open `presentation_assets/dashboard.html` in a browser for the static, self-contained dashboard. To regenerate its graphics and summary from the verified ranking CSVs, run:

```powershell
python -B presentation_assets/build_presentation_assets.py
```

The visual assets compare the three top-five lists, metrics at K=5/10/20, the white-space score against later observed additions, and the methodology limits. Browser screenshot capture was unavailable during the final audit; the deliverables are the actual chart PNGs generated from the project outputs.

## Integrity notes

The CBP outcome is establishment net additions across the industry. It does not measure a specific chain's performance, profit, survival, or causal return on entry. The post-2017 CBP disclosure rule means absent small cells are unknown, not zero. The project checks that both evaluation endpoint rows exist for all selected candidates. Official raw payloads are reproducibly downloaded from the sources documented in `SOURCES.md`; raw files and distributable ZIP archives are excluded from Git, while the manifest, analytical panel, QA, tables, figures, and documentation are included.

## Reports and independent review

`REPORT.md` is the authoritative final project report. `reports/README.md` maps it to the approved methodology, feasibility evidence, generated tables, and figures. The GitHub repository is [punitgauttam/Restaurant-Market-Expansion-ML](https://github.com/punitgauttam/Restaurant-Market-Expansion-ML), on branch `main`. Follow the reproducibility commands above from a clean clone. A clone requires network access to download official raw source files before rebuilding the dataset.
