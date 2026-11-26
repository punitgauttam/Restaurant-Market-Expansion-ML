"""Deterministic population, white-space, and Ridge rankings."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_FEATURES = [
    "population", "current_establishments", "restaurants_per_10k",
]

def _rank(frame: pd.DataFrame, score, method: str) -> pd.DataFrame:
    columns = ["metro_id"] + (["metro_name"] if "metro_name" in frame.columns else [])
    result = frame[columns].copy()
    result["method"] = method
    result["score"] = np.asarray(score, dtype=float)
    result = result.sort_values(["score", "metro_id"], ascending=[False, True], kind="mergesort")
    result["rank"] = np.arange(1, len(result) + 1)
    return result.reset_index(drop=True)

def population_ranking(candidates: pd.DataFrame) -> pd.DataFrame:
    return _rank(candidates, candidates["population"], "population")

def whitespace_ranking(candidates: pd.DataFrame) -> pd.DataFrame:
    density = candidates["national_establishments_per_capita"].astype(float)
    if density.isna().any() or not np.isfinite(density.to_numpy()).all():
        raise ValueError("National establishments-per-capita must be finite and nonmissing.")
    if (density < 0).any():
        raise ValueError("National establishments-per-capita cannot be negative.")
    if not np.allclose(density.to_numpy(), density.iloc[0], rtol=1e-9, atol=1e-12):
        raise ValueError("National establishments-per-capita must be one cutoff-wide value shared by all candidates.")
    score = (candidates["population"] * density - candidates["current_establishments"])
    return _rank(candidates, score, "white_space")

def ridge_ranking(train: pd.DataFrame, candidates: pd.DataFrame,
                  features: list[str] | None = None, alpha: float = 1.0):
    """Fit preprocessing on historical rows only; alpha is prespecified."""
    features = features or [c for c in DEFAULT_FEATURES
                            if c in train.columns and c in candidates.columns]
    if not features:
        raise ValueError("No shared approved Ridge features are available.")
    if set(features) & {"net_additions", "target_start", "target_end", "target_release_date"}:
        raise ValueError("Outcome/time fields cannot be predictors.")
    if train[features].isna().all().any():
        bad = train[features].columns[train[features].isna().all()].tolist()
        raise ValueError(f"All training values missing for features: {bad}")
    model = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=alpha)),
    ])
    model.fit(train[features], train["net_additions"])
    scores = model.predict(candidates[features])
    return _rank(candidates, scores, "ridge"), model
