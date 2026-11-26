"""Merge and summarize the completed third-rater and robustness forms."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

from analyze_human_scoring import icc_two_way, normalized_levels


ROOT = Path(__file__).resolve().parent


def read_csv_fallback(path):
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"cannot decode {path}")


def summarize_third_rater():
    form = read_csv_fallback(ROOT / "docs" / "third_rater_blind_form.csv")
    mapping = pd.read_csv(
        ROOT / "results" / "noweb_all" / "open_probe6_human" / "third_rater_blind_map.csv"
    )
    old = pd.read_csv(
        ROOT / "results" / "noweb_all" / "open_probe6_human" / "human_details.csv"
    )
    scored = form.merge(mapping, on="blind_id", validate="one_to_one")
    scored = scored.merge(
        old[["answer_key", "human_rater1", "human_rater2", "final_human_score", "model"]],
        on=["answer_key", "model"],
        how="left",
        validate="one_to_one",
    )
    for column in ("third_rater_score", "human_rater1", "human_rater2", "final_human_score"):
        scored[column] = pd.to_numeric(scored[column], errors="raise")
    if scored["third_rater_score"].isna().any():
        raise ValueError("third-rater form contains missing scores")
    if (
        (scored["third_rater_score"] < 0)
        | (scored["third_rater_score"] > scored["max_score"])
    ).any():
        raise ValueError("third-rater score outside the item rubric")
    if ((scored["third_rater_score"] * 2) % 1 != 0).any():
        raise ValueError("third-rater score is not on the 0.5 grid")

    scored["two_rater_mean"] = (
        scored["human_rater1"] + scored["human_rater2"]
    ) / 2
    scored.to_csv(
        ROOT / "results" / "noweb_all" / "open_probe6_human" / "third_rater_scored.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary = (
        scored.groupby("model")
        .agg(
            two_rater_mean=("two_rater_mean", "sum"),
            prior_adjudicated=("final_human_score", "sum"),
            third_rater=("third_rater_score", "sum"),
            max_score=("max_score", "sum"),
            n_answers=("third_rater_score", "size"),
        )
        .reset_index()
    )
    for source, target in (
        ("two_rater_mean", "two_rater_mean_pct"),
        ("prior_adjudicated", "prior_adjudicated_pct"),
        ("third_rater", "third_rater_pct"),
    ):
        summary[target] = summary[source] / summary["max_score"] * 100
    summary = summary.sort_values(["third_rater", "two_rater_mean"], ascending=False)
    summary.to_csv(
        ROOT / "results" / "noweb_all" / "open_probe6_human" / "third_rater_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    y = scored[["human_rater1", "human_rater2", "third_rater_score"]].to_numpy(float)
    icc21, icc2k = icc_two_way(y)
    pairs = [
        ("human_rater1", "human_rater2"),
        ("human_rater1", "third_rater_score"),
        ("human_rater2", "third_rater_score"),
    ]
    qwk = [
        float(
            cohen_kappa_score(
                normalized_levels(scored[left], scored["max_score"]),
                normalized_levels(scored[right], scored["max_score"]),
                weights="quadratic",
            )
        )
        for left, right in pairs
    ]
    reliability = {
        "n_answers": int(len(scored)),
        "ICC_2_1": icc21,
        "ICC_2_k": icc2k,
        "pairwise_quadratic_weighted_kappa": qwk,
        "mean_pairwise_quadratic_weighted_kappa": float(np.mean(qwk)),
        "third_vs_prior_exact": int((scored["third_rater_score"] == scored["final_human_score"]).sum()),
        "third_vs_prior_within_0_5": int(
            ((scored["third_rater_score"] - scored["final_human_score"]).abs() <= 0.5).sum()
        ),
        "third_vs_prior_mean_absolute_difference": float(
            (scored["third_rater_score"] - scored["final_human_score"]).abs().mean()
        ),
    }
    (
        ROOT / "results" / "noweb_all" / "open_probe6_human" / "third_rater_reliability.json"
    ).write_text(json.dumps(reliability, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary, reliability


def summarize_robustness():
    form = pd.read_csv(
        ROOT / "docs" / "robustness_open5_blind_form.csv", encoding="utf-8-sig"
    )
    mapping = pd.read_csv(
        ROOT / "results" / "noweb_all" / "core50_open5" / "blind_map.csv"
    )
    scored = form.merge(mapping, on="blind_id", validate="one_to_one")
    scored["rater_score"] = pd.to_numeric(scored["rater_score"], errors="raise")
    if scored["rater_score"].isna().any():
        raise ValueError("robustness form contains missing scores")
    if ((scored["rater_score"] < 0) | (scored["rater_score"] > scored["max_score"])).any():
        raise ValueError("robustness score outside the rubric")
    if ((scored["rater_score"] * 2) % 1 != 0).any():
        raise ValueError("robustness score is not on the 0.5 grid")
    scored.to_csv(
        ROOT / "results" / "noweb_all" / "core50_open5" / "rater_scored.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = (
        scored.groupby("model")
        .agg(
            score=("rater_score", "sum"),
            max_score=("max_score", "sum"),
            n_tasks=("rater_score", "size"),
        )
        .reset_index()
    )
    summary["accuracy"] = summary["score"] / summary["max_score"]
    summary = summary.sort_values(["score", "model"], ascending=[False, True])
    summary.to_csv(
        ROOT / "results" / "noweb_all" / "core50_open5" / "rater_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return summary


def main():
    third_summary, reliability = summarize_third_rater()
    robust_summary = summarize_robustness()
    print("Third-rater summary")
    print(third_summary.to_string(index=False))
    print("Reliability")
    print(json.dumps(reliability, indent=2))
    print("Option-free robustness summary")
    print(robust_summary.to_string(index=False))


if __name__ == "__main__":
    main()
