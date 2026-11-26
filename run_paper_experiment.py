# -*- coding: utf-8 -*-
"""论文实验批量运行器：模型 × 题库，输出 CSV / JSON / 图表。

用法示例：
    python run_paper_experiment.py --dry-run
    python run_paper_experiment.py --per-dimension 5
    python run_paper_experiment.py --repeats 3
    python run_paper_experiment.py --models deepseek,qwen,glm,gpt4omini
"""

import argparse
import io
import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from llm_client import build_answer_prompt, build_client, chat, ollama_chat
from scorer import grade_question

load_dotenv()

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

SYSTEM_PROMPT = (
    "你是中文语言能力评测的受测模型，请严格按题目要求作答。"
    "禁止联网搜索或调用任何外部工具，只凭自身知识回答。"
)

PAPER_MODELS = [
    {
        "key": "deepseek",
        "label": "DeepSeek Flash",
        "base_url": "https://api.deepseek.com",
        "model_id": "deepseek-flash",
        "env": "DEEPSEEK_API_KEY",
    },
    {
        "key": "qwen",
        "label": "Qwen Max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_id": "qwen-max",
        "env": "DASHSCOPE_API_KEY",
    },
    {
        "key": "qwenplus",
        "label": "Qwen Plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_id": "qwen-plus",
        "env": "DASHSCOPE_API_KEY",
    },
    {
        "key": "glm",
        "label": "GLM-4 Plus",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_id": "glm-4-plus",
        "env": "ZHIPU_API_KEY",
    },
    {
        "key": "gpt4omini",
        "label": "GPT-4o mini",
        "base_url": "https://api.openai.com/v1",
        "base_env": "OPENAI_BASE_URL",
        "model_id": "gpt-4o-mini",
        "env": "OPENAI_API_KEY",
    },
    {
        "key": "gpt54mini",
        "label": "GPT-5.4 mini",
        "base_url": "https://api.openai.com/v1",
        "base_env": "OPENAI_BASE_URL",
        "model_id": "gpt-5.4-mini",
        "env": "OPENAI_API_KEY",
    },
    {
        "key": "gpt5",
        "label": "GPT-5.4",
        "base_url": "https://api.openai.com/v1",
        "base_env": "OPENAI_BASE_URL",
        "model_id": "gpt-5.4",
        "env": "OPENAI_API_KEY",
    },
    {
        "key": "ollama",
        "label": "Ollama Qwen3.5 4B",
        "base_url": "http://localhost:11434/v1",
        "model_id": "qwen3.5:4b",
        "env": "",
    },
]


def resolve_base_url(preset):
    env_name = preset.get("base_env")
    if env_name:
        return os.environ.get(env_name, "") or preset["base_url"]
    return preset["base_url"]


def safe_err(exc, key):
    msg = f"{type(exc).__name__}: {exc}"
    if key:
        msg = msg.replace(key, "***")
    return msg[:240]


