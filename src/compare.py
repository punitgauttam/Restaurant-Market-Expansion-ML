"""Candidate construction and same-universe ranking."""
from __future__ import annotations
import pandas as pd
from .models import population_ranking, whitespace_ranking, ridge_ranking

def select_candidates(evaluation_slice: pd.DataFrame, n: int = 100) -> pd.DataFrame:
    """Select top-N solely by population known at the evaluation cutoff."""
    if n < 20:
        raise ValueError("Candidate count must be at least 20 for K=20 sensitivity.")
    if evaluation_slice.metro_id.duplicated().any():
        raise ValueError("Evaluation slice must have one row per metro.")
    if evaluation_slice.population.isna().any():
        raise ValueError("Candidate population has missing values; eligibility cannot be established.")
    if len(evaluation_slice) < n:
        raise ValueError(f"Requested {n} eligible metros but only {len(evaluation_slice)} are available.")
    return (evaluation_slice.sort_values(["population", "metro_id"],
                                         ascending=[False, True], kind="mergesort")
            .head(n).copy().reset_index(drop=True))

def build_rankings(train: pd.DataFrame, candidates: pd.DataFrame, features=None, alpha=1.0):
    ids = set(candidates.metro_id)
    if not ids:
        raise ValueError("Candidate universe must be nonempty.")
    if train.metro_id.duplicated().any() or candidates.metro_id.duplicated().any():
        raise ValueError("One row per metro is required in each period.")
    train_ids = set(train.metro_id)
    missing = ids - train_ids
    if missing:
        raise ValueError(f"Training geography does not cover evaluation candidates: {sorted(missing)[:5]}")
    if "net_additions" not in train or train.net_additions.isna().any():
        raise ValueError("Historical training labels must be complete and observed.")
    if train.isna().any().any():
        raise ValueError("Historical training feature rows contain missing values; resolve source missingness explicitly.")
    # Intentionally retain the full historical training sample, not only the later top-100.
    pop = population_ranking(candidates)
    white = whitespace_ranking(candidates)
    ridge, model = ridge_ranking(train, candidates, features=features, alpha=alpha)
    for ranking in (pop, white, ridge):
        if set(ranking.metro_id) != ids or len(ranking) != len(ids):
            raise AssertionError("Methods must rank exactly the same candidate universe.")
    return pd.concat([pop, white, ridge], ignore_index=True), model
