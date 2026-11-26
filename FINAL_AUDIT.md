# Final project audit - Restaurant Market Expansion

**Audit date:** 2026-11-26<br>
**Readiness:** **READY WITH DOCUMENTED LIMITATIONS**

This audit independently checked the project files, source manifest and file hashes, processed panel, candidate selection, fitted-method rankings, evaluation metrics, report figures, documented methodology, and existing archive. The current design and reported results are reproducible from the available local inputs. No Git repository metadata is present in this workspace; no Git operation that changes repository state was performed.

## Verification results

| Component | Status | Evidence | Remaining issue |
|---|---|---|---|
| Feasibility gate | PASS | `validate_feasibility_gate` accepted `PASS_WITH_LIMITATIONS` and approved design; data build passed its source, geography and coverage checks. | List 1's directory timestamp does not prove its first-publication date. |
| Official input manifest | PASS | 13 active source records; all returned HTTP 200, paths exist, byte counts and SHA-256 hashes match. The 14th record is the retained List 2 audit workbook; it also exists and hashes correctly. | Official NAICS concordance workbook bytes are cited but not retained. |
| Source/geography/NAICS | PASS WITH LIMITATIONS | Builder reads List 1 and filters to MSA area type; List 2 contains principal cities and is not used. Actual CBP target fields/codes and 383 MSA / 1,169 county-pair match were verified. Kalawao/Maui reporting difference is explicitly reconciled. | Fixed OMB 2017 assignments are retrospectively applied; identifier matching is not a historical polygon overlay. |
| Chronology and leakage | PASS | Panel cutoffs are 2010-01-01 and 2018-02-01. Features and release dates precede their cutoffs; targets follow cutoffs. The runner drops held-out labels before ranking. Top-100 selection sorts only by 2016 population and CBSA tie-breaker. | The retrospective fixed geography and one evaluation window remain design limitations. |
| Processed panel | PASS | Re-read and validated 483 unique panel rows: 383 training MSAs and 100 evaluation candidates; no missing required values. QA JSON agrees. | None for the defined candidate set. |
| Three rankings | PASS | Rebuilt all 300 ranking rows from the panel and approved features. All 100 candidates are shared by all methods; every rank matches; maximum score difference from saved output was 1.14e-13. Ridge alpha is 1.0. | Ridge's top-5/10/20 ordering matches population in this evaluation. |
| Evaluation metrics | PASS | Independently recomputed all nine method/K metric rows using unique metro outcomes. Saved totals, hindsight references, regrets, overlaps, precision, NDCG and Spearman values matched to floating-point precision. | Hindsight is an evaluation reference, not a selectable forecast. |
| Report and figures | PASS | Reported top-five totals and sensitivity metrics match CSVs. Both PNGs exist, were visually reviewed, and are embedded in `REPORT.md`. | No PDF renderer was available; PDF pagination/page count is unverified. |
| Tests/build/reproduction | PASS | 37 tests passed; compileall, cached source validation, gate validation, dataset build and approved pipeline exited 0. A repeat pipeline run left hashes unchanged for all 25 processed/QA/table/figure files. | None for the tested Windows/Python environment. |
| Submission archive | PASS | Existing archive was preserved. New audited archive opens, passes ZIP CRC/integrity test, includes all required files, and excludes transient caches and nested archives. | The audited archive is a separate file from the earlier package. |
| Git review | PARTIAL | `git rev-parse`, `git branch`, `git rev-parse HEAD`, and `git status --short --untracked-files=all` each returned `fatal: not a git repository`. No `.git` directory is present at the project root. | Branch, HEAD, tracked changes and actual Git status cannot be determined in this folder. |

## Verified model results

Top-five selections and observed 2018-2021 net additions:

