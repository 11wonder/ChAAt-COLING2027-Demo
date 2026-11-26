# Figure Brief

## Figure 1 — System architecture

- Core conclusion: ChAAt preserves one auditable path from source-verified data
  to a scored model failure and its human-readable explanation.
- Results-level question: Why is ChAAt a diagnostic system rather than a
  benchmark leaderboard?
- Archetype: schematic-led composite.
- Destination: main paper, full text width.
- Final size: 160 mm × 84 mm; live typography at 6–7 pt.
- Main path: data tiers -> model runner -> scoring/audit -> diagnostic review.
- Secondary path: the review layer returns through an explicit source trace to
  the original item and provenance.
- New contribution: the review layer is the only coral-accented component.
- Existing components: three data tiers, model runner, scoring and audit.
- Controls/robustness: tool/web access is disabled; key audit and multi-rater
  review are separate from score calculation.
- Caption draft: System architecture. Source-audited items feed a controlled
  model runner and scoring layer; diagnostic views retain a trace back to each
  item instead of reporting only an aggregate score.

## Figure 2 — Failure-localization evidence

- Core conclusion: the interface connects an aggregate capability gap to the
  exact item, model output, and source-grounded explanation.
- Results-level question: Does the system actually support failure localization?
- Archetype: image-plate + vector annotation.
- Destination: main paper, full text width.
- Final size: 160 mm × 112 mm; screenshot labels are supplemented by ≥6 pt
  vector labels so meaning does not depend on tiny UI text.
- Hero evidence: one real Failure Explorer capture with GPT-4o mini, Idiom, and
  FN-E8-03 expanded.
- Reading path: select model and dimension -> open a failed item -> compare
  expected/model answers and read the explanation.
- Image integrity: crop only; no local retouching of UI content.
- Caption draft: Failure localization in ChAAt. Selecting a model and dimension
  exposes an exact failed item, the expected and model answers, and the
  source-grounded explanation while preserving access to aggregate views.

## Assumptions

- The system labels and item content are taken from the current local demo.
- FN-E8-03 remains the demonstration failure case.
- The screenshot contains no credentials, private paths, or browser chrome.
- The 41-item tier contains exam-style items drawn mostly from public mock
  exams and exam-preparation material; it is not described as official exams.
