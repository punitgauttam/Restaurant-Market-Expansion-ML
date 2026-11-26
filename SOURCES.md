# Source register — prospect selection

Research checkpoint: 2026-11-26. Official Census Bureau and OMB sources. Release dates are as listed on official source pages; the CBP 2007 date is month-precision and conservatively represented as 2009-07-31. All required raw inputs were acquired, format-validated, and SHA-256 checksummed; see data/raw/download_manifest.csv.

| Input | Official page / direct file | Release date | Use |
|---|---|---:|---|
| CBP 2007 county | https://www.census.gov/data/datasets/2007/econ/cbp/2007-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2007/cbp07co.zip | July 2009 (month only) | Training features; 2002 NAICS 722211 |
| PEP 2008 county | https://www2.census.gov/programs-surveys/popest/datasets/2000-2008/counties/totals/co-est2008-alldata.csv ; layout https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2000-2008/co-est2008-alldata.pdf | 2009-03-19 | Training population |
| CBP 2010 county | https://www.census.gov/data/datasets/2010/econ/cbp/2010-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2010/cbp10co.zip | 2012-06-26 | Training outcome start; 2007 NAICS 722211 |
| CBP 2013 county | https://www.census.gov/data/datasets/2013/econ/cbp/2013-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2013/cbp13co.zip | 2015-04-23 | Training outcome end; 2012 NAICS 722513 |
| CBP 2015 county | https://www.census.gov/data/datasets/2015/econ/cbp/2015-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2015/cbp15co.zip | 2017-04-20 | Evaluation features; 2012 NAICS 722513 |
| PEP 2016 county | https://www2.census.gov/programs-surveys/popest/datasets/2010-2016/counties/totals/co-est2016-alldata.csv ; layout https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2016/co-est2016-alldata.pdf | 2017-03-23 | Evaluation population and top-100 candidate rule |
| CBP 2018 MSA | https://www.census.gov/data/datasets/2018/econ/cbp/2018-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2018/cbp18msa.zip | 2020-06-25 | Held-out outcome start; 2017 NAICS 722513 |
| CBP 2021 MSA | https://www.census.gov/data/datasets/2021/econ/cbp/2021-cbp.html ; https://www2.census.gov/programs-surveys/cbp/datasets/2021/cbp21msa.zip | 2023-04-27 | Held-out outcome end; 2017 NAICS 722513 |
| OMB Bulletin 17-01 | https://www.whitehouse.gov/wp-content/uploads/legacy_drupal_files/omb/bulletins/2017/b-17-01.pdf | 2017-08-15 | Official metro delineation and definitions |
| Census List 1 county-assignment workbook (MSA rows) | https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2017/delineation-files/list1.xls | Directory last modified 2018-01-23 | Fixed OMB Bulletin 17-01 MSA county assignments; filter to Metropolitan Statistical Area |

| CBP county geography 2002–2011 | https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef02.txt | Reference-file vintage | FIPS/name lookup for historical county coverage audit |
| CBP county geography 2012–2016 | https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef12.txt | Reference-file vintage | FIPS/name lookup for historical county coverage audit |
| CBP county geography 2017–2021 | https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef17.txt | Reference-file vintage | FIPS/name lookup for historical county coverage audit |
| CBP MSA geography 2017–2021 | https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/metro-area-geography-reference/msa_county_reference17.txt | Directory last modified 2021-09-13 | Ex-post check of 2018/2021 CBSA-to-county membership against OMB List 1 MSA assignments; never a 2018 predictor |

## Key documentation

