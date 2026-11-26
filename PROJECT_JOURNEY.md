# Project journey

## 2026-11-26 — Final reports audit and specified GitHub reconciliation
- The user supplied the exact existing remote `punitgauttam/Restaurant-Market-Expansion-ML` and `main`, resolving the prior missing-remote blocker. Cloned it to a separate temporary directory; the working project itself remains without `.git` metadata.
- Remote HEAD was `56ea0ef32e95101b36d896ebff2229c91829b605` (`Initial commit: MLB project setup`) with only `.gitignore`, `AGENT.md`, and an outdated project-plan README. Remote and local AGENT.md blobs match exactly. Preserved the original remote README content as `README_MLB_PROJECT_SETUP.md`, normalizing only Markdown hard-line-break whitespace; no remote files were deleted.
- Audited `REPORT.md` against generated tables: 9/9 metric rows and 15/15 top-five market/outcome cells matched; both linked report figures exist. Added `reports/README.md` and a repeatable `reports/verify_reports.py` audit. Created four clearly identified chart copies in `reports/screenshots/`; no browser screenshot is claimed because the UI connector is unavailable.
- Improved `.gitignore` to retain processed panel, QA, tables, figures, docs and presentation assets while excluding raw source payloads, archives, caches, secrets and environments. The raw manifest stays included with hashes.
- Reran validation: pytest 37 passed; compileall exit 0; 13 active cached sources validated; feasibility gate accepted; dataset check confirmed 383 training MSAs, 100 evaluation candidates and 1,169 county links; approved pipeline regenerated rankings successfully. White-space K=5 remains +838 versus -8 for Population/Ridge.
- Refreshed `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip` with reports and screenshots; the 84-member archive passed integrity and all member-hash checks. Archive files are excluded from GitHub.
- The first isolated clone install exposed the yanked Windows-incompatible Matplotlib 3.9.1 pin. PyPI's official release record explains the Windows wheel removal. Changed `requirements.txt` to `matplotlib==3.9.1.post1` and verified that its CPython 3.11 Windows x64 wheel is downloadable. This is packaging-only; methodology and numeric outputs are unchanged. Final clean-clone verification follows the update push.
- Copied 69 eligible local files to the temporary clone and verified each SHA-256 against the working project. Staged diff review is in progress; the original project directory and the GitHub remote have not been modified by this reconciliation step.

## 2026-11-26 — Final Git recovery, cleanup, visual assets, and post-cleanup reproduction
- Searched the project and ancestor directories for `.git` directories and `.git` files, then searched nearby OneDrive Desktop project locations. No repository root or intended remote for this project could be established. Other nearby Git metadata belonged to unrelated folders and was not used. Per the user's stop condition, did not initialize Git, stage, commit, or push.
- Proposed cleanup was limited to 17 inspected `.pyc` bytecode files under project `__pycache__` folders. Removed exactly those files; preserved `.pytest_cache`, all sources, datasets, logs, audit evidence, and archives. Later Python validation may recreate ignored bytecode.
- Added a reproducible presentation builder and created four 240-DPI PNG visuals, a self-contained HTML dashboard with embedded charts, and `presentation_summary.md` from verified outputs. Visually inspected the charts and fixed overlapping headings and text overflow. Browser review/screenshot was unavailable because the native UI connector could not connect; no browser screenshot is claimed.
- Revalidated with existing Python 3.11.9: `pytest -q` passed 37 tests; `compileall` passed; cached source validation retained 13/13 active HTTP 200 records and matching hashes; dataset QA passed (383 training MSAs, 100 evaluation MSAs, 1,169 OMB MSA-county links); approved ranking pipeline exited 0 with unchanged headline results.
- Updated README and final audit for the Git stop, cleanup scope, presentation assets, and screenshot limitation. Preserved earlier audited ZIP; created `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip` with 77 members. ZIP integrity and all member SHA-256 values matched the workspace at archive time.
- Remaining external action: identify the original Git repository and intended remote. Until then, no Git history operation or independent clone handoff can be completed safely.

