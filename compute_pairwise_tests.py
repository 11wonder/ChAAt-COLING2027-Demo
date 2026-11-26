"""Exact McNemar tests for the six ChAAt main models."""

from itertools import combinations
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest


ROOT = Path(__file__).resolve().parent
DETAILS = ROOT / "results" / "noweb_all" / "core50" / "paper_details.csv"
OUT = DETAILS.parent / "mcnemar_pairwise.csv"


def main():
    details = pd.read_csv(DETAILS)
    per_item = details.groupby(["id", "model"]).correct.mean().unstack()
    strict = per_item.eq(1)
    rows = []
    for left, right in combinations(strict.columns, 2):
        left_only = int((strict[left] & ~strict[right]).sum())
        right_only = int((~strict[left] & strict[right]).sum())
        discordant = left_only + right_only
        p_value = (
            binomtest(min(left_only, right_only), discordant, 0.5).pvalue
            if discordant
            else 1.0
        )
        rows.append(
            {
                "model_a": left,
                "model_b": right,
                "a_stable_pass_b_not": left_only,
                "b_stable_pass_a_not": right_only,
                "discordant": discordant,
                "exact_two_sided_p": p_value,
            }
        )
    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False)
    focus = result[
        ((result.model_a == "DeepSeek Flash") & (result.model_b == "GPT-5.4"))
        | ((result.model_a == "DeepSeek Flash") & (result.model_b == "Qwen Max"))
    ]
    print(focus.to_string(index=False))
    print(OUT)


if __name__ == "__main__":
    main()