| Rank | Population | Additions | White-space | Additions | Ridge | Additions |
|---:|---|---:|---|---:|---|---:|
| 1 | New York-Newark-Jersey City | -285 | Miami-Fort Lauderdale-West Palm Beach | 92 | New York-Newark-Jersey City | -285 |
| 2 | Los Angeles-Long Beach-Anaheim | -185 | Tampa-St. Petersburg-Clearwater | 138 | Los Angeles-Long Beach-Anaheim | -185 |
| 3 | Chicago-Naperville-Elgin | -93 | Houston-The Woodlands-Sugar Land | 243 | Chicago-Naperville-Elgin | -93 |
| 4 | Dallas-Fort Worth-Arlington | 312 | Phoenix-Mesa-Scottsdale | 193 | Dallas-Fort Worth-Arlington | 312 |
| 5 | Houston-The Woodlands-Sugar Land | 243 | Riverside-San Bernardino-Ontario | 172 | Houston-The Woodlands-Sugar Land | 243 |

| Method | K | Selected additions | Hindsight reference | Regret | Overlap | Precision@K | NDCG@K | Spearman rho |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Population | 5 | -8 | 1,202 | 1,210 | 2 | 0.40 | 0.300 | -0.007 |
| White-space | 5 | 838 | 1,202 | 364 | 3 | 0.60 | 0.592 | 0.410 |
| Ridge | 5 | -8 | 1,202 | 1,210 | 2 | 0.40 | 0.300 | -0.000 |
| Population | 10 | 29 | 1,848 | 1,819 | 3 | 0.30 | 0.353 | -0.007 |
| White-space | 10 | 1,081 | 1,848 | 767 | 5 | 0.50 | 0.554 | 0.410 |
| Ridge | 10 | 29 | 1,848 | 1,819 | 3 | 0.30 | 0.353 | -0.000 |
| Population | 20 | 139 | 2,552 | 2,413 | 8 | 0.40 | 0.426 | -0.007 |
| White-space | 20 | 1,359 | 2,552 | 1,193 | 10 | 0.50 | 0.548 | 0.410 |
| Ridge | 20 | 53 | 2,552 | 2,499 | 8 | 0.40 | 0.424 | -0.000 |

The white-space ranking led on captured additions and regret at K=5, 10 and 20 in this single held-out period. This is an industry-wide establishment-count result. It does not establish chain-level revenue, profit, market share, survival, or causal effects of entry.

## Exact validation commands and outcomes

The interpreter used was the existing Python 3.11.9 executable discovered in the current-user Python registry because `python` is not on PATH. No packages were installed or changed.

1. `& $pythonExe -m pytest -q` - exit 0; **37 passed**.
2. `& $pythonExe -m compileall -q src run_all.py tests` - exit 0.
3. `& $pythonExe -m src.fetch_data` - exit 0; 13 cached active files revalidated; all active manifest records retain HTTP 200 and verified SHA-256.
4. `& $pythonExe -c "from src.validation import validate_feasibility_gate; validate_feasibility_gate('outputs/feasibility.md')"` - exit 0; gate and design approval accepted.
5. `& $pythonExe -m src.build_dataset` - exit 0; `DATASET_BUILT_QA_PASSED`; 383 training MSAs, 100 evaluation candidates.
6. `& $pythonExe run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01` - exit 0; 383 training rows, 100 candidates, Ridge alpha 1.0; tables and figures regenerated.
7. Repeated the approved `run_all.py` command and compared SHA-256 values for all 25 files in `data/processed/`, `outputs/dataset_qa.json`, `outputs/tables/` and `outputs/figures/` - exit 0; 0 changed, 0 added, 0 removed.
8. Independent audit: recomputed all 14 manifest file hashes; rebuilt model scores/ranks; recalculated all nine metric rows; verified both archives' required members and integrity. All corrected checks passed.

An initial audit calculation used the repeated per-method outcome rows when constructing the hindsight set; that audit calculation was corrected to deduplicate outcomes by metro, after which all nine saved metric rows matched. A separate display-only query requested `metro_name` from `per_metro_evaluation.csv`, which does not contain that column; names were verified from the shortlist and rankings tables. Neither issue required changing model outputs.

An initial broad archive filename filter matched the legitimate `feature_metadata_template.csv` because its name contains the substring `temp`; an exact cache/credential check produced no flagged members. An initial comparison also treated the expected absence of the new audit file from the older archive as a failure; the prior ZIP is intentionally pre-audit and is preserved, while the new archive was checked against the full final workspace.