## Current status (2026-11-26)
- Approved design: 2010-01-01 training cutoff and 2018-02-01 evaluation cutoff; 2010-2013 training label and 2018-2021 held-out label.
- Gate: `PASS_WITH_LIMITATIONS`; 13 active official sources are locally validated. Census List 1 is the county crosswalk; List 2 is a retained principal-cities audit artifact.
- Verified panel: 383 training MSAs, 100 evaluation candidates, 483 rows. Full pipeline and 37 tests pass; white-space top-five captured 838 net additions, compared with -8 each for population and Ridge.
- See the final dated execution entry below for exact verification; all earlier blocked states and methodology proposals are retained as historical chronology and were superseded by later evidence/decisions.


## 2026-11-26 — Specification review and feasibility research

- Read the user-supplied `AGENT.md` and `README.md`; copied the complete originals into this package unchanged.
- Confirmed scope: rank top 5 US metropolitan markets from the same approximately 100 eligible candidates; compare population baseline, white-space score and Ridge; evaluate K=5 with K=10/20 sensitivity; outcome is industry-wide limited-service establishment net additions, not chain profit.
- Verified original timing conflict from official Census publication pages: 2005–2009 ACS 5-year released 2010-12-14; 2009 CBP page dated 2011-06-30; 2010–2014 ACS 5-year released 2015-12-03; 2014 CBP released 2016-04-24; 2012 CBP released 2014-05-29.
- Researched a candidate alternate chronology with matched five-year train/evaluation target windows: training decision 2010-01-01, target 2010–2015; evaluation decision 2018-01-01, target 2018–2023. Official feature and outcome publication dates align chronologically in the sources register. This shift requires explicit approval and has not been applied to the source README.
- Corrected NAICS mapping evidence: 2007 code 722211 maps to 2012 code 722513 without a content change; 2017 CBP uses the 2017 NAICS classification. Actual CBP file code fields still need inspection.
- Strengthened implementation: release-date metadata gates, target publication-date checks, same-candidate selection by evaluation-cutoff population, train-only Ridge preprocessing, K shortlists, regret, overlap/precision, NDCG with nonnegative linear relevance, and Spearman correlation.
- First unit-test run: 4 passed, 2 failed due string-vs-timestamp comparison in `validate_train_eval`. Fixed by parsing dates before comparing.
- A later unit-test run exposed two stale test expectations after the proposed evaluation cutoff changed to 2018; updated fixtures to test the intended boundary conditions rather than the old date.
- Final unit-test run after the feature-metadata and held-out-label checks: `pytest -q` — **9 passed**.
- `python -m compileall -q src run_all.py tests` — completed successfully.
- CLI smoke test on a temporary synthetic fixture with 25 metros and two cutoffs: `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-01-01 --candidate-count 25` — exit code 0; generated 12 CSV tables (three full-method outputs, nine shortlists, plus evaluation/detail tables). The values were test fixtures only and are not project findings.

## 2026-11-26 — Network retrieval attempt

- Environment: Python 3.13.5; pandas 2.2.3; NumPy 2.3.5; scikit-learn 1.8.0; SciPy 1.17.0; pytest 9.0.2; requests 2.32.5.
- Attempted HEAD requests to `https://www.census.gov`, official CBP bulk ZIP `https://www2.census.gov/programs-surveys/cbp/datasets/2015/cbp15co.zip`, and Census ACS API `https://api.census.gov/data/2016/acs/acs5?...`.
- All three hosts failed DNS resolution before an HTTP response: `curl: (6) Could not resolve host`.
- No download was completed, no archive was extracted, and no raw source file was changed or fabricated.

## Status / next action

The code scaffold, temporal gates and evaluation functions have passed unit tests and a synthetic CLI smoke test. The actual project data and model results remain unverified. The main external blocker is DNS/network access to official Census sources. The substantive user decision still required is whether to approve the alternate 2010–2015 training / 2018–2023 evaluation chronology.


## 2026-11-26 — Reassessment of revised historical windows and geography