- CBP 2018 dataset page: https://www.census.gov/data/datasets/2018/econ/cbp/2018-cbp.html — CBP describes CSV downloads, count during the week of March 12, and that from reference year 2017 cells with fewer than three establishments are dropped from publication.
- CBP 2021 dataset page: https://www.census.gov/data/datasets/2021/econ/cbp/2021-cbp.html — direct MSA file is provided.
- CBP MSA record layouts: https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts/metro-record-layout.html — 2018–2023 MSA schema.
- CBP record layouts: https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts.html.
- OMB/Census directory of 2017 delineation workbooks: https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2017/delineation-files/ . `list1.xls` and `list2.xls` are both listed with 2018-01-23 09:24 timestamps. List 1 is the county-assignment table; List 2 is the principal-cities table.
- Census CBP MSA reference: https://www.census.gov/programs-surveys/cbp/technical-documentation/reference/metro-area-geography-reference.html — MSA references are grouped into 2017–2021 and 2022–2023 batches. Census methodology says MSA updates are implemented in five-year batches. CBP 2018 and 2021 are in the same published MSA geography batch; actual file audit confirmed 383 MSA industry rows in each endpoint and an exact 1,169-pair match with the CBP 2017-2021 geography reference.
- Census CBP county reference: https://www.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference.html — county boundary reference batches include 2002–2011, 2012–2016 and 2017–2021. These are downloaded by the pipeline and their county FIPS sets are tested against the fixed 2017 OMB county list before aggregation. A missing code blocks the build. This first check detects identifier coverage only; county names/boundaries must still be reconciled explicitly if a code or name changes.
- CBP methodology / NAICS vintage schedule: https://www.census.gov/programs-surveys/cbp/technical-documentation/methodology.html — CBP uses 2002 NAICS for 2003–2007, 2007 NAICS for 2008–2011, 2012 NAICS for 2012–2016, and 2017 NAICS for 2017 onward. It also confirms that prior to reference year 2017, establishment counts were published when payroll was withheld for cells with fewer than three establishments; from 2017, such cells are dropped.
- Census NAICS concordance files (2002→2007; 2007→2012; 2012→2017): https://www.census.gov/naics/concordances/concordances.html. The published 2002→2007 table lists 722211 Limited-Service Restaurants → 722211 Limited-Service Restaurants; the 2007→2012 Federal Register concordance maps 722211 to 722513 and marks the 2012 industry content as unchanged. The concordance references are cited, but official workbook bytes are not retained in the raw input package. The downloaded CBP files' actual NAICS fields and target values were inspected and are recorded in `outputs/dataset_qa.json`.
- Federal Register 2012 NAICS recommendations (2007→2012 mapping table): https://www.govinfo.gov/content/pkg/FR-2010-05-12/pdf/2010-11290.pdf.
- NAICS 2017 code 722513 details and crosswalk: https://www.census.gov/naics/?details=722513&input=722513&year=2017. The downloaded CBP files were inspected and contain the expected target code in the applicable vintage-specific field.
- CBP noise infusion: https://www.census.gov/programs-surveys/cbp/technical-documentation/methodology.html.

## Historical retrieval status (superseded by the local Windows acquisition below)

The active downloader enumerates 13 required sources: six CBP ZIPs, two PEP county CSVs, three CBP county references, one CBP MSA reference, and Census List 1. An additional `omb_2017_msa_list2` workbook is retained as an audit artifact after inspection showed it contains principal cities, not county FIPS.

## Current acquisition record - 2026-11-26
All 13 active source files have been retrieved from the official URLs, format-validated, and recorded with byte size and SHA-256 in `data/raw/download_manifest.csv`. Each URL returned HTTP 200 during a bounded status probe. The CSV also includes cached local validation status. The additional List 2 workbook is an audit artifact and is not part of the active 13-source input set. Earlier DNS/TCP failures in the project history were execution-sandbox restrictions and are superseded by successful authorized local execution.

The active List 1 workbook is the county assignment crosswalk. List 2 is the principal-cities table. The 2017-2021 CBP MSA reference was compared against the List 1 MSA county set and matched exactly (383 MSA codes, 1,169 county pairs). The full acquisition and parsing evidence is summarized in `outputs/feasibility.md` and `outputs/dataset_qa.json`.
