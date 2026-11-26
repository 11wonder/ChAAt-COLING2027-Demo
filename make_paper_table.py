# -*- coding: utf-8 -*-
"""根据 paper_summary.csv 生成论文最终主表（均值±标准差）。"""

import argparse

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary", default="results/noweb_all/core50/paper_summary.csv"
    )
    parser.add_argument(
        "--details", default="results/noweb_all/core50/paper_details.csv"
    )
    parser.add_argument(
        "--out", default="results/noweb_all/core50/final_paper_table.md"
    )
    args = parser.parse_args()

    s = pd.read_csv(args.summary)
    overall = s[s["dimension"] == "overall"][["model", "accuracy", "std"]].sort_values(
        "accuracy", ascending=False
    )
    d = s[s["dimension"] != "overall"].pivot_table(
        index="model", columns="dimension_label", values="accuracy"
    )

    order = overall["model"].tolist()
    d = d.loc[order]
    cols = [
        "成语与熟语",
        "古汉语",
        "方言书面语",
        "网络新词与谐音",
        "歧义与语用",
        "字音字形与病句",
        "文化常识",
    ]
    cols = [c for c in cols if c in d.columns]
    d = d[cols]

    lines = []
    lines.append("| 模型 | " + " | ".join(d.columns) + " | 总体 |")
    lines.append("| --- | " + " | ".join(["---"] * (len(d.columns) + 1)) + " |")
    for m in order:
        cells = [f"{d.loc[m, c]:.0%}" for c in cols]
        ov = overall.loc[overall["model"] == m, "accuracy"].iloc[0]
        sd = overall.loc[overall["model"] == m, "std"].iloc[0]
        cells.append(f"{ov:.0%}±{sd:.0%}")
        lines.append("| " + m + " | " + " | ".join(cells) + " |")

    md = "\n".join(lines)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(md)

    df = pd.read_csv(args.details)
    print(
        "empty_outputs",
        int(
            (df["output"].isna() | (df["output"].astype(str).str.strip() == "")).sum()
        ),
    )


if __name__ == "__main__":
    main()