- Rejected the earlier proposed 2010–2015 / 2018–2023 five-year design as the preferred option: Census CBP MSA reference files are split into 2017–2021 and 2022–2023 geography batches, and 2017+ county industry/geography cells with fewer than 3 establishments are dropped. A direct 2018-to-2023 MSA comparison may therefore use changed county membership; county aggregation would inherit suppressed/missing small-county cells.
- Identified a more defensible candidate: 2010-01-01 training decision with CBP 2007 + PEP 2008 features, and a 2010–2013 training target; 2018-01-01 evaluation decision with CBP 2015 + PEP 2016 features, and a 2018–2021 held-out target. Both target windows are 3 years, and the training outcome's latest source was released by 2015-04-23, before the later decision.
- Located a cutoff-available geography reference: OMB Bulletin 17-01 dated 2017-08-15 and Census historical August 2017 CBSA delineation workbook `list1.xls`. This avoids using the later CBP `msa_county_reference17.txt` file (last modified 2021-09-13) as if it were known at the 2018 cutoff. Workbook tabs, county membership, and code matching to 2018/2021 CBP MSA records remain unverified.
- Identified exact direct bulk files and official directory listings for CBP 2007/2010/2013/2015 county ZIPs; CBP 2018/2021 MSA ZIPs; county PEP 2008/2016 CSVs; and OMB 2017 delineation XLS. Approximate download sizes remain below 100 MB total.
- Added an official-source allowlisted downloader with bounded retries, per-file cap, SHA-256 logging, ZIP integrity/path checks, executable-member rejection and no automatic extraction. Added data contract, source acquisition instructions, revised design proposal and unverified feature metadata template. The original `README.md` and `AGENT.md` remain unchanged.
- Repeated direct DNS/HTTP checks for `www.census.gov`, `www2.census.gov` and `api.census.gov`; all failed name resolution before any HTTP status. No source bytes were retrieved.
- The suggested 3-year design is not approved; no feature/data build or model fit was attempted.


## 2026-11-26 — Downloader, gate enforcement and regression verification

- Executed `python -m src.fetch_data --list`; it enumerated nine official source files and their proposed publication dates.
- Attempted three representative downloads through `python -m src.fetch_data --only pep_2008_county,omb_2017_delineation,cbp_2007_county`. Each failed after the configured retries with `NameResolutionError` for `www2.census.gov`; the full URLs, UTC timestamps and error messages are preserved in `data/raw/download_manifest.csv`.
- A separate direct container download retry failed; opening the direct Census CSV through the browser returned HTTP 403. No source file bytes were downloaded.
- Added fail-closed `FEASIBILITY_GATE` and `DESIGN_APPROVAL` enforcement to `run_all.py`; it will refuse to fit models while the gate is blocked or the material timeline revision is unapproved.
- Hardened archive inspection against Windows-style path traversal, symlink entries, executable files and oversized archive members. White-space scoring now requires one shared national density across all candidate metros.
- Added regression tests for these controls. Latest `pytest -q`: **17 passed**. `python -m compileall -q src run_all.py tests`: passed.
- Re-ran the full CLI on a temporary synthetic-only fixture after the gate change: 25 fixture metros, 3 methods, 12 CSV outputs, exit code 0. The temporary fixture and outputs were deleted and are not included as project data.
- Added explicit caveat that the proposed design backcasts older county observations to 2017 CBSA geography; this is a consistent-boundary harmonisation, not a claim that the 2017 geographic definitions were available in 2010.

## Status at that stage (2026-11-26; historical and superseded)

Implementation and tests are in place; real data acquisition is blocked by this runtime's DNS/network failure. The feasibility gate remains `BLOCKED`, design approval remains `PENDING`, and no production model fitting or project result is claimed.


