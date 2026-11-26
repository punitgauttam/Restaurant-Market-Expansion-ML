"""Held-out ranking evaluation, retaining negative net additions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

def _ndcg_linear_gain(relevance: np.ndarray, order: np.ndarray, k: int) -> float:
    """NDCG with documented relevance=max(0, net_additions), linear gain."""
    k = min(k, len(relevance))
    discounts = 1.0 / np.log2(np.arange(2, k + 2))
    dcg = float(np.sum(relevance[order[:k]] * discounts))
    ideal = np.argsort(-relevance, kind="stable")
    idcg = float(np.sum(relevance[ideal[:k]] * discounts))
    return float(dcg / idcg) if idcg > 0 else float("nan")

def evaluate_rankings(rankings: pd.DataFrame, outcomes: pd.DataFrame,
                       ks=(5, 10, 20)) -> tuple[pd.DataFrame, pd.DataFrame]:
    if outcomes["metro_id"].duplicated().any():
        raise ValueError("Outcomes must contain one row per metro.")
    if outcomes["net_additions"].isna().any():
        raise ValueError("Missing held-out outcomes must be resolved/documented before scoring.")
    if set(outcomes.metro_id) != set(rankings.metro_id):
        raise ValueError("Evaluation outcomes and rankings must have exactly the same candidate universe.")
    if set(rankings["method"].unique()) != {"population", "white_space", "ridge"}:
        raise ValueError("Expected exactly population, white_space and ridge rankings.")
    if rankings.duplicated(["method", "metro_id"]).any():
        raise ValueError("Duplicate metro ranks within a method.")
    universes = [set(g.metro_id) for _, g in rankings.groupby("method")]
    if any(u != universes[0] for u in universes[1:]):
        raise ValueError("All methods must rank the same candidate universe.")
    merged = rankings.merge(outcomes[["metro_id", "net_additions"]], on="metro_id",
                            how="left", validate="many_to_one")
    if merged.net_additions.isna().any():
        raise ValueError("A ranked metro lacks a held-out outcome.")
    actual = outcomes.sort_values(["net_additions", "metro_id"],
                                  ascending=[False, True], kind="mergesort")
    outcome = actual.set_index("metro_id").net_additions
    actual_order_ids = actual.metro_id.tolist()
    rows = []
    details = []
    for method, group in merged.groupby("method", sort=True):
        group = group.sort_values("rank", kind="mergesort").reset_index(drop=True)
        # Higher model score should align with higher outcome.
        rho = spearmanr(group.score, group.net_additions).statistic
        rho = float(rho) if np.isfinite(rho) else float("nan")
        for k in ks:
            selected = group.head(k)
            actual_top = set(actual_order_ids[:k])
            overlap = len(set(selected.metro_id) & actual_top)
            best_total = float(outcome.loc[actual_order_ids[:k]].sum())
            selected_total = float(selected.net_additions.sum())
            rel = np.maximum(0.0, group.net_additions.to_numpy(dtype=float))
            ranked_positions = np.arange(len(group))
            ndcg = _ndcg_linear_gain(rel, ranked_positions, k)
            rows.append({
                "method": method, "k": k,
                "selected_net_additions": selected_total,
                "hindsight_best_net_additions": best_total,
                "regret": best_total - selected_total,
                "overlap_actual_top_k": overlap,
                "precision_at_k": overlap / min(k, len(group)),
                "ndcg_at_k_nonnegative_linear_gain": ndcg,
                "spearman_rho": rho,
            })
        details.append(group[["metro_id", "method", "rank", "score", "net_additions"]])
    return pd.DataFrame(rows), pd.concat(details, ignore_index=True)
