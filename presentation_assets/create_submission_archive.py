"""Create and verify a presentation-inclusive submission ZIP."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "dist" / "Restaurant_Market_Expansion_Submission_Presentation_2026-11-26.zip"
EXCLUDED_DIRS = {"dist", ".git", "__pycache__", ".pytest_cache", ".venv", "venv"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        files.append(path)
    files.sort(key=lambda p: p.relative_to(ROOT).as_posix().casefold())

    DEST.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(DEST, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())

    with ZipFile(DEST, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC/integrity verification failed")
        members = archive.namelist()
        if len(members) != len(set(members)):
            raise RuntimeError("ZIP contains duplicate member names")
        missing = [name for name in (
            "FINAL_AUDIT.md",
            "presentation_assets/dashboard.html",
            "presentation_assets/top_five_comparison.png",
            "presentation_assets/method_comparison.png",
            "presentation_assets/white_space_markets.png",
            "presentation_assets/methodology_limitations.png",
            "presentation_assets/presentation_summary.md",
        ) if name not in members]
        if missing:
            raise RuntimeError(f"Required archive members are missing: {missing}")
        mismatches = []
        for name in members:
            local_path = ROOT / Path(name)
            if not local_path.is_file() or digest(archive.read(name)) != digest(local_path.read_bytes()):
                mismatches.append(name)
        if mismatches:
            raise RuntimeError(f"Archive member hashes differ from workspace: {mismatches}")

    print(f"Archive: {DEST.relative_to(ROOT)}")
    print(f"Members: {len(files)}")
    print(f"Bytes: {DEST.stat().st_size}")
    print(f"SHA-256: {digest(DEST.read_bytes())}")
    print("ZIP integrity and every member SHA-256: PASS")


if __name__ == "__main__":
    main()