## 2026-11-26 — User approved revised chronology and parser corrections
- User approved the three-year design: training decision cutoff 2010-01-01 (CBP2010–2013 label) and evaluation decision cutoff 2018-02-01 (CBP2018–2021 label).
- Refinement: Census directory records OMB Bulletin 17-01 List 2 workbook `list2.xls` last modified 2018-01-23; selected 2018-02-01 evaluation cutoff, with this metadata caveat documented.
- Corrected geographic source from List 1 to List 2 (MSA-only list).
- Corrected CBP2010 industry code to 2007 NAICS 722211; CBP2013/2015 use 722513 in the 2012 NAICS vintage; CBP2018/2021 use 722513 in the 2017 NAICS vintage.
- Updated sources, data contract, design proposal and fail-closed feasibility documentation.
- Raw downloads and full tests are still pending; no model fitting is permitted while the gate remains BLOCKED.

- Additional classification audit: Census CBP vintage schedule states CBP 2003–2007 uses 2002 NAICS; 2008–2011 uses 2007 NAICS; 2012–2016 uses 2012 NAICS; 2017 onward uses 2017 NAICS. Corrected CBP2007 metadata to 2002 NAICS 722211 and CBP2010 metadata to 2007 NAICS 722211. The exact 2002→2007 concordance workbook still needs inspection after source access is restored.


## 2026-11-26 — Final v4 implementation checks
- Confirmed from the Census CBP methodology that pre-2017 establishment counts remain published even when payroll for cells below three establishments is suppressed; from 2017, cells with fewer than three establishments are dropped. Builder policy reflects this distinction and still fails on explicit missing count values.
- Confirmed the 2002→2007 Limited-Service Restaurants code remains 722211 in the published concordance; confirmed 2007→2012 mapping 722211→722513 with unchanged industry content. Added source references and corrected NAICS-vintage documentation.
- Confirmed Census CBP publishes the 2017–2021 MSA geography batch, covering both selected 2018 and 2021 endpoint files; actual ID alignment remains pending file download.
- Fixed the train-label release-date test fixture to use a release after the 2018-02-01 evaluation cutoff.
- Verification: `python -m pytest -q` — 23 passed; `python -m compileall -q src run_all.py tests` — passed; `python -m src.fetch_data --list` — 9 sources listed.
- Gate safety check: `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01` exited 2 with the expected blocked-gate message. No model fit occurred.
- Dataset-builder check: `python -m src.build_dataset --check-only` exited 1 because `data/raw/omb_2017_bulletin17_01_list2.xls` is not present.
- Retry status: three representative file downloads (OMB List 2, CBP 2007, PEP 2008) failed before receiving an HTTP response because `www2.census.gov` could not be resolved by this runtime. The exact errors are in `data/raw/download_manifest.csv`.
- Outcome: implementation and tests are ready; the real-data feasibility gate remains BLOCKED. No raw data, processed panel, rankings or model metrics were produced.


## 2026-11-26 — County FIPS reference validation added
- Census CBP county reference documentation lists three relevant batches: 2002–2011 (`georef02.txt`), 2012–2016 (`georef12.txt`) and 2017–2021 (`georef17.txt`).
- Added these three official text files to the downloader. The project now enumerates 12 sources: eight CBP/PEP inputs, OMB List 2 and three supplemental county-geography references.
- Added a builder check that compares every county in the fixed OMB List 2 MSA universe against each CBP county-reference FIPS set; missing identifiers block fixed-geography aggregation pending reconciliation. This is a coverage check only, not proof of boundary equivalence.
- Inspected the published `georef12.txt` header and records: CSV columns are `fipstate`, `fipscty`, `ctyname`; `999` identifies statewide totals and is excluded from county records.
- Browser retrieval of `georef17.txt` returned a Unicode-decoding error. Added Windows-1252 fallback in text validation and county-reference parsing, with regression tests.
- `python -m pytest -q`: **30 passed**. `python -m compileall -q src run_all.py tests`: passed. `python -m src.fetch_data --list`: 12 official source URLs listed.
- Raw county-reference bytes have not been retrieved locally because this runtime cannot resolve the official `www2.census.gov` host. No geography coverage result is claimed.


