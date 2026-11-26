"""Fail-closed checks for temporal and data integrity."""
from __future__ import annotations
import pandas as pd

META_REQUIRED = {
    "feature_name", "source", "reference_period", "release_date",
    "decision_cutoff", "transformation", "missingness_policy",
    "leakage_check_status",
}
PANEL_REQUIRED = {
    "metro_id", "decision_cutoff", "target_start", "target_end",
    "target_release_date", "net_additions", "population",
    "current_establishments", "national_establishments_per_capita",
}


def validate_feasibility_gate(path) -> None:
    """Refuse model execution until feasibility and design approval are explicit."""
    from pathlib import Path
    text = Path(path).read_text(encoding="utf-8")
    status = None
    approval = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("FEASIBILITY_GATE:"):
            status = stripped.split(":", 1)[1].strip().upper()
        elif stripped.startswith("DESIGN_APPROVAL:"):
            approval = stripped.split(":", 1)[1].strip().upper()
    if status not in {"PASS", "PASS_WITH_LIMITATIONS"}:
        raise ValueError("Feasibility gate is not PASS/PASS_WITH_LIMITATIONS; model fitting is blocked.")
    if approval != "APPROVED":
        raise ValueError("The historical design has not been explicitly approved; model fitting is blocked.")

def validate_feature_metadata(metadata: pd.DataFrame) -> pd.DataFrame:
    missing = META_REQUIRED - set(metadata.columns)
    if missing:
        raise ValueError(f"Feature metadata missing columns: {sorted(missing)}")
    if metadata.empty:
        raise ValueError("Feature metadata is empty; feature eligibility is unverified.")
    m = metadata.copy()
    status = m.leakage_check_status.astype(str).str.upper()
    allowed = {"PASS", "UNVERIFIED", "FAIL", "EXCLUDED"}
    if not status.isin(allowed).all():
        raise ValueError(f"Unknown leakage_check_status values: {sorted(set(status)-allowed)}")
    m["decision_cutoff"] = pd.to_datetime(m.decision_cutoff, errors="coerce")
    if m.decision_cutoff.isna().any():
        raise ValueError("Invalid or missing decision_cutoff in feature metadata.")
    # A PASS is only permitted when a public release date is evidenced and precedes cutoff.
    m["release_date"] = pd.to_datetime(m.release_date, errors="coerce")
    passed = status.eq("PASS")
    if m.loc[passed, "release_date"].isna().any():
        raise ValueError("PASS feature metadata requires a verified release_date.")
    if (m.loc[passed, "release_date"] > m.loc[passed, "decision_cutoff"]).any():
        raise ValueError("Feature marked PASS was released after its decision cutoff.")
    if m.duplicated(["feature_name", "decision_cutoff"]).any():
        raise ValueError("Duplicate feature metadata rows for a decision cutoff.")
    return m

def eligible_features(metadata: pd.DataFrame, cutoff) -> set[str]:
    """Return only features independently verified by the specified cutoff."""
    cutoff = pd.Timestamp(cutoff)
    rows = metadata[metadata.decision_cutoff == cutoff]
    eligible = rows[rows.leakage_check_status.astype(str).str.upper() == "PASS"]
    return set(eligible.feature_name.astype(str))

def validate_panel(panel: pd.DataFrame) -> pd.DataFrame:
    missing = PANEL_REQUIRED - set(panel.columns)
    if missing:
        raise ValueError(f"Panel missing required columns: {sorted(missing)}")
    p = panel.copy()
    if p.empty:
        raise ValueError("Panel is empty.")
    if p.duplicated(["metro_id", "decision_cutoff"]).any():
        raise ValueError("Duplicate (metro_id, decision_cutoff) observations.")
    for col in ("decision_cutoff", "target_start", "target_end", "target_release_date"):
        p[col] = pd.to_datetime(p[col], errors="coerce")
        if p[col].isna().any():
            raise ValueError(f"Invalid or missing dates in {col}.")
    if (p.target_start <= p.decision_cutoff).any():
        raise ValueError("Target period must begin strictly after decision cutoff.")
    if (p.target_end < p.target_start).any():
        raise ValueError("target_end precedes target_start.")
    # A target label cannot be public before the last source observation ends.
    if (p.target_release_date < p.target_end).any():
        raise ValueError("Target release date precedes target period end.")
    required_values = ["metro_id", "net_additions", "population",
                       "current_establishments", "national_establishments_per_capita"]
    if p[required_values].isna().any().any():
        raise ValueError("Missing required values. Suppressed/unavailable values must not become zero.")
    if (p.population <= 0).any():
        raise ValueError("Population must be positive.")
    if (p.current_establishments < 0).any():
        raise ValueError("Establishment counts cannot be negative.")
    if (p.national_establishments_per_capita < 0).any():
        raise ValueError("National establishments per capita cannot be negative.")
    return p

def validate_train_eval(train: pd.DataFrame, candidates: pd.DataFrame) -> None:
    if train.empty or candidates.empty:
        raise ValueError("Training and evaluation candidate slices must both be nonempty.")
    t = train.copy()
    e = candidates.copy()
    for frame in (t, e):
        for col in ("decision_cutoff", "target_start", "target_end", "target_release_date"):
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
            if frame[col].isna().any():
                raise ValueError(f"Invalid or missing {col} in train/evaluation slice.")
    train_cutoffs = t.decision_cutoff.unique()
    eval_cutoffs = e.decision_cutoff.unique()
    if len(train_cutoffs) != 1 or len(eval_cutoffs) != 1:
        raise ValueError("Use exactly one training cutoff and one evaluation cutoff per run.")
    train_cutoff, eval_cutoff = pd.Timestamp(train_cutoffs[0]), pd.Timestamp(eval_cutoffs[0])
    if train_cutoff >= eval_cutoff:
        raise ValueError("Training cutoff must precede evaluation cutoff.")
    if (t.target_end >= eval_cutoff).any():
        raise ValueError("Training outcome period must end before evaluation decision cutoff.")
    if (t.target_release_date > eval_cutoff).any():
        raise ValueError("Training labels were not publicly available by evaluation cutoff.")
    if (e.target_start <= eval_cutoff).any():
        raise ValueError("Evaluation outcome must begin after evaluation decision cutoff.")
    if (e.target_release_date <= eval_cutoff).any():
        raise ValueError("Evaluation outcomes must remain unpublished at the evaluation cutoff.")
    if t.metro_id.duplicated().any() or e.metro_id.duplicated().any():
        raise ValueError("Training/evaluation slices must have one row per metro.")
