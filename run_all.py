from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from src.validation import (validate_panel, validate_feature_metadata,
                            validate_train_eval, eligible_features,
                            validate_feasibility_gate)
from src.compare import select_candidates, build_rankings
from src.models import DEFAULT_FEATURES
from src.evaluate import evaluate_rankings
from src.visualize import generate_figures

def main():
    parser = argparse.ArgumentParser(description="Reproduce US metro market rankings.")
    parser.add_argument("--input", default="data/processed/metro_panel.csv")
    parser.add_argument("--metadata", default="data/processed/feature_metadata.csv")
    parser.add_argument("--feasibility", default="outputs/feasibility.md")
    parser.add_argument("--train-cutoff", required=True, help="ISO date, e.g. 2010-01-01")
    parser.add_argument("--evaluation-cutoff", required=True, help="ISO date, e.g. 2018-02-01")
    parser.add_argument("--candidate-count", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="Prespecified Ridge alpha; not tuned on evaluation data.")
    args = parser.parse_args()

    if not abs(args.alpha - 1.0) < 1e-12:
        parser.error("Ridge alpha is prespecified at 1.0 and cannot be changed in the approved run.")

    try:
        validate_feasibility_gate(args.feasibility)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    panel = validate_panel(pd.read_csv(args.input, dtype={"metro_id": str}))
    metadata = validate_feature_metadata(pd.read_csv(args.metadata))
    train_cutoff = pd.Timestamp(args.train_cutoff)
    evaluation_cutoff = pd.Timestamp(args.evaluation_cutoff)
    train = panel[panel.decision_cutoff == train_cutoff].copy()
    evaluation_all = panel[panel.decision_cutoff == evaluation_cutoff].copy()
    candidates = select_candidates(evaluation_all, args.candidate_count)
    validate_train_eval(train, candidates)

    eval_eligible = eligible_features(metadata, evaluation_cutoff)
    required_eval = {"population", "current_establishments", "national_establishments_per_capita"}
    if not required_eval.issubset(eval_eligible):
        missing = sorted(required_eval - eval_eligible)
        raise SystemExit(f"Required baseline/white-space features are not verified at evaluation cutoff: {missing}")
    train_eligible = eligible_features(metadata, train_cutoff)
    ridge_features = [f for f in DEFAULT_FEATURES
                      if f in train_eligible and f in eval_eligible
                      and f in train.columns and f in candidates.columns]
    if not ridge_features:
        raise SystemExit("No Ridge features are verified and common to both cutoffs.")

    # Held-out evaluation labels are not passed to ranking or preprocessing steps.
    rankings, model = build_rankings(train, candidates.drop(columns=["net_additions"]),
                                     features=ridge_features, alpha=1.0)
    heldout = candidates[["metro_id", "net_additions"]].copy()
    metrics, per_metro = evaluate_rankings(rankings, heldout)
    rankings_with_outcomes = rankings.merge(heldout, on="metro_id", how="left", validate="many_to_one")

    output = Path("outputs/tables")
    output.mkdir(parents=True, exist_ok=True)
    candidate_list = candidates.sort_values(["population", "metro_id"], ascending=[False, True], kind="mergesort")[
        ["metro_id", "metro_name", "population"]
    ].copy()
    candidate_list.insert(0, "population_rank", range(1, len(candidate_list) + 1))
    candidate_list.to_csv(output / "evaluation_candidates_top100.csv", index=False)
    rankings_with_outcomes.to_csv(output / "full_rankings.csv", index=False)
    metrics.to_csv(output / "method_comparison.csv", index=False)
    per_metro.to_csv(output / "per_metro_evaluation.csv", index=False)

    feature_columns = ["metro_id", "metro_name", "population", "current_establishments",
                       "restaurants_per_10k", "national_establishments_per_capita", "net_additions"]
    explanation = candidates[feature_columns].copy()
    rank_wide = rankings.pivot(index="metro_id", columns="method", values="rank")
    rank_wide.columns = [f"{method}_rank" for method in rank_wide.columns]
    score_wide = rankings.pivot(index="metro_id", columns="method", values="score")
    score_wide.columns = [f"{method}_score" for method in score_wide.columns]
    explanation = explanation.merge(rank_wide.reset_index(), on="metro_id", validate="one_to_one")
    explanation = explanation.merge(score_wide.reset_index(), on="metro_id", validate="one_to_one")
    explanation.to_csv(output / "metro_explanations.csv", index=False)

    metric_definitions = pd.DataFrame([
        ("selected_net_additions", "Sum of observed net establishment additions among the method's top K; may be negative."),
        ("hindsight_best_net_additions", "Sum for the K metros with the largest observed outcomes; evaluation reference only."),
        ("regret", "Hindsight-best total minus selected total for the same K."),
        ("overlap_actual_top_k", "Count of selected metros also in the actual outcome top K; ties break by metro ID."),
        ("precision_at_k", "Overlap count divided by K (or available candidate count if smaller)."),
        ("ndcg_at_k_nonnegative_linear_gain", "NDCG using relevance=max(0, net_additions), linear gain, and logarithmic rank discounts; NaN when ideal gain is zero."),
        ("spearman_rho", "Spearman correlation between method score order and observed net additions across the full candidate universe."),
    ], columns=["metric", "definition"])
    metric_definitions.to_csv(output / "metric_definitions.csv", index=False)

    for k in (5, 10, 20):
        for method, group in rankings_with_outcomes.groupby("method"):
            group.sort_values("rank").head(k).to_csv(
                output / f"shortlist_{method}_top{k}.csv", index=False)

    figures = generate_figures(rankings_with_outcomes, metrics, Path("outputs/figures"))
    print(f"Wrote candidate universe, rankings, shortlists, evaluation tables, explanations, and figures to {output.parent}")
    print(f"Ridge alpha=1.0; training rows={len(train)}; evaluation candidates={len(candidates)}; features={ridge_features}")
    print(f"Figures: {[str(path) for path in figures]}")

if __name__ == "__main__":
    main()