## Archive and Git state

- Earlier archive retained unchanged: `dist/Restaurant_Market_Expansion_Submission.zip` (68 members; integrity passed when checked). It predates the final audit corrections and does not contain this audit file.
- New audited archive: `dist/Restaurant_Market_Expansion_Submission_Audited_2026-11-26.zip` (69 files). It was built from the final workspace files (excluding `dist`, caches and virtual environments), includes all 13 active raw sources, processed data, code, tests, docs, tables, figures and this audit, passed `ZipFile.testzip()`, and every archived member hash matched the final workspace file.
- Git branch/HEAD/status are unavailable because the current project directory is not inside a Git work tree. No files were staged; no commit, push, tag, merge, reset, rebase, clean, or branch switch was performed.
- The existing `.gitignore` ignores `data/raw/*`, `data/processed/*`, and `outputs/tables/*` except selected placeholders/manifests. It was not modified. If the project files are later placed in Git and processed deliverables should be committed, a proposed targeted change is:

```diff
 # Existing broad ignore rules remain in place.
 # Add these exceptions after the applicable directory-wide ignore rules:
 !data/processed/metro_panel.csv
 !data/processed/feature_metadata.csv
 !data/processed/data_dictionary.csv
 !data/processed/omb_2017_msa_county_crosswalk.csv
 !outputs/tables/*.csv
 # Keep the separately distributed archive out of a source commit:
 dist/
```

This proposal is not applied. The raw files can remain excluded from a Git commit if the separately verified submission archive is the deliverable for those inputs.

## Files changed during this audit

**Directly edited:** `CURRENT_PLAN.md`, `README.md`, `SOURCES.md`, `REPORT.md`, `IMPLEMENTATION_STATUS.md`, `PROJECT_JOURNEY.md`, `docs/revised_design_proposal.md`, `outputs/feasibility.md`, `src/build_dataset.py`; added `FINAL_AUDIT.md`.

**Regenerated or rewritten during verification:** `data/raw/download_manifest.csv`; `data/processed/metro_panel.csv`, `feature_metadata.csv`, `data_dictionary.csv`, and `omb_2017_msa_county_crosswalk.csv`; `outputs/dataset_qa.json`; the 15 table files `evaluation_candidates_top100.csv`, `full_rankings.csv`, `method_comparison.csv`, `metric_definitions.csv`, `metro_explanations.csv`, `per_metro_evaluation.csv`, `shortlist_population_top5.csv`, `shortlist_population_top10.csv`, `shortlist_population_top20.csv`, `shortlist_white_space_top5.csv`, `shortlist_white_space_top10.csv`, `shortlist_white_space_top20.csv`, `shortlist_ridge_top5.csv`, `shortlist_ridge_top10.csv`, and `shortlist_ridge_top20.csv` under `outputs/tables/`; `outputs/figures/captured_net_additions_by_k.png` and `outputs/figures/top5_markets_observed_outcomes.png`; and the new audited archive under `dist/`.

**Preserved:** downloaded official raw-source files, the earlier `dist/Restaurant_Market_Expansion_Submission.zip`, and `.gitignore`. No unrelated project files were changed.

## Remaining limitations

- The evaluation spans 2018-2021 and includes COVID-19; there is only one evaluation window.
- OMB 2017 geography is applied retrospectively. The List 1 directory last-modified date is not proof of first publication.
- Official NAICS concordance workbook bytes are not retained, though referenced concordance evidence and the downloaded CBP files' target fields/codes were inspected.
- CBP post-2017 missing small cells remain unknown and cannot be interpreted as zero. The candidates used here have observed rows for both endpoints.
- Report pagination is unverified because no PDF renderer was found and no PDF was generated.
- Git branch, HEAD, and tracked/untracked state are unavailable because this workspace has no `.git` metadata.

## Follow-up: Git recovery, cleanup, and presentation assets - 2026-11-26

### Git recovery result

