"""Structural audit for the de-duplicated ChAAt question bank."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUESTIONS = ROOT / "data" / "questions_final_hard50_core_shuffled.json"
OUT = ROOT / "docs" / "KEY_AUDIT.json"


def main():
    payload = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    questions = payload["questions"]
    dimensions = set(payload["meta"]["dimensions"])
    issues = []
    ids = [question["id"] for question in questions]
    if len(ids) != len(set(ids)):
        issues.append({"scope": "bank", "issue": "duplicate item ids"})

    answer_distribution = Counter()
    for question in questions:
        item = question["id"]
        options = {}
        for raw in question["options"]:
            letter, text = raw.split(".", 1)
            options[letter.strip()] = text.strip()
        if len(options) != len(question["options"]):
            issues.append({"scope": item, "issue": "duplicate option letters"})
        if len(set(options.values())) != len(options):
            issues.append({"scope": item, "issue": "duplicate option text"})
        if question["dimension"] not in dimensions:
            issues.append({"scope": item, "issue": "unknown dimension"})
        if not question.get("source_ref", "").startswith("http"):
            issues.append({"scope": item, "issue": "missing or invalid source_ref"})
        if not question.get("explanation", "").strip():
            issues.append({"scope": item, "issue": "missing explanation"})

        answer = question["answer"].strip()
        if any(letter not in options for letter in answer):
            issues.append({"scope": item, "issue": "answer letter outside options"})
        answer_distribution[answer] += 1
        accepted = question.get("accepted", [])
        if question["type"] == "multiple_select":
            if len(accepted) != 1 or accepted[0].strip() != answer:
                issues.append({"scope": item, "issue": "accepted multiple-select key mismatch"})
        elif question["type"] == "multiple_choice":
            expected_text = options.get(answer)
            if not accepted or accepted[0].strip() != expected_text:
                issues.append({"scope": item, "issue": "accepted single-choice key mismatch"})
        else:
            issues.append({"scope": item, "issue": "unsupported question type"})

    report = {
        "path": str(QUESTIONS.relative_to(ROOT)),
        "questions": len(questions),
        "dimension_counts": dict(Counter(q["dimension"] for q in questions)),
        "answer_distribution": dict(sorted(answer_distribution.items())),
        "structural_issues": issues,
        "passed": not issues,
        "manual_semantic_checks": [
            {
                "id": "RX-06",
                "result": "fixed explanation and source remapping; key B retained",
            },
            {
                "id": "RX-17",
                "result": "source remapping corrected; key C retained",
            },
            {
                "id": "RX-19",
                "result": "explanation corrected; key D retained",
            },
        ],
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
