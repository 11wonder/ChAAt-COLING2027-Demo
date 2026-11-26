# -*- coding: utf-8 -*-
"""开放题探针：模型作答 + 关键词量表打分。

用法：
    python run_open_probe.py

注意：当前用关键词量表自动评分，正式论文建议辅以人工抽检。
"""

import argparse
import io
import json
import os
import re
import time

import pandas as pd
from dotenv import load_dotenv

from llm_client import build_client, chat, ollama_chat
from run_paper_experiment import PAPER_MODELS, resolve_base_url

load_dotenv()

ANSWER_SYSTEM = (
    "你是中文语言能力评测的受测模型。请用中文简洁回答，覆盖关键点。"
    "禁止联网搜索或调用任何外部工具，只凭自身知识回答。"
)
JUDGE_SYSTEM = "你是严格、客观的中文能力评分员。只输出 JSON。"


def ask_model(preset, client, prompt):
    last = None
    for attempt in range(3):
        try:
            if preset["key"] == "ollama":
                answer = ollama_chat(
                    resolve_base_url(preset),
                    preset["model_id"],
                    prompt,
                    system=ANSWER_SYSTEM,
                    temperature=0.0,
                    max_tokens=2048,
                )
            else:
                answer = chat(
                    client,
                    preset["model_id"],
                    prompt,
                    system=ANSWER_SYSTEM,
                    temperature=0.0,
                    max_tokens=2048,
                    extra_body=(
                        {"thinking": {"type": "disabled"}}
                        if preset["key"] == "deepseek"
                        else None
                    ),
                )
            if (answer or "").strip():
                return answer
            last = RuntimeError("empty response")
        except Exception as exc:  # noqa: BLE001
            last = exc
        if attempt < 2:
            time.sleep(1.5 * (attempt + 1))
    raise last


def judge_answer(judge_client, task, answer):
    prompt = (
        f"题目：{task['question']}\n"
        f"参考答案：{task['reference']}\n"
        f"评分点：{task['rubric']}\n"
        f"模型回答：{answer}\n\n"
        "请按 0/1/2 打分：0=关键点错误或缺失；1=部分正确；2=完整正确。\n"
        '只输出 JSON：{"score": 0, "reason": "一句话"}'
    )
    raw = chat(
        judge_client,
        "deepseek-flash",
        prompt,
        system=JUDGE_SYSTEM,
        temperature=0.0,
        max_tokens=200,
    )
    try:
        data = json.loads(raw)
        return int(data.get("score", 0)), str(data.get("reason", ""))[:120]
    except Exception:  # noqa: BLE001
        match = re.search(r'"score"\s*:\s*([0-2])', raw)
        if match:
            return int(match.group(1)), "正则提取分数"
        match = re.search(r"\b([0-2])\b", raw)
        if match:
            return int(match.group(1)), "正则提取数字"
        return None, "评分解析失败"


def keyword_score(task, answer):
    text = answer or ""
    points = task.get("key_points", [])
    if not points:
        return 0
    hits = sum(1 for group in points if any(k in text for k in group))
    if hits == len(points) or (len(points) >= 4 and hits >= len(points) - 1):
        return 2
    if hits >= max(1, len(points) // 2):
        return 1
    return 0


def subpoint_hit(text, sp):
    if "requires" in sp:
        return all(any(alt in text for alt in group) for group in sp["requires"])
    return any(k in text for k in sp.get("keywords", []))


def fine_score(task, answer):
    subs = task.get("subpoints")
    if not subs:
        return keyword_score(task, answer)
    text = answer or ""
    return sum(float(sp["weight"]) for sp in subs if subpoint_hit(text, sp))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="")
    parser.add_argument("--outdir", default="results/noweb_all/open_probe6")
    parser.add_argument("--questions", default="data/questions_open_probe.json")
    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="保留输出目录中未被本次 --models 重跑的模型结果",
    )
    args = parser.parse_args()

    with io.open(args.questions, encoding="utf-8") as f:
        qdata = json.load(f)
    tasks = qdata["questions"]

    selected = PAPER_MODELS
    if args.models:
        wanted = {x.strip() for x in args.models.split(",") if x.strip()}
        selected = [p for p in PAPER_MODELS if p["key"] in wanted]

    rows = []
    for idx, preset in enumerate(selected, 1):
        key = os.environ.get(preset["env"], "") if preset["env"] else ""
        if preset["env"] and not key:
            print(f"[{idx}/{len(selected)}] 跳过 {preset['label']}：未配置 {preset['env']}")
            continue
        print(f"[{idx}/{len(selected)}] {preset['label']}")
        client = build_client(resolve_base_url(preset), key or "ollama")
        for task in tasks:
            try:
                answer = ask_model(preset, client, task["question"])
            except Exception as exc:  # noqa: BLE001
                answer = ""
                print(f"  ! {task['id']} 作答失败：{type(exc).__name__}")
            keyword_score = fine_score(task, answer)
            max_score = task.get("max_score", 2)
            rows.append(
                {
                    "model": preset["label"],
                    "id": task["id"],
                    "dimension": task["dimension"],
                    "keyword_score": keyword_score,
                    "keyword_max_score": max_score,
                    "keyword_reason": "关键词子评分点预筛，非正式评分",
                    "answer": answer,
                }
            )
            print(f"  {task['id']}: {keyword_score}/{max_score}（关键词预筛）")

    os.makedirs(args.outdir, exist_ok=True)
    details_path = os.path.join(args.outdir, "open_details.csv")
    new_df = pd.DataFrame(rows)
    if args.merge_existing and os.path.exists(details_path):
        old_df = pd.read_csv(details_path)
        rerun_labels = {p["label"] for p in selected}
        old_df = old_df[~old_df["model"].isin(rerun_labels)]
        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df

    if df.empty:
        raise SystemExit("没有成功运行的模型，未覆盖现有开放题结果。")

    df.to_csv(details_path, index=False, encoding="utf-8-sig")

    valid = df.dropna(subset=["keyword_score"]).copy()
    summary = (
        valid.groupby("model")
        .agg(
            keyword_score=("keyword_score", "sum"),
            keyword_max_score=("keyword_max_score", "sum"),
        )
        .reset_index()
    )
    summary["keyword_percent"] = (
        summary["keyword_score"] / summary["keyword_max_score"]
    )
    summary = summary.sort_values("keyword_percent", ascending=False)
    summary.to_csv(
        os.path.join(args.outdir, "open_summary_keyword.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    print("\n关键词预筛分（非正式，必须再用独立裁判复核）：")
    for _, r in summary.iterrows():
        print(
            f"  {r['model']:24s} {r['keyword_percent']:.0%}  "
            f"({r['keyword_score']:.1f}/{r['keyword_max_score']:.1f})"
        )


if __name__ == "__main__":
    main()
