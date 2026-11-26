# -*- coding: utf-8 -*-
"""题目难度与区分度校准。

用法：
    python calibrate_items.py

输出：
    results/noweb_all/core50/item_calibration.csv
    results/noweb_all/core50/item_calibration.md
"""

import argparse
import io
import json
import os

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--details", default="results/noweb_all/core50/paper_details.csv"
    )
    parser.add_argument(
        "--questions", default="data/questions_final_hard50_core_shuffled.json"
    )
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    outdir = args.outdir or os.path.dirname(args.details) or "."
    os.makedirs(outdir, exist_ok=True)

    qmap = {}
    labels = {}
    for path in [p.strip() for p in args.questions.split(",") if p.strip()]:
        with io.open(path, encoding="utf-8") as f:
            qdata = json.load(f)
        qmap.update({q["id"]: q for q in qdata["questions"]})
        labels.update(qdata["meta"]["dimensions"])

    df = pd.read_csv(args.details)
    df["correct"] = df["correct"].astype(bool)

    model_acc = df.groupby("model")["correct"].mean().sort_values(ascending=False)
    models = list(model_acc.index)
    # Fixed comparison groups: the two strongest minus the two weakest
    # models by overall accuracy. This avoids a floating "half" definition
    # for a six-model leaderboard.
    top = models[:2]
    bottom = models[-2:]

    rows = []
    for qid, sub in df.groupby("id"):
        per_model = sub.groupby("model")["correct"].mean()
        p = float(sub["correct"].mean())
        top_acc = float(per_model.reindex(top).mean())
        bottom_acc = float(per_model.reindex(bottom).mean())
        d = top_acc - bottom_acc

        flags = []
        if p >= 0.9:
            flags.append("too_easy")
        if p <= 0.1:
            flags.append("too_hard_or_ambiguous")
        if 0.2 <= p <= 0.8:
            flags.append("model_split")
        if d < 0:
            flags.append("negative_discrimination")
        if not flags:
            flags.append("ok")

        q = qmap.get(qid, {})
        rows.append(
            {
                "id": qid,
                "dimension": q.get("dimension", ""),
                "dimension_label": labels.get(q.get("dimension", ""), ""),
                "p": p,
                "d": d,
                "flag": ";".join(flags),
                "question": q.get("question", ""),
                "source_ref": q.get("source_ref", ""),
            }
        )

    out = pd.DataFrame(rows)
    dim_order = {k: i for i, k in enumerate(labels)}
    out["_dim"] = out["dimension"].map(dim_order).fillna(99)
    out = out.sort_values(["_dim", "id"]).drop(columns=["_dim"])

    csv_path = os.path.join(outdir, "item_calibration.csv")
    out.to_csv(csv_path, index=False, encoding="utf-8-sig")

    lines = [
        "# 题目难度与区分度校准",
        "",
        f"- 模型排序：{', '.join(f'{m} ({model_acc[m]:.0%})' for m in models)}",
        f"- 强组（前二）：{', '.join(top)}",
        f"- 弱组（后二）：{', '.join(bottom)}",
        "",
        "| ID | 维度 | 通过率 p | 区分度 D | 标记 | 题目 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"| {r['id']} | {r['dimension_label']} | {r['p']:.0%} | "
            f"{r['d']:.2f} | {r['flag']} | {r['question'][:36]} |"
        )
    md_path = os.path.join(outdir, "item_calibration.md")
    with io.open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"已输出：{csv_path}")
    print(f"已输出：{md_path}")
    print("\n标记统计：")
    print(out["flag"].value_counts().to_string())
    print("\n区分度最高的 10 题：")
    top10 = out.sort_values(["d", "p"], ascending=[False, True]).head(10)
    for _, r in top10.iterrows():
        print(f"  {r['id']}  p={r['p']:.0%}  D={r['d']:.2f}  {r['dimension_label']}")


if __name__ == "__main__":
    main()
