from pathlib import Path
import zipfile
import pytest
from src.fetch_data import validate_file, SOURCES, GEOGRAPHY_SOURCE

def test_source_manifest_uses_official_hosts_and_https():
    all_sources = {**SOURCES, "omb": GEOGRAPHY_SOURCE}
    assert len(all_sources) == 13
    assert all(s["url"].startswith("https://www2.census.gov/") for s in all_sources.values())


def test_county_geography_sources_are_txt_and_official():
    geo = {k: v for k, v in SOURCES.items() if k.startswith("cbp_county_geo_")}
    assert set(geo) == {
        "cbp_county_geo_2002_2011",
        "cbp_county_geo_2012_2016",
        "cbp_county_geo_2017_2021",
    }
    assert all(item["kind"] == "txt" for item in geo.values())


def test_text_validation_rejects_html(tmp_path):
    f = tmp_path / "georef.txt"
    f.write_text("<html>not a geography file</html>", encoding="utf-8")
    with pytest.raises(ValueError, match="not empty/binary/HTML"):
        validate_file(f, "txt")


def test_text_validation_accepts_windows_1252_county_names(tmp_path):
    f = tmp_path / "georef.txt"
    f.write_bytes('"fipstate","fipscty","ctyname"\n"06","037","County Café, CA"\n'.encode("cp1252"))
    validate_file(f, "txt")


def test_zip_validation_accepts_valid_non_executable_archive(tmp_path):
    f = tmp_path / "good.zip"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("table.csv", "NAICS,EST\n722211,12\n")
    validate_file(f, "zip")


def test_zip_validation_rejects_path_traversal(tmp_path):
    f = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("../outside.txt", "bad")
    with pytest.raises(ValueError, match="Unsafe archive member"):
        validate_file(f, "zip")


def test_zip_validation_rejects_executable_member(tmp_path):
    f = tmp_path / "exe.zip"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("payload.bat", "echo not run")
    with pytest.raises(ValueError, match="Unexpected executable"):
        validate_file(f, "zip")

def test_zip_validation_rejects_windows_path_traversal(tmp_path):
    f = tmp_path / "windows_unsafe.zip"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr(r"..\\outside.txt", "bad")
    with pytest.raises(ValueError, match="Unsafe archive member"):
        validate_file(f, "zip")
