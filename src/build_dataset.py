"""Build the two-period CBSA panel from verified official Census/OMB files.

Raw ZIPs are read in place; nothing is extracted or executed. The builder fails
closed if expected schemas, geography joins, counts, or candidate outcomes fail.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unicodedata
import zipfile
from typing import Iterable

import numpy as np
import pandas as pd

from .fetch_data import ROOT, SOURCES, GEOGRAPHY_SOURCE

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
TRAIN_CUTOFF = "2010-01-01"
EVAL_CUTOFF = "2018-02-01"  # after the List 1 county geography workbook's 2018-01-23 posting
CANDIDATE_COUNT = 100
OMB_EXPECTED_MSA_COUNT = 383
OMB_EXPECTED_COUNTY_COUNT = 1169
HISTORIC_KALAWAO_FIPS = "15005"
HISTORIC_MAUI_REPORTING_FIPS = "15009"
HISTORIC_KALAWAO_MSA = "27980"


COUNTY_GEO_REF_IDS = (
    "cbp_county_geo_2002_2011",
    "cbp_county_geo_2012_2016",
    "cbp_county_geo_2017_2021",
)
MSA_GEO_REF_ID = "cbp_msa_geo_2017_2021"

CBP_ID = {
    "cbp_2007_county": ("cbp07co", "county", "722211"),  # 2002 NAICS vintage
    "cbp_2010_county": ("cbp10co", "county", "722211"),
    "cbp_2013_county": ("cbp13co", "county", "722513"),
    "cbp_2015_county": ("cbp15co", "county", "722513"),
    "cbp_2018_msa": ("cbp18msa", "msa", "722513"),
    "cbp_2021_msa": ("cbp21msa", "msa", "722513"),
}


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _code(value: object, width: int) -> str | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "-", "(x)"}:
        return None
    # Excel numeric cells often arrive as e.g. 10420.0.
    if re.fullmatch(r"\d+\.0+", s):
        s = s.split(".", 1)[0]
    digits = re.sub(r"\D", "", s)
    if not digits:
        return None
    return digits.zfill(width)


def _read_cbp_zip(source_id: str) -> pd.DataFrame:
    if source_id not in CBP_ID:
        raise ValueError(f"Unsupported CBP source ID: {source_id}")
    stem, geography, target_naics = CBP_ID[source_id]
    zpath = RAW / SOURCES[source_id]["filename"]
    if not zpath.is_file():
        raise FileNotFoundError(f"Missing raw source: {zpath}")
    with zipfile.ZipFile(zpath) as archive:
        members = [n for n in archive.namelist()
                   if not n.endswith("/") and Path(n).suffix.lower() in {".txt", ".csv"}
                   and Path(n).name.lower().startswith(stem)]
        if len(members) != 1:
            raise ValueError(f"{source_id}: expected one {stem} text member; found {members}")
        with archive.open(members[0]) as stream:
            frame = pd.read_csv(stream, dtype=str, encoding="utf-8-sig", low_memory=False)
    frame.columns = [_norm(c) for c in frame.columns]
    required_geo = {"est", "fipstate", "fipscty"} if geography == "county" else {"est", "msa"}
    missing_geo = required_geo - set(frame.columns)
    if missing_geo:
        raise ValueError(f"{source_id}: file schema missing geography/count columns {sorted(missing_geo)}; got {frame.columns.tolist()}")
    naics_columns = [c for c in frame.columns if c in {"naics", "naics2002", "naics2007", "naics2012", "naics2017"}]
    if len(naics_columns) != 1:
        raise ValueError(f"{source_id}: expected exactly one NAICS code field; found {naics_columns}")
    if naics_columns[0] != "naics":
        frame = frame.rename(columns={naics_columns[0]: "naics"})
    frame["naics"] = frame["naics"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    frame["est"] = pd.to_numeric(frame["est"].str.replace(",", "", regex=False), errors="coerce")
    frame.attrs["source_id"] = source_id
    frame.attrs["target_naics"] = target_naics
    frame.attrs["geography"] = geography
    frame.attrs["row_count"] = int(len(frame))
    if geography == "county":
        frame["state_fips"] = frame["fipstate"].map(lambda x: _code(x, 2))
        frame["county_fips_part"] = frame["fipscty"].map(lambda x: _code(x, 3))
        frame["county_fips"] = frame["state_fips"].fillna("") + frame["county_fips_part"].fillna("")
        frame.loc[frame["county_fips"].str.len() != 5, "county_fips"] = None
    else:
        frame["cbsa_code"] = frame["msa"].map(lambda x: _code(x, 5))
    return frame


def _read_pep(source_id: str, year: int) -> pd.DataFrame:
    path = RAW / SOURCES[source_id]["filename"]
    if not path.is_file():
        raise FileNotFoundError(f"Missing raw source: {path}")
    try:
        frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError:
        frame = pd.read_csv(path, dtype=str, encoding="cp1252", low_memory=False)
    frame.columns = [_norm(c) for c in frame.columns]
    required = {"sumlev", "state", "county", f"popestimate{year}"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{source_id}: missing PEP fields {sorted(missing)}")
    frame = frame[frame["sumlev"].astype(str).str.zfill(3) == "050"].copy()
    # 50 states plus DC; territories are outside the proposed US metro universe.
    frame["state_fips"] = frame["state"].map(lambda x: _code(x, 2))
    frame["county_fips_part"] = frame["county"].map(lambda x: _code(x, 3))
    frame["county_fips"] = frame["state_fips"].fillna("") + frame["county_fips_part"].fillna("")
    frame = frame[frame["state_fips"].between("01", "56")].copy()
    frame["population"] = pd.to_numeric(frame[f"popestimate{year}"].str.replace(",", "", regex=False), errors="coerce")
    if frame["county_fips"].duplicated().any():
        raise ValueError(f"{source_id}: duplicate county FIPS in PEP county rows")
    if frame.population.isna().any() or (frame.population <= 0).any():
        raise ValueError(f"{source_id}: population contains missing/nonpositive county values")
    return frame[["county_fips", "population"]]


def read_omb_msa_list1(path: Path | None = None) -> pd.DataFrame:
    """Read List 1 county assignments and retain OMB-defined MSAs only.

    Census List 2 is a principal-cities list and contains no county FIPS
    assignments. List 1 contains both metro and micro geographies; its area
    type field is used to select only Metropolitan Statistical Areas.
    """
    path = path or (RAW / GEOGRAPHY_SOURCE["filename"])
    if not path.is_file():
        raise FileNotFoundError(f"Missing OMB Bulletin 17-01 List 1 workbook: {path}")
    xls = pd.ExcelFile(path, engine="xlrd")
    found = None
    required_aliases = {
        "cbsa_code": {"cbsacode", "cbsa"},
        "state_fips": {"fipsstatecode", "statefipscode", "statefips"},
        "county_fips_part": {"fipscountycode", "countyfipscode", "countyfips"},
        "area_type": {"metropolitanmicropolitanstatisticalarea"},
        "county_name": {"countycountyequivalent"},
    }
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
        for idx in range(min(len(raw), 30)):
            vals = {_norm(v) for v in raw.iloc[idx].tolist() if pd.notna(v)}
            if all(any(alias in vals for alias in aliases)
                   for aliases in required_aliases.values()):
                found = (raw, idx)
                break
        if found:
            break
    if not found:
        raise ValueError("Could not locate CBSA/FIPS/area-type header row in OMB List 1 workbook.")
    raw, header_idx = found
    headers = [_norm(v) for v in raw.iloc[header_idx].tolist()]
    positions: dict[str, int] = {}
    for canonical, aliases in required_aliases.items():
        matches = [i for i, h in enumerate(headers) if h in aliases]
        if len(matches) != 1:
            raise ValueError(f"OMB List 1: expected one column for {canonical}; headers={headers}")
        positions[canonical] = matches[0]
    title_matches = [i for i, h in enumerate(headers) if h in {"cbsatitle", "cbsaname", "areatitle"}]
    if not title_matches:
        raise ValueError(f"OMB List 1: CBSA title column not found; headers={headers}")
    positions["metro_name"] = title_matches[0]
    result = raw.iloc[header_idx + 1:, [positions[k] for k in positions]].copy()
    result.columns = list(positions.keys())
    result["area_type"] = result.area_type.astype(str).str.strip()
    result = result[result.area_type.eq("Metropolitan Statistical Area")].copy()
    result["cbsa_code"] = result.cbsa_code.map(lambda x: _code(x, 5))
    result["state_fips"] = result.state_fips.map(lambda x: _code(x, 2))
    result["county_fips_part"] = result.county_fips_part.map(lambda x: _code(x, 3))
    result["county_fips"] = result.state_fips.fillna("") + result.county_fips_part.fillna("")
    result["metro_name"] = result.metro_name.astype(str).str.strip()
    result = result[(result.state_fips >= "01") & (result.state_fips <= "56")
                    & result.cbsa_code.notna() & (result.county_fips.str.len() == 5)
                    & result.metro_name.ne("") & result.metro_name.ne("nan")].copy()
    if result.cbsa_code.nunique() != OMB_EXPECTED_MSA_COUNT:
        raise ValueError(f"OMB List 1 MSA filter expected {OMB_EXPECTED_MSA_COUNT} US MSAs; found {result.cbsa_code.nunique()}")
    if result.county_fips.nunique() != OMB_EXPECTED_COUNTY_COUNT:
        raise ValueError(f"OMB List 1 MSA filter expected {OMB_EXPECTED_COUNTY_COUNT} unique US counties; found {result.county_fips.nunique()}")
    if result.county_fips.duplicated().any():
        raise ValueError("OMB List 1 MSA assignments put a county in multiple MSAs; resolve before aggregation.")
    title_counts = result.groupby("cbsa_code").metro_name.nunique()
    if (title_counts > 1).any():
        raise ValueError("OMB List 1 has inconsistent metro names for a CBSA code.")
    return result[["cbsa_code", "metro_name", "county_fips", "county_name"]].sort_values(
        ["cbsa_code", "county_fips"]).reset_index(drop=True)


def _county_rows_coverage(cbps: dict[str, pd.DataFrame], crosswalk: pd.DataFrame) -> None:
    for source_id, frame in cbps.items():
        if "county_fips" not in frame:
            continue
        expected = set(crosswalk.county_fips)
        if source_id in {"cbp_2007_county", "cbp_2010_county"}:
            # In CBP's 2002-2011 county vintage, Kalawao (15005) is not a
            # separate reporting unit; its establishments are reported with
            # Maui (15009). Both counties map to CBSA 27980 in the fixed OMB
            # geography. Retain and count the historical reporting unit once.
            codes_to_msa = crosswalk.set_index("county_fips").cbsa_code.astype(str)
            if (codes_to_msa.get(HISTORIC_KALAWAO_FIPS) != HISTORIC_KALAWAO_MSA
                    or codes_to_msa.get(HISTORIC_MAUI_REPORTING_FIPS) != HISTORIC_KALAWAO_MSA):
                raise ValueError("Historical Kalawao/Maui reporting reconciliation no longer maps to one MSA.")
            expected.discard(HISTORIC_KALAWAO_FIPS)
        seen = set(frame.county_fips.dropna().unique())
        missing = sorted(expected - seen)
        if missing:
            raise ValueError(f"{source_id}: {len(missing)} OMB MSA counties absent from CBP file; sample={missing[:8]}")


def _county_industry_to_msa(frame: pd.DataFrame, crosswalk: pd.DataFrame,
                            source_id: str) -> tuple[pd.Series, float, int]:
    code = CBP_ID[source_id][2]
    # Pre-2017 county files publish the establishment count even when payroll
    # is suppressed for cells below three establishments. An omitted NAICS
    # row therefore represents no reportable establishments; an explicit row
    # with missing EST is not converted to zero.
    selected = frame[frame.naics == code].copy()
    if selected.duplicated("county_fips").any():
        raise ValueError(f"{source_id}: duplicate county-industry rows for {code}")
    if selected.est.isna().any() or (selected.est < 0).any():
        raise ValueError(f"{source_id}: EST missing/negative for explicit NAICS {code} rows")
    county_counts = selected.set_index("county_fips").est.astype(float)
    aggregation_crosswalk = crosswalk
    if source_id in {"cbp_2007_county", "cbp_2010_county"}:
        # Do not impute a separate value to absent FIPS 15005. The CBP
        # historical reporting unit 15009 is included once and already maps
        # to the same MSA.
        aggregation_crosswalk = crosswalk[
            crosswalk.county_fips.ne(HISTORIC_KALAWAO_FIPS)
        ].copy()
    mapped = aggregation_crosswalk.set_index("county_fips").join(county_counts.rename("est"), how="left")
    # Fill zero only for pre-2017 files, for which CBP's own disclosure note
    # confirms establishment counts remain published below three.
    mapped["est"] = mapped.est.fillna(0.0)
    msa_counts = mapped.groupby("cbsa_code").est.sum()
    if "state_fips" in selected:
        state_mask = selected.state_fips.between("01", "56")
    else:
        # Lightweight fixture compatibility; production CBP parser always adds state_fips.
        state_mask = selected.county_fips.astype(str).str[:2].between("01", "56")
    if "county_fips_part" in selected:
        county_mask = selected.county_fips_part.between("001", "998")
    else:
        # CBP geography reference documentation uses county code 999 for state totals.
        county_mask = selected.county_fips.astype(str).str[-3:].between("001", "998")
    us_county_selected = selected[state_mask & county_mask].copy()
    # Avoid double-counting state summary records in the national numerator.
    national_total = float(us_county_selected.est.sum())
    return msa_counts, national_total, int(len(us_county_selected))


def _msa_industry_counts(frame: pd.DataFrame, source_id: str, crosswalk: pd.DataFrame) -> tuple[pd.Series, int]:
    code = CBP_ID[source_id][2]
    selected = frame[frame.naics == code].copy()
    selected = selected[selected.cbsa_code.isin(set(crosswalk.cbsa_code))].copy()
    if selected.duplicated("cbsa_code").any():
        raise ValueError(f"{source_id}: duplicate MSA-industry rows for {code}")
    if selected.est.isna().any() or (selected.est < 0).any():
        raise ValueError(f"{source_id}: explicit MSA EST value is missing/negative")
    return selected.set_index("cbsa_code").est.astype(float), int(len(selected))


def _aggregate_pep_to_msa(pep: pd.DataFrame, crosswalk: pd.DataFrame, source_id: str) -> tuple[pd.Series, float]:
    missing = sorted(set(crosswalk.county_fips) - set(pep.county_fips))
    if missing:
        raise ValueError(f"{source_id}: {len(missing)} OMB counties lack PEP population; sample={missing[:8]}")
    mapped = crosswalk.merge(pep, on="county_fips", how="left", validate="many_to_one")
    if mapped.population.isna().any():
        raise ValueError(f"{source_id}: missing population after CBSA join")
    return mapped.groupby("cbsa_code").population.sum(), float(pep.population.sum())


def _assert_county_crosswalk_coverage(frame: pd.DataFrame, crosswalk: pd.DataFrame, source_id: str) -> None:
    expected = set(crosswalk.county_fips)
    seen = set(frame.county_fips.dropna().unique())
    missing = sorted(expected - seen)
    if missing:
        raise ValueError(f"{source_id}: CBP lacks {len(missing)} counties in OMB MSA universe; sample={missing[:8]}")


def _read_county_geography_reference(source_id: str) -> pd.DataFrame:
    """Read a CBP county FIPS reference file and return county codes/names."""
    if source_id not in COUNTY_GEO_REF_IDS:
        raise ValueError(f"Unsupported county geography reference: {source_id}")
    path = RAW / SOURCES[source_id]["filename"]
    if not path.is_file():
        raise FileNotFoundError(f"Missing county geography reference: {path}")
    encodings = ["utf-8-sig", "cp1252"]
    frame = None
    errors = []
    for encoding in encodings:
        try:
            frame = pd.read_csv(path, dtype=str, encoding=encoding)
            break
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    if frame is None:
        raise ValueError(f"{source_id}: unsupported county-reference encoding: {errors}")
    frame.columns = [_norm(c) for c in frame.columns]
    name_column = next((name for name in ("ctyname", "countyname") if name in frame.columns), None)
    required = {"fipstate", "fipscty"}
    missing = required - set(frame.columns)
    if missing or name_column is None:
        if name_column is None:
            missing.add("ctyname/county_name")
        raise ValueError(f"{source_id}: reference file missing fields {sorted(missing)}")
    frame["state_fips"] = frame.fipstate.map(lambda x: _code(x, 2))
    frame["county_fips_part"] = frame.fipscty.map(lambda x: _code(x, 3))
    frame["county_fips"] = frame.state_fips.fillna("") + frame.county_fips_part.fillna("")
    frame = frame[frame.state_fips.between("01", "56")
                  & frame.county_fips_part.notna()
                  & frame.county_fips_part.ne("999")].copy()
    if frame.county_fips.duplicated().any():
        raise ValueError(f"{source_id}: duplicate county FIPS in reference file")
    if frame[name_column].isna().any() or frame[name_column].astype(str).str.strip().eq("").any():
        raise ValueError(f"{source_id}: missing county names")
    return frame[["county_fips", name_column]].rename(columns={name_column: "county_name"}).reset_index(drop=True)


def _normalize_county_name(value: object) -> str:
    name = str(value).split(",", 1)[0].strip().casefold()
    name = "".join(ch for ch in unicodedata.normalize("NFKD", name)
                   if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", name)

def validate_county_geography_vintages(crosswalk: pd.DataFrame) -> dict:
    """Compare OMB fixed geography codes/names with CBP county references.

    Kalawao County (15005) is the single recorded exception in the 2002-2011
    CBP batch; it is contained in the Maui County (15009) reporting unit. Both
    map to CBSA 27980, so county aggregation remains one MSA observation.
    """
    expected = set(crosswalk.county_fips)
    if not expected:
        raise ValueError("OMB MSA crosswalk contains no counties")
    summary = {}
    for source_id in COUNTY_GEO_REF_IDS:
        reference = _read_county_geography_reference(source_id)
        available = set(reference.county_fips)
        missing = sorted(expected - available)
        reconciled = []
        if source_id == "cbp_county_geo_2002_2011" and missing == [HISTORIC_KALAWAO_FIPS]:
            county_to_msa = crosswalk.set_index("county_fips").cbsa_code.astype(str)
            if (county_to_msa.get(HISTORIC_KALAWAO_FIPS) != HISTORIC_KALAWAO_MSA
                    or county_to_msa.get(HISTORIC_MAUI_REPORTING_FIPS) != HISTORIC_KALAWAO_MSA
                    or HISTORIC_MAUI_REPORTING_FIPS not in available):
                raise ValueError("Kalawao 15005 is absent from the 2002-2011 reference and its Maui 15009 reconciliation failed.")
            reconciled = [HISTORIC_KALAWAO_FIPS]
            missing = []
        if missing:
            raise ValueError(
                f"{source_id}: {len(missing)} OMB 2017 counties are absent from this CBP county reference vintage; "
                f"county FIPS changes must be reconciled before fixed-MSA aggregation. Sample={missing[:10]}"
            )
        name_differences = []
        recognized_name_variants = []
        unexplained_name_differences = []
        if "county_name" in crosswalk.columns:
            comparable = crosswalk[crosswalk.county_fips.isin(available)].merge(
                reference, on="county_fips", suffixes=("_omb", "_cbp"), validate="one_to_one")
            for row in comparable.itertuples(index=False):
                if _normalize_county_name(row.county_name_omb) != _normalize_county_name(row.county_name_cbp):
                    difference = {"county_fips": row.county_fips,
                                  "omb_name": row.county_name_omb,
                                  "cbp_name": row.county_name_cbp}
                    name_differences.append(difference)
                    normalized_names = {
                        _normalize_county_name(row.county_name_omb),
                        _normalize_county_name(row.county_name_cbp),
                    }
                    if (row.county_fips == "35013"
                            and normalized_names == {"donaanacounty", "doaanacounty"}):
                        recognized_name_variants.append({
                            **difference,
                            "resolution": "CBP georef17 uses byte 0xB1 (plus/minus under Windows-1252) in the Doña Ana label; FIPS 35013 and OMB name resolve the county identity.",
                        })
                    else:
                        unexplained_name_differences.append(difference)
        if unexplained_name_differences:
            raise ValueError(f"{source_id}: unexplained county-name differences: {unexplained_name_differences[:10]}")
        summary[source_id] = {
            "reference_counties": int(len(reference)),
            "omb_msa_counties_covered": int(len(expected)),
            "unmatched_omb_counties": 0,
            "reconciled_historical_codes": reconciled,
            "county_name_differences": name_differences,
            "recognized_name_variants": recognized_name_variants,
        }
    return summary


def _read_msa_geography_reference(source_id: str = MSA_GEO_REF_ID) -> pd.DataFrame:
    """Read CBP's 2017-2021 MSA-to-county reference using flexible header aliases."""
    if source_id != MSA_GEO_REF_ID:
        raise ValueError(f"Unsupported CBP MSA geography reference: {source_id}")
    path = RAW / SOURCES[source_id]["filename"]
    if not path.is_file():
        raise FileNotFoundError(f"Missing CBP MSA geography reference: {path}")
    frame = None
    errors = []
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            candidate = pd.read_csv(path, dtype=str, sep=None, engine="python", encoding=encoding)
            candidate.columns = [_norm(c) for c in candidate.columns]
            frame = candidate
            break
        except Exception as exc:
            errors.append(f"{encoding}: {type(exc).__name__}: {exc}")
    if frame is None:
        raise ValueError("Could not parse CBP MSA geography reference: " + "; ".join(errors))

    aliases = {
        "cbsa_code": {"msa", "msacode", "cbsacode", "cbsa", "areacode"},
        "state_fips": {"fipstate", "statefips", "fipsstate", "statefipscode"},
        "county_fips_part": {"fipscty", "fipscounty", "countyfips", "fipscountycode"},
    }
    positions = {}
    for canonical, allowed in aliases.items():
        matches = [col for col in frame.columns if col in allowed]
        if len(matches) != 1:
            raise ValueError(f"CBP MSA geography reference: expected one {canonical} column; columns={frame.columns.tolist()}")
        positions[canonical] = matches[0]
    out = pd.DataFrame({k: frame[v] for k, v in positions.items()})
    out["cbsa_code"] = out.cbsa_code.map(lambda x: _code(x, 5))
    out["state_fips"] = out.state_fips.map(lambda x: _code(x, 2))
    out["county_fips_part"] = out.county_fips_part.map(lambda x: _code(x, 3))
    out["county_fips"] = out.state_fips.fillna("") + out.county_fips_part.fillna("")
    out = out[(out.state_fips >= "01") & (out.state_fips <= "56")
              & out.cbsa_code.notna() & out.county_fips.str.len().eq(5)].copy()
    if out.duplicated(["cbsa_code", "county_fips"]).any():
        raise ValueError("CBP MSA geography reference has duplicate MSA/county assignments")
    return out[["cbsa_code", "county_fips"]].sort_values(
        ["cbsa_code", "county_fips"]).reset_index(drop=True)


