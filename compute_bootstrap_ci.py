"""Item-cluster bootstrap confidence intervals for the ChAAt core results."""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DETAILS = ROOT / "results" / "noweb_all" / "core50" / "paper_details.csv"
OUT = DETAILS.parent / "bootstrap_ci.csv"
SEED = 20261126
REPLICATES = 10000


def main():
    details = pd.read_csv(DETAILS)
    per_item = details.groupby(["model", "id"], as_index=False)["correct"].mean()
    rng = np.random.default_rng(SEED)
    rows = []
    for model, group in per_item.groupby("model"):
        values = group["correct"].to_numpy(dtype=float)
        draws = rng.choice(values, size=(REPLICATES, len(values)), replace=True).mean(axis=1)
        rows.append(
            {
                "model": model,
                "n_items": len(values),
                "accuracy": values.mean(),
                "boot_ci_low": np.quantile(draws, 0.025),
                "boot_ci_high": np.quantile(draws, 0.975),
                "replicates": REPLICATES,
                "seed": SEED,
            }
        )
    result = pd.DataFrame(rows).sort_values("accuracy", ascending=False)
    result.to_csv(OUT, index=False)
    print(result.to_string(index=False))
    print(OUT)


if __name__ == "__main__":
    main()
