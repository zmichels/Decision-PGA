"""Document-extraction gap evaluation layer for Decision-PGA.

The suite is a deterministic review matrix, not a live document-understanding
benchmark. It keeps document extraction separate from the broader application
review while reusing the same conservative fit vocabulary.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal


FitLabel = Literal["promising", "redundant", "needs_adapter", "inconclusive"]

DOCUMENT_EXTRACTION_GAP_FAMILIES = (
    "field_value_ambiguity",
    "span_source_localization",
    "table_line_item_extraction",
    "cross_page_entity_linking",
    "ocr_layout_noise",
    "conflicting_values_and_versions",
    "human_review_triage",
    "extraction_monitoring",
)

DOCUMENT_EXTRACTION_GAP_MATRIX_FIELDS = (
    "gap_family",
    "use_case",
    "current_failure_mode",
    "decision_pga_contribution",
    "baseline_comparison",
    "implementation_difficulty",
    "fit_label",
    "recommended_next_step",
)


@dataclass(frozen=True)
class DocumentExtractionScenario:
    """One document-extraction gap and conservative Decision-PGA fit."""

    gap_family: str
    use_case: str
    touchstone: str
    expected_reading: str
    current_failure_mode: str
    decision_pga_contribution: str
    baseline_comparison: str
    baseline_reading: str
    pga_reading: str
    incremental_value: str
    implementation_difficulty: str
    fit_label: FitLabel
    recommended_next_step: str
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "gap_family": self.gap_family,
            "use_case": self.use_case,
            "touchstone": self.touchstone,
            "expected_reading": self.expected_reading,
            "current_failure_mode": self.current_failure_mode,
            "decision_pga_contribution": self.decision_pga_contribution,
            "baseline_comparison": self.baseline_comparison,
            "baseline_reading": self.baseline_reading,
            "pga_reading": self.pga_reading,
            "incremental_value": self.incremental_value,
            "implementation_difficulty": self.implementation_difficulty,
            "fit_label": self.fit_label,
            "recommended_next_step": self.recommended_next_step,
            "evidence": list(self.evidence),
        }

    def gap_matrix_row(self) -> dict[str, str]:
        payload = self.to_dict()
        return {
            field: str(payload[field])
            for field in DOCUMENT_EXTRACTION_GAP_MATRIX_FIELDS
        }


@dataclass(frozen=True)
class DocumentExtractionEvaluationReport:
    """A deterministic document-extraction gap review."""

    scenarios: tuple[DocumentExtractionScenario, ...]
    summary: dict[str, object]

    def scenario_by_gap(self, gap_family: str) -> DocumentExtractionScenario:
        for scenario in self.scenarios:
            if scenario.gap_family == gap_family:
                return scenario
        raise ValueError(f"unknown document-extraction gap family: {gap_family}")

    def gap_matrix_rows(self) -> list[dict[str, str]]:
        return [scenario.gap_matrix_row() for scenario in self.scenarios]

    def to_dict(self) -> dict[str, object]:
        return {
            "source": "document_extraction_evaluation",
            "summary": self.summary,
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "gap_matrix": self.gap_matrix_rows(),
        }


def run_document_extraction_evaluation_suite() -> DocumentExtractionEvaluationReport:
    """Return the deterministic document-extraction gap review suite."""

    scenarios = _document_extraction_scenarios()
    if tuple(scenario.gap_family for scenario in scenarios) != DOCUMENT_EXTRACTION_GAP_FAMILIES:
        raise ValueError("document extraction scenarios must match gap-family order.")

    fit_counts = Counter(scenario.fit_label for scenario in scenarios)
    promising = [
        scenario.gap_family
        for scenario in scenarios
        if scenario.fit_label == "promising"
    ]
    adapter_needed = [
        scenario.gap_family
        for scenario in scenarios
        if scenario.fit_label == "needs_adapter"
    ]
    summary: dict[str, object] = {
        "scenario_count": len(scenarios),
        "gap_families": list(DOCUMENT_EXTRACTION_GAP_FAMILIES),
        "fit_counts": dict(sorted(fit_counts.items())),
        "recommended_deep_dives": [
            {
                "direction": "field-value candidate extraction",
                "gap_family": "field_value_ambiguity",
                "why": "Candidate values and extraction confidence maps are the closest document-extraction analogue to current probability-cloud inputs.",
            },
            {
                "direction": "table and line-item extraction",
                "gap_family": "table_line_item_extraction",
                "why": "Line-item association is high-value and explicitly represented in modern document-extraction benchmarks, but needs row/column candidate adapters.",
            },
        ],
        "promising_gaps": promising,
        "adapter_needed_gaps": adapter_needed,
        "claim": (
            "Decision-PGA is most credible for document extraction when candidate "
            "values, spans, line items, or source snippets can be represented as "
            "probability clouds. It is not a parser; it is a diagnostic layer for "
            "extraction ambiguity, provenance uncertainty, and review routing."
        ),
    }
    return DocumentExtractionEvaluationReport(scenarios=scenarios, summary=summary)


def _document_extraction_scenarios() -> tuple[DocumentExtractionScenario, ...]:
    return (
        DocumentExtractionScenario(
            gap_family="field_value_ambiguity",
            use_case="field-value candidate extraction",
            touchstone="Can a diagnostic distinguish one reliable extracted value from two plausible competing values or many weak candidates?",
            expected_reading="A binary value conflict should trigger targeted review; diffuse candidates should trigger broader evidence gathering.",
            current_failure_mode="Document extraction pipelines often return a single field value even when nearby text, OCR alternatives, or repeated fields support multiple plausible values.",
            decision_pga_contribution="Measures whether candidate field values form a tight extraction, a two-value ambiguity, diffuse uncertainty, or a drift pattern across extraction attempts.",
            baseline_comparison="Compare against extractor confidence, entropy, top-1 margin, self-consistency agreement, and human-review thresholds.",
            baseline_reading="Confidence and margin can flag weak extraction, but often hide whether the uncertainty is a clean two-value dispute or broad extraction failure.",
            pga_reading="PC1 fraction and anisotropy can separate structured value ambiguity from diffuse field confusion when candidates are aligned.",
            incremental_value="Potentially gives extraction systems a more precise review action: accept, compare two candidates, gather page context, or abstain.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Deep-dive candidate: build field-value candidate fixtures and compare PGA against confidence, entropy, margin, and agreement baselines.",
            evidence=(
                "KIE benchmarks such as Kleister and DocILE expose practical field extraction problems with complex layouts.",
                "Current Decision-PGA provider-score adapters already accept candidate-aligned score maps.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="span_source_localization",
            use_case="source span and provenance localization",
            touchstone="Can a diagnostic tell whether an extracted value has one clear source or multiple plausible supporting spans?",
            expected_reading="A high-confidence value with unstable source spans should be treated differently from a value that is both correct and well localized.",
            current_failure_mode="Extraction models can output a correct value without stable provenance, making auditing and human review harder.",
            decision_pga_contribution="Could summarize probability clouds over candidate source spans, snippets, boxes, or page regions.",
            baseline_comparison="Compare against OCR confidence, bounding-box overlap, retrieval scores, and extractor confidence.",
            baseline_reading="Localization scores measure span confidence, but do not always expose structured ambiguity among multiple source locations.",
            pga_reading="PGA could distinguish one-source stability from source ambiguity if span candidates are normalized into labels.",
            incremental_value="Useful for audit-heavy extraction workflows, but needs a span-candidate adapter.",
            implementation_difficulty="high",
            fit_label="needs_adapter",
            recommended_next_step="Define a span/source candidate adapter that maps document boxes or snippets into stable probability labels.",
            evidence=(
                "DocILE explicitly combines key information extraction with localization requirements.",
                "DUE and DUDE emphasize real-world layouts where document structure matters.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="table_line_item_extraction",
            use_case="table and line-item extraction",
            touchstone="Can a report detect when field values are correct individually but assigned to the wrong row, item, or table group?",
            expected_reading="Row-association uncertainty should not be collapsed into generic field confidence.",
            current_failure_mode="Line items create combinatorial ambiguity: a value can be read correctly but attached to the wrong product, charge, party, or date.",
            decision_pga_contribution="Could diagnose probability clouds over row assignments, item groups, and column/value pairings.",
            baseline_comparison="Compare against table-structure F1, row-level accuracy, entropy, margin, and consistency across extraction passes.",
            baseline_reading="Table metrics score final structure but are less useful for routing ambiguous row assignments before acceptance.",
            pga_reading="PGA may separate one dominant row-conflict axis from broad table-structure failure.",
            incremental_value="Potentially high because line-item recognition is both practical and explicitly benchmarked.",
            implementation_difficulty="high",
            fit_label="promising",
            recommended_next_step="Build a compact line-item fixture with row-assignment candidates and compare PGA against row-confidence baselines.",
            evidence=(
                "DocILE includes Line Item Recognition as a practical task beyond simple key-value extraction.",
                "Layout-aware document models show that text, image, and layout jointly matter for document AI.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="cross_page_entity_linking",
            use_case="cross-page entity linking and repeated fields",
            touchstone="Can uncertainty over repeated mentions be separated from uncertainty over the extracted value itself?",
            expected_reading="A stable value with uncertain entity linkage should route to provenance review, not value correction.",
            current_failure_mode="Long documents can repeat parties, dates, identifiers, and amounts across pages with subtle scope differences.",
            decision_pga_contribution="Could measure dispersion over entity-link candidates when a document parser exposes candidate mentions.",
            baseline_comparison="Compare against entity-link confidence, mention count, retrieval score spread, and agreement between passes.",
            baseline_reading="Mention-level scores may not summarize whether ambiguity is local, cross-page, or diffuse.",
            pga_reading="PGA can be useful after entity candidates are aligned, especially for binary entity-link conflicts.",
            incremental_value="Likely useful for contracts, reports, and multi-page regulatory documents, but adapter work comes first.",
            implementation_difficulty="high",
            fit_label="needs_adapter",
            recommended_next_step="Defer until field-value and span/source adapters define candidate identity conventions.",
            evidence=(
                "Kleister highlights long formal documents with scanned and born-digital inputs.",
                "DUDE explicitly targets multi-page and multi-domain visually rich documents.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="ocr_layout_noise",
            use_case="OCR and layout corruption triage",
            touchstone="Can the method tell when extraction uncertainty is caused by document conversion rather than model reasoning?",
            expected_reading="OCR/layout noise should trigger reprocessing or human review, not an extraction prompt tweak.",
            current_failure_mode="Bad OCR, reading-order errors, broken tables, and merged tokens are often misdiagnosed as LLM hallucination.",
            decision_pga_contribution="Could compare candidate clouds across OCR/layout variants to flag sensitivity to document ingestion.",
            baseline_comparison="Compare against OCR confidence, parsing warnings, layout-model confidence, entropy, and extraction agreement.",
            baseline_reading="OCR scores are local; extraction agreement is global. Neither necessarily explains how ingestion noise changes decisions.",
            pga_reading="Geodesic drift across ingestion variants could flag conversion-sensitive extraction.",
            incremental_value="Useful for pipeline triage, but requires controlled ingestion variants or parser metadata.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Add ingestion-variant fixtures where the same document field is extracted after controlled OCR/layout perturbations.",
            evidence=(
                "Document AI work such as LayoutLMv3 emphasizes text-image-layout alignment.",
                "DocVQA reports gaps on questions where document structure is crucial.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="conflicting_values_and_versions",
            use_case="conflicting values across revisions, attachments, or document sets",
            touchstone="Can a diagnostic separate true value conflict from retrieval or scope confusion?",
            expected_reading="Conflicting values should produce a structured conflict state with source-aware review instructions.",
            current_failure_mode="Document sets can contain old versions, superseded forms, attachments, or tables whose values disagree.",
            decision_pga_contribution="Could analyze probability clouds over candidate values plus source/version groups.",
            baseline_comparison="Compare against retrieval rank, recency heuristics, entropy, margin, and agreement between documents.",
            baseline_reading="Retrieval rank and recency are useful but may not capture the geometry of competing extracted values.",
            pga_reading="A value/source adapter could reveal one conflict axis versus a broad document-set failure.",
            incremental_value="Promising but needs source/version metadata to avoid treating all candidate values as equivalent.",
            implementation_difficulty="high",
            fit_label="needs_adapter",
            recommended_next_step="Prototype a source-version candidate schema after the field-value fixture suite is in place.",
            evidence=(
                "Document collection QA and RAG workflows often depend on selecting the right document and the right value.",
                "Decision-PGA already treats regime shifts as a distinct diagnostic state.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="human_review_triage",
            use_case="human review queue routing",
            touchstone="Can extraction uncertainty route cases to the right reviewer action rather than a generic manual-review bucket?",
            expected_reading="Different uncertainty shapes should map to accept, compare candidates, inspect source, rerun OCR, or escalate.",
            current_failure_mode="Production extraction systems often use single confidence thresholds that create large undifferentiated review queues.",
            decision_pga_contribution="Maps extraction candidate clouds into action-oriented states that can prioritize review effort.",
            baseline_comparison="Compare against fixed confidence thresholds, entropy, top-1 margin, and agreement between extraction passes.",
            baseline_reading="Thresholds catch low-confidence cases but do not explain what the reviewer should do first.",
            pga_reading="Shape metrics can prioritize two-candidate disputes separately from diffuse extraction failures.",
            incremental_value="Good candidate for near-term demos once field-value fixtures exist.",
            implementation_difficulty="medium",
            fit_label="promising",
            recommended_next_step="Use the field-value fixture suite to define review actions and measure queue-quality improvements.",
            evidence=(
                "DocILE notes localization is useful for human-in-the-loop interactions and auditing.",
                "Decision-PGA already emits action-oriented diagnostic states.",
            ),
        ),
        DocumentExtractionScenario(
            gap_family="extraction_monitoring",
            use_case="document extraction regression monitoring",
            touchstone="Can teams detect when an extraction pipeline has changed failure shape, even if aggregate accuracy moves slowly?",
            expected_reading="Prompt, OCR, model, or schema updates should preserve expected diagnostic states on representative fixtures.",
            current_failure_mode="Accuracy, F1, and pass rates can hide that failures have shifted from clean ambiguity to diffuse extraction collapse.",
            decision_pga_contribution="Provides deterministic JSON/CSV reports for candidate-cloud shape changes in CI or offline evaluation.",
            baseline_comparison="Compare against accuracy, F1, exact match, field-level confidence, entropy, and margin thresholds.",
            baseline_reading="Aggregate metrics are essential but can flatten failure modes that matter for downstream review workflows.",
            pga_reading="PGA state regressions can act as a lightweight early-warning layer over fixture suites.",
            incremental_value="Useful after at least one candidate-cloud adapter and fixture set exists.",
            implementation_difficulty="low",
            fit_label="promising",
            recommended_next_step="Add expected-state fixtures for field-value and table-line-item examples, then run them in CI.",
            evidence=(
                "Decision-PGA evaluation reports already support deterministic local benchmark runs.",
                "Document extraction systems often need regression checks across schema, prompt, OCR, and model changes.",
            ),
        ),
    )