## 2026-11-26 — Approved design, selection-bias audit, and CBP MSA reference addition
- User approved the revised three-year train/evaluation windows in chat. Current implementation uses 2010-01-01 training cutoff and 2018-02-01 evaluation cutoff; this supersedes earlier exploratory alternatives in the log.
- Verified on official Census pages that both CBP 2018 and CBP 2021 pages list MSA ZIP files; each file page specifies establishment counts for the week of March 12.
- Verified the Census CBP MSA geography reference page lists a 2017–2021 batch; the directory lists `msa_county_reference17.txt` last modified 2021-09-13. Added this file as an ex-post validation source only, not as a pre-2018 predictor. Its actual bytes and schema still need local retrieval.
- Identified and corrected a methodological leak risk: the earlier builder used the future 2016-population top-100 candidate IDs to filter historical Ridge training rows. It now trains on all eligible OMB 17-01 US MSAs and selects the top 100 only for the 2018 evaluation rankings.
- Corrected the national CBP establishment numerator to restrict it to the 50 states and DC, matching the PEP denominator's geography; territorial records are not mixed into the US national density.
- Added a post-cutoff CBP MSA-to-county membership comparison against OMB List 2. This is a geography QA check; any mismatch blocks data building.
- Corrected data contract and docs to describe 383 historical training geographies vs 100 evaluation candidates; all ranking methods still use the same 100 candidates.
- Corrected the disclosure limitation to focus specifically on EST count publication: pre-2017 establishment counts were published for cells with fewer than three establishments; from 2017 those cells are dropped.
- Actual raw Census files are still unavailable from this runtime due outbound DNS resolution failure; no raw-data or model result claims are made.

- Added a county-only restriction to CBP national establishment totals: state-summary FIPS rows are excluded so the white-space density numerator is not double-counted. Added a regression fixture with a statewide 999 row.

## 2026-11-26 — v5 full-source attempt and final current checks
- Added the CBP 2017–2021 MSA/county reference file (`msa_county_reference17.txt`) from the official Census MSA geography reference directory; its 2021-09-13 directory timestamp marks it as an ex-post QA reference, not a 2018 predictor.
- Corrected training sample selection: use all eligible OMB 17-01 MSAs for Ridge fitting; top-100 selection by 2016 population applies only to the 2018 evaluation candidate universe.
- Restricted national establishment totals to county rows in the 50 states and DC, excluding county-code 999 state summaries to prevent double counting.
- Full 13-source acquisition attempt: 0 downloaded; all 13 requests failed before HTTP with DNS `NameResolutionError` for `www2.census.gov`. The complete manifest is saved to `data/raw/download_manifest.csv`.
- Final v5 checks: `python -m pytest -q` — 34 passed; `python -m compileall -q src run_all.py tests` — passed; `python -m src.fetch_data --list` — 13 sources.
- Ran controlled synthetic CLI smoke test with 30 historical training rows and 25 evaluation candidates. All three methods ranked the same 25 candidates; expected rankings, shortlists and evaluation metrics were generated; process exited successfully. Removed synthetic fixtures and generated tables afterward. This verified orchestration only, not Census parsing or project results.
- Full 13-source acquisition attempt failed before HTTP for every source due `www2.census.gov` DNS resolution error; exact exception details are preserved in `data/raw/download_manifest.csv`.
- Real raw-file parsing, geography match, panel creation and model fitting remain blocked.

## 2026-11-26 - Current execution retry and report reconciliation
- Re-read the current plan, revised design proposal, data contract, source-acquisition procedure, implementation status, feasibility record, source register, project journey, report, and original brief files.
- Inventory: project source/test files are present; data/raw/ contains only .gitkeep and download_manifest.csv; data/processed/ contains only .gitkeep and a feature metadata template. No panel or analytical result files are present. The workspace has no Git metadata.
- Interpreter discovery: python, py, python3, uv, and conda are absent from command lookup/PATH; no project .venv exists. Commands python -m pytest -q, python -m compileall -q src run_all.py tests, python -m src.fetch_data --list, python -m src.fetch_data, python -m src.build_dataset, python -m src.build_dataset --check-only, and python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01 could not start (CommandNotFoundException: python is not recognized). These are environment launch failures, not test or application results.
- Network diagnostic: Resolve-DnsName www2.census.gov succeeded and returned four IPv4 addresses (172.65.90.24-.27) and IPv6 addresses. Test-NetConnection www2.census.gov -Port 443 failed TCP connectivity to all four IPv4 addresses. WinHTTP reports direct access with no proxy.
- Retried all 13 approved official HTTPS sources using bounded PowerShell transfers into data/raw/, with format checks, ZIP member path/executable/symlink checks, decompression reads, and SHA-256 on accepted files. 0/13 downloaded. Each failed with Unable to connect to the remote server; no HTTP response or payload was received. No source file was written. The manifest records the attempt and exact URLs/errors.
- Updated REPORT.md to describe the blocked state and approved design without claiming results. The feasibility gate remains BLOCKED. No synthetic data or fake charts/results were created.
- Current verification: tests, compile, parser, data build, and ranking run were not executable because Python is unavailable. Prior v5 test/smoke-test results remain historical log entries and were not reproduced in this execution.

