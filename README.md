# Prospect Selection: Which US Metros Should a Fast-Food Chain Prioritise?

**Course:** Machine Learning for Business Analytics — Plaksha MS-AI, Monsoon 2026  
**Weight:** 35% of course grade  
**Presentations:** 26–27 November 2026 (12 minutes + 6 minutes Q&A; every team member presents)  
**Final submission:** 1 December 2026, 11:59 pm — dataset, reproducible Python script, brief run instructions, and public data sources.

> **Status: PROJECT PLAN — not an implemented or validated analysis.** No dataset download, geographic harmonisation, model result, or source availability is claimed to have been verified. Complete the feasibility gate before implementation. The professor's project brief is authoritative; this README is the team's proposed implementation.

## 1. Business decision and scope

A hypothetical limited-service restaurant chain has resources to **prioritise K = 5 metropolitan markets** out of approximately **100 candidate US metropolitan statistical areas (CBSAs)**. We will also compare **K = 10 and K = 20** as sensitivity checks. The output is an ordered ranking and two competing top-K shortlists for the **same decision situation**.

**Business objective:** identify metropolitan markets that appear to have strong capacity for additional limited-service restaurant establishments. **Observable evaluation proxy:** the **net change in industry-wide limited-service restaurant establishment counts** over a later period. This is *not* the chain's expected profit, store survival, market share, or a causal estimate of what would happen if it entered. A metro with high industry growth is not necessarily the best investment for a particular chain.

**Proposed retrospective setup:** rank eligible markets at a historical decision cutoff associated with 2014 and evaluate against 2014–2019 growth. **The exact information cutoff must be fixed after checking publication/release dates.** If necessary, move the decision cutoff or use older data; document the change before fitting models. Do not describe an annual data vintage as information available on 1 January of that year without proof.

**Candidate rule:** use the 100 largest eligible CBSAs by a *pre-outcome, available-at-cutoff* population estimate under a documented fixed geographic vintage. Establish the universe independently of 2014–2019 outcomes. Record exclusions, ties, missing data, and any change in sample size. Use the same candidates and target definition for every method. Existing restaurants are allowed: the decision is **market expansion/prioritisation, not first-ever market entry**.

## 2. Questions the project must answer

1. What exactly is the constrained business decision, and what does one dataset row represent?
2. Can public data support a historical, reproducible ranking with a genuine observable later outcome?
3. Do the two approaches select different markets, and *why*?
4. How do they compare with a meaningful, simple population baseline on held-out evidence?
5. What do the results establish, and what can they **not** establish about business success?

A complicated model is **not** a grading objective. The professor grades the coherence of problem, data, method, evaluation and conclusions.

## 3. Mandatory feasibility gate — before modelling

The agent must create a documented `outputs/feasibility.md` and establish:

- Official source URLs and successful downloads/API access for the required CBP and ACS vintages, plus a county-to-CBSA mapping.
- Actual industry classification codes and comparability across **2009, 2014 and 2019** (including the 2007-to-2012 NAICS revision). Do not assume a code is identical across vintages.
- Which years' features were **publicly released by each simulated decision cutoff**. Track reference period **and** release date for each variable.
- County/CBSA boundary vintage, county changes, aggregation rules and geographic coverage.
- Suppressed/missing establishment counts, zero versus suppressed distinction, sample attrition and whether the outcome is credible for enough metros.
- A usable **earlier training decision** with pre-decision features and later observed outcome, plus an independent later evaluation decision. Verify both before promising Ridge training.

**Gate outcome:** `PASS`, `PASS WITH DOCUMENTED LIMITATIONS`, or `BLOCKED`. If blocked, explain the specific issue and propose the smallest defensible adjustment; **do not silently switch the problem, fabricate observations, or proceed as though data were validated**. Ask the user before a substantive change of geography, category, target or time windows.

## 4. Proposed public data

| Layer | Candidate source | Intended use | Verification required |
|---|---|---|---|
| Restaurant establishments | US Census Bureau **County Business Patterns (CBP)**, 2009/2014/2019 | Limited-service restaurant counts, prior growth, later outcome | NAICS harmonisation, suppression, county coverage, release dates |
| Population and demographics | US Census Bureau **American Community Survey (ACS) 5-year**; candidate vintages 2005–2009 and 2010–2014, plus earlier vintages if required | Population, income, age, education, household change | Publication timing, variable definitions, comparability |
| Geography | Official Census/OMB CBSA delineation and county-to-CBSA crosswalk | Aggregate county observations into a consistent metro universe | Fixed vintage and boundary-change policy |

