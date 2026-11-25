# AGENT.md — Execution Contract for the Prospect Selection Project

**Read `README.md` first.** The professor's original project brief is the authority; `README.md` is the agreed implementation plan. Your role is to produce an **auditable, reproducible, honest** ranking analysis, not an impressive-looking demo. Do not claim completion before real data and scripts have been tested.

## 0. Operating context and non-negotiable rules

- This may be executed by a **locally hosted coding agent** using **Ollama** and a DeepSeek-family model. Do not assume model name, context window, tool calling, GPU availability, internet access, shell permissions or agent framework. Check them first. **Ollama is for orchestrating code work; it is not a source of research evidence.** The analytical model is scikit-learn Ridge, not the local LLM.
- Work in small, inspectable phases. Before every material change, state the intended action and acceptance test. After each phase, summarize files changed, commands run, outputs, failures and unresolved risks.
- **Do not invent** data, observations, citations, opening dates, model metrics, test results, or source availability. Mark unverified claims `UNVERIFIED`.
- Never silently change geography, industry, decision date, outcome, candidate definition, K or comparison methods. Propose a change with rationale and **ask the user** before changing the central project.
- Never treat suppression as zero; never interpolate a future outcome into a historical feature; never leak test labels into feature design, tuning, candidate selection or model selection.
- Do not commit, push, tag, delete user files, overwrite original inputs, or install major system software without explicit user permission. No autonomous Git commits/tags.
- Never expose API keys or secrets in logs or files. Prefer environment variables. Avoid unnecessary large downloads and verify storage limits.
- If tools/network are unavailable, record the blocker and ask for access or a user-provided verified extract. **Do not simulate successful downloads.**
- Prioritise the professor's deliverables: dataset + reproducible Python script + instructions + source documentation + defensible presentation. Dashboard and elaborate reports are optional.

## 1. Working protocol for a local coding agent

1. Inspect repository contents and current git status without modifying them. Check OS, Python version, free disk/RAM, network reachability and installed packages. Report findings.
2. Read `README.md` and the professor's project brief if present. If they conflict, surface the conflict and follow the brief after confirming with the user.
3. Maintain `PROJECT_JOURNEY.md` as a chronological log: timestamps, decisions, source attempts, commands, errors, diagnoses, fixes, results and what remains unverified. Preserve failed attempts.
4. Work with small source files and deterministic functions. Use explicit CLI options, helpful errors, type hints where useful, and structured logging. Prefer `pandas`, `numpy`, `scikit-learn`, `requests`, `matplotlib` and `pytest` over an unnecessary framework.
5. Write a short checkpoint summary at the end of every phase. **Pause for user review at the feasibility gate and before any scope-changing decision.**
6. Do not confuse the local LLM's own predictions with project outcomes. The project's ground truth comes from official datasets.

## 2. Phase 0 — Set up and inspect (no modelling)

**Actions:** inventory existing files; establish Python environment; plan dependencies; create missing directories only when needed. Confirm that `README.md` is the current specification. Do not assume scaffolded files exist.

**Acceptance:** environment and repository inventory recorded; no source data overwritten; execution plan and blockers visible to user.

## 3. Phase 1 — Data feasibility gate (mandatory STOP/GO)

**Goal:** prove the proposed dataset and time split are usable **before** implementing a model.

**Tasks:**

1. Find exact official CBP downloads/API endpoints for 2009, 2014, 2019; identify limited-service restaurant NAICS codes under the applicable classifications, and validate cross-year comparability.
2. Find official ACS 5-year extracts for demographic variables, including vintages usable at each *actual* decision cutoff. **Document the publication/release date separately from the reference year.**
3. Find official county-to-CBSA delineation/crosswalk; document its vintage and boundary treatment. Check county FIPS consistency and how missing/unassigned counties are handled.
4. Download a **small representative sample first**. Validate schema, types, county coverage, count fields, missing/suppressed values, and that industry counts are not accidentally all-industry totals.
5. Verify whether the earlier training window (proposed 2009–2014) can use **pre-2009-cutoff** features, and whether the later evaluation window (2014–2019) can use **pre-2014-cutoff** features. Check when CBP and ACS values became public; if annual release timing makes the dates impossible, propose explicit revised cutoffs and matching target periods. Do not quietly label a retrospective year-end extract as information available on January 1 of that year.
6. Estimate sample size, suppression and missingness after county aggregation. Verify whether approximately 100 metros remain under a pre-outcome population-based selection rule.
7. Verify API terms, licenses, URLs, query parameters, access dates, checksums where possible, and API-key requirements. Log everything in `SOURCES.md`.

