# -*- coding: utf-8 -*-
"""生成论文主图：无障碍配色、冗余标签、PNG(300dpi)+PDF。

数据来源：results/noweb_all/core50/paper_summary.csv
输出：results/noweb_all/core50/figs/fig1_heatmap.* 与 fig2_radar.*
"""

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
ENGLISH_LABELS = {
    "成语与熟语": "Idiom",
    "古汉语": "Classical\nChinese",
    "方言书面语": "Dialect",
    "网络新词与谐音": "Slang",
    "歧义与语用": "Pragmatics &\nPronunciation",
    "字音字形与病句": "Language Use",
    "文化常识": "Culture",
}
DIMENSION_ORDER = [
    "Idiom",
    "Classical\nChinese",
    "Dialect",
    "Slang",
    "Pragmatics &\nPronunciation",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary", default="results/noweb_all/core50/paper_summary.csv"
    )
    parser.add_argument(
        "--outdir", default="results/noweb_all/core50/figs"
    )
    args = parser.parse_args()

    s = pd.read_csv(args.summary)
    overall = s[s["dimension"] == "overall"].set_index("model")["accuracy"]
    d = s[s["dimension"] != "overall"].pivot_table(
        index="model", columns="dimension_label", values="accuracy"
    )
    order = overall.sort_values(ascending=False).index.tolist()
    d = d.loc[order].rename(columns=ENGLISH_LABELS)
    dims = [name for name in DIMENSION_ORDER if name in d.columns]
    d = d[dims]
    values = d.values.astype(float)
    models = list(d.index)

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(3.5, 2.8), layout="constrained")
    im = ax.imshow(values, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(dims)), dims, fontsize=5.8)
    ax.set_yticks(range(len(models)), models, fontsize=6.0)
    for i in range(len(models)):
        for j in range(len(dims)):
            v = values[i, j]
            ax.text(
                j,
                i,
                f"{v:.0%}",
                ha="center",
                va="center",
                fontsize=5.6,
                color="white" if v < 0.55 else "black",
                fontweight="bold",
            )
    cb = fig.colorbar(im, ax=ax, fraction=0.02)
    cb.set_label("Accuracy", fontsize=6.0)
    cb.ax.tick_params(labelsize=5.5)
    ax.set_title("Model × dimension accuracy", fontsize=7.2, pad=5)
    fig.savefig(os.path.join(outdir, "fig1_heatmap.png"), dpi=600)
    fig.savefig(os.path.join(outdir, "fig1_heatmap.tiff"), dpi=600)
    fig.savefig(os.path.join(outdir, "fig1_heatmap.svg"))
    fig.savefig(os.path.join(outdir, "fig1_heatmap.pdf"))
    plt.close(fig)

    angles = (
        (
            np.linspace(0, 2 * np.pi, len(dims), endpoint=False)
            + np.pi / 2
        )
        % (2 * np.pi)
    ).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(
        figsize=(3.35, 3.55), subplot_kw=dict(polar=True), layout="constrained"
    )
    handles = []
    labels = []
    for i, m in enumerate(models):
        vals = values[i].tolist() + values[i].tolist()[:1]
        (line,) = ax.plot(
            angles,
            vals,
            label=m,
            color=OKABE_ITO[i % len(OKABE_ITO)],
            linewidth=2,
        )
        handles.append(line)
        labels.append(m)
        ax.fill(angles, vals, alpha=0.06, color=OKABE_ITO[i % len(OKABE_ITO)])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([])
    for angle, label in zip(angles[:-1], dims):
        cosine = np.cos(angle)
        sine = np.sin(angle)
        ha = "left" if cosine > 0.15 else "right" if cosine < -0.15 else "center"
        va = "bottom" if sine > 0.15 else "top" if sine < -0.15 else "center"
        ax.text(
            angle,
            1.14,
            label,
            ha=ha,
            va=va,
            fontsize=5.8,
            clip_on=False,
        )
    ax.set_ylim(0, 1.08)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels([])
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
        fontsize=5.3,
        frameon=False,
        columnspacing=1.0,
        handlelength=1.8,
    )
    ax.set_title("Per-dimension capability comparison", fontsize=7.2, pad=14)
    fig.savefig(os.path.join(outdir, "fig2_radar.png"), dpi=600)
    fig.savefig(os.path.join(outdir, "fig2_radar.tiff"), dpi=600)
    fig.savefig(os.path.join(outdir, "fig2_radar.svg"))
    fig.savefig(os.path.join(outdir, "fig2_radar.pdf"))
    plt.close(fig)

    print("已生成：")
    for name in [
        "fig1_heatmap.png",
        "fig1_heatmap.svg",
        "fig1_heatmap.tiff",
        "fig1_heatmap.pdf",
        "fig2_radar.png",
        "fig2_radar.svg",
        "fig2_radar.tiff",
        "fig2_radar.pdf",
    ]:
        print(" ", os.path.join(outdir, name))


if __name__ == "__main__":
    main()
