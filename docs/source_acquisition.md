# Official source acquisition and build procedure

## Source retrieval

List official Census/OMB URLs:
```powershell
python -m src.fetch_data --list
```

Download all sources:
```powershell
python -m src.fetch_data
```

The county-assignment workbook is source ID `omb_2017_msa_list1`; filter its area-type field to metropolitan statistical areas. Census List 2 (`list2.xls`) is a principal-cities workbook and is not used for county assignments.
```powershell
python -m src.fetch_data --only omb_2017_msa_list1
```

The bounded downloader permits only HTTPS requests to `www2.census.gov`, caps file sizes, retries three times, verifies ZIP CRCs and signatures, rejects traversal/symlink/executable archive members, and records SHA-256, retrieval timestamps, HTTP status and validation status. It does not extract archives automatically. The active 13 source requests returned HTTP 200; cached files are revalidated locally without redownloading.

## Build the analytical panel

After all source files download successfully:
```powershell
python -m src.build_dataset
```

The builder reads archives in place and validates the List 1 county-assignment workbook after filtering to MSAs, CBP/PEP fields, county and MSA coverage, NAICS vintages, missingness, top-100 candidate pool and required outcomes. It compares the post-cutoff CBP 2017–2021 MSA reference file's MSA/county pairs with OMB 17-01 MSA assignments derived from Census List 1 as an ex-post geography audit; that file is not used as a simulated 2018 feature. It cross-checks every OMB MSA county FIPS against all three CBP county-reference vintages; an unmatched code blocks the build for explicit reconciliation. This is a code-coverage test, not proof that county boundaries or names are historically equivalent. It writes `data/processed/metro_panel.csv`, `feature_metadata.csv`, `data_dictionary.csv`, `omb_2017_msa_county_crosswalk.csv`, and `outputs/dataset_qa.json` only after its checks pass.

## Reproduce results

The current feasibility gate is `PASS_WITH_LIMITATIONS`, supported by actual-source inspection in `outputs/feasibility.md`. Reproduce the completed analysis with:
```powershell
python run_all.py --train-cutoff 2010-01-01 --evaluation-cutoff 2018-02-01
```

The runner checks that the gate is `PASS` or `PASS_WITH_LIMITATIONS`. It writes full rankings, top-5/10/20 shortlists, metric definitions, explanations and figures. The final analysis is summarized in `REPORT.md`.