**Required output:** `outputs/feasibility.md` with a source-by-source evidence table, release-date matrix, NAICS mapping, geographic policy, sample counts, missingness, risks, exact tested download commands, and decision: **PASS / PASS WITH DOCUMENTED LIMITATIONS / BLOCKED**.

**STOP:** if the outcome is unobservable, dates leak future information, NAICS cannot be harmonised, or too few valid metros remain, **do not train**. Propose the smallest defensible alternative, seek user approval, and update README + journal if approved.

## 4. Phase 2 — Define the decision and build the dataset

**Prerequisite:** feasibility gate approved.

1. Freeze the candidate universe from the 100 largest eligible CBSAs using a population estimate demonstrably available at the evaluation cutoff; record geography vintage, tie policy and exclusions. Never use future growth to choose candidates.
2. Preserve untouched source files in `data/raw/`. Make acquisition repeatable; use cached local files when available.
3. Build county-to-metro aggregation with tests for duplicated FIPS, county double counting, unmatched counties and suppressed observations. Record geographic/industry comparability decisions.
4. Create one observation per `(metro_id, decision_cutoff)` and a data dictionary. Make the training and evaluation datasets independently reproducible.
5. Define the target `net_additions = later_establishments - earlier_establishments` (can be negative). Also compute growth rate as an optional separate target with explicit handling for zero baselines.
6. Include only verified cutoff-eligible features: population, income, age/education where comparable, restaurant establishments per capita, earlier growth where truly available. Avoid post-cutoff statistics.
7. Produce QA outputs: row counts, date ranges, NAICS mapping, missingness, suppression, geographic coverage, feature distributions and label distributions. Explain every dropped row.

**Acceptance:** reproducible processed tables, documented schema, stable candidate universe, no future feature dates, passing data-integrity tests.

## 5. Phase 3 — Implement the rankings

Implement in `src/models.py` with deterministic interfaces, using **exactly the same candidate set**:

- **Population baseline:** descending eligible population.
- **Approach A, white-space:** `population × national_establishments_per_capita − existing_establishments`, with national density calculated from cutoff-eligible data and clearly documented geography. No target leakage.
- **Approach B, Ridge:** train on an earlier historical decision/outcome window using its own earlier features, then predict net additions for the held-out later decision. Fit imputation/scaling inside an sklearn `Pipeline`; do not fit preprocessors on held-out data. Choose alpha using only training-side information (or prespecify it if honest validation is not possible).

Keep negative predictions. Fix reproducible tie-breaking by metro ID. Save full rankings and top-5/10/20 lists. **Do not add gradient boosting unless the baseline/A/B analysis is already correct and the user agrees it is worth the time.**

**Acceptance:** every metro has exactly one rank per method; feature timing checks pass; methods produce reproducible scores and shortlists; no held-out outcomes used in fitting.

## 6. Phase 4 — Evaluate against genuinely held-out outcomes

**Primary:** observed total net additions captured by top K and regret versus the hindsight-best K, for K=5 (main), 10 and 20 (sensitivity). Compare all methods against the population baseline. Regret is a hindsight evaluation device, **not** a historical selection method.

**Supporting:** overlap/precision@K with actual top-K metros, Spearman correlation and NDCG@K with a documented nonnegative relevance transformation when outcomes can be negative. Handle ties, missingness and zero/negative denominators consistently. Show actual top-K selections, not just aggregate scores.

**Optional if time/data support it:** bootstrap with a documented metro-level resampling unit, random-selection/permutation reference (supplementary only), growth-rate sensitivity, or another complete temporal test window. Do not manufacture p-values or confidence intervals.

**Acceptance:** evaluation code tested on small hand-calculated fixtures; `outputs/tables/` contains full ranking, method comparison, shortlist overlap, per-metro explanations and metric definitions; no metric is described as profit or chain-specific success.

## 7. Phase 5 — Explain and defend the decision

Create a concise `REPORT.md` for internal use with:

1. Decision, K, candidate construction and why it is a real constrained business choice.
2. Data provenance, observation definition, availability cutoff, NAICS and CBSA harmonisation.
3. Training/evaluation chronology and leakage prevention.
4. Side-by-side **Approach A vs Approach B** top-5 lists, plus population baseline; overlapping and differing metros.
5. Primary metrics, supporting metrics, actual outcome values, uncertainty if computed, and which method won **or did not win**.
6. Feature-level explanation of why notable metros moved between methods; no invented causal explanations.
7. Honest limitations: industry-wide expansion is not chain profit, one test regime, missingness, boundary/code issues, observational design, possible model instability.
8. A brief answer to the professor's four guiding questions and an explicit statement of what the evidence cannot establish.

