# Tester Feedback Template

## Install And Run

- Did setup work from `docs/tester-guide.md`?
- What command failed first, if any?
- Was any dependency or Python-version step unclear?

## Method Clarity

- What did you think Decision-PGA is measuring?
- Which terms were unclear: Fisher-Rao, square-root geometry, PC1 fraction,
  anisotropy, margin, regime shift?
- Did the generated `advantage_report.md` make an honest claim?

## Diagnostic Usefulness

- Which state felt useful: `stable`, `binary_ambiguity`,
  `diffuse_uncertainty`, `boundary_sensitive`, `regime_shift`?
- Which state felt vague or redundant?
- Did the recommended action match what you would want an agent to do?

## PGA vs Simpler Baselines

- Where did entropy or margin seem sufficient?
- Where did PGA add interpretive value?
- Where did PGA look redundant, noisy, or overfit to synthetic examples?

## Tooling

- Was JSON input/output understandable enough to wrap from another tool?
- Would a local MCP server be useful in your workflow?
- What example payload should be added next?