Official starting points: [Census CBP](https://www.census.gov/programs-surveys/cbp.html), [Census ACS](https://www.census.gov/programs-surveys/acs.html), [Census API](https://api.census.gov/data.html). These are **starting points, not proof that every required extract is accessible**. A Census API key may be useful; confirm whether the chosen endpoints require one. Log exact URLs, query parameters, dates accessed, licensing/terms and checksums where practical in `SOURCES.md`.

**One row:** a `(metro_id, decision_cutoff)` observation with documented pre-cutoff features and a future outcome. Preserve raw source values and a separate cleaned analytical table. Report exclusions and missingness explicitly.

## 5. Ranking methods

All methods rank the **same eligible metros** for the same cutoff and use only permitted information.

| Role | Method | Ranking rule |
|---|---|---|
| **Simple baseline** | Population | Rank by population known at the cutoff. |
| **Approach A** | White-space heuristic | `expected_establishments = population × national_establishments_per_capita`; `score = expected_establishments − current_establishments`. Estimate national density using only cutoff-eligible data, with consistent industry/geographic definitions. |
| **Approach B** | Ridge regression | Predict future **absolute net additions** from cutoff-eligible demographics, restaurant density, prior establishment growth and other justified features; rank by predictions. |

**Primary comparison:** Approach A versus Approach B; **benchmark:** population baseline. Ridge is the sole required ML model. Gradient boosting is optional only after the core comparison works, and must not displace the main analysis.

**Training/evaluation design:** the proposed historical training label is establishment change **2009–2014**, and the proposed independent evaluation label is change **2014–2019**. For the *training* row, predictors must have been available at the earlier decision cutoff (not 2014 values). For the *evaluation* row, predictors must have been available at the later decision cutoff (not 2019 values). Exact cutoffs and feature vintages remain **to be verified**. Fit imputation, scaling, feature selection and Ridge tuning only on training-side data; no test-outcome inspection for model selection. If only one earlier period is available, use a prespecified/simple Ridge configuration or training-only validation and state uncertainty.

Do not force the model to predict positive growth: net additions may be negative. Document the white-space score's interpretation and whether the national average includes the candidate metro itself.

## 6. Evaluation and comparison

**Primary outcome:** `count_2019 − count_2014` for the same harmonised metro and industry definition. Negative outcomes are allowed. Evaluate at **K = 5** primarily; K = 10 and 20 are robustness checks.

**Primary decision metrics:**

- **Realised total net additions in selected top K**, reported alongside the population baseline and the hindsight-best K. This is a *proxy* measure, not realised chain benefit.
- **Regret@K** = hindsight-best total minus the method's selected total (lower is better). Report the raw values; avoid misleading ratios when totals are zero or negative.

**Supporting metrics:** overlap/precision@K against actual top-K metros, NDCG@K **with an explicit treatment of negative gains** (e.g., documented nonnegative relevance transformation), and Spearman rank correlation. Use the same tie-handling policy across methods. Report exact shortlists, overlaps, and rank changes, with concrete feature-based explanations.

**Uncertainty and robustness (only if feasible):** bootstrap metros with a clear resampling unit; random-selection/permutation reference as supplemental context (never the sole baseline); compare absolute additions with growth rate as a *separate* target and discuss denominator effects. A second test window is optional **only if complete earlier features and labels exist**. Do not claim statistically significant superiority without a valid test and sufficient evidence.

**Evaluation integrity:** do not use 2014–2019 labels to select features, tune Ridge, choose metros, change K, select a favorable time period or revise the business target. The hindsight-best list is used **only for evaluation**, never as a feasible historical decision.

## 7. Limitations and interpretation

- Industry-wide establishment growth is a proxy for market opportunity, **not chain-level profit or a proven successful opening**; it also reflects supply, regulation, land availability, competition and development.
- Counts may be suppressed; NAICS definitions, ACS estimates, CBSA boundaries and publication dates may not align perfectly.
- One historical test window may reflect a particular economic regime; external validity is limited.
- Large markets may dominate absolute additions; growth rates favor smaller bases. Report this trade-off rather than declaring one target universally correct.
- The analysis is observational and does **not** establish causal returns from entering a selected metro.
- A weak result or a population baseline win is still a valid finding when honestly evaluated and explained.

## 8. Reproducibility and repository layout

The following is a **planned structure**, not a claim that these files already exist:

```text
.
├── README.md                  project specification and run instructions
├── AGENT.md                   staged instructions and safeguards for coding agent
├── SOURCES.md                 exact public datasets, URLs, release dates, access dates
├── REPORT.md                  internal results and limitations (optional for submission)
├── PROJECT_JOURNEY.md         decisions, pivots, experiments, failures (internal)
├── requirements.txt           pinned Python dependencies
├── run_all.py                 one entry point reproducing principal slide results
├── data/
│   ├── raw/                   untouched source extracts
│   └── processed/             documented metro-level dataset
├── src/
│   ├── fetch_data.py
│   ├── build_dataset.py
│   ├── models.py
│   ├── evaluate.py
│   └── compare.py
├── tests/                     data integrity and evaluation tests
├── outputs/
│   ├── feasibility.md
│   ├── figures/
│   └── tables/
└── app/                       optional Streamlit app, only if time remains
```

### Planned execution (after implementation)

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Optional, only if required by the selected Census API endpoints:
# export CENSUS_API_KEY="..."                 # Linux/macOS
# $env:CENSUS_API_KEY="..."                  # PowerShell

python run_all.py
# If implemented: python run_all.py --skip-download
```

The agent must make the final commands match the actual implementation, test them in a clean environment where possible, and ensure `run_all.py` reproduces the tables/figures used in the presentation. Never commit keys, credentials or unnecessary large files.

## 9. Required deliverables and presentation

- [ ] Public-source dataset with observation definition, data dictionary and missingness notes.
- [ ] Python script reproducing the **principal** presentation results.
- [ ] Brief tested run instructions and exact data sources.
- [ ] Presentation (12 minutes + 6 minutes Q&A): decision and K, candidate set, data and outcome, three methods, **two approach shortlists**, baseline comparison, evidence, why rankings differ, limitations; every member participates.

`REPORT.md`, `PROJECT_JOURNEY.md`, extended robustness, and Streamlit UI are **internal/optional** aids; the professor **does not require a written report or dashboard**. Prioritise valid evidence and the presentation over extras.

## 10. Honest current status and next action

This document specifies a plan only. **No model results, downloads, API compatibility checks, or historical-release-date checks have been completed.** Next: follow `AGENT.md` **Phase 0 (environment) and Phase 1 (feasibility)**, review the findings with the user, then implement the smallest defensible end-to-end pipeline.

## 14. Autonomous execution and data/security requirements

**The coding agent owns the end-to-end execution.** The user should not be expected to manually locate, download, clean, merge, or upload datasets. The agent must independently research official public sources, fetch the required files or API extracts, validate them, build the dataset, implement the methods, run the evaluation, and prepare reproducible outputs. Do not ask the user to perform routine project work.

If a source requires a free API key or account credential, first determine whether the same public data can be obtained without one. Prefer unauthenticated official downloads where practical. If a key is genuinely required, explain the exact blocker and offer a secure local configuration path; never ask the user to paste a secret into chat, a source file, a notebook, a log, or a Git commit.

### Local-first data handling

- Run the agent, models, data processing and analysis locally. Do not send project datasets, source extracts, prompts containing local data, credentials, or generated results to third-party cloud model APIs or external services.
- Internet access may be used **only to retrieve public source material and verify documentation/licensing**. Keep network activity limited to the official sources and endpoints needed for this project.
- A local Ollama model does not by itself guarantee system security. Treat the agent as software with potentially broad filesystem and shell access; restrict it to the project workspace where possible and require explicit confirmation before destructive or out-of-scope operations.
- Use public, non-sensitive data only. Do not collect personal data or attempt to identify individuals.

### Data integrity and security

- Verify HTTPS and official source domains before downloading. Record source URLs, retrieval timestamps, licences/terms, query parameters, file sizes and SHA-256 checksums where practical.
- Treat downloaded files as untrusted input. Do not execute scripts, macros, binaries or installers found inside downloaded archives. Inspect archive contents before extraction and reject path traversal, unexpected executable files and suspiciously large payloads.
- Preserve raw downloads unchanged in `data/raw/`; write transformations to `data/interim/` or `data/processed/`. Never overwrite the only copy of a source file.
- Validate file types, schemas, row counts, geographic identifiers, year fields, code values, duplicates, missingness and suppression markers before using data.
- Keep credentials out of code and version control. Use environment variables or an ignored local configuration file; provide a safe `.env.example` with placeholders only. Redact secrets from logs and reports.
- Do not upload local files or datasets to external websites, paste services, public repositories or cloud storage.
- Maintain a data lineage record connecting every derived feature and target to its original source, reference period, release date, transformation and validation checks.

### Leakage and evaluation security

The agent is responsible for preventing **temporal leakage, target leakage and evaluation contamination**. For every feature, it must verify when the information was publicly available, not merely the year the data describes. It must also ensure that test-period outcomes never influence candidate selection, feature engineering, preprocessing, model selection, hyperparameter tuning, threshold choices or narrative conclusions. Any leakage risk must be documented and resolved before results are reported.

The agent must run automated assertions that:
1. every feature's availability date is on or before its simulated decision cutoff;
2. every target period begins after that cutoff;
3. training and evaluation observations are separated as specified;
4. preprocessing and tuning are fitted using training data only;
5. the same candidate universe and target definition are used by all ranking methods.

If these checks cannot be established from evidence, mark the analysis blocked or revise the historical design transparently before modelling. Never conceal the uncertainty.