Prepare presentation-ready tables/figures that can be regenerated by `run_all.py`. A Streamlit UI is **optional** and should not delay the core submission.

## 8. Phase 6 — Package and verify reproducibility

- Provide `run_all.py` as the documented entry point. It must regenerate the **principal** slide results from the submitted dataset or documented public downloads; support an offline/cached-data path when practical.
- Pin dependencies, test clean execution, use relative paths, and avoid hardcoded secrets or machine-specific absolute paths.
- Run `pytest`, data QA, pipeline execution, and compare the regenerated output with presentation numbers. Capture actual commands, exit codes, versions and results in the journal.
- Ensure dataset, script, run instructions and sources satisfy the professor's final deliverables. **A written report and UI are not required by the brief.**
- Do not commit or push without explicit permission. Present a final manifest of files, verified results, unresolved limitations and how to reproduce.

## 9. Priority and time budget

**P0:** valid public outcome data, valid historical features, no leakage, working baseline and two approaches, same candidate universe.  
**P1:** correct held-out metrics, two shortlists, interpretable comparisons, reproducible script, presentation.  
**P2:** uncertainty/sensitivity, extra model, dashboard, visual polish.

If short on time, **reduce P2 scope, not integrity**. If feasibility fails, say so clearly rather than manufacturing a finished project.

## 10. Mandatory phase checkpoint template

At the end of each phase report:

```text
PHASE: <name>
STATUS: PASS / PARTIAL / BLOCKED
FILES CHANGED: <paths>
COMMANDS ACTUALLY RUN: <commands and outcomes>
VERIFIED EVIDENCE: <datasets, dates, counts, metrics, or tests>
UNVERIFIED / RISKS: <specific issues>
DECISIONS MADE: <and rationale>
USER APPROVAL NEEDED: <yes/no, for what>
NEXT ACTION: <one concrete next step>
```

**Final instruction:** Prefer a small, correct, explainable project to a large project that only looks complete.

## 11. Autonomous ownership: do the work, do not delegate routine tasks to the user

The agent is responsible for completing the project end to end. The user has limited time and should not be asked to manually find datasets, download files, run routine cleaning, construct tables, or perform standard validation.

**You must independently:**
- Research and identify the authoritative public datasets and documentation.
- Fetch the datasets using official bulk downloads or APIs.
- Retry sensible official endpoints and investigate documented alternatives when a download fails.
- Inspect, clean, harmonise and join the data.
- Build and validate the analytical dataset.
- Implement the population baseline, white-space score and Ridge model.
- Evaluate and compare the methods, generate tables/figures, and write the internal report.
- Create and test the reproducible run script and final submission package.

Do not stop after merely providing download instructions or code that expects the user to fetch the data. The normal expected outcome is that the agent itself downloads and prepares the data. If a source is genuinely inaccessible from the machine after reasonable retries and alternative official endpoints have been checked, document the exact error, attempts and evidence; then continue with other independent work where possible. Ask the user only when a real external dependency or a substantive change in project scope makes progress impossible.

Do not ask for approval for routine, reversible work within the agreed scope. Seek approval only before changing the business question, geography, industry category, outcome definition or core time design; spending money; creating accounts; accepting legal terms on the user's behalf; exposing data externally; or performing destructive actions outside the project workspace.

## 12. Local-agent and data-security operating rules

The intended execution environment is a locally hosted coding agent using a local model through Ollama (the exact DeepSeek model and agent framework will be selected separately). Design the workflow to be model-agnostic and local-first.

### Network and privacy boundaries
- Use the network only for necessary public-data retrieval and official documentation/licence verification.
- Do not call hosted LLM APIs, external embedding APIs, cloud inference endpoints, paste services or external data-processing services.
- Do not transmit project files, raw or processed datasets, prompts containing dataset contents, logs, credentials or results to third parties.
- Do not send local files to a web search or other external service. Search public documentation using general queries that do not reveal private local content.
- This project should use public aggregate data only. Do not acquire personal, confidential, proprietary or restricted data.