def validate_cbp_msa_geography(crosswalk: pd.DataFrame) -> dict:
    """Compare ex-post CBP 2017-2021 MSA county membership with OMB 17-01 List 2."""
    cbp_ref = _read_msa_geography_reference()
    omb_pairs = set(zip(crosswalk.cbsa_code.astype(str), crosswalk.county_fips.astype(str)))
    cbp_pairs_all = set(zip(cbp_ref.cbsa_code.astype(str), cbp_ref.county_fips.astype(str)))
    expected_codes = set(crosswalk.cbsa_code.astype(str))
    cbp_codes = {code for code, _ in cbp_pairs_all}
    # CBP can carry micropolitan codes in the same file; only List 2 MSA IDs are compared.
    cbp_pairs = {(code, county) for code, county in cbp_pairs_all if code in expected_codes}
    missing_pairs = sorted(omb_pairs - cbp_pairs)
    extra_pairs = sorted(cbp_pairs - omb_pairs)
    missing_codes = sorted(expected_codes - cbp_codes)
    if missing_pairs or extra_pairs or missing_codes:
        raise ValueError(
            "CBP 2017-2021 MSA geography does not exactly match OMB List 2; "
            f"missing_pairs={len(missing_pairs)} sample={missing_pairs[:8]}, "
            f"extra_pairs={len(extra_pairs)} sample={extra_pairs[:8]}, "
            f"missing_codes={missing_codes[:8]}"
        )
    return {"cbp_reference_rows": int(len(cbp_ref)),
            "omb_msa_count": int(len(expected_codes)),
            "omb_msa_county_pairs": int(len(omb_pairs)),
            "exact_omb_pair_match": True,
            "reference_vintage": "2017-2021",
            "validation_only_not_evaluation_cutoff_feature": True}

