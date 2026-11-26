# ChAAt Final Core Results

Date: 2026-11-26

## Protocol

- Dataset: `data/questions_final_hard50_core_shuffled.json`
- Items: 50 (idiom 13, classical 15, dialect 9, slang 8,
  pragmatics/pronunciation 5)
- Models: six
- Repetitions: three at temperature 0
- Calls: 900
- Empty responses: 0
- Tool access: disabled
- External search: disabled
- Answer positions: deterministically balanced with seed `20261125`

## Overall results

| Model | Accuracy | Item-bootstrap 95% interval |
| --- | ---: | ---: |
| DeepSeek Flash | 100.0% | saturated at 100% |
| GPT-5.4 | 92.0% | 84.0–98.0% |
| Qwen Max | 82.0% | 71.3–91.3% |
| GLM-4 Plus | 77.3% | 65.3–88.0% |
| Ollama Qwen3.5 4B | 66.0% | 52.0–78.0% |
| GPT-4o mini | 31.3% | 19.3–44.0% |

The intervals use 10,000 item-cluster bootstrap resamples with seed
`20261126`; see `bootstrap_ci.csv`.

## Matched small-model control

GPT-5.4 mini scores 88.7% versus 92.0% for GPT-5.4. The models tie on 43
items; GPT-5.4 mini wins two and GPT-5.4 wins five.

## Item discrimination

For each item, $D$ is the mean accuracy of the top two models minus the mean
accuracy of the bottom two models, ranked by overall accuracy. Twelve items
reach $D=1.00$: six classical, three Cantonese, two idiom, and one pronunciation
item. Their pass rates range from 33% to 67%. The full calculation is in
`item_calibration.csv`.

## Interpretation boundary

This is a compact diagnostic probe. It does not estimate population-level
Chinese competence, and the leaderboard should not be generalized to other
checkpoints or model families.