The project root and its ancestors were checked for both `.git` directories and `.git` files. A bounded search of nearby OneDrive Desktop project folders found unrelated Git metadata in `mlb` and a nested `rag mini\\.cache\\uv\\sdists-v11` path; neither contains this project and neither was used. The project parent contains no other repository metadata. No origin URL, project repository root, branch, or HEAD can therefore be established with confidence. The explicit stop condition applies: no `git init`, staging, commit, or push was performed. The original Git history and intended remote remain unknown.

### Safe cleanup

Before cleanup, inspection found exactly 17 generated `.pyc` files under the project's root, `src`, and `tests` `__pycache__` folders. Those exact bytecode files were removed after checking their paths. No raw or processed data, source files, outputs, logs, temporary/editor files, `.git` data, or files outside the project were removed. `.pytest_cache` was retained as project execution evidence. Validation later regenerated ignored bytecode caches; the distributable archive excludes caches.

### Presentation assets and browser review

Created `presentation_assets/dashboard.html`, `presentation_assets/build_presentation_assets.py`, `presentation_assets/presentation_summary.md`, and the four requested PNGs: `top_five_comparison.png`, `method_comparison.png`, `white_space_markets.png`, and `methodology_limitations.png`. The charts use the verified CSV outputs; the builder saves PNGs at 240 DPI. The self-contained dashboard embeds those chart images. Chart PNGs were visually inspected and text overflow was corrected. A genuine browser-rendered dashboard screenshot could not be captured because the available native UI connector failed to connect (`Computer Use native pipe is unavailable`); no screenshot is claimed.

### Post-cleanup reproduction

- Existing interpreter: Python 3.11.9; no packages installed or changed.
- `python -m pytest -q`: exit 0, **37 passed**.
- `python -m compileall -q src run_all.py tests`: exit 0.
- `python -m src.fetch_data`: exit 0; all 13 cached active official files were revalidated, each retaining HTTP 200 and a matching SHA-256 in the manifest.
- `python -m src.build_dataset --check-only`: exit 0; `DATASET_BUILT_QA_PASSED`, 383 training MSAs, 100 evaluation candidates, and 1,169 OMB MSA-county membership rows.
- Feasibility-gate validation was accepted by the approved pipeline; `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01`: exit 0; 383 training rows, 100 shared candidates, Ridge alpha 1.0.
- Rebuilt presentation assets after the reproduced rankings. Top-five observed additions remain +838 for white-space and -8 for population and Ridge.

### Follow-up archive and remaining blockers

The previous `Restaurant_Market_Expansion_Submission_Audited_2026-11-26.zip` remains preserved. New archive: `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip` (77 members). ZIP integrity and every archived member SHA-256 matched the workspace at archive time. The archive contains source, raw and processed data, tables, figures, documentation, final audit, and all presentation assets; it excludes `dist`, caches, virtual environments, and bytecode. Archive-generation and verification code is `presentation_assets/create_submission_archive.py`. Git publication and `INDEPENDENT_REVIEW.md` cannot be completed without a confidently identified original repository and intended remote. No branch, URL, commit hash, push result, or clone instructions are fabricated.

## Final reports and GitHub repository audit - 2026-11-26