def _source_release(source_id: str) -> str:
    return str(SOURCES[source_id]["release_date"])


def _feature_metadata() -> pd.DataFrame:
    rows = []
    design = [
        (TRAIN_CUTOFF, "population", "PEP county 2008", "2008-07-01", _source_release("pep_2008_county"), "sum county POPESTIMATE2008 by OMB 17-01 CBSA"),
        (TRAIN_CUTOFF, "current_establishments", "CBP county 2007", "2007; week containing March 12", _source_release("cbp_2007_county"), "filter NAICS 722211; sum county EST by OMB 17-01 CBSA"),
        (TRAIN_CUTOFF, "restaurants_per_10k", "CBP 2007 + PEP 2008", "2007/2008", _source_release("cbp_2007_county"), "current establishments / population * 10000"),
        (TRAIN_CUTOFF, "national_establishments_per_capita", "CBP 2007 + PEP 2008", "2007/2008", _source_release("cbp_2007_county"), "US county EST sum / US county population sum"),
        (EVAL_CUTOFF, "population", "PEP county 2016", "2016-07-01", _source_release("pep_2016_county"), "sum county POPESTIMATE2016 by OMB 17-01 CBSA"),
        (EVAL_CUTOFF, "current_establishments", "CBP county 2015", "2015; week containing March 12", _source_release("cbp_2015_county"), "filter NAICS 722513; sum county EST by OMB 17-01 CBSA"),
        (EVAL_CUTOFF, "restaurants_per_10k", "CBP 2015 + PEP 2016", "2015/2016", max(_source_release("cbp_2015_county"), _source_release("pep_2016_county")), "current establishments / population * 10000"),
        (EVAL_CUTOFF, "national_establishments_per_capita", "CBP 2015 + PEP 2016", "2015/2016", max(_source_release("cbp_2015_county"), _source_release("pep_2016_county")), "US county EST sum / US county population sum"),
    ]
    for cutoff, feature, source, period, release, transform in design:
        rows.append({"feature_name": feature, "source": source, "reference_period": period,
                     "release_date": release, "decision_cutoff": cutoff,
                     "transformation": transform,
                     "missingness_policy": "Explicit missing values are never imputed; pre-2017 absent target NAICS rows are treated as zero under CBP EST publication rules, while post-2017 absent MSA cells remain unknown and are rejected.",
                     "leakage_check_status": "PASS"})
    return pd.DataFrame(rows)


