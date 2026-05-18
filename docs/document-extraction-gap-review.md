# Decision-PGA Document Extraction Gap Review

This is a separate review from the broader application-gap bridge. It focuses
on data extraction from documents and treats "DU" as available for decision
uncertainty, while using the clearer term "document extraction" for the
document side.

Decision-PGA is not a document understanding model. It may become useful when
document extraction systems can expose candidate values, spans, table rows,
source snippets, versions, or review actions as probability clouds.

## Gap Matrix

| Gap family | Current tooling limit | Decision-PGA fit | Missing adapter | Evaluation route |
| --- | --- | --- | --- | --- |
| Field-value ambiguity | Single confidence scores do not explain whether uncertainty is a two-value dispute or broad extraction failure. | Promising; values and alternates can be categorical candidates. | Candidate field-value extraction records with probabilities or repeated samples. | Compare PGA against confidence, entropy, margin, and extraction agreement. |
| Span/source localization | A value can be correct while source provenance is unstable. | Needs adapter; spans or boxes must become candidate labels. | Span/source candidate normalization. | Compare with OCR confidence, bounding-box overlap, and retrieval scores. |
| Table/line-item extraction | Correct values can be assigned to the wrong row, item, or group. | Promising; row and item assignments are structured candidates. | Row/column/item candidate adapter. | Compare with table F1, row confidence, and assignment agreement. |
| Cross-page entity linking | Repeated fields and entity mentions create long-document ambiguity. | Needs adapter; entity mentions must be aligned across pages. | Entity-link candidate identity schema. | Compare with mention confidence and agreement across extraction passes. |
| OCR/layout noise | Bad ingestion can be mistaken for LLM hallucination or weak reasoning. | Promising; compare extraction clouds across ingestion variants. | OCR/layout variant fixture generation. | Compare with OCR confidence, parser warnings, and extraction agreement. |
| Conflicting values and versions | Stale documents, attachments, and revisions can disagree. | Needs adapter; source/version metadata must be explicit. | Candidate value plus source/version grouping. | Compare with recency heuristics, retrieval rank, entropy, and margin. |
| Human review triage | Low-confidence thresholds create broad review queues without action guidance. | Promising; uncertainty shape can map to different review actions. | Review action labels and outcome fixtures. | Compare reviewer effort and accept/reject quality against confidence thresholds. |
| Extraction monitoring | Aggregate F1 or exact match can hide changing failure shapes. | Promising after fixtures exist; deterministic reports fit CI. | Expected diagnostic states for extraction fixtures. | Track state regressions across model, prompt, OCR, and schema changes. |

## Practical Readout

Start with two tracks:

1. Field-value candidate extraction, because it maps directly onto current
   Decision-PGA probability-cloud and provider-score inputs.
2. Table and line-item extraction, because row/item association is a concrete
   document-extraction problem where scalar confidence can be misleading.

Span/source localization, cross-page linking, and version conflicts are
important, but they need careful candidate-label adapters before PGA metrics
are meaningful.

## Conservative Limits

- Decision-PGA does not OCR documents.
- Decision-PGA does not parse layout.
- Decision-PGA does not know which extracted value is correct without
  candidate labels and evaluation fixtures.
- Decision-PGA can only diagnose the uncertainty shape of inputs it is given.
- The document-extraction suite is a structured review, not a live extraction
  benchmark.

## Suggested Next Slice

Add a field-value candidate fixture suite:

- labels: candidate extracted values for a schema field;
- optional metadata: source spans, page numbers, OCR confidence, extraction
  pass, model/provider;
- baselines: confidence, entropy, top-1 margin, agreement, exact match;
- outputs: state routing for accept, targeted review, gather context, rerun
  OCR/layout, or escalate.
