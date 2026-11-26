# Phase 1 - Data feasibility gate

FEASIBILITY_GATE: PASS_WITH_LIMITATIONS
DESIGN_APPROVAL: APPROVED

## Decision and evidence (2026-11-26)

The approved historical design is feasible on actual official source files. All 13 active sources were retrieved and validated. The manifest records source URL, file, retrieval time, byte count, SHA-256, HTTP status and cached validation status in `data/raw/download_manifest.csv`. Each active source URL returned HTTP 200 during the verification probe. A previously acquired List 2 workbook is retained as a separate audit artifact; it is a principal-cities list and is not used as the county crosswalk.

The active OMB Bulletin 17-01 geography source is Census List 1, filtered to `Metropolitan Statistical Area`. It yields 383 US MSAs and 1,169 unique county assignments. Its directory last-modified metadata is 2018-01-23, before the approved 2018-02-01 evaluation cutoff, but that metadata does not prove first-publication date.

### Source and schema checks

- Six CBP files parse with their expected establishment field and one NAICS field. Target codes are 722211 for 2007/2010 and 722513 for 2013/2015/2018/2021. Target industry row counts are 3,000; 2,989; 2,987; 2,988; 383; and 383, respectively. The six files span 2002, 2007, 2012, and 2017 NAICS vintages as documented in `SOURCES.md`.
- PEP 2008 and PEP 2016 population files parse; all fixed OMB counties have population records. The 2016 PEP source required a Windows-1252 decoding fallback. Values were not interpolated.
- The CBP 2017-2021 MSA/county reference has 1,825 metro and micro-area pairs. Its MSA code set and 1,169 MSA county pairs exactly match the List 1 MSA crosswalk. CBP 2018 and 2021 target files each contain all 383 fixed MSA rows.
- County reference batches contain 3,140 (2002-2011), 3,143 (2012-2016), and 3,142 (2017-2021) US county codes. The only unmatched OMB code in the oldest reference and CBP 2007/2010 is Kalawao, FIPS 15005. Older files report the Maui unit, FIPS 15009, which is counted once; no restaurant count is imputed to Kalawao. PEP population remains separately observed (117 in 2008; 88 in 2016). A name encoding difference for FIPS 35013 is resolved by FIPS and documented in the QA output.
- The processed panel contains 483 rows: 383 full-sample training MSAs and 100 evaluation candidates. Required features and outcomes are complete. Every candidate has both 2018 and 2021 MSA target observations. No candidate was selected using the held-out outcome.

### Chronology, target, and geography

| Stage | Cutoff | Pre-cutoff features | Outcome | Release evidence |
|---|---|---|---|---|
| Training | 2010-01-01 | CBP 2007, PEP 2008 | CBP 2013 minus CBP 2010 | CBP 2010 released 2012-06-26; CBP 2013 released 2015-04-23 |
| Evaluation | 2018-02-01 | CBP 2015, PEP 2016 | CBP 2021 MSA minus CBP 2018 MSA | CBP 2018 released 2020-06-25; CBP 2021 released 2023-04-27 |

Counts are the CBP establishment measure anchored to the week containing March 12. County inputs are aggregated retrospectively to OMB 2017 boundaries. This is fixed-boundary harmonization, not a claim that the 2017 map was known in 2010. Training includes all eligible MSAs; only evaluation is limited to the 100 largest by 2016 population. The post-cutoff CBP 2017-2021 MSA reference is used only for ex-post geography validation.

### Limitations

- CBP omits post-2017 industry/geography cells below three establishments. A missing row is unknown, not zero, and any candidate missing either evaluation endpoint is rejected. For pre-2017 county data, CBP still published EST when payroll was suppressed for small cells; an absent target NAICS row therefore represents no reported establishments and is explicitly treated as zero. Explicit target rows with missing EST are rejected. These vintage-specific rules are documented in the builder and QA output.
- The OMB List 1 directory timestamp is not proof of first public release. The NAICS concordance references are documented, but concordance workbooks are not separately retained in raw files; actual target codes in each input were inspected.
- Historical county geography is checked through identifiers and published references, not historical polygon overlays. The Kalawao/Maui reporting-unit difference is reconciled at MSA aggregation.
- The 2018-2021 outcome includes COVID-19 and is a single unusual evaluation period.
- The label is industry-wide establishment net additions, not chain profit, survival, market share, or a causal estimate of entry returns.

## Gate decision

**PASS_WITH_LIMITATIONS.** The approved model pipeline has completed and can be reproduced from the cached source files. Empirical findings and metric definitions are in `REPORT.md` and the generated CSVs under `outputs/tables/`. Dataset QA is in `outputs/dataset_qa.json`. Earlier blocked-run records remain in `PROJECT_JOURNEY.md`; they describe prior execution restrictions and are superseded by the verified local run recorded there.
