# Paraphrase Robustness Probe

Date: 2026-11-26

## Design

Ten discriminating source items were rewritten while preserving their answer
targets and semantic distinctions. The six main models each answered each
paraphrase once at temperature 0 with tools and web search disabled.

This is an exploratory wording-robustness probe. It is not part of the main
leaderboard and is not a definitive contamination test.

## Matched results

| Model | Original 10-item subset | Paraphrase 10 | Delta |
| --- | ---: | ---: | ---: |
| DeepSeek Flash | 100% | 100% | 0 |
| GPT-5.4 | 70% | 100% | +30 |
| Qwen Max | 80% | 90% | +10 |
| GLM-4 Plus | 83% | 80% | -3 |
| Ollama Qwen3.5 4B | 50% | 90% | +40 |
| GPT-4o mini | 37% | 60% | +23 |

Six-model Spearman rank correlation: `rho=0.471`, `p=0.346`.

## Interpretation boundary

The outcome does not show a systematic collapse under paraphrase, but several
rewrites are easier than the originals. The sample is too small to support a
contamination-resistance claim. The probe should be reported as exploratory.
