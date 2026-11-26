import pandas as pd
import pytest
from src.models import population_ranking, whitespace_ranking, ridge_ranking
from src.validation import validate_panel, validate_feature_metadata, validate_train_eval, eligible_features
from src.compare import select_candidates, build_rankings
from src.evaluate import evaluate_rankings

def test_population_tie_break_is_stable():
    d = pd.DataFrame({"metro_id": ["002", "001"], "population": [100, 100]})
    assert population_ranking(d).metro_id.tolist() == ["001", "002"]

def test_white_space_formula():
    d = pd.DataFrame({"metro_id": ["001"], "population": [100],
                      "current_establishments": [5],
                      "national_establishments_per_capita": [.1]})
    assert whitespace_ranking(d).score.iloc[0] == 5

def test_panel_rejects_target_start_at_cutoff():
    d = pd.DataFrame({"metro_id": ["001"], "decision_cutoff": ["2014-01-01"],
                      "target_start": ["2014-01-01"], "target_end": ["2019-03-12"],
                      "target_release_date": ["2021-04-22"], "net_additions": [1],
                      "population": [10], "current_establishments": [2],
                      "national_establishments_per_capita": [.1]})
    with pytest.raises(ValueError, match="strictly after"):
        validate_panel(d)

def test_metadata_rejects_late_release():
    m = pd.DataFrame([{"feature_name":"pop", "source":"ACS", "reference_period":"2010-2014",
        "release_date":"2015-12-03", "decision_cutoff":"2014-01-01",
        "transformation":"raw", "missingness_policy":"preserve",
        "leakage_check_status":"PASS"}])
    with pytest.raises(ValueError, match="released after"):
        validate_feature_metadata(m)

def test_train_labels_must_be_public_by_eval_cutoff():
    train = pd.DataFrame({"metro_id":["001"], "decision_cutoff":["2010-01-01"],
       "target_start":["2010-03-12"], "target_end":["2013-03-12"],
       "target_release_date":["2018-02-02"]})
    ev = pd.DataFrame({"metro_id":["001"], "decision_cutoff":["2018-02-01"],
       "target_start":["2018-03-12"], "target_end":["2021-03-12"],
       "target_release_date":["2023-04-27"]})
    with pytest.raises(ValueError, match="not publicly available"):
        validate_train_eval(train, ev)

def test_methods_same_candidate_set_and_metrics():
    rows=[]
    for period, cutoff, start, end, release in [
        ("train", "2010-01-01", "2010-03-12", "2013-03-12", "2015-04-23"),
        ("eval", "2018-02-01", "2018-03-12", "2021-03-12", "2023-04-27")]:
        for i in range(25):
            rows.append({"metro_id":f"{i:03d}", "decision_cutoff":cutoff,
                "target_start":start, "target_end":end, "target_release_date":release,
                "net_additions":float((i%7)-2), "population":1000+i*100,
                "current_establishments":20+i,
                "national_establishments_per_capita":.02,
                "median_household_income":50000+i*100,
                "median_age":35+i*.1, "education_bachelors_share":.2,
                "restaurants_per_10k":2+i*.01, "prior_net_additions":float(i-5)})
    p=pd.DataFrame(rows)
    train=p[p.decision_cutoff=="2010-01-01"]
    ev=p[p.decision_cutoff=="2018-02-01"]
    candidates=select_candidates(ev,25)
    validate_train_eval(train,candidates)
    ranks,_=build_rankings(train,candidates.drop(columns=["net_additions"]))
    metrics,detail=evaluate_rankings(ranks,candidates[["metro_id","net_additions"]])
    assert set(ranks.method)=={"population","white_space","ridge"}
    assert len(ranks)==75
    assert set(metrics.k)=={5,10,20}
    assert len(detail)==75
    assert (metrics.regret >= -1e-9).all()


def test_unverified_feature_is_excluded_not_promoted():
    m = pd.DataFrame([
      {"feature_name":"population", "source":"ACS", "reference_period":"2012-2016",
       "release_date":"2017-12-07", "decision_cutoff":"2018-02-01",
       "transformation":"sum", "missingness_policy":"none",
       "leakage_check_status":"PASS"},
      {"feature_name":"income", "source":"ACS", "reference_period":"2012-2016",
       "release_date":"", "decision_cutoff":"2018-02-01",
       "transformation":"sum", "missingness_policy":"preserve",
       "leakage_check_status":"UNVERIFIED"},
    ])
    checked=validate_feature_metadata(m)
    assert eligible_features(checked, "2018-02-01")=={"population"}


def test_evaluation_outcome_must_be_unpublished_at_cutoff():
    train = pd.DataFrame({"metro_id":["001"], "decision_cutoff":["2010-01-01"],
       "target_start":["2010-03-12"], "target_end":["2013-03-12"],
       "target_release_date":["2015-04-23"]})
    ev = pd.DataFrame({"metro_id":["001"], "decision_cutoff":["2018-02-01"],
       "target_start":["2018-03-12"], "target_end":["2023-03-12"],
       "target_release_date":["2017-12-31"]})
    with pytest.raises(ValueError, match="remain unpublished"):
        validate_train_eval(train, ev)


def test_candidate_selection_requires_full_requested_universe():
    d=pd.DataFrame({"metro_id":["001","002"],"population":[200,100]})
    with pytest.raises(ValueError, match="only 2 are available"):
        select_candidates(d, 20)

def test_white_space_requires_shared_national_density():
    d = pd.DataFrame({"metro_id": ["001", "002"], "population": [100, 200],
                      "current_establishments": [5, 8],
                      "national_establishments_per_capita": [.1, .2]})
    with pytest.raises(ValueError, match="one cutoff-wide value"):
        whitespace_ranking(d)

def test_feasibility_gate_blocks_without_explicit_approval(tmp_path):
    from src.validation import validate_feasibility_gate
    gate = tmp_path / "feasibility.md"
    gate.write_text("FEASIBILITY_GATE: BLOCKED\nDESIGN_APPROVAL: PENDING\n")
    with pytest.raises(ValueError, match="not PASS"):
        validate_feasibility_gate(gate)


def test_feasibility_gate_requires_design_approval(tmp_path):
    from src.validation import validate_feasibility_gate
    gate = tmp_path / "feasibility.md"
    gate.write_text("FEASIBILITY_GATE: PASS\nDESIGN_APPROVAL: PENDING\n")
    with pytest.raises(ValueError, match="not been explicitly approved"):
        validate_feasibility_gate(gate)


def test_build_rankings_keeps_full_training_universe():
    train = pd.DataFrame({
        "metro_id":["001","002","003","004"],
        "population":[100,200,300,400],
        "current_establishments":[2,3,4,5],
        "restaurants_per_10k":[2.0,1.5,1.33,1.25],
        "national_establishments_per_capita":[0.02,0.02,0.02,0.02],
        "net_additions":[1.0,2.0,-1.0,3.0],
    })
    candidates = train.loc[train.metro_id.isin(["001","002"])].drop(columns="net_additions").copy()
    rankings, model = build_rankings(train, candidates, features=["population","current_establishments","restaurants_per_10k"])
    assert len(rankings) == 6
    assert model.named_steps["ridge"].coef_.shape[0] == 3
    assert set(rankings.metro_id) == {"001","002"}
