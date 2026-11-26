# Implementation status and verification history

The opening v5 sections below record the state before authorized local Windows execution was established. They are historical and superseded by **Authoritative current status** at the end of this file. The approved design has not changed.

## Decision at the time of the blocked v5 run (historical; superseded)
- User approved the revised three-year historical design in this conversation.
- `DESIGN_APPROVAL: APPROVED`.
- `FEASIBILITY_GATE: BLOCKED` because none of the raw official files could be downloaded in this execution environment.
- Do not train or report real-world results until the actual source files have been retrieved and audited.

## Approved historical design
| Role | Decision cutoff | Features | Outcome |
|---|---|---|---|
| Training | 2010-01-01 | CBP 2007 (2002 NAICS 722211) + PEP 2008 population | CBP 2013 establishments minus CBP 2010 establishments |
| Evaluation | 2018-02-01 | CBP 2015 (2012 NAICS 722513) + PEP 2016 population | CBP 2021 MSA establishments minus CBP 2018 MSA establishments |

Both labels are about three years apart and use the CBP week-containing-March-12 measure. The 2018–2021 evaluation interval includes COVID-19. OMB Bulletin 17-01 List 2 is used for a fixed 2017 MSA geography; historic county rows are retrospectively aggregated to that boundary.

## v5 methodological corrections
- Ridge training uses all eligible OMB 17-01 US MSAs (383 if source coverage confirms), instead of filtering historical training rows by the future 2016-population top-100 evaluation shortlist. The top 100 are selected only at the 2018 evaluation cutoff. All three methods rank that exact same top-100 evaluation set.
- National CBP establishment density uses county rows only in the 50 states + DC; state-summary rows are excluded to avoid double counting and align with the PEP population denominator.
- Added the official CBP 2017–2021 MSA-to-county reference file as an ex-post geometry verification source. It was last modified in 2021 and is not used as a 2018 predictor. The builder compares CBP MSA/county pairs with OMB List 2 and fails closed on any mismatch.
- Documented the post-2017 CBP rule that industry/geography cells with fewer than three establishments are dropped. Such missing metro outcomes are not zero and block candidate evaluation.
- Corrected disclosure caveat: this analysis ranks by `EST` and does not use noisy employment/payroll values; the key comparability issue for `EST` is the change to dropping cells under three establishments from 2017.

## Files and code
- `src/fetch_data.py`: official-source downloader with 13 sources, HTTPS host allowlist, file size limits, ZIP validation, archive path/symlink/executable rejection, SHA-256 and manifest logging.
- `src/build_dataset.py`: parses PEP, CBP and OMB source files, validates county geography batches, compares CBP MSA reference county pairs, creates the training/evaluation panel and dataset QA.
- `src/models.py`, `src/compare.py`, `src/evaluate.py`: population, white-space and Ridge ranking; all ranking methods use one evaluation candidate universe; metrics include net additions, hindsight-best, regret, overlap/precision, NDCG and Spearman.
- `src/validation.py` and `run_all.py`: release date checks, temporal separation, target publication checks, candidate-universe checks, and hard feasibility gate.
- `tests/`: unit and synthetic-fixture regression tests.

## Verification recorded at that time (historical; superseded)
- `python -m pytest -q`: **34 passed**.
- `python -m compileall -q src run_all.py tests`: passed.
- `python -m src.fetch_data --list`: enumerated **13** official source URLs.
- Full source acquisition attempt: **0/13 downloaded**. All failed before HTTP with DNS `NameResolutionError` for `www2.census.gov`; full details are in `data/raw/download_manifest.csv`.
- `run_all.py` with the repository feasibility file: expected block (gate is BLOCKED); no Ridge fitting is performed.
- Controlled synthetic CLI smoke test: 30 historical training rows and 25 evaluation candidates; all three methods ranked the same candidate universe; generated full rankings, top-5/10/20 shortlists and nine metric rows; process exited successfully. Temporary fixture data and generated tables were removed afterward. This tests orchestration only, not project findings.
- The parser tests use controlled in-memory fixtures; they do not prove that actual Census files parse.

