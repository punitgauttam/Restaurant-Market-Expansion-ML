"""Download official public source files without extracting or executing archives.

Only the Census Bureau and OMB source hosts are permitted. Downloads are streamed,
size-bounded, SHA-256 hashed, and recorded in data/raw/download_manifest.csv.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import time
import zipfile
import stat
from pathlib import PurePosixPath
from datetime import datetime, timezone

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MAX_FILE_BYTES = 40 * 1024 * 1024
MAX_UNCOMPRESSED_MEMBER_BYTES = 250 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
RETRIES = 3
TIMEOUT = (10, 30)
ALLOWED_HOSTS = {"www2.census.gov"}

SOURCES = {
    "cbp_2007_county": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2007/cbp07co.zip",
        "filename": "cbp07co.zip", "kind": "zip", "release_date": "2009-07-31",
        "release_date_precision": "month (conservative month-end for cutoff checks)",
        "reference_period": "CBP reference year 2007", "listed_size_mb": 16.0,
    },
    "cbp_2010_county": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2010/cbp10co.zip",
        "filename": "cbp10co.zip", "kind": "zip", "release_date": "2012-06-26",
        "reference_period": "CBP reference year 2010", "listed_size_mb": 15.6,
    },
    "cbp_2013_county": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2013/cbp13co.zip",
        "filename": "cbp13co.zip", "kind": "zip", "release_date": "2015-04-23",
        "reference_period": "CBP reference year 2013", "listed_size_mb": 14.0,
    },
    "cbp_2015_county": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2015/cbp15co.zip",
        "filename": "cbp15co.zip", "kind": "zip", "release_date": "2017-04-20",
        "reference_period": "CBP reference year 2015", "listed_size_mb": 15.0,
    },
    "cbp_2018_msa": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2018/cbp18msa.zip",
        "filename": "cbp18msa.zip", "kind": "zip", "release_date": "2020-06-25",
        "reference_period": "CBP reference year 2018; MSA geography batch 2017-2021", "listed_size_mb": 6.9,
    },
    "cbp_2021_msa": {
        "url": "https://www2.census.gov/programs-surveys/cbp/datasets/2021/cbp21msa.zip",
        "filename": "cbp21msa.zip", "kind": "zip", "release_date": "2023-04-27",
        "reference_period": "CBP reference year 2021; MSA geography batch 2017-2021", "listed_size_mb": 5.9,
    },
    "pep_2008_county": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2000-2008/counties/totals/co-est2008-alldata.csv",
        "filename": "co-est2008-alldata.csv", "kind": "csv", "release_date": "2009-03-19",
        "reference_period": "County population estimate as of 2008-07-01", "listed_size_mb": 3.1,
    },
    "pep_2016_county": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2016/counties/totals/co-est2016-alldata.csv",
        "filename": "co-est2016-alldata.csv", "kind": "csv", "release_date": "2017-03-23",
        "reference_period": "County population estimate as of 2016-07-01", "listed_size_mb": 2.4,
    },
    "cbp_county_geo_2002_2011": {
        "url": "https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef02.txt",
        "filename": "georef02.txt", "kind": "txt", "release_date": "UNVERIFIED",
        "reference_period": "CBP county FIPS reference batch 2002-2011",
        "listed_size_mb": 0.1,
    },
    "cbp_county_geo_2012_2016": {
        "url": "https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef12.txt",
        "filename": "georef12.txt", "kind": "txt", "release_date": "UNVERIFIED",
        "reference_period": "CBP county FIPS reference batch 2012-2016",
        "listed_size_mb": 0.1,
    },
    "cbp_county_geo_2017_2021": {
        "url": "https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/state-county-geography-reference/georef17.txt",
        "filename": "georef17.txt", "kind": "txt", "release_date": "UNVERIFIED",
        "reference_period": "CBP county FIPS reference batch 2017-2021",
        "listed_size_mb": 0.1,
    },
    "cbp_msa_geo_2017_2021": {
        "url": "https://www2.census.gov/programs-surveys/cbp/technical-documentation/reference/metro-area-geography-reference/msa_county_reference17.txt",
        "filename": "msa_county_reference17.txt", "kind": "txt", "release_date": "UNVERIFIED",
        "asset_last_modified_date": "2021-09-13",
        "reference_period": "CBP MSA/county reference batch 2017-2021; post-cutoff validation only",
        "listed_size_mb": 0.14,
    },
}

# Census List 1 contains county assignments for both metropolitan and
# micropolitan areas; the builder filters its area-type column to MSAs only.
# Census List 2 is a principal-cities workbook, not a county crosswalk. The
# List 1 directory timestamp is 2018-01-23, before the approved 2018-02-01
# evaluation cutoff. OMB Bulletin 17-01 itself is dated 2017-08-15.
GEOGRAPHY_SOURCE = {
    "url": "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2017/delineation-files/list1.xls",
    "filename": "omb_2017_bulletin17_01_list1.xls", "kind": "xls",
    "release_date": "2017-08-15", "asset_last_modified_date": "2018-01-23",
    "reference_period": "OMB Bulletin 17-01 county assignments; filter List 1 to Metropolitan Statistical Area",
    "listed_size_mb": 0.42,
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_file(path: Path, kind: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("Download is empty or missing.")
    if kind == "zip":
        if not zipfile.is_zipfile(path):
            raise ValueError("Expected a ZIP archive; payload is not a ZIP.")
        with zipfile.ZipFile(path) as zf:
            # Check metadata before decompressing members for CRC validation;
            # official CBP county tables are about 180 MB uncompressed.
            total_uncompressed = 0
            for info in zf.infolist():
                # Treat both slash conventions as separators, even on POSIX.
                normalized = info.filename.replace("\\", "/")
                member = PurePosixPath(normalized)
                if (member.is_absolute() or ".." in member.parts
                        or any(part.endswith(":") for part in member.parts[:1])):
                    raise ValueError(f"Unsafe archive member path: {info.filename!r}")
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    raise ValueError(f"Archive symlink is not accepted: {info.filename!r}")
                if info.file_size > MAX_UNCOMPRESSED_MEMBER_BYTES:
                    raise ValueError(f"Archive member exceeds uncompressed size limit: {info.filename!r}")
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
                    raise ValueError("Archive exceeds total uncompressed size limit.")
                if info.filename.lower().endswith((".exe", ".dll", ".bat", ".cmd", ".ps1", ".sh", ".msi", ".com")):
                    raise ValueError(f"Unexpected executable archive member: {info.filename!r}")
            bad = zf.testzip()
            if bad:
                raise ValueError(f"ZIP CRC check failed for member {bad!r}.")
    elif kind == "csv":
        head = path.read_bytes()[:4096]
        if not head.strip() or b"\x00" in head or head.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            raise ValueError("Expected a text CSV payload; received empty/binary/HTML content.")
        head.decode("utf-8-sig", errors="replace")
    elif kind == "xls":
        signature = path.read_bytes()[:8]
        if signature != bytes.fromhex("D0CF11E0A1B11AE1"):
            raise ValueError("Expected a legacy XLS workbook (OLE2 signature not found).")
    elif kind == "txt":
        head = path.read_bytes()[:4096]
        if not head.strip() or b"\x00" in head or head.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            raise ValueError("Expected a text geography reference, not empty/binary/HTML content.")
        try:
            head.decode("utf-8-sig", errors="strict")
        except UnicodeDecodeError:
            # Some older Census reference text files contain Windows-1252
            # county-name characters. Accept that text encoding explicitly.
            head.decode("cp1252", errors="strict")
    else:
        raise ValueError(f"Unsupported source kind: {kind}")


def download_one(name: str, source: dict, overwrite: bool = False) -> dict:
    from urllib.parse import urlparse
    parsed = urlparse(source["url"])
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"URL is outside the approved HTTPS source host list: {source['url']}")

    RAW.mkdir(parents=True, exist_ok=True)
    destination = RAW / source["filename"]
    if destination.exists() and not overwrite:
        validate_file(destination, source["kind"])
        return {"source_id": name, "url": source["url"], "file": str(destination.relative_to(ROOT)),
                "retrieved_at_utc": datetime.fromtimestamp(
                    destination.stat().st_mtime, timezone.utc).isoformat(),
                "bytes": destination.stat().st_size,
                "sha256": _sha256(destination), "http_status": "", "status": "EXISTS_VALIDATED"}

    last_error = None
    for attempt in range(1, RETRIES + 1):
        temp_path = None
        try:
            with requests.get(source["url"], stream=True, timeout=TIMEOUT,
                              headers={"User-Agent": "RestaurantMarketExpansionResearch/1.0"}) as response:
                response.raise_for_status()
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_FILE_BYTES:
                    raise ValueError(f"File exceeds configured {MAX_FILE_BYTES} byte cap.")
                fd, temp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".part", dir=RAW)
                os.close(fd)
                temp_path = Path(temp_name)
                size = 0
                with temp_path.open("wb") as out:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if not chunk:
                            continue
                        size += len(chunk)
                        if size > MAX_FILE_BYTES:
                            raise ValueError(f"Download exceeded configured {MAX_FILE_BYTES} byte cap.")
                        out.write(chunk)
            validate_file(temp_path, source["kind"])
            digest = _sha256(temp_path)
            temp_path.replace(destination)
            return {"source_id": name, "url": source["url"], "file": str(destination.relative_to(ROOT)),
                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                    "bytes": destination.stat().st_size, "sha256": digest,
                    "http_status": response.status_code, "status": "DOWNLOADED"}
        except Exception as exc:  # recorded, bounded retry; do not suppress failure
            last_error = f"{type(exc).__name__}: {exc}"
            if temp_path and temp_path.exists():
                temp_path.unlink()
            if attempt < RETRIES:
                time.sleep(2 ** (attempt - 1))
    return {"source_id": name, "url": source["url"], "file": source["filename"],
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "bytes": "", "sha256": "", "http_status": "", "status": "FAILED", "error": last_error}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch official Census/OMB public source files (no extraction).")
    parser.add_argument("--only", help="Comma-separated source IDs; default downloads all sources.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing verified raw source files.")
    parser.add_argument("--list", action="store_true", help="List source IDs and URLs without downloading.")
    args = parser.parse_args()

    all_sources = {**SOURCES, "omb_2017_msa_list1": GEOGRAPHY_SOURCE}
    if args.list:
        for name, source in all_sources.items():
            print(f"{name}\t{source['release_date']}\t{source.get('asset_last_modified_date', '')}\t{source['url']}")
        return 0

    selected = [x.strip() for x in args.only.split(",")] if args.only else list(all_sources)
    unknown = sorted(set(selected) - set(all_sources))
    if unknown:
        parser.error(f"Unknown source IDs: {unknown}")

    results = [download_one(name, all_sources[name], args.overwrite) for name in selected]
    manifest = RAW / "download_manifest.csv"
    columns = ["source_id", "url", "file", "retrieved_at_utc", "bytes", "sha256", "http_status", "status", "error"]
    existing = []
    if manifest.exists():
        with manifest.open(encoding="utf-8", newline="") as f:
            existing = list(csv.DictReader(f))
    by_id = {row.get("source_id"): row for row in existing}
    for result in results:
        previous = by_id.get(result["source_id"], {})
        if not result.get("http_status"):
            result["http_status"] = previous.get("http_status", "")
        by_id[result["source_id"]] = result
    with manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(by_id.values())
    print(json.dumps(results, indent=2))
    failures = [r for r in results if r["status"] == "FAILED"]
    print(f"Manifest written: {manifest}")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
