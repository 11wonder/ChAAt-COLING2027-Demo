# Submission Consistency Fixes

Date: 2026-11-26

## Statistical definitions

- Discrimination is now defined consistently as the mean accuracy of the top
  two models minus the mean accuracy of the bottom two models, after ranking the
  six models by overall accuracy.
- The recomputed result is `D=1.00` on 12 items, not `D=0.67` on seven items.
  The 12 items comprise six classical, three Cantonese, two idiom, and one
  pronunciation item. Their pass rates range from 33% to 67%.
- The statistical-reporting paragraph now states that comparisons are
  descriptive plus one exact paired McNemar test for the closest pair.

## Sampling and construct labels

- The 41-item tier is described as **exam-style items**, mostly drawn from
  public mock exams and exam-preparation material. The paper no longer claims
  official-exam authority.
- The `pragmatics` display label is **Pragmatics & pronunciation**. The paper
  states that the five items comprise two pronunciation, one ambiguity, and two
  honorific items.
- The limitations now explicitly note possible pretraining contamination and
  classify the paraphrase and option-free probes as exploratory.

## Figures, UI, and video sources

- Figure 1 now says `41 exam-style items / mostly mock exams` and
  `multi-rater review`.
- Figure 2's caption explains that GPT-4o mini selected B, "a long time ago",
  while the key is E, "not long ago".
- The heatmap and radar use the display label `Pragmatics & Pronunciation`.
- The Demo Mode and refreshed screenshots use the corrected tier, dimension,
  and rater language.
- Demo narration, captions, and motion text sources use the corrected wording.
  The existing MP4 is marked stale and must be regenerated before submission.

## Paper layout and availability

- The main results table is now a single-column table and appears on page 3,
  next to the Results section rather than on page 5.
- The availability statement says that a credential-free review demo is
  included and that the public repository and hosted demo will be released
  upon acceptance.

## Licensing

- `DATA_LICENSE.md` now identifies `RX-06`, `RX-17`, and `RX-19` as
  exam-preparation-derived core items explicitly excluded from CC BY 4.0.
- The paper states the same three-item exception and does not describe the
  complete 50-item core as uniformly CC BY 4.0.