def _data_dictionary() -> pd.DataFrame:
    rows = [
        ("metro_id", "Five-digit CBSA code, retained as text to preserve leading zeroes.", "OMB Bulletin 17-01 MSA assignments", "identifier"),
        ("metro_name", "Official 2017 metropolitan statistical area title.", "OMB Bulletin 17-01 MSA assignments", "text"),
        ("decision_cutoff", "Simulated information cutoff for the observation.", "Approved design", "date"),
        ("target_start", "CBP week-containing-March-12 anchor for the first target year.", "CBP", "date"),
        ("target_end", "CBP week-containing-March-12 anchor for the last target year.", "CBP", "date"),
        ("target_release_date", "Public release date of the final CBP source used in the target.", "Census CBP release record", "date"),
        ("net_additions", "Later limited-service CBP EST minus earlier EST; may be negative.", "CBP; NAICS vintage mapped by source year", "establishments"),
        ("population", "County PEP population summed to the fixed OMB 2017 MSA geography.", "Census PEP county estimates", "people"),
        ("current_establishments", "Limited-service restaurants at the feature vintage, aggregated to fixed MSA geography.", "CBP EST; NAICS vintage mapped by source year", "establishments"),
        ("restaurants_per_10k", "Current establishments divided by population and multiplied by 10,000.", "Derived from CBP and PEP", "establishments per 10,000 people"),
        ("national_establishments_per_capita", "US county-only CBP establishments divided by US county PEP population; state summaries excluded.", "Derived from CBP and PEP", "establishments per person"),
    ]
    return pd.DataFrame(rows, columns=["field", "definition", "source", "unit_or_format"])


