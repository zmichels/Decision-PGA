# Decision-PGA and the Extraction Confidence Gap in Document AI

Document AI is often discussed as document understanding: reading pages,
tables, forms, contracts, reports, and scanned records well enough to answer
questions or fill a schema. But production extraction work usually fails at a
more specific layer. A system does not merely need to know what a document is
"about." It needs to decide which value, span, row, source, page, entity, or
version should populate a downstream record.

Document extraction is not just document understanding. It is a sequence of
small, auditable decisions under noisy OCR, layout ambiguity, repeated fields,
tables, cross-page references, and schema constraints. That makes it a natural
neighbor for Decision-PGA, provided we are precise about the boundary:
Decision-PGA is not a document parser, OCR engine, or extraction model. It is a
candidate-cloud diagnostic layer that may help decide whether an extraction is
stable enough to accept, ambiguous enough to review, diffuse enough to rerun,
or unstable enough to reprocess.

## Why extraction confidence needs shape

Most extraction systems already have confidence scores, agreement checks, or
human-review thresholds. Those tools are necessary, but they can collapse very
different failure modes into the same "low confidence" bucket:

- Two plausible invoice totals.
- A correct value with unstable source span.
- A table cell attached to the wrong line item.
- A field repeated across pages with different scopes.
- OCR corruption that changes the extracted value across ingestion variants.
- Conflicting values in old and new versions of a document.

These cases should not trigger the same next action. A clean two-value dispute
calls for targeted review. A broken table calls for structure inspection. OCR
sensitivity calls for reprocessing. A version conflict calls for source and
recency review. Decision-PGA's potential contribution is to report the geometry
of candidate extraction clouds, not to replace the extraction model itself.

## What document AI already does well

Document AI has strong benchmarks and model families. DocILE focuses on
Document Information Localization and Extraction and includes line-item
recognition, fine-grained labels, real and synthetic business documents, and
layout-diverse test cases: https://arxiv.org/abs/2302.05658. Kleister targets
key information extraction in long, complex formal documents such as NDAs and
charity reports: https://arxiv.org/abs/2105.05796. DUE groups visual question
answering, key information extraction, and machine reading comprehension across
rich document layouts:
https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/069059b7ef840f0c74a814ec9237b6ec-Abstract-round2.html.

DUDE pushes toward practical multi-page, multi-domain visually rich document
evaluation: https://arxiv.org/abs/2305.08455. LayoutLMv3 shows the importance
of unified text, image, and layout modeling in Document AI:
https://arxiv.org/abs/2204.08387. DocVQA highlights that models struggle
especially when document structure is crucial:
https://arxiv.org/abs/2007.00398. LLM information-extraction surveys show how
generative models now participate in structured extraction workflows:
https://arxiv.org/abs/2312.17617.

The gap is not that the field lacks extraction models. The gap is that
extraction pipelines still need readable, local, action-oriented diagnostics
for the uncertainty states that happen between raw document processing and
final schema acceptance.

## Where extraction tools still leave gaps

Several failure families matter:

- Field-value ambiguity. A model may output one value while the document offers
  two plausible candidates.
- Span or source localization. The value may be right, but its source may be
  unstable or unauditable.
- Table and line-item extraction. Values can be read correctly but assigned to
  the wrong row, item, column, or group.
- Cross-page entity linking. Repeated mentions can blur whether a value belongs
  to the right party, account, clause, item, or period.
- OCR and layout noise. Bad text extraction or reading order can look like
  model hallucination unless ingestion sensitivity is measured.
- Conflicting values and versions. Document sets often include revisions,
  attachments, historical forms, or stale records.
- Human review triage. A single low-confidence queue hides the actual reviewer
  action needed.
- Extraction monitoring. Aggregate exact match or F1 can hide shifts in the
  shape of extraction failures.

## What Decision-PGA contributes

Decision-PGA can analyze probability clouds over categorical alternatives.
For document extraction, those alternatives might be:

- candidate field values;
- candidate source spans or page regions;
- candidate table rows or line items;
- candidate entity links;
- candidate document versions or source groups;
- candidate review actions.

If an adapter can turn extraction outputs into those candidate clouds,
Decision-PGA can report total dispersion, PC1 fraction, anisotropy, margin, and
drift. Those metrics can distinguish a tight extraction from a two-candidate
ambiguity, a diffuse extraction failure, or a source-sensitive regime shift.

That is the useful alignment with decision uncertainty (DU): not every
document-extraction failure is equally uncertain, and not every uncertain
extraction needs the same decision.

## Early use-case map

The first document-extraction suite maps eight candidate gaps:

- Field-value candidate extraction: the best first deep dive because it maps
  cleanly to the current candidate-score interface.
- Span/source localization: important for auditability, but needs a stable
  span-candidate adapter.
- Table and line-item extraction: high practical value because row and item
  associations create structured ambiguity.
- Cross-page entity linking: important for long documents, but likely depends
  on field and span conventions first.
- OCR/layout noise: promising as a pipeline-triage diagnostic across ingestion
  variants.
- Conflicting values and versions: likely valuable, but needs source/version
  metadata.
- Human review triage: promising once field-value fixtures define review
  actions.
- Extraction monitoring: useful for CI after candidate-cloud fixtures exist.

The two strongest next tracks are field-value candidate extraction and table
or line-item extraction. Field-value fixtures prove the simplest bridge. Table
and line-item fixtures test whether PGA helps with a real document problem
that scalar confidence often flattens.

## What must be proven next

The evidence standard should stay conservative:

- Every report should include confidence, entropy, margin, and agreement
  baselines when available.
- PGA should be called useful only if it improves state separability or review
  routing over those baselines.
- Adapter-limited use cases should be labeled as such.
- The report should state plainly when PGA is redundant, weak, or
  inconclusive.

The next test should answer a narrow question: when multiple plausible field
values or line-item assignments exist, does Decision-PGA better route the
case to accept, targeted review, broader context gathering, OCR rerun, or
escalation?

## Development roadmap for document-extraction diagnostics

1. Build field-value candidate fixtures. Represent values, alternates, and
   source snippets as candidate labels with probabilities or repeated samples.
2. Compare against confidence, entropy, margin, exact-match agreement, and
   self-consistency baselines.
3. Add a table/line-item fixture where row assignments and item groupings are
   candidate labels.
4. Add an ingestion-variant fixture to test OCR/layout sensitivity.
5. Generate separate document-extraction reports with JSON, CSV, Markdown, and
   PDF artifacts.
6. Only after candidate-cloud fixtures work should the project add adapters for
   real OCR/layout/model providers.

Decision-PGA's opportunity in document extraction is small but sharp: it can
become a local diagnostic layer that helps document pipelines explain what kind
of extraction uncertainty they are seeing and what review action should happen
next.
