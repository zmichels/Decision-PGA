# Evaluation Harness

Decision-PGA includes a deterministic synthetic benchmark for checking whether
PGA geometry adds signal beyond entropy, margins, and simple drift metrics.

Run the default checked-in benchmark:

```bash
decision-pga evaluate --config examples/evaluation_config.json --output reports/latest
```

The explicit suite name for this behavior is `benchmark`:

```bash
decision-pga evaluate --suite benchmark --config examples/evaluation_config.json --output reports/latest
```

The command writes:

- `metrics.json`: complete machine-readable report.
- `summary.csv`: one row per scenario.
- `confusion_matrix.csv`: expected vs PGA-predicted states.
- `advantage_report.md`: concise human-readable interpretation.
- `separability.png`, `confusion_matrix.png`, `pga_vs_baseline_deltas.png`.

The conservative advantage claim is intentionally modest. PGA is treated as
useful only when it improves separability or state classification over
entropy/margin baselines on held-out deterministic fixtures. If it does not,
the generated report says so.

No benchmark scenario calls a model API. The fixture set is synthetic-first so
that class count, sample count, ambiguity, diffusion, and regime-shift behavior
can be tested without provider variance.

## Application Gap Suite

The application suite is a structured use-case review rather than a synthetic
performance benchmark:

```bash
decision-pga evaluate --suite application --output reports/application-latest
```

It writes:

- `application_metrics.json`: complete machine-readable application review.
- `application_summary.csv`: one row per application scenario.
- `gap_matrix.csv`: compact gap matrix for testers and planning.
- `application_report.md`: conservative human-readable interpretation.
- `decision-pga-gap-review.pdf`: generated article-style PDF.

Use `--suite all` to write both benchmark and application artifacts to one
output directory:

```bash
decision-pga evaluate --suite all --config examples/evaluation_config.json --output reports/all-latest
```

## Document Extraction Gap Suite

The document-extraction suite is separate from the broader application suite.
It focuses on data extraction from documents: candidate field values, source
spans, table rows, line items, OCR/layout variants, version conflicts, review
triage, and monitoring.

```bash
decision-pga evaluate --suite document-extraction --output reports/document-extraction-latest
```

It writes:

- `document_extraction_metrics.json`: complete machine-readable extraction review.
- `document_extraction_summary.csv`: one row per extraction scenario.
- `document_extraction_gap_matrix.csv`: compact gap matrix for planning.
- `document_extraction_report.md`: conservative human-readable interpretation.
- `decision-pga-document-extraction-gap-review.pdf`: generated article-style PDF.

`--suite all` now writes benchmark, application, and document-extraction
artifacts together.