def _build_panel(crosswalk: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    pep08 = _read_pep("pep_2008_county", 2008)
    pep16 = _read_pep("pep_2016_county", 2016)

    cbp = {source_id: _read_cbp_zip(source_id) for source_id in CBP_ID}
    county_sources = {k: v for k, v in cbp.items() if CBP_ID[k][1] == "county"}
    _county_rows_coverage(county_sources, crosswalk)

    pep08_msa, pep08_us_total = _aggregate_pep_to_msa(pep08, crosswalk, "pep_2008_county")
    pep16_msa, pep16_us_total = _aggregate_pep_to_msa(pep16, crosswalk, "pep_2016_county")

    cbp07_msa, cbp07_us_total, cbp07_industry_rows = _county_industry_to_msa(cbp["cbp_2007_county"], crosswalk, "cbp_2007_county")
    cbp10_msa, _, cbp10_rows = _county_industry_to_msa(cbp["cbp_2010_county"], crosswalk, "cbp_2010_county")
    cbp13_msa, _, cbp13_rows = _county_industry_to_msa(cbp["cbp_2013_county"], crosswalk, "cbp_2013_county")
    cbp15_msa, cbp15_us_total, cbp15_industry_rows = _county_industry_to_msa(cbp["cbp_2015_county"], crosswalk, "cbp_2015_county")

    est18_msa, est18_rows = _msa_industry_counts(cbp["cbp_2018_msa"], "cbp_2018_msa", crosswalk)
    est21_msa, est21_rows = _msa_industry_counts(cbp["cbp_2021_msa"], "cbp_2021_msa", crosswalk)

    all_codes = sorted(crosswalk.cbsa_code.unique())
    names = crosswalk.drop_duplicates("cbsa_code").set_index("cbsa_code").metro_name
    population16 = pep16_msa.reindex(all_codes)
    if population16.isna().any():
        raise ValueError("Some OMB MSAs have no complete PEP2016 population.")
    all_metros = pd.DataFrame({"metro_id": all_codes, "metro_name": [names[x] for x in all_codes],
                               "population": population16.to_numpy()})
    # The future (2016) population cutoff defines only the evaluation candidate set.
    # Historical Ridge training must not be filtered by that later-selected top-100 list.
    candidates = all_metros.sort_values(["population", "metro_id"], ascending=[False, True], kind="mergesort").head(CANDIDATE_COUNT).copy()
    ids = set(candidates.metro_id)

    # This cutoff is set after the machine-readable Census List 1 file posted on 2018-01-23.
    # The CBP2018 reference-week anchor (week containing March 12) remains after cutoff.
    nat_density_train = cbp07_us_total / pep08_us_total
    nat_density_eval = cbp15_us_total / pep16_us_total
    if not np.isfinite(nat_density_train) or not np.isfinite(nat_density_eval):
        raise ValueError("National establishments-per-capita density is non-finite.")

    train = all_metros[["metro_id", "metro_name"]].copy()
    train = train.sort_values("metro_id", kind="mergesort").reset_index(drop=True)
    train["decision_cutoff"] = TRAIN_CUTOFF
    train["target_start"] = "2010-03-12"
    train["target_end"] = "2013-03-12"
    train["target_release_date"] = _source_release("cbp_2013_county")
    train["net_additions"] = train.metro_id.map(cbp13_msa - cbp10_msa)
    train["population"] = train.metro_id.map(pep08_msa)
    train["current_establishments"] = train.metro_id.map(cbp07_msa)
    train["restaurants_per_10k"] = train.current_establishments / train.population * 10000
    train["national_establishments_per_capita"] = nat_density_train

    evaluation = candidates.copy()
    evaluation["decision_cutoff"] = EVAL_CUTOFF
    evaluation["target_start"] = "2018-03-12"
    evaluation["target_end"] = "2021-03-12"
    evaluation["target_release_date"] = _source_release("cbp_2021_msa")
    evaluation["net_additions"] = evaluation.metro_id.map(est21_msa - est18_msa)
    evaluation["current_establishments"] = evaluation.metro_id.map(cbp15_msa)
    evaluation["restaurants_per_10k"] = evaluation.current_establishments / evaluation.population * 10000
    evaluation["national_establishments_per_capita"] = nat_density_eval

    panel = pd.concat([train, evaluation], ignore_index=True)
    panel = panel.sort_values(["decision_cutoff", "metro_id"], kind="mergesort").reset_index(drop=True)
    feature_columns = ["population", "current_establishments", "restaurants_per_10k", "national_establishments_per_capita"]
    missing = panel[feature_columns + ["net_additions"]].isna()
    if missing.any().any():
        missing_by_column = missing.sum().to_dict()
        missing_metros = panel.loc[missing.any(axis=1), ["decision_cutoff", "metro_id", "metro_name"]]
        raise ValueError("Top-100 dataset contains missing/suppressed values; no zero imputation allowed. "
                         f"Missing by column={missing_by_column}; metros={missing_metros.head(20).to_dict('records')}")
    if len(candidates) != CANDIDATE_COUNT or candidates.metro_id.nunique() != CANDIDATE_COUNT:
        raise ValueError("Candidate set does not contain exactly 100 distinct MSAs.")

    qa = {
        "status": "DATASET_BUILT_QA_PASSED",
        "omb_us_msa_count": int(crosswalk.cbsa_code.nunique()),
        "omb_us_county_membership_rows": int(len(crosswalk)),
        "candidate_count": int(len(candidates)),
        "training_metro_count": int(len(train)),
        "evaluation_candidate_count": int(len(candidates)),
        "candidate_metro_ids": sorted(ids),
        "training_sample_rule": "All OMB 17-01 US MSAs with complete historical training features/labels; not filtered by the later 2016-population top-100 evaluation shortlist.",
        "training_cutoff": TRAIN_CUTOFF,
        "evaluation_cutoff": EVAL_CUTOFF,
        "candidate_selection_rule": "Top 100 US MSAs by 2016-07-01 PEP population using OMB Bulletin 17-01 MSA county assignments (Census List 1 filtered to Metropolitan Statistical Area); ties by ascending CBSA code.",
        "training_label_available_date": _source_release("cbp_2013_county"),
        "evaluation_label_available_date": _source_release("cbp_2021_msa"),
        "cbp_industry_rows": {
            "2007_2002NAICS_722211": cbp07_industry_rows, "2010_2007NAICS_722211": cbp10_rows,
            "2013_722513": cbp13_rows, "2015_722513": cbp15_industry_rows,
            "2018_msa_722513": est18_rows, "2021_msa_722513": est21_rows,
        },
        "national_density": {"training": nat_density_train, "evaluation": nat_density_eval},
        "covid_period_limitation": "Evaluation outcome 2018-2021 includes the COVID-19 disruption and is not directly comparable with an unaffected economic period.",
        "missingness_policy": "Explicit missing values are never imputed. In pre-2017 county files, an absent target NAICS row is treated as zero under CBP's EST publication rule (EST remained published for small cells); explicit rows with missing EST are rejected. Post-2017 absent MSA cells remain unknown and are rejected for candidates.",
        "historical_county_reconciliation": {
            "county_fips": HISTORIC_KALAWAO_FIPS,
            "county_name": "Kalawao County, HI",
            "historical_cbp_reporting_fips": HISTORIC_MAUI_REPORTING_FIPS,
            "historical_reporting_name": "Maui County, HI",
            "cbsa_code": HISTORIC_KALAWAO_MSA,
            "evidence": "FIPS 15005 is absent from the 2002-2011 CBP county reference and CBP 2007/2010 rows; later county references include it. OMB List 1 assigns both 15005 and 15009 to CBSA 27980. The historical CBP reporting unit 15009 is counted once; no count is imputed to 15005. PEP population is observed separately for both FIPS.",
        },
    }
    return panel, qa


def build() -> dict:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "tables").mkdir(parents=True, exist_ok=True)
    crosswalk = read_omb_msa_list1()
    county_geo_qa = validate_county_geography_vintages(crosswalk)
    msa_geo_qa = validate_cbp_msa_geography(crosswalk)
    panel, qa = _build_panel(crosswalk)
    qa["county_geography_vintages"] = county_geo_qa
    qa["cbp_msa_geography"] = msa_geo_qa
    metadata = _feature_metadata()
    panel.to_csv(PROCESSED / "metro_panel.csv", index=False)
    metadata.to_csv(PROCESSED / "feature_metadata.csv", index=False)
    _data_dictionary().to_csv(PROCESSED / "data_dictionary.csv", index=False)
    crosswalk.to_csv(PROCESSED / "omb_2017_msa_county_crosswalk.csv", index=False)
    qa["panel_rows"] = int(len(panel))
    qa["panel_unique_metros"] = int(panel.metro_id.nunique())
    qa_path = OUTPUTS / "dataset_qa.json"
    qa_path.write_text(json.dumps(qa, indent=2), encoding="utf-8")
    return qa