def ask_with_retry(preset, client, prompt, temperature, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            if preset["key"] == "ollama":
                output = ollama_chat(
                    preset["base_url"],
                    preset["model_id"],
                    prompt,
                    system=SYSTEM_PROMPT,
                    temperature=temperature,
                    max_tokens=1024,
                )
            else:
                output = chat(
                    client,
                    preset["model_id"],
                    prompt,
                    system=SYSTEM_PROMPT,
                    temperature=temperature,
                    max_tokens=1024,
                )
            if not (output or "").strip():
                raise RuntimeError("empty response")
            return output
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last


def pick_questions(questions, per_dimension):
    if not per_dimension:
        return questions
    buckets = {}
    for q in questions:
        buckets.setdefault(q["dimension"], []).append(q)
    picked = []
    for arr in buckets.values():
        picked.extend(arr[:per_dimension])
    return picked


def evaluate_model(preset, questions, temperature, repeats):
    key = os.environ.get(preset["env"], "") if preset["env"] else ""
    if preset["env"] and not key:
        return None, "未配置环境变量 " + preset["env"]
    base_url = resolve_base_url(preset)
    client = build_client(base_url, key or "ollama")
    rows = []
    total = len(questions) * repeats
    done = 0
    for rep in range(1, repeats + 1):
        for q in questions:
            prompt = build_answer_prompt(q)
            try:
                output = ask_with_retry(preset, client, prompt, temperature)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {q['id']} 调用失败：{safe_err(exc, key)}")
                output = ""
            ok, detail = grade_question(output, q)
            rows.append(
                {
                    "model": preset["label"],
                    "dimension": q["dimension"],
                    "id": q["id"],
                    "repeat": rep,
                    "question": q["question"],
                    "expected": q.get("answer", ""),
                    "output": output,
                    "correct": bool(ok),
                    "detail": detail,
                    "explanation": q.get("explanation", ""),
                    "difficulty": q.get("difficulty", ""),
                    "source": q.get("source", ""),
                }
            )
            done += 1
            if done % 10 == 0 or done == total:
                print(f"  {preset['label']}: {done}/{total}")
    return rows, None


def build_summary(rows, model_label, dim_labels, repeats, n_questions):
    summary = []
    for dim, label in dim_labels.items():
        accs = []
        nq = 0
        for rep in range(1, repeats + 1):
            sub = [r for r in rows if r["dimension"] == dim and r["repeat"] == rep]
            if sub:
                accs.append(sum(1 for r in sub if r["correct"]) / len(sub))
                nq = len(sub)
        if not accs:
            continue
        summary.append(
            {
                "model": model_label,
                "dimension": dim,
                "dimension_label": label,
                "accuracy": float(np.mean(accs)) if accs else 0.0,
                "std": float(np.std(accs)) if len(accs) > 1 else 0.0,
                "n_questions": nq,
                "repeats": repeats,
            }
        )
    overall = []
    for rep in range(1, repeats + 1):
        sub = [r for r in rows if r["repeat"] == rep]
        if sub:
            overall.append(sum(1 for r in sub if r["correct"]) / len(sub))
    summary.append(
        {
            "model": model_label,
            "dimension": "overall",
            "dimension_label": "总体",
            "accuracy": float(np.mean(overall)) if overall else 0.0,
            "std": float(np.std(overall)) if len(overall) > 1 else 0.0,
            "n_questions": n_questions,
            "repeats": repeats,
        }
    )
    return summary


def make_markdown(summary_df, dim_labels):
    sub = summary_df[summary_df["dimension"] != "overall"]
    wide = sub.pivot(index="model", columns="dimension", values="accuracy")
    dim_keys = [k for k in dim_labels if k in wide.columns]
    overall = summary_df[summary_df["dimension"] == "overall"].set_index("model")[
        "accuracy"
    ]
    header = "| 模型 | " + " | ".join(dim_labels[k] for k in dim_keys) + " | 总体 |"
    sep = "| --- | " + " | ".join(["---"] * (len(dim_keys) + 1)) + " |"
    lines = [header, sep]
    for model in wide.index:
        cells = [f"{float(wide.loc[model, k]):.0%}" for k in dim_keys]
        ov = overall.get(model, float("nan"))
        cells.append("—" if pd.isna(ov) else f"{float(ov):.0%}")
        lines.append(f"| {model} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot_figures(summary_df, dim_labels, outdir="figs"):
    sub = summary_df[summary_df["dimension"] != "overall"].copy()
    dim_keys = [k for k in dim_labels if k in set(sub["dimension"])]
    wide = sub.pivot(index="model", columns="dimension", values="accuracy")[dim_keys]
    labels = [dim_labels[k] for k in dim_keys]
    models = list(wide.index)
    values = wide.values.astype(float)
    os.makedirs(outdir, exist_ok=True)

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(models), 2)))[: len(models)]
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for i, model in enumerate(models):
        vals = values[i].tolist() + values[i].tolist()[:1]
        ax.plot(angles, vals, label=model, color=colors[i], linewidth=2)
        ax.fill(angles, vals, alpha=0.08, color=colors[i])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], fontsize=8)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=min(3, len(models)),
        fontsize=9,
        frameon=False,
    )
    ax.set_title("中文特色任务能力雷达图（真实评测）", fontsize=13, pad=18)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "paper_radar.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, max(3.0, 0.7 * len(models) + 1.5)))
    im = ax.imshow(values, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=10)
    for i in range(len(models)):
        for j in range(len(labels)):
            ax.text(
                j,
                i,
                f"{values[i, j]:.0%}",
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color="white" if values[i, j] < 0.35 else "black",
            )
    cb = fig.colorbar(im, ax=ax, fraction=0.02)
    cb.set_label("准确率", fontsize=10)
    ax.set_title("模型 × 维度准确率热力图（真实评测）", fontsize=13)
    fig.tight_layout()
    fig.savefig(
        os.path.join(outdir, "paper_heatmap.png"), dpi=150, bbox_inches="tight"
    )
    plt.close(fig)


