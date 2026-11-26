# -*- coding: utf-8 -*-
"""评分器：客观题精确匹配 + 生成题 LLM-as-judge。

本文件不依赖 Streamlit，便于单独测试与复现。
"""

import json
import re


def normalize(text):
    """去掉标点与空白，只保留中文、字母、数字，便于容错比较。"""
    if text is None:
        return ""
    t = str(text).strip().lower()
    return re.sub(r"[^\u3400-\u9fffa-zA-Z0-9]", "", t)


def option_letter(text):
    """从模型输出中提取 A-H 选项字母（单选）。"""
    up = (text or "").upper()
    explicit = re.search(
        r"(?:答案|正确选项|ANSWER|OPTION)\s*(?:是|为|:|：)?\s*([A-H])", up
    )
    if explicit:
        return explicit.group(1)
    found = re.findall(r"(?:^|[^A-Z])([A-H])(?:[^A-Z]|$)", up)
    return found[-1] if found else None


def correct_option_text(q):
    """返回正确答案对应的选项正文（去掉“A.”前缀）。"""
    letter = (q.get("answer") or "").upper()
    for opt in q.get("options", []):
        m = re.match(r"^\s*([A-H])\s*[\.、．:：]\s*(.*)$", opt)
        if m and m.group(1).upper() == letter:
            return m.group(2).strip()
    return ""


def grade_multiple_choice(output, q):
    letter = option_letter(output)
    answer = (q.get("answer") or "").upper()
    if letter:
        return letter == answer, letter
    correct_text = correct_option_text(q)
    if correct_text and normalize(correct_text) in normalize(output):
        return True, "文本匹配"
    return False, (output or "").strip()[:50]


def grade_fill_blank(output, q):
    out_norm = normalize(output)
    accepted = q.get("accepted") or [q.get("answer", "")]
    for acc in accepted:
        if normalize(acc) in out_norm:
            return True, acc
    return False, (output or "").strip()[:50]


def option_letters(text):
    """提取多选答案中的全部选项字母。"""
    up = (text or "").upper().strip()
    if re.fullmatch(r"[A-H\s,，、/和与]+", up):
        return re.findall(r"[A-H]", up)
    explicit = re.search(
        r"(?:答案|正确选项|ANSWER|OPTION)\s*(?:是|为|:|：)?\s*"
        r"([A-H](?:\s*[,，、/和与]?\s*[A-H])*)",
        up,
    )
    if explicit:
        return re.findall(r"[A-H]", explicit.group(1))
    return re.findall(r"(?:^|[^A-Z])([A-H])(?:[^A-Z]|$)", up)


def grade_multiple_select(output, q):
    answer = set((q.get("answer") or "").upper())
    got = set(option_letters(output))
    return got == answer, "".join(sorted(got))


JUDGE_PROMPT = (
    "你是一名严格的中文能力评测裁判。请判断模型对下面题目的回答是否正确。\n"
    "题目：{question}\n参考答案：{reference}\n模型回答：{answer}\n"
    '只输出 JSON：{{"correct": true 或 false, "reason": "一句话理由"}}'
)


def grade_generation(output, q, judge=None):
    if judge is None:
        return False, "未配置裁判模型"
    reference = q.get("answer") or (q.get("accepted") or [""])[0]
    prompt = JUDGE_PROMPT.format(
        question=q.get("question", ""), reference=reference, answer=output
    )
    try:
        raw = judge(prompt)
        data = json.loads(raw)
        return bool(data.get("correct")), str(data.get("reason", raw))[:80]
    except Exception as exc:  # noqa: BLE001
        return False, f"裁判解析失败：{exc}"


def grade_question(output, q, judge=None):
    t = q.get("type", "multiple_choice")
    if t == "fill_blank":
        return grade_fill_blank(output, q)
    if t == "multiple_select":
        return grade_multiple_select(output, q)
    if t == "generation":
        return grade_generation(output, q, judge=judge)
    return grade_multiple_choice(output, q)


def summarize(rows):
    """按维度聚合，返回 {dimension: {accuracy, total, correct}}。"""
    dims = {}
    for r in rows:
        d = dims.setdefault(r["dimension"], {"total": 0, "correct": 0})
        d["total"] += 1
        if r["correct"]:
            d["correct"] += 1
    out = {}
    for k, v in dims.items():
        out[k] = {
            "accuracy": v["correct"] / v["total"] if v["total"] else 0.0,
            "total": v["total"],
            "correct": v["correct"],
        }
    return out