def main() -> int:
    parser = argparse.ArgumentParser(description="Build validated two-period MSA panel from official raw files.")
    parser.add_argument("--check-only", action="store_true", help="Validate inputs and print QA without writing outputs.")
    args = parser.parse_args()
    try:
        crosswalk = read_omb_msa_list1()
        county_geo_qa = validate_county_geography_vintages(crosswalk)
        msa_geo_qa = validate_cbp_msa_geography(crosswalk)
        panel, qa = _build_panel(crosswalk)
        qa["county_geography_vintages"] = county_geo_qa
        qa["cbp_msa_geography"] = msa_geo_qa
        if not args.check_only:
            PROCESSED.mkdir(parents=True, exist_ok=True)
            panel.to_csv(PROCESSED / "metro_panel.csv", index=False)
            _feature_metadata().to_csv(PROCESSED / "feature_metadata.csv", index=False)
            _data_dictionary().to_csv(PROCESSED / "data_dictionary.csv", index=False)
            crosswalk.to_csv(PROCESSED / "omb_2017_msa_county_crosswalk.csv", index=False)
            OUTPUTS.mkdir(parents=True, exist_ok=True)
            (OUTPUTS / "dataset_qa.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
        print(json.dumps(qa, indent=2))
        return 0
    except Exception as exc:
        print(f"DATASET BUILD BLOCKED: {type(exc).__name__}: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