- The later user instruction identified `https://github.com/punitgauttam/Restaurant-Market-Expansion-ML` and `main`, resolving the earlier missing-remote blocker. Local project root still has no `.git`; the exact remote was cloned into a separate temporary directory for comparison and reconciliation.
- Remote `main` initially pointed to `56ea0ef32e95101b36d896ebff2229c91829b605` (`Initial commit: MLB project setup`) and contained only `.gitignore`, `AGENT.md`, and a README describing an unimplemented proposal. The remote `AGENT.md` blob matched the local `AGENT.md` exactly. No restaurant project artifacts existed on that branch. The original remote README content is preserved in `README_MLB_PROJECT_SETUP.md`; only its Markdown hard-line-break whitespace was normalized. The remote branch history is retained.
- Created `reports/README.md` as an index to the single authoritative `REPORT.md`, approved methodology, feasibility evidence, source provenance, generated tables, and figures. Added `reports/verify_reports.py`; it confirmed 9/9 evaluation rows and 15/15 top-five names/outcomes match generated CSVs, both referenced report figures exist, and four screenshot-folder PNGs exactly match the generated presentation charts.
- The browser/UI connector remained unavailable, so no actual browser-rendered dashboard screenshot is claimed. `reports/screenshots/` contains clearly documented byte-identical copies of the actual generated charts, while original PNGs remain in `presentation_assets/` and `outputs/figures/`.
- Updated `.gitignore` to exclude raw source payloads, archives, caches, secrets, and environments while explicitly including processed datasets, manifest, output tables/figures, reports, and presentation assets. Raw official payloads remain reproducible via the documented downloader and are not staged.
- Current local verification: Python 3.11.9; 37 tests passed; compileall passed; cached source/manifest validation passed for all 13 active sources; feasibility gate passed; dataset check reported 383 training MSAs, 100 evaluation candidates, and 1,169 county links; approved ranking pipeline exited 0. Report cross-check results are in `reports/README.md`.
- Refreshed the separate presentation-inclusive local archive at `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip`; 84 members. ZIP integrity and all member hashes passed. ZIPs remain excluded from Git.
- A clean-clone install surfaced a packaging issue in the old pin: PyPI yanked Matplotlib 3.9.1 and removed its Windows wheels because of reported Windows segfaults, causing pip to attempt an unavailable source build. Updated only the plotting dependency pin to `matplotlib==3.9.1.post1`; verified PyPI offers a compatible CPython 3.11 Windows x64 wheel. No model method, feature, target, or result was changed. The fresh post-fix clone-and-run result is recorded after verification.
- Repository reconciliation was performed only in the temporary clone. The proposed staged set consists of the verified project source, dependencies, processed panel and QA, tables, figures, reports, and documentation, with the remote `AGENT.md` preserved. Raw payloads, ZIP archives, caches, environments, credentials, and temporary files are excluded.

## Final clean-clone verification and GitHub publication - 2026-11-26

- The attached execution shell is Windows PowerShell 5.1 on the user's Windows machine; this is not a Linux or remote container. The project workspace is mounted at the supplied OneDrive path, and the local files are readable. The workspace copy itself has no `.git` metadata, so Git history was recovered from the user-supplied GitHub remote in a disposable temporary clone.
- Python 3.11.9 is installed in the Microsoft Store package and is not on PATH. The workspace sandbox denies direct access to its WindowsApps executable. Running the same installed interpreter and its venv via the authorized elevated command route succeeded; the isolated clone venv reports Python 3.11.9 and pip 24.0. No dependency reinstall or downgrade was needed for the final verification.
- A fresh clone at `3636a4af6fe7b8aff3dfc34e6a4f885ef25a7b52` installed the pinned requirements successfully from binary wheels. The first install attempt against the prior `matplotlib==3.9.1` pin attempted a source build and failed because no compiler was available; `requirements.txt` now pins the compatible `3.9.1.post1` release. This is a packaging-only change; methodology and results are unchanged.
- From that clean clone, `src.fetch_data` acquired and SHA-validated all 13 official inputs; `src.build_dataset` completed with `DATASET_BUILT_QA_PASSED` (383 training MSAs, 100 evaluation candidates, 1,169 OMB county/MSA membership rows); and the approved `run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01` run completed with Ridge alpha 1.0.
- The clean-clone test suite passed **37/37** in 2.02 seconds; `compileall` passed. `reports/verify_reports.py` confirmed 9/9 method metric rows and 15/15 top-five names/outcomes against the regenerated CSVs; both report figure links exist; the four review PNGs match the generated presentation charts byte-for-byte.
- Reproduced top-five observed net additions: white-space **838**, population **-8**, Ridge **-8**. This is a single evaluation window (2018-2021), which includes the COVID-19 disruption; it is not evidence of generalization across economic regimes.
- The four files in `reports/screenshots/` are presentation chart exports, not browser captures. The browser UI connector was unavailable, so no browser-rendered dashboard screenshot is claimed.
- GitHub main retains the original initial commit and now contains the project and the Windows-compatible dependency fix. The follow-up audit documentation and refreshed presentation archive were finalized after this independent clone run; the documentation update is included in the subsequent GitHub main commit.
