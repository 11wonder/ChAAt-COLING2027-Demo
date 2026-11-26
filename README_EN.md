# ChAAt

ChAAt is an auditable demonstration system for diagnosing Chinese-internal
linguistic gaps in large language models. It connects aggregate
model-by-dimension scores to source-verified items, expected answers, model
outputs, and explanations.

This repository accompanies the COLING 2027 System Demonstrations submission
*ChAAt: A Chinese-specific Ability Atlas for Probing Linguistic Diversity in
Large Language Models*.

- Paper: `paper/main_submission_final.pdf`
- LaTeX source: `paper/main.tex`
- External-validation plan: `docs/EXTERNAL_VALIDATION_PLAN.md`

## Demonstration

```powershell
pip install -r requirements.txt
streamlit run app_demo.py
```

The review demo loads bundled, precomputed results. It requires no API key and
does not access the network.

## Evaluation tiers

- 50-item de-duplicated diagnostic core
- 41 real-school-exam validity items
- 6 open-ended production tasks

The core covers idiom, classical Chinese, dialect, internet slang, and
pragmatics. Six models are evaluated three times at temperature zero with
external search disabled.

| Model | Overall |
| --- | ---: |
| DeepSeek Flash | 100% |
| GPT-5.4 | 92% |
| Qwen Max | 82% |
| GLM-4 Plus | 77% |
| Ollama Qwen3.5 4B | 66% |
| GPT-4o mini | 31% |

## Reproduce

```powershell
python run_paper_experiment.py `
  --questions data/questions_final_hard50_core_shuffled.json `
  --models deepseek,qwen,glm,gpt4omini,gpt5,ollama `
  --repeats 3 `
  --outdir results/noweb_all/core50

python make_paper_table.py
python make_paper_figures.py
python compute_bootstrap_ci.py
python compute_pairwise_tests.py
python audit_question_bank.py
```

Exploratory probes:

```powershell
python run_paper_experiment.py `
  --questions data/questions_robustness_paraphrase10.json `
  --models deepseek,qwen,glm,gpt4omini,gpt5,ollama `
  --repeats 1 `
  --outdir results/noweb_all/core50_paraphrase10

python run_open_probe.py `
  --questions data/questions_robustness_open5.json `
  --models deepseek,qwen,glm,gpt4omini,gpt5,ollama `
  --outdir results/noweb_all/core50_open5
```

## Licensing

Software is released under the MIT License. ChAAt-authored diagnostic items are
released under CC BY 4.0. Third-party examination excerpts are not
redistributed. See `LICENSE` and `DATA_LICENSE.md`.

## Positioning

ChAAt is a compact diagnostic instrument, not a replacement for large-scale
benchmarks such as RegioZH, CHENGYU-BENCH, YUE-PUB, C-Eval, CMMLU, or SuperCLUE.
The external-validation and licensing plan is documented in
`docs/EXTERNAL_VALIDATION_PLAN.md`.
