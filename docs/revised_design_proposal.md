# Approved historical design — 3-year prospect selection backtest

**Status: APPROVED BY USER in this conversation on 2026-11-26.** This supersedes the proposed dates in the original README for the implementation run. The original README is preserved as `README_ORIGINAL.md`; `AGENT.md` remains the execution contract.

## Why the original design cannot be used prospectively

The original design proposes 2009–2014 training and 2014–2019 evaluation. But CBP 2014 was released in 2016, so the 2014 target value was not available at a 2014 decision. The proposed historical information cutoff and outcome chronology therefore do not fit together.

## Approved working design

| Role | Decision cutoff | Features available by cutoff | Target outcome | Target publication |
|---|---|---|---|---|
| Training row | **2010-01-01** | County CBP 2007, limited-service restaurants under 2002 NAICS 722211; county PEP 2008 population | CBP 2013 establishments minus CBP 2010 establishments, both measured for the week containing March 12 | CBP 2010 released 2012-06-26; CBP 2013 released 2015-04-23 |
| Evaluation row | **2018-02-01** | County CBP 2015, limited-service restaurants under 2012 NAICS 722513; county PEP 2016 population | CBP 2021 MSA establishments minus CBP 2018 MSA establishments, for the week containing March 12 | CBP 2018 released 2020-06-25; CBP 2021 released 2023-04-27 |

Both outcome windows are approximately three years, with establishment counts anchored to the CBP reference week containing March 12. These are reference-week anchors, not daily observations. The evaluation cutoff is **February 1, 2018** rather than January 1 because the official Census directory lists the machine-readable county-assignment workbook (Census List 1) as last modified on January 23, 2018. OMB Bulletin 17-01 itself is dated August 15, 2017. The directory timestamp is evidence of the file's last-modified metadata, not a complete archival proof of first publication; this is disclosed as a limitation.

The user approved the three-year redesign. The one-month cutoff refinement was separately communicated and adopted to place the 2017 county-assignment workbook metadata before the evaluation cutoff. The active source is Census List 1 filtered to MSAs; Census List 2 is a principal-cities table and is not the county crosswalk. The forecast business objective remains prioritising 5 of the same 100 candidate US metropolitan markets using population, white-space and Ridge methods. K=5 is primary; K=10/20 are sensitivity analyses.

## Geography and candidate construction

- Use OMB Bulletin 17-01 MSA county assignments from Census List 1, filtering its area-type field to `Metropolitan Statistical Area`. The downloaded Census `list2.xls` is titled Principal Cities and has no county FIPS; it is retained only as audit evidence.
- Retain the 383 US MSAs and their county membership under OMB 17-01. Territories/Puerto Rico are excluded from the US universe.
- Aggregate historical county CBP/PEP values to these fixed 2017 OMB county-to-MSA assignments. Build the training sample from all eligible US MSAs. Separately rank the evaluation-time MSAs by 2016 PEP population and retain the top 100; ties are broken by ascending CBSA code. This prevents the later top-100 selection from influencing which historical training rows are included.
- Use direct MSA CBP files for 2018 and 2021 outcomes. The CBP 2017-2021 MSA/county reference exactly matches the 383 OMB MSA codes and 1,169 List 1 county assignments used here.

**Retrospective geography caveat:** applying 2017 OMB membership to 2007–2015 county data is fixed-boundary harmonisation. It is not a claim that the 2017 definitions were available at the 2010 training cutoff. The analysis is a retrospective model-development exercise evaluated at a 2018 decision, and the training units are harmonised to the later fixed geography. The report must disclose this, quantify county assignment differences when comparison vintages are available, and avoid describing the training decision map as a contemporaneous 2010 map.

## NAICS harmonisation

- CBP 2007: 2002 NAICS **722211**; CBP 2010: 2007 NAICS **722211**. The downloaded CBP files were inspected and contain the expected single NAICS fields and target values. The published 2002→2007 concordance row maps 722211 Limited-Service Restaurants to the same 2007 code and title. The official concordance workbook is cited, but its raw bytes are not retained in this package.
- CBP 2013 and CBP 2015: 2012 NAICS **722513** (Limited-Service Restaurants).
- CBP 2018 and CBP 2021: 2017 NAICS **722513**.

The NAICS editions are not the same across the full period: Census states CBP 2003–2007 uses 2002 NAICS, 2008–2011 uses 2007 NAICS, 2012–2016 uses 2012 NAICS, and 2017 onward uses 2017 NAICS. The published 2002→2007 concordance lists 722211 Limited-Service Restaurants → 722211 Limited-Service Restaurants. The 2007→2012 Federal Register concordance maps 722211 Limited-Service Restaurants to 722513 Limited-Service Restaurants and states the content is unchanged. The downloaded CBP files were inspected and contain the expected vintage-specific codes: 722211 for 2007/2010 and 722513 for 2013/2015/2018/2021; counts are recorded in `outputs/dataset_qa.json`. The official concordance files themselves are cited but not retained as raw inputs, so their local byte-level provenance remains unavailable.

## Methods and leakage controls

1. Population baseline: rank by 2016 population available at the evaluation cutoff.
2. White-space: `population × national_establishments_per_capita − current_establishments`, using CBP 2015 and PEP 2016 national density available by the evaluation cutoff.
3. Ridge: train on all eligible historical MSA rows with 2010-cutoff features and 2010–2013 net-addition labels; evaluate/rank the top-100 2018-cutoff candidates. Primary predictors: population, current establishments, establishments per 10,000 residents. Median imputation and scaling are fitted only on training rows; Ridge alpha is prespecified at 1.0. No evaluation labels are used for candidate selection, features, tuning or ranking.

All three methods must use the exact same top-100 evaluation CBSA IDs. Ridge's training sample can be larger (all eligible historical MSAs) and is not selected using 2016 population. Negative net additions and negative Ridge predictions are retained. Suppressed/unavailable values remain missing and cannot silently become zero.

## Critical data limitations

- From CBP reference year 2017, industry/geography cells with fewer than three establishments are dropped from publication. Missing 2018/2021 MSA-industry rows are therefore unknown, not zero. The builder rejects any candidate lacking either evaluation endpoint.
- The evaluation period 2018–2021 includes the COVID-19 pandemic and associated business disruptions. Treat results as a single unusual historical stress period, not a typical or stable growth regime.
- CBP data are subject to disclosure-avoidance methods. For the project variable `EST`, the documented comparability issue to handle explicitly is that pre-2017 establishment counts were published for small cells, whereas from 2017 cells with fewer than three establishments are omitted. Do not assume a missing post-2017 row is zero. The project does not use employment or payroll to rank markets.
- The outcome is industry-wide establishment net additions, not chain-specific profitability, survival, market share, opening feasibility or a causal estimate of market entry success.
- The geography is fixed retrospectively to OMB 2017; CBP 2018/2021 uses the 2017–2021 MSA batch. The downloaded CBP reference contains the same 383 MSA codes and 1,169 List 1 MSA county pairs. This identifier comparison does not establish historical polygon equivalence.

## Approval and remaining gate

The temporal redesign is approved. **The feasibility gate is PASS_WITH_LIMITATIONS** following local acquisition and data QA; see `outputs/feasibility.md` for the evidence and remaining limitations.
