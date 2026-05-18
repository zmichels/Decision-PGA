import json
import tempfile
import unittest
from pathlib import Path

from decision_pga.application_evaluation import (
    APPLICATION_GAP_FAMILIES,
    run_application_evaluation_suite,
)
from decision_pga.application_reporting import write_application_evaluation_report


class TestApplicationEvaluation(unittest.TestCase):
    def test_application_suite_returns_deterministic_gap_families(self):
        first = run_application_evaluation_suite().to_dict()
        second = run_application_evaluation_suite().to_dict()

        self.assertEqual(first, second)
        self.assertEqual(first["source"], "application_evaluation")
        self.assertEqual(
            [scenario["gap_family"] for scenario in first["scenarios"]],
            list(APPLICATION_GAP_FAMILIES),
        )

    def test_fit_labels_are_stable_and_conservative(self):
        report = run_application_evaluation_suite()
        labels = {scenario.fit_label for scenario in report.scenarios}

        self.assertLessEqual(
            labels,
            {"promising", "redundant", "needs_adapter", "inconclusive"},
        )
        self.assertIn("promising", labels)
        self.assertIn("needs_adapter", labels)
        self.assertEqual(
            report.scenario_by_gap("tool_action_ambiguity").recommended_next_step,
            "Deep-dive candidate: build a tool/action selection fixture set and compare PGA against entropy, margin, and switch-rate baselines.",
        )

    def test_gap_matrix_contains_required_columns_and_expected_gap_families(self):
        report = run_application_evaluation_suite()
        rows = report.gap_matrix_rows()

        self.assertEqual(len(rows), len(APPLICATION_GAP_FAMILIES))
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
        self.assertEqual({row["gap_family"] for row in rows}, set(APPLICATION_GAP_FAMILIES))

    def test_application_report_writer_outputs_article_gap_matrix_and_pdf(self):
        report = run_application_evaluation_suite()

        with tempfile.TemporaryDirectory() as tmpdir:
            written = write_application_evaluation_report(report, tmpdir)
            names = {Path(path).name for path in written}
            metrics = json.loads(Path(tmpdir, "application_metrics.json").read_text(encoding="utf-8"))
            markdown = Path(tmpdir, "application_report.md").read_text(encoding="utf-8")

        self.assertEqual(
            names,
            {
                "application_metrics.json",
                "application_summary.csv",
                "gap_matrix.csv",
                "application_report.md",
                "decision-pga-gap-review.pdf",
            },
        )
        self.assertEqual(metrics["summary"]["scenario_count"], len(APPLICATION_GAP_FAMILIES))
        self.assertIn("Recommended deep dives", markdown)
        self.assertIn("agent tool/action selection", markdown)
        self.assertIn("RAG/evidence conflict", markdown)

    def test_article_markdown_exists_with_sources_limits_and_roadmap(self):
        article = Path("docs/articles/decision-pga-gap-review.md")
        text = article.read_text(encoding="utf-8")

        self.assertIn("Decision-PGA and the Coming Need for Decision-State Diagnostics in Agentic AI", text)
        self.assertIn("What Decision-PGA contributes", text)
        self.assertIn("not yet validated as a production safety layer", text)
        self.assertIn("Development roadmap toward agent-facing tools", text)
        for link in [
            "https://www.nature.com/articles/s41586-024-07421-0",
            "https://arxiv.org/abs/2503.15850",
            "https://arxiv.org/abs/2604.22985",
            "https://arxiv.org/abs/2511.08798",
            "https://arxiv.org/abs/2412.01033",
            "https://machinelearning.apple.com/research/estimate-uncertainty-well",
            "https://www.mdpi.com/2504-2289/9/12/320",
            "https://aclanthology.org/2025.emnlp-main.1060.pdf",
        ]:
            self.assertIn(link, text)


if __name__ == "__main__":
    unittest.main()
