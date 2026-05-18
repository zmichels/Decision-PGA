# Decision-PGA Document Extraction Scenarios

This scenario backlog is separate from the broader application-gap suite.

Run it with:

```bash
decision-pga evaluate --suite document-extraction --output reports/document-extraction-latest
```

The command writes `document_extraction_metrics.json`,
`document_extraction_summary.csv`, `document_extraction_gap_matrix.csv`,
`document_extraction_report.md`, and
`decision-pga-document-extraction-gap-review.pdf`.

## Selected Deep Dives

### 1. Field-Value Candidate Extraction

Use candidate extracted values as labels. Feed repeated extraction attempts,
provider scores, or parser confidence maps into Decision-PGA.

Why it is compelling:

- It is the simplest bridge from document extraction to probability clouds.
- It can support accept, targeted review, gather context, rerun, and escalation
  actions.
- It makes "uncertain extraction" more specific than a confidence threshold.

What to test:

- Can PGA separate two-value disputes from diffuse extraction failure at
  comparable entropy?
- Does shape-aware routing reduce unnecessary manual review?
- Does it catch field-specific regressions after prompt, model, OCR, or schema
  changes?

### 2. Table And Line-Item Extraction

Use candidate rows, item groups, or row-value assignments as labels.

Why it is compelling:

- Values can be correct while the row association is wrong.
- Line-item extraction is a practical benchmarked problem.
- Structured ambiguity is exactly where scalar confidence tends to flatten the
  story.

What to test:

- Can PGA identify one dominant row-conflict axis versus broad table failure?
- Does it improve review routing over row confidence and table F1 alone?
- Can report artifacts make line-item uncertainty readable without opening a
  notebook?

### 3. OCR/Layout Sensitivity

Use the same field-value labels across ingestion variants: OCR settings,
layout parser settings, chunking policies, or reading-order variants.

Why it is compelling:

- Bad ingestion often masquerades as model hallucination.
- Geodesic drift across variants can flag pipeline sensitivity.
- It could guide whether to rerun OCR/layout or change the extraction prompt.

What to test:

- Does half-window or variant-to-variant drift detect controlled ingestion
  perturbations?
- Does the diagnostic distinguish ingestion sensitivity from value ambiguity?
- Does it produce clearer review actions than extractor confidence alone?

## Full Backlog

| Gap family | Use case | Current failure mode | Decision-PGA contribution | Baseline comparison | Difficulty | Recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| Field-value ambiguity | Candidate field extraction | One value is accepted despite plausible alternatives. | Shape-aware value ambiguity diagnostics. | Confidence, entropy, margin, agreement. | Medium | Build field-value fixtures. |
| Span/source localization | Provenance audit | Value may be right but source is unstable. | Candidate-source dispersion diagnostics. | OCR confidence, box overlap, retrieval score. | High | Define span/source candidate labels. |
| Table/line-item extraction | Row and item assignment | Correct values are attached to wrong rows or items. | Row-assignment uncertainty shape. | Table F1, row confidence, agreement. | High | Build compact line-item fixtures. |
| Cross-page entity linking | Long-document repeated fields | Repeated mentions blur scope and ownership. | Entity-link candidate dispersion. | Mention confidence, retrieval rank. | High | Defer until span conventions exist. |
| OCR/layout noise | Pipeline triage | Ingestion errors look like LLM errors. | Drift across ingestion variants. | OCR confidence, parser warnings, agreement. | Medium | Add controlled OCR/layout perturbations. |
| Conflicting values and versions | Document-set extraction | Revisions and attachments disagree. | Value/source/version conflict geometry. | Recency, retrieval rank, entropy. | High | Prototype source/version grouping. |
| Human review triage | Review queue routing | Thresholds do not explain reviewer action. | Action-oriented extraction states. | Confidence thresholds, agreement. | Medium | Map field fixtures to review actions. |
| Extraction monitoring | Regression checks | Aggregate metrics hide failure-shape drift. | State regression reports. | F1, exact match, confidence. | Low | Add expected-state fixtures to CI. |
