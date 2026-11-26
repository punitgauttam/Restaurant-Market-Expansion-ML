# Current approved plan — Restaurant Market Expansion

**Current authority for implementation:** `docs/revised_design_proposal.md` (approved in chat on 2026-11-26). The original README is preserved as `README_ORIGINAL.md`; `AGENT.md` remains the execution contract. The revised timing plan supersedes the original proposed 2009–2014 / 2014–2019 backtest dates.

## Business decision
Rank the top 100 eligible US Metropolitan Statistical Areas (MSAs) by pre-outcome population, then compare three methods for prioritising five markets for limited-service restaurant expansion:

1. Population baseline.
2. White-space heuristic: `population × national_establishments_per_capita − current_establishments`.
3. Ridge regression on earlier all eligible historical training observations, with imputation/scaling fitted only on training rows and a prespecified alpha of 1.0.

K=5 is primary; K=10 and K=20 are sensitivity checks. Historical Ridge training uses all eligible OMB 17-01 US MSAs; the 2016-population top-100 selection is used only to define the 2018 evaluation ranking universe. All ranking methods use exactly that same 100-market evaluation set. Evaluation uses industry-wide net establishment additions as an observable proxy, not chain profitability or causal entry returns.

## Approved dates

| Stage | Decision cutoff | Available input features | Later outcome |
|---|---|---|---|
| Training | 2010-01-01 | CBP 2007 county counts (2002 NAICS 722211) + PEP 2008 county population | CBP 2013 establishments minus CBP 2010 establishments |
| Evaluation | 2018-02-01 | CBP 2015 county counts (2012 NAICS 722513) + PEP 2016 county population | CBP 2021 MSA establishments minus CBP 2018 MSA establishments |

All CBP counts use the week containing March 12 reference. The evaluation window includes the COVID-19 disruption and must be interpreted as one unusual historical test period.

## Geography and classification

Use the 2017 OMB MSA-only county assignments for retrospective aggregation of historical county CBP/PEP inputs. The official Census 2017 county-assignment workbook is List 1; filter its Metropolitan/Micropolitan Statistical Area field to Metropolitan Statistical Area. Census List 2 is a principal-cities workbook without county FIPS and is retained only as an audit artifact. The 2017-2021 CBP MSA reference exactly matches all 383 OMB MSA codes and 1,169 county pairs. The historical Kalawao/Maui reporting-unit code change is explicitly reconciled; the Dona Ana name discrepancy is a source-encoding variant keyed to FIPS 35013. Fixed 2017 geography is retrospective, not a claim that 2017 boundaries were known at the 2010 cutoff.

CBP NAICS vintages: 2002 for 2007; 2007 for 2010; 2012 for 2013/2015; 2017 for 2018/2021. Limited-service restaurant code mapping used: 2002/2007 NAICS 722211; 2012/2017 NAICS 722513. The actual downloaded CBP files were inspected and contain the expected vintage-specific NAICS fields and values. The published 2002→2007 concordance lists 722211→722211; the 2007→2012 table maps 722211 to 722513 with unchanged industry content. The official concordance workbooks are cited but are not retained as raw inputs, so their byte-level provenance is not independently packaged.

## Current execution state

**Design approval: APPROVED. Feasibility gate: PASS_WITH_LIMITATIONS.** Actual source acquisition, county/MSA geography checks, NAICS fields, data coverage, and panel completeness are recorded in `outputs/feasibility.md` and `outputs/dataset_qa.json`. Earlier blocked-network notes are historical and superseded by the local Windows execution completed on 2026-11-26.
