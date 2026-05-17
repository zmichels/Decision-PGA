import json
import tempfile
import unittest
from pathlib import Path

from decision_pga.evaluation import (
    EvaluationConfig,
    ScenarioSpec,
    run_evaluation,
)
from decision_pga.reporting import write_evaluation_report


class TestEvaluationHarness(unittest.TestCase):
    def test_synthetic_scenarios_are_deterministic_by_seed(self):
        config = EvaluationConfig(
            seed=7,
            scenarios=(
                ScenarioSpec("stable_fixture", "stable", "stable", 48, 5, seed=101),
                ScenarioSpec("binary_fixture", "binary_ambiguity", "binary_ambiguity", 48, 5, seed=102),
            ),
        )

        first = run_evaluation(config).to_dict()
        second = run_evaluation(config).to_dict()

        self.assertEqual(first, second)

    def test_benchmark_contains_expected_rows_confusion_and_advantage(self):
        report = run_evaluation(EvaluationConfig.default_smoke(seed=11))
        payload = report.to_dict()
        names = {row["name"] for row in payload["scenarios"]}

        self.assertIn("entropy_matched_binary", names)
        self.assertIn("entropy_matched_diffuse", names)
        self.assertIn("confusion_matrix", payload)
        self.assertIn("advantage", payload)
        self.assertGreater(
            payload["advantage"]["pga_binary_diffuse_gap"],
            payload["advantage"]["entropy_binary_diffuse_gap"],
        )

    def test_report_writer_outputs_stable_files(self):
        report = run_evaluation(EvaluationConfig.default_smoke(seed=13))

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "report"
            written = write_evaluation_report(report, output_dir)

            expected = {
                "metrics.json",
                "summary.csv",
                "confusion_matrix.csv",
                "advantage_report.md",
                "separability.png",
                "confusion_matrix.png",
                "pga_vs_baseline_deltas.png",
            }
            self.assertEqual({path.name for path in written}, expected)
            metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["config"]["seed"], 13)
            self.assertIn("Conservative advantage readout", (output_dir / "advantage_report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
