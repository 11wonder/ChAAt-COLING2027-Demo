# Figure QA Notes

## Export contract

- Target: COLING 2027 System Demonstrations, full text width.
- Final width: 160 mm, matching the official COLING A4, 2.5 cm-margin text block.
- Formats: editable SVG, PDF, and 400-dpi PNG preview.
- Typography: Arial-compatible sans serif; measured PDF text from 5.59 to 6.80 pt.

The schematic auditor's only warning is that 160 mm is not one of the
Nature-family default widths (89 or 183 mm). This is an intentional journal
contract for the 160 mm COLING text block, not an uncontrolled rescale.

## Figure 1

- Role: explain why the system is an auditable diagnostic workflow.
- Content: source-audited data tiers, controlled model runner, scoring and
  audit, and the failure-localization review layer.
- Accent: coral marks only the new review contribution and the source-trace
  return path.
- SVG audit: PASS WITH WARNINGS (intentional 160 mm COLING width only).
- PDF text audit: PASS; minimum text 5.595 pt.
- Collision audit: PASS; 0 failures and 0 warnings.

## Figure 2

- Role: demonstrate that the interface can locate a concrete failure.
- Hero evidence: unretouched local UI capture of GPT-4o mini, Idiom, and
  expanded item FN-E8-03.
- Image treatment: crop only; no local retouching or simulated values.
- SVG audit: PASS WITH WARNINGS (intentional 160 mm COLING width only).
- PDF text audit: PASS; minimum vector text 5.693 pt.
- Collision audit: PASS; 0 failures and 0 warnings.
- The UI capture remains a raster inset; its meaning is independently stated in
  vector labels at the top so critical information does not depend on tiny
  screenshot text.

## Panel alignment

The alignment gate is not applicable: neither figure is a multi-panel
quantitative grid. Figure 1 is a schematic; Figure 2 contains one UI evidence
plate and a process strip rather than comparable plot areas.