### Remaining external prerequisites
1. Provide an execution environment with Python and the pinned project dependencies available.
2. Restore outbound TCP 443 access to the official Census/OMB hosts (or provide verified official source files in data/raw/ with provenance).
3. Rerun the 13-source acquisition, raw-file inspection, geography/NAICS/missingness audit, dataset build, tests, compile, and full ranking pipeline. Keep the feasibility gate blocked until all evidence passes.
- Additional official-host diagnostics: TCP 443 also failed for www.census.gov, api.census.gov, and www.whitehouse.gov; this is not isolated to the Census bulk-data hostname.

## 2026-11-26 - Follow-up execution requested by user
- Re-read all requested controlling project documents. Re-inventory confirmed no Python interpreter/launcher is available (`Get-Command python`, `where.exe python`, and `where.exe py` returned no executable).
- Executed the requested command set: `python -m pip install -r requirements.txt`, `python -m pytest -q`, `python -m compileall -q src run_all.py tests`, `python -m src.fetch_data`, `python -m src.build_dataset`, and the approved `run_all.py` invocation. Each stopped at shell command resolution with `CommandNotFoundException: python is not recognized`; dependencies therefore were not installed and no Python test/build/model process started.
- Fresh network diagnostic: `Resolve-DnsName www2.census.gov` succeeded. `Test-NetConnection` failed TCP 443. An official CBP HEAD request failed before HTTP status with `System.Net.WebException: Unable to connect to the remote server`; inner exception was `System.Net.Sockets.SocketException: An attempt was made to access a socket in a way forbidden by its access permissions 172.65.90.27:443`.
- No downloads or analysis were possible. The existing manifest remains 0/13 successful; no raw source files, processed panel, tables, or figures exist. No code/model methodology was changed and no ZIP was created.

## 2026-11-26 - Local execution access restored and project completed
- Environment diagnosis: attached execution is local Windows PowerShell in the actual project directory. The current-user Python 3.11 registry key resolved the Windows Store Python 3.11.9 executable, which is absent from PATH and denied by default sandboxed invocation. Using the explicitly authorized local interpreter resolved the mismatch; pip 26.2 and installed project packages were confirmed without reinstalling.
- HTTPS checks through the authorized interpreter succeeded. Acquired and validated all 13 active official inputs; status probe returned HTTP 200 for every source. The manifest now records per-source status and hashes. The additional List 2 workbook was verified as Principal Cities; active county assignments use List 1.
- Corrected downloader ZIP member size bound after official CBP county archive metadata showed single CSV members of 179-187 MB uncompressed. Added the correct List 1 source, cp1252 handling, county field parsing, and explicit Kalawao/Maui historical unit reconciliation. These changes are backed by actual input inspection and parser tests.
- Feasibility gate set to `PASS_WITH_LIMITATIONS` after verifying NAICS values and row counts, 383 MSA / 1,169 county geography match, endpoint coverage, feature completeness, source chronology, and documented exceptions. No suppression was treated as zero.
- Dataset build: 383 training MSAs, 100 evaluation candidates, 483 panel rows, zero missing required values. Data dictionary and QA outputs generated.
- Approved model command completed: `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01`; fixed Ridge alpha 1.0, 383 training rows, 100 shared candidates. White-space captured 838 / 1,081 / 1,359 observed net additions at K=5/10/20. Population captured -8 / 29 / 139; Ridge captured -8 / 29 / 53. White-space had the lowest regret in all three K settings. See `REPORT.md` and `outputs/tables/method_comparison.csv`.
- Replaced stale blocked-state README and report, corrected the source-acquisition guide and feasibility evidence, and retained earlier failed access attempts as historical chronology rather than current status.
- Final validation completed after the figure update: `pip --version` reported pip 26.2; pytest passed 37/37; compileall exited 0; downloader validated all cached active sources; dataset build passed QA; approved model pipeline exited 0 and regenerated outputs. Both figures were visually checked after the label layout fix. Full command outcomes are in `IMPLEMENTATION_STATUS.md`.
- Created `dist/Restaurant_Market_Expansion_Submission.zip` after analysis completion. The archive contains 68 files and passed `ZipFile.testzip()`; it includes the 13 active official inputs, retained List 2 audit workbook, manifest, code, processed data, report, tables, and figures.

