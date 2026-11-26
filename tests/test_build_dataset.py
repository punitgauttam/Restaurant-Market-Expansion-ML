from pathlib import Path
import zipfile
import pandas as pd
import pytest

import src.build_dataset as builder
from src.fetch_data import SOURCES


def test_cbp_2010_uses_2007_naics_vintage():
    assert builder.CBP_ID["cbp_2010_county"][2] == "722211"
    assert builder.CBP_ID["cbp_2013_county"][2] == "722513"


def test_omb_list1_parser_keeps_msas_only_and_preserves_fips(tmp_path, monkeypatch):
    path = tmp_path / "list1.xls"
    path.write_bytes(b"fixture")
    raw = pd.DataFrame([
        ["List 1 metadata", None, None, None, None, None],
        ["CBSA Code", "CBSA Title", "Metropolitan/Micropolitan Statistical Area",
         "FIPS State Code", "FIPS County Code", "County/County Equivalent"],
        ["01000", "Metro A", "Metropolitan Statistical Area", "01", "001", "Autauga County"],
        ["01001", "Micro B", "Micropolitan Statistical Area", "01", "003", "Baldwin County"],
    ])

    class FakeWorkbook:
        sheet_names = ["List 1"]

    monkeypatch.setattr(builder.pd, "ExcelFile", lambda *args, **kwargs: FakeWorkbook())
    monkeypatch.setattr(builder.pd, "read_excel", lambda *args, **kwargs: raw)
    monkeypatch.setattr(builder, "OMB_EXPECTED_MSA_COUNT", 1)
    monkeypatch.setattr(builder, "OMB_EXPECTED_COUNTY_COUNT", 1)
    result = builder.read_omb_msa_list1(path)
    assert result[["cbsa_code", "county_fips"]].values.tolist() == [["01000", "01001"]]
    assert result.county_name.tolist() == ["Autauga County"]


def test_historical_kalawao_maui_count_is_not_imputed_or_doubled():
    crosswalk = pd.DataFrame({
        "cbsa_code": ["27980", "27980"],
        "metro_name": ["Kahului-Wailuku-Lahaina, HI"] * 2,
        "county_fips": ["15005", "15009"],
    })
    cbp = pd.DataFrame({
        "county_fips": ["15009"], "county_fips_part": ["009"],
        "state_fips": ["15"], "naics": ["722211"], "est": [127],
    })
    builder._county_rows_coverage({"cbp_2010_county": cbp}, crosswalk)
    msa_counts, national_total, nrows = builder._county_industry_to_msa(
        cbp, crosswalk, "cbp_2010_county"
    )
    assert msa_counts.loc["27980"] == 127
    assert national_total == 127
    assert nrows == 1


def test_pep_reader_falls_back_to_windows_1252_for_official_text(tmp_path, monkeypatch):
    source = "pep_2016_county"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", "pep.csv")
    (tmp_path / "pep.csv").write_bytes(
        b"SUMLEV,STATE,COUNTY,POPESTIMATE2016,NAME\n050,15,005,88,Kala\xf1ao County\n"
    )
    result = builder._read_pep(source, 2016)
    assert result.to_dict("records") == [{"county_fips": "15005", "population": 88}]


def test_cbp_reader_accepts_vintage_specific_naics_field(tmp_path, monkeypatch):
    source = "cbp_2010_county"
    filename = "cbp10co.zip"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", filename)
    zpath = tmp_path / filename
    with zipfile.ZipFile(zpath, "w") as archive:
        archive.writestr("cbp10co.txt", "FIPSTATE,FIPSCTY,NAICS2007,EST\n01,001,722211,8\n")
    result = builder._read_cbp_zip(source)
    assert result.loc[0, "naics"] == "722211"
    assert result.loc[0, "county_fips"] == "01001"
    assert result.loc[0, "est"] == 8


def test_county_pre2017_missing_industry_row_only_zero_after_explicit_method(tmp_path):
    crosswalk = pd.DataFrame({
        "cbsa_code": ["10100", "10100", "20200"],
        "metro_name": ["Metro A", "Metro A", "Metro B"],
        "county_fips": ["01001", "01003", "02013"],
    })
    cbp = pd.DataFrame({
        "county_fips": ["01001", "01003", "02013"],
        "naics": ["722211", "00", "00"],
        "est": [5, 100, 50],
    })
    counts, _, nrows = builder._county_industry_to_msa(cbp, crosswalk, "cbp_2010_county")
    assert counts.loc["10100"] == 5
    assert counts.loc["20200"] == 0
    assert nrows == 1


def test_post_2017_missing_msa_industry_row_is_not_filled_with_zero():
    frame = pd.DataFrame({"cbsa_code": ["10100"], "naics": ["722513"], "est": [12]})
    crosswalk = pd.DataFrame({"cbsa_code": ["10100", "20200"]})
    counts, nrows = builder._msa_industry_counts(frame, "cbp_2018_msa", crosswalk)
    assert counts.loc["10100"] == 12
    assert "20200" not in counts.index
    assert nrows == 1


def test_cbp_parser_rejects_ambiguous_naics_fields(tmp_path, monkeypatch):
    source = "cbp_2010_county"
    filename = "cbp10co.zip"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", filename)
    zpath = tmp_path / filename
    with zipfile.ZipFile(zpath, "w") as archive:
        archive.writestr("cbp10co.txt", "FIPSTATE,FIPSCTY,NAICS,NAICS2007,EST\n01,001,722211,722211,8\n")
    with pytest.raises(ValueError, match="exactly one NAICS"):
        builder._read_cbp_zip(source)