## Evidence boundary at that time (historical; superseded)
**Verified:** official web pages and metadata indicate relevant CBP/PEP/OMB files exist, their release dates fit the proposed information chronology, CBP 2018 and 2021 pages list direct MSA files, Census lists a 2017–2021 CBP MSA geography batch, and relevant NAICS code mapping is documented.

**Unverified:** every raw file's bytes, checksums and real schema; OMB workbook sheet layout and actual 383/1,169 row counts; exact county FIPS membership across historical CBP vintages; CBP MSA county-pair match to OMB List 2; actual CBP/PEP row coverage; missing/suppressed counts among top 100; processed panel; actual candidate list; model rankings and metrics.

## Reproduction when Census network access is available
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m src.fetch_data
python -m src.build_dataset
```

Only after the complete data QA report and `outputs/feasibility.md` justify PASS or PASS_WITH_LIMITATIONS should the gate be changed and the model pipeline run: `python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01`. Never manually pass the gate merely to produce metrics.

## Latest execution attempt - 2026-11-26
- Current terminal environment has no Python launcher/interpreter on PATH, so requested pytest, compileall, fetch CLI, dataset-builder, and ranking commands could not start.
- DNS for www2.census.gov currently resolves, but TCP 443 connections to all returned IPv4 addresses fail. A bounded PowerShell retry of all 13 official sources obtained 0 files; each failed with Unable to connect to the remote server. The raw directory still has no data files.
- Prior recorded 34-test and synthetic orchestration results are historical and could not be reproduced in this environment. They do not establish real-data validity.
- REPORT.md now states the blocked status and contains no empirical results. FEASIBILITY_GATE remains BLOCKED.

## 2026-11-26 - Follow-up execution requested by user
- Re-read all requested controlling project documents. Re-inventory confirmed no Python interpreter/launcher is available (`Get-Command python`, `where.exe python`, and `where.exe py` returned no executable).
- Executed the requested command set: `python -m pip install -r requirements.txt`, `python -m pytest -q`, `python -m compileall -q src run_all.py tests`, `python -m src.fetch_data`, `python -m src.build_dataset`, and the approved `run_all.py` invocation. Each stopped at shell command resolution with `CommandNotFoundException: python is not recognized`; dependencies therefore were not installed and no Python test/build/model process started.
- Fresh network diagnostic: `Resolve-DnsName www2.census.gov` succeeded. `Test-NetConnection` failed TCP 443. An official CBP HEAD request failed before HTTP status with `System.Net.WebException: Unable to connect to the remote server`; inner exception was `System.Net.Sockets.SocketException: An attempt was made to access a socket in a way forbidden by its access permissions 172.65.90.27:443`.
- No downloads or analysis were possible. The existing manifest remains 0/13 successful; no raw source files, processed panel, tables, or figures exist. No code/model methodology was changed and no ZIP was created.

## Authoritative current status - 2026-11-26
- Resolved the execution mismatch: Windows PowerShell is attached to the project workspace. Python 3.11.9 exists in the Windows Store installation and is registered for the current user, but its executable is not on PATH and sandboxed direct invocation is denied. The authorized local interpreter was invoked directly.
- Python 3.11.9, pip 26.2, and installed requirements were confirmed. Census HTTPS access works from the authorized local process; all 13 active official sources returned HTTP 200 and are validated with SHA-256 in the manifest.
- Actual-source parser, geography reconciliation, feasibility QA, data build, rankings, metrics, explanations, and figures completed. Gate: `PASS_WITH_LIMITATIONS`.
- The approved full model command completed with 383 training MSAs, 100 evaluation candidates, and alpha 1.0. White-space top-five captured 838 net additions; population and Ridge captured -8 each.
- Final validation: `pip 26.2`; `python -m pytest -q` passed 37/37; `python -m compileall -q src run_all.py tests` exited 0; `python -m src.fetch_data` revalidated all 13 cached files and preserved HTTP 200 statuses; `python -m src.build_dataset` exited 0 with `DATASET_BUILT_QA_PASSED`; the approved `run_all.py` command exited 0 and regenerated tables and figures. Visual inspection confirmed both figures render cleanly.
- Final outputs: 383 training MSA rows; 100 evaluation candidates; 483 panel rows; no missing required values; white-space top-five observed total 838; population and Ridge top-five totals -8 each. No unresolved execution-access blocker remains.
- Final archive: `dist/Restaurant_Market_Expansion_Submission.zip`, 68 files; ZIP integrity test passed. Contains all 13 active raw inputs plus the retained List 2 audit artifact and manifest.
- The pre-submission audit is recorded in `FINAL_AUDIT.md`; the separate audited archive preserves the earlier ZIP and contains the final audited workspace state (69 members; CRC and member-hash validation passed).

## Follow-up: Git recovery, cleanup, visuals, and repeat execution - 2026-11-26
- Project and ancestor `.git` directories/files were absent. A bounded nearby OneDrive Desktop search found unrelated Git metadata only; the intended repository and remote could not be established. No Git init, stage, commit, or push occurred.
- Removed exactly 17 inspected `.pyc` files from project `__pycache__` folders; preserved `.pytest_cache` and all research evidence. Python validation recreated only ignored cache files.
- Added `presentation_assets/build_presentation_assets.py`; regenerated the static dashboard, four high-resolution chart PNGs, and summary from the verified CSVs. Chart layout was visually corrected. The native UI connector did not connect, so no rendered-browser screenshot was captured.
- Post-cleanup: Python 3.11.9; 37 tests passed; compileall passed; 13 active cached official sources revalidated; dataset gate/QA and the approved 383-training/100-candidate pipeline passed. The top-five results remain +838 white-space and -8 for Population and Ridge.
- Preserved the previous audited archive and created the presentation-inclusive `dist/Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip` (77 members). ZIP integrity and every member hash matched at archive time; see `FINAL_AUDIT.md`.

## Final reports audit and remote reconciliation - 2026-11-26
- User supplied the existing GitHub remote and `main`. The temporary clone's initial HEAD is `56ea0ef32e95101b36d896ebff2229c91829b605` (`Initial commit: MLB project setup`); the remote initially held only `.gitignore`, the same `AGENT.md` as local, and an outdated plan README. Original README bytes are retained locally as `README_MLB_PROJECT_SETUP.md` before the root README update.
- `reports/README.md` indexes the authoritative report/evidence. `reports/verify_reports.py` passed: all 9 metric rows and 15 top-five names/outcomes match the generated CSVs, both report figures exist, and four screenshots-folder chart files are byte-identical to the actual generated charts. No browser screenshot was captured.
- `.gitignore` retains required analytical data and outputs while excluding raw payloads, archives, caches, secrets and environments. The 13-source manifest remains included.
- Latest check: 37 tests passed; compileall passed; source validation passed; gate and dataset geography QA passed (383/100/1,169); approved pipeline exited 0. See `FINAL_AUDIT.md` for details.
- Refreshed presentation-inclusive archive contains 84 members, passes ZIP integrity, and has all member hashes matching the workspace; kept out of the GitHub staging set.
- Verified 69 eligible local files copied byte-for-byte into the temporary clone for review. Commit/push status is recorded after that phase completes.
- Clean-clone dependency installation identified the yanked Matplotlib 3.9.1 Windows release. The pin is updated to 3.9.1.post1 (a compatible Windows x64 wheel was verified); this fixes packaging only. Final post-fix clean-clone test/build status is recorded after rerunning it.

## Independent clean-clone verification - 2026-11-26
- Environment: Windows PowerShell 5.1 attached to the user's local workspace; Python 3.11.9 is installed in the Store package but off PATH, and sandbox restrictions block direct execution. The authorized elevated route ran the installed interpreter. The workspace folder has no `.git` metadata; the exact user-provided GitHub remote was cloned to a disposable temp directory to preserve existing history.
- Final implementation commit under independent verification: `3636a4af6fe7b8aff3dfc34e6a4f885ef25a7b52`. Requirements installed successfully in a clean Python 3.11.9 venv. `matplotlib` is pinned to 3.9.1.post1 for its compatible Windows wheel; analysis behavior is unchanged.
- Clean clone fetched/validated 13/13 official sources; full build passed with 383 training MSAs, 100 evaluation MSAs and 1,169 county/MSA links; approved model pipeline completed (alpha=1.0).
- Verification: pytest **37 passed**, compileall passed, report audit passed (9/9 metrics, 15/15 top-five values, 2 report figures, 4/4 chart matches). Top-five observed outcomes: +838 white-space; -8 population; -8 Ridge.