### Filesystem and command safety
- Keep all project writes inside the repository/workspace. Do not inspect unrelated personal directories or files.
- Never run downloaded code, binaries, macros, shell scripts or installers. Download data and documentation only; inspect archives before extraction.
- Before extracting archives, list their contents and reject absolute paths, `..` traversal, symlinks escaping the workspace, executable payloads or unexpected file types.
- Do not use `sudo`, alter system configuration, install system-wide packages, delete user files, or run broad cleanup commands. Use a project virtual environment.
- Do not overwrite raw source files. Preserve originals and write derived outputs separately.
- Do not commit, push, publish, upload or share files without explicit permission.
- Use bounded downloads and reasonable retry/backoff. Avoid hammering APIs or violating source terms.

### Secrets and credentials
- Prefer official public downloads that require no API key.
- If a key is necessary, do not ask the user to paste it into chat. Provide a local-only environment-variable or ignored configuration-file method, and continue with tasks that do not require the key.
- Never write secrets into source code, notebooks, README/AGENT, logs, reports, command history or Git-tracked files.
- Add appropriate secret/config patterns to `.gitignore`; provide `.env.example` containing placeholders only. Redact credentials from diagnostic output.
- Never create accounts, accept terms, incur charges or use paid APIs without explicit user approval.

### Supply-chain and source validation
- Prefer official Census Bureau and other primary-source domains. Verify HTTPS and check redirects before downloading.
- Record exact URL, retrieval timestamp, source title, reference period, publication/release date, licence/terms, file size, checksum and retrieval method in `SOURCES.md`.
- Treat all downloaded files as untrusted data. Validate file format, size, schema, expected columns, encodings and row counts. Never execute content embedded in a data file.
- Record any third-party dependency, version and installation source. Use pinned project dependencies where feasible.

## 13. Mandatory automated leakage and data-quality controls

Before any model fitting, implement and run checks that fail loudly when:
- a feature's documented public release date is later than the simulated decision cutoff;
- a feature reference period or aggregation accidentally includes post-cutoff observations;
- a target/outcome field appears in the feature matrix;
- training labels overlap the evaluation outcome window;
- preprocessing, feature selection or hyperparameter tuning is fitted using evaluation data;
- candidate metros were selected using future outcomes;
- the ranking methods use different candidate sets or inconsistent target definitions;
- suppressed, unavailable or missing values have been silently converted to zero;
- county-to-CBSA aggregation duplicates or drops geography without a recorded explanation;
- NAICS definitions are treated as comparable without evidence.

For each feature, retain machine-readable metadata such as `feature_name`, `source`, `reference_period`, `release_date`, `decision_cutoff`, `transformation`, `missingness_policy`, and `leakage_check_status`.

Create tests for these controls and include their results in `outputs/feasibility.md` and the final run log. If a release date cannot be established, mark that feature as unverified and exclude it from the primary model until resolved.

## 14. Autonomous recovery and progress policy

When a download or API request fails:
1. Capture the exact URL/endpoint, HTTP status or exception, timestamp and a short redacted diagnostic.
2. Check official documentation for endpoint changes, required parameters, rate limits and alternative official bulk files.
3. Retry with bounded backoff; do not loop indefinitely.
4. Try a documented alternative official endpoint or file format.
5. Validate any alternative against the intended geography, industry, period and definitions.
6. Record whether the issue is resolved, remains a limitation, or blocks the project.

Do not stop all work because one source is unavailable. Continue independent research, code scaffolding, schema tests and documentation while keeping modelling blocked if the required evidence is missing. Do not replace unavailable observations with synthetic data or AI-generated values.

At each checkpoint, distinguish clearly between **completed autonomously**, **blocked by an external dependency**, and **requires user decision**. The user should receive concise checkpoint summaries, not a stream of routine questions. Do not claim that a dataset was fetched, a test passed or a result was reproduced unless the action actually succeeded.

## 15. Updated final acceptance criteria

The project is not complete until the agent has:
- fetched and retained the required public source datasets itself, or documented a specific unavoidable access blocker and an approved alternative;
- produced a source register and data lineage;
- passed the automated release-date, temporal-leakage, target-leakage and geographic-integrity checks;
- created the candidate dataset and data dictionary;
- implemented all three rankings on the same candidates;
- evaluated the rankings against held-out observed outcomes;
- generated the principal tables and figures from a reproducible script;
- run tests and a clean end-to-end reproduction;
- prepared `REPORT.md`, run instructions and a final deliverables manifest.

A project with a polished report but no verified downloaded data, or with results contaminated by future information, **fails acceptance**.