def test_cbp_reader_accepts_2002_naics_field_for_2007_vintage(tmp_path, monkeypatch):
    source = "cbp_2007_county"
    filename = "cbp07co.zip"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", filename)
    zpath = tmp_path / filename
    with zipfile.ZipFile(zpath, "w") as archive:
        archive.writestr("cbp07co.txt", "FIPSTATE,FIPSCTY,NAICS2002,EST\n01,001,722211,9\n")
    result = builder._read_cbp_zip(source)
    assert result.loc[0, "naics"] == "722211"
    assert result.attrs["target_naics"] == "722211"


def test_county_geography_reference_parser_preserves_fips(tmp_path, monkeypatch):
    source = "cbp_county_geo_2012_2016"
    filename = "georef12.txt"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", filename)
    (tmp_path / filename).write_text(
        '"fipstate","fipscty","ctyname"\n"1","1","Autauga County"\n"6","37","Los Angeles County"\n"72","001","Puerto Rico"\n',
        encoding="utf-8",
    )
    result = builder._read_county_geography_reference(source)
    assert result.county_fips.tolist() == ["01001", "06037"]
    assert result.county_name.tolist() == ["Autauga County", "Los Angeles County"]


def test_county_geography_vintage_validation_passes_when_all_codes_present(monkeypatch):
    references = {
        "cbp_county_geo_2002_2011": pd.DataFrame({"county_fips": ["01001", "01003"]}),
        "cbp_county_geo_2012_2016": pd.DataFrame({"county_fips": ["01001", "01003"]}),
        "cbp_county_geo_2017_2021": pd.DataFrame({"county_fips": ["01001", "01003"]}),
    }
    monkeypatch.setattr(builder, "_read_county_geography_reference", lambda sid: references[sid])
    crosswalk = pd.DataFrame({"county_fips": ["01001", "01003"]})
    result = builder.validate_county_geography_vintages(crosswalk)
    assert set(result) == set(builder.COUNTY_GEO_REF_IDS)
    assert all(v["unmatched_omb_counties"] == 0 for v in result.values())


def test_county_geography_vintage_validation_blocks_unmatched_codes(monkeypatch):
    references = {
        "cbp_county_geo_2002_2011": pd.DataFrame({"county_fips": ["01001"]}),
        "cbp_county_geo_2012_2016": pd.DataFrame({"county_fips": ["01001", "01003"]}),
        "cbp_county_geo_2017_2021": pd.DataFrame({"county_fips": ["01001", "01003"]}),
    }
    monkeypatch.setattr(builder, "_read_county_geography_reference", lambda sid: references[sid])
    crosswalk = pd.DataFrame({"county_fips": ["01001", "01003"]})
    with pytest.raises(ValueError, match="county FIPS changes must be reconciled"):
        builder.validate_county_geography_vintages(crosswalk)


def test_county_geography_parser_falls_back_to_windows_1252(tmp_path, monkeypatch):
    source = "cbp_county_geo_2017_2021"
    filename = "georef17.txt"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source], "filename", filename)
    (tmp_path / filename).write_bytes(
        '"fipstate","fipscty","ctyname"\n"06","037","County Cafés, CA"\n'.encode("cp1252")
    )
    result = builder._read_county_geography_reference(source)
    assert result.loc[0, "county_fips"] == "06037"
    assert "Cafés" in result.loc[0, "county_name"]


def test_cbp_msa_geography_reference_parser_and_exact_match(tmp_path, monkeypatch):
    source_id = "cbp_msa_geo_2017_2021"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source_id], "filename", "msa_ref.txt")
    (tmp_path / "msa_ref.txt").write_text(
        "MSA,FIPSTATE,FIPSCTY\n10100,01,001\n10100,01,003\n20200,02,013\n",
        encoding="utf-8"
    )
    ref = builder._read_msa_geography_reference()
    crosswalk = pd.DataFrame({"cbsa_code":["10100","10100","20200"],
                              "county_fips":["01001","01003","02013"]})
    result = builder.validate_cbp_msa_geography(crosswalk)
    assert len(ref) == 3
    assert result["exact_omb_pair_match"] is True


def test_cbp_msa_geography_mismatch_blocks(tmp_path, monkeypatch):
    source_id = "cbp_msa_geo_2017_2021"
    monkeypatch.setattr(builder, "RAW", tmp_path)
    monkeypatch.setitem(builder.SOURCES[source_id], "filename", "msa_ref.txt")
    (tmp_path / "msa_ref.txt").write_text(
        "MSA,FIPSTATE,FIPSCTY\n10100,01,001\n20200,02,013\n",
        encoding="utf-8"
    )
    crosswalk = pd.DataFrame({"cbsa_code":["10100","10100","20200"],
                              "county_fips":["01001","01003","02013"]})
    with pytest.raises(ValueError, match="does not exactly match"):
        builder.validate_cbp_msa_geography(crosswalk)


def test_national_establishment_density_excludes_cbp_state_summary_rows():
    crosswalk = pd.DataFrame({
        "cbsa_code": ["10100"], "metro_name": ["Metro A"], "county_fips": ["01001"]
    })
    cbp = pd.DataFrame({
        "county_fips": ["01001", "01999"],
        "county_fips_part": ["001", "999"],
        "state_fips": ["01", "01"],
        "naics": ["722211", "722211"],
        "est": [5, 500],
    })
    msa_counts, national_total, nrows = builder._county_industry_to_msa(
        cbp, crosswalk, "cbp_2010_county"
    )
    assert msa_counts.loc["10100"] == 5
    assert national_total == 5
    assert nrows == 1
