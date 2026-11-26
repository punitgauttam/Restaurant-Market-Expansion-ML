# Data contract — approved design

## Processed panel

`data/processed/metro_panel.csv` has one training row for each of the 383 US MSAs in 2017 OMB MSA assignments (Census List 1 filtered to MSA) and one evaluation row for each of the 100 largest eligible MSAs by 2016 population. The top-100 evaluation set is the shared ranking universe. Ridge trains on the full eligible historical MSA sample, not a sample selected by later population.

Required columns:
- `metro_id`: 5-character CBSA/MSA code as string. The training slice can contain all 383 US MSAs; the evaluation slice contains the top 100.
- `metro_name`: official MSA title from 2017 OMB MSA assignments (Census List 1 filtered to MSA).
- `decision_cutoff`: `2010-01-01` or `2018-02-01`.
- `target_start`, `target_end`: March 12 CBP reference-week anchors for 2010–2013 or 2018–2021.
- `target_release_date`: public release date of the later CBP target file.
- `net_additions`: later CBP establishment count minus earlier CBP establishment count; may be negative.
- `population`: PEP 2008 for training / PEP 2016 for evaluation, aggregated by 2017 2017 OMB MSA assignments (Census List 1 filtered to MSA) membership.
- `current_establishments`: CBP 2007 for training / CBP 2015 for evaluation, limited-service NAICS.
- `restaurants_per_10k`: current establishments divided by population × 10,000.
- `national_establishments_per_capita`: same-cutoff national restaurant establishments divided by the corresponding national PEP population. The numerator uses county rows only (state-summary rows are excluded) and matches the 50 states plus DC geography of the denominator.

## Source vintage map

| Source ID | Geography | Industry code | Use |
|---|---|---|---|
| `cbp_2007_county` | County | 2002 NAICS 722211 | Training feature |
| `cbp_2010_county` | County | 2007 NAICS 722211 | Training target start |
| `cbp_2013_county` | County | 2012 NAICS 722513 | Training target end |
| `pep_2008_county` | County | population estimate 2008-07-01 | Training population |
| `cbp_2015_county` | County | 2012 NAICS 722513 | Evaluation feature |
| `pep_2016_county` | County | population estimate 2016-07-01 | Evaluation population/candidates |
| `cbp_2018_msa` | MSA | 2017 NAICS 722513 | Evaluation target start |
| `cbp_2021_msa` | MSA | 2017 NAICS 722513 | Evaluation target end |
| `omb_2017_msa_list1` | MSA and county assignment | n/a | Fixed 2017 geography and candidate construction |

Downloaded CBP files expose one NAICS code field and contain the approved vintage-specific limited-service codes; source counts are in outputs/dataset_qa.json.

## Feature metadata

`data/processed/feature_metadata.csv` records feature_name, source, reference_period, release_date, decision_cutoff, transformation, missingness_policy, and leakage_check_status. The downloaded sources, release chronology, and joins passed the documented QA; the 2017-2021 CBP geography reference is used only as post-cutoff validation.

## Suppression and missingness

Never replace an explicit missing/suppressed/unknown value with zero. Pre-2017 CBP documentation says establishment counts remained published when payroll was suppressed; if an entire industry row is absent in a pre-2017 county file, this may represent no reported establishments, but this must be confirmed against the actual file and documented. Beginning 2017, CBP drops cells with fewer than three establishments, so an absent evaluation MSA-industry row is unknown and must not be zero-filled. The builder fails closed on candidate outcomes missing either endpoint.