## 2026-11-26 - Final pre-submission audit
- Recomputed all 14 manifest file hashes (13 active sources plus retained List 2 audit workbook); all files, sizes and hashes matched. All active sources have recorded HTTP 200 status.
- Revalidated 483 panel rows (383 training, 100 evaluation), re-derived the top 100 from evaluation-cutoff population, rebuilt 300 ranking rows and verified ranks/scores against saved outputs (maximum score difference 1.14e-13). Independently recalculated all nine metric rows after deduplicating the per-method outcome table; saved and recalculated values matched to floating-point precision.
- Clarified published CBP missingness treatment: pre-2017 absent target-industry rows are treated as zero under CBP's EST publication convention; explicit missing EST values fail; post-2017 absent/suppressed MSA outcomes remain unknown and fail candidate completeness. No approved design or model setting changed.
- Re-ran pytest (37 passed), compileall, cached source validation, gate validation, dataset build and approved pipeline; all exited 0. A repeated pipeline run produced identical hashes for all 25 processed/QA/table/figure artifacts.
- Updated current-plan/source/report/history consistency, linked the report figures, and wrote `FINAL_AUDIT.md`. The earlier ZIP is preserved; a new audited archive is created separately and verified.
- Git review could not return branch, HEAD or status because this folder has no `.git` metadata. No staging or Git history operation was performed. `.gitignore` was not modified; a targeted future exception proposal is documented in the audit.
- Preserved the earlier 68-member ZIP and created `dist/Restaurant_Market_Expansion_Submission_Audited_2026-11-26.zip` (69 members). The audited ZIP passed integrity testing and every member hash matched the final workspace state; no cache, virtual environment, credential, or nested archive was included.

## 2026-11-26 - Independent clean-clone verification
- Resolved interpreter access in the Windows PowerShell execution session: Python 3.11.9 is installed but off PATH in the Microsoft Store package, and the sandbox blocks direct WindowsApps invocation. The authorized elevated route ran the installed interpreter and the clean clone venv successfully (pip 24.0). This workspace copy has no `.git`; Git work was performed in a disposable clone of the explicitly supplied remote.
- Fresh clone at `3636a4af6fe7b8aff3dfc34e6a4f885ef25a7b52`: pinned requirements installed; all 13 official sources downloaded and validated; full dataset rebuild passed (383 training MSAs, 100 evaluation candidates, 1,169 county/MSA pairs); approved pipeline completed at Ridge alpha 1.0.
- Independent clone: pytest 37/37 passed, compileall passed, and report consistency check passed (9/9 metrics, 15/15 top-five rows, 2 figures and 4/4 chart-image matches). Top-five selected outcomes reproduce: white-space +838, population -8, Ridge -8.
- The only dependency adjustment is `matplotlib==3.9.1.post1`, after the prior yanked release attempted a local source build without a compiler. No analysis method changed. Browser-rendered screenshot remains unavailable; the four review images are genuine generated charts, not browser captures.