def save_payload(outdir, all_rows, summaries, used, args, n_questions):
    payload = {
        "config": {
            "questions_file": args.questions,
            "questions": n_questions,
            "repeats": args.repeats,
            "temperature": args.temperature,
            "models": used,
        },
        "rows": all_rows,
        "summary": summaries,
    }
    with io.open(
        os.path.join(outdir, "paper_results.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--questions", default="data/questions_final_hard50_core_shuffled.json"
    )
    parser.add_argument("--per-dimension", type=int, default=0)
    parser.add_argument("--models", default="")
    parser.add_argument("--ids", default="")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--outdir", default="results/run")
    parser.add_argument("--figdir", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.figdir:
        args.figdir = os.path.join(args.outdir, "figs")

    paths = [p.strip() for p in args.questions.split(",") if p.strip()]
    questions = []
    dim_labels = {}
    for path in paths:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
        questions.extend(data["questions"])
        dim_labels.update(data["meta"]["dimensions"])
    questions = pick_questions(questions, args.per_dimension)
    if args.ids:
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        questions = [q for q in questions if q["id"] in wanted]
    selected = PAPER_MODELS
    if args.models:
        wanted = {x.strip() for x in args.models.split(",") if x.strip()}
        selected = [p for p in PAPER_MODELS if p["key"] in wanted]

    if args.dry_run:
        print("模型配置检查（不会显示 Key）：")
        for preset in selected:
            key = os.environ.get(preset["env"], "") if preset["env"] else ""
            if not preset["env"]:
                status = "本地，无需 Key"
            elif key:
                status = "已配置"
            else:
                status = "未配置"
            print(f"  {preset['key']:10s} {preset['label']:22s} {status}")
        print(
            f"\n题目数：{len(questions)}；模型数：{len(selected)}；"
            f"重复次数：{args.repeats}；预计调用：{len(questions) * len(selected) * args.repeats} 次"
        )
        return

    os.makedirs(args.outdir, exist_ok=True)
    all_rows = []
    summaries = []
    used = []
    for idx, preset in enumerate(selected, 1):
        print(f"\n[{idx}/{len(selected)}] {preset['label']} ({preset['model_id']})")
        rows, err = evaluate_model(preset, questions, args.temperature, args.repeats)
        if err:
            print("  跳过：" + err)
            continue
        used.append(preset["label"])
        all_rows.extend(rows)
        summaries.extend(
            build_summary(
                rows, preset["label"], dim_labels, args.repeats, len(questions)
            )
        )
        save_payload(args.outdir, all_rows, summaries, used, args, len(questions))

    if not all_rows:
        print("\n没有任何模型成功运行。请检查 .env 中的 API Key。")
        return

    summary_df = pd.DataFrame(summaries)
    detail_df = pd.DataFrame(all_rows)
    summary_df.to_csv(
        os.path.join(args.outdir, "paper_summary.csv"), index=False, encoding="utf-8-sig"
    )
    detail_df.to_csv(
        os.path.join(args.outdir, "paper_details.csv"), index=False, encoding="utf-8-sig"
    )
    table = make_markdown(summary_df, dim_labels)
    with io.open(
        os.path.join(args.outdir, "paper_table.md"), "w", encoding="utf-8"
    ) as f:
        f.write(table + "\n")
    plot_figures(summary_df, dim_labels, outdir=args.figdir)

    print("\n" + table)
    print(
        f"\n完成：{args.outdir}/paper_summary.csv、paper_details.csv、paper_table.md；"
        f"{args.figdir}/paper_radar.png、paper_heatmap.png"
    )


if __name__ == "__main__":
    main()
