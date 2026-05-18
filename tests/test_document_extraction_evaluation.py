import json
import tempfile
import unittest
from pathlib import Path

from decision_pga.document_extraction_evaluation import (
    DOCUMENT_EXTRACTION_GAP_FAMILIES,
    run_document_extraction_evaluation_suite,
)
from decision_pga.document_extraction_reporting import (
    write_document_extraction_evaluation_report,
)


class TestDocumentExtractionEvaluation(unittest.TestCase):
    def test_document_extraction_suite_returns_deterministic_gap_families(self):
        first = run_document_extraction_evaluation_suite().to_dict()
        second = run_document_extraction_evaluation_suite().to_dict()

        self.assertEqual(first, second)
        self.assertEqual(first["source"], "document_extraction_evaluation")
        self.assertEqual(
            [scenario["gap_family"] for scenario in first["scenarios"]],
            list(DOCUMENT_EXTRACTION_GAP_FAMILIES),
        )

    def test_document_extraction_fit_labels_are_stable_and_conservative(self):
        report = run_document_extraction_evaluation_suite()
        labels = {scenario.fit_label for scenario in report.scenarios}

        self.assertLessEqual(
            labels,
            {"promising", "redundant", "needs_adapter", "inconclusive"},
        )
        self.assertIn("promising", labels)
        self.assertIn("needs_adapter", labels)
        self.assertEqual(
            report.scenario_by_gap("field_value_ambiguity").recommended_next_step,
            "Deep-dive candidate: build field-value candidate fixtures and compare PGA against confidence, entropy, margin, and agreement baselines.",
        )

    def test_document_extraction_gap_matrix_contains_required_columns(self):
        report = run_document_extraction_evaluation_suite()
        rows = report.gap_matrix_rows()

        self.assertEqual(len(rows), len(DOCUMENT_EXTRACTION_GAP_FAMILIES))
        self.assertEqual(
            set(rows[0]),
            {
                "gap_family",
                "use_case",
                "current_failure_mode",
                "decision_pga_contribution",
                "baseline_comparison",
                "implementation_difficulty",
                "fit_label",
                "recommended_next_step",
            },
        )
        self.assertEqual(
            {row["gap_family"] for row in rows},
            set(DOCUMENT_EXTRACTION_GAP_FAMILIES),
        )

    def test_document_extraction_report_writer_outputs_separate_artifacts(self):
        report = run_document_extraction_evaluation_suite()

        with tempfile.TemporaryDirectory() as tmpdir:
            written = write_document_extraction_evaluation_report(report, tmpdir)
            names = {Path(path).name for path in written}
            metrics = json.loads(Path(tmpdir, "document_extraction_metrics.json").read_text(encoding="utf-8"))
            markdown = Path(tmpdir, "document_extraction_report.md").read_text(encoding="utf-8")

        self.assertEqual(
            names,
            {
                "document_extraction_metrics.json",
                "document_extraction_summary.csv",
                "document_extraction_gap_matrix.csv",
                "document_extraction_report.md",
                "decision-pga-document-extraction-gap-review.pdf",
            },
        )
        self.assertEqual(metrics["summary"]["scenario_count"], len(DOCUMENT_EXTRACTION_GAP_FAMILIES))
        self.assertIn("Recommended deep dives", markdown)
        self.assertIn("field-value candidate extraction", markdown)
        self.assertIn("table and line-item extraction", markdown)

    def test_document_extraction_article_exists_with_sources_limits_and_roadmap(self):
        article = Path("docs/articles/decision-pga-document-extraction-gap-review.md")
        text = article.read_text(encoding="utf-8")

        self.assertIn("Decision-PGA and the Extraction Confidence Gap in Document AI", text)
        self.assertIn("Document extraction is not just document understanding", text)
        self.assertIn("not a document parser, OCR engine, or extraction model", text)
        self.assertIn("Development roadmap for document-extraction diagnostics", text)
        for link in [
            "https://arxiv.org/abs/2302.05658",
            "https://arxiv.org/abs/2105.05796",
            "https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/069059b7ef840f0c74a814ec9237b6ec-Abstract-round2.html",
            "https://arxiv.org/abs/2305.08455",
            "https://arxiv.org/abs/2204.08387",
            "https://arxiv.org/abs/2007.00398",
            "https://arxiv.org/abs/2312.17617",
        ]:
            self.assertIn(link, text)


if __name__ == "__main__":
    unittest.main()
