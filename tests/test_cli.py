import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestDecisionPGACLI(unittest.TestCase):
    def test_probability_cloud_payload_returns_json_diagnostic(self):
        payload = {
            "source": "probability_cloud",
            "labels": ["approve", "reject", "defer"],
            "probabilities": [
                [0.88, 0.08, 0.04],
                [0.86, 0.10, 0.04],
                [0.89, 0.07, 0.04],
                [0.87, 0.09, 0.04],
            ],
        }

        result = _run_cli_with_payload(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "probability_cloud")
        self.assertEqual(output["diagnostic"]["state"], "stable")
        self.assertEqual(output["diagnostic"]["recommended_action"], "proceed")

    def test_model_outputs_payload_reads_from_stdin(self):
        payload = {
            "source": "model_outputs",
            "kind": "logprobs",
            "observations": [
                {"approve": -0.13, "reject": -2.53, "defer": -3.10},
                {"approve": -0.16, "reject": -2.30, "defer": -3.20},
                {"approve": -0.12, "reject": -2.66, "defer": -3.30},
                {"approve": -0.14, "reject": -2.44, "defer": -3.05},
            ],
        }

        result = _run_cli_with_stdin(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "model_outputs")
        self.assertEqual(output["adapter"]["input_kinds"], ["logprobs"])
        self.assertEqual(output["diagnostic"]["state"], "stable")

    def test_sampled_responses_payload_detects_regime_shift(self):
        payload = {
            "source": "sampled_responses",
            "labels": ["approve", "reject", "defer"],
            "responses": ["approve"] * 12 + ["reject"] * 12,
            "window_size": 6,
            "step": 6,
        }

        result = _run_cli_with_payload(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "sampled_responses")
        self.assertEqual(output["adapter"]["source_kind"], "sampled_responses")
        self.assertEqual(output["diagnostic"]["state"], "regime_shift")

    def test_provider_scores_payload_feeds_model_output_diagnostic(self):
        payload = {
            "source": "provider_scores",
            "score_path": ["output", "scores"],
            "candidates": ["approve", "reject", "defer"],
            "kind": "logprobs",
            "records": [
                {"output": {"scores": {"approve": -0.13, "reject": -2.53, "defer": -3.10}}},
                {"output": {"scores": {"approve": -0.16, "reject": -2.30, "defer": -3.20}}},
                {"output": {"scores": {"approve": -0.12, "reject": -2.66, "defer": -3.30}}},
                {"output": {"scores": {"approve": -0.14, "reject": -2.44, "defer": -3.05}}},
            ],
        }

        result = _run_cli_with_payload(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "provider_scores")
        self.assertEqual(output["adapter"]["labels"], ["approve", "reject", "defer"])
        self.assertEqual(output["diagnostic"]["recommended_action"], "proceed")

    def test_kinematic_trajectory_payload_returns_motion_metrics(self):
        payload = {
            "source": "kinematic_trajectory",
            "label": "rag tool whiplash",
            "labels": ["retrieve", "draft", "ask_user"],
            "steps": ["input", "rag", "output"],
            "runs": [
                [
                    [0.70, 0.20, 0.10],
                    [0.45, 0.45, 0.10],
                    [0.20, 0.70, 0.10],
                ],
                [
                    [0.72, 0.18, 0.10],
                    [0.48, 0.42, 0.10],
                    [0.10, 0.20, 0.70],
                ],
            ],
        }

        result = _run_cli_with_payload(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "kinematic_trajectory")
        self.assertEqual(output["diagnostic"]["source_kind"], "kinematic_trajectory")
        self.assertEqual(output["diagnostic"]["steps"], ["input", "rag", "output"])
        self.assertGreater(output["diagnostic"]["systemic_kinetic_energy"], 0.0)
        self.assertGreater(output["diagnostic"]["systemic_jerk"], 0.0)

    def test_invalid_source_returns_machine_readable_error(self):
        payload = {"source": "unknown"}

        result = _run_cli_with_stdin(payload)
        error = json.loads(result.stderr)

        self.assertEqual(result.returncode, 2)
        self.assertIn("error", error)
        self.assertEqual(result.stdout, "")

    def test_evaluate_command_writes_report_files(self):
        config = {
            "seed": 17,
            "scenarios": [
                {
                    "name": "stable_fixture",
                    "kind": "stable",
                    "expected_state": "stable",
                    "n_samples": 36,
                    "n_classes": 5,
                    "seed": 201,
                },
                {
                    "name": "binary_fixture",
                    "kind": "binary_ambiguity",
                    "expected_state": "binary_ambiguity",
                    "n_samples": 36,
                    "n_classes": 5,
                    "seed": 202,
                },
                {
                    "name": "diffuse_fixture",
                    "kind": "diffuse_uncertainty",
                    "expected_state": "diffuse_uncertainty",
                    "n_samples": 36,
                    "n_classes": 5,
                    "seed": 203,
                },
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "evaluation_config.json"
            output_dir = Path(tmpdir) / "report"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--config",
                    str(config_path),
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(output["source"], "evaluation")
            self.assertTrue((output_dir / "metrics.json").exists())
            self.assertTrue((output_dir / "summary.csv").exists())
            self.assertTrue((output_dir / "advantage_report.md").exists())

    def test_evaluate_benchmark_suite_option_preserves_existing_report_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "benchmark"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--suite",
                    "benchmark",
                    "--config",
                    "examples/evaluation_config.json",
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            written = {Path(path).name for path in output["written_files"]}

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "evaluation")
        self.assertEqual(
            written,
            {
                "metrics.json",
                "summary.csv",
                "confusion_matrix.csv",
                "advantage_report.md",
                "separability.png",
                "confusion_matrix.png",
                "pga_vs_baseline_deltas.png",
            },
        )

    def test_evaluate_application_suite_writes_gap_review_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "application"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--suite",
                    "application",
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            written = {Path(path).name for path in output["written_files"]}

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "application_evaluation")
        self.assertEqual(
            written,
            {
                "application_metrics.json",
                "application_summary.csv",
                "gap_matrix.csv",
                "application_report.md",
                "decision-pga-gap-review.pdf",
            },
        )

    def test_evaluate_document_extraction_suite_writes_separate_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "document-extraction"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--suite",
                    "document-extraction",
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            written = {Path(path).name for path in output["written_files"]}

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "document_extraction_evaluation")
        self.assertEqual(
            written,
            {
                "document_extraction_metrics.json",
                "document_extraction_summary.csv",
                "document_extraction_gap_matrix.csv",
                "document_extraction_report.md",
                "decision-pga-document-extraction-gap-review.pdf",
            },
        )

    def test_evaluate_all_suite_writes_benchmark_and_application_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "all"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--suite",
                    "all",
                    "--config",
                    "examples/evaluation_config.json",
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            written = {Path(path).name for path in output["written_files"]}

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "evaluation_bundle")
        self.assertIn("metrics.json", written)
        self.assertIn("application_metrics.json", written)
        self.assertIn("document_extraction_metrics.json", written)
        self.assertIn("decision-pga-gap-review.pdf", written)
        self.assertIn("decision-pga-document-extraction-gap-review.pdf", written)

    def test_evaluate_invalid_suite_returns_machine_readable_error(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "decision_pga.cli",
                "evaluate",
                "--suite",
                "not-a-suite",
                "--output",
                "reports/unused",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        error = json.loads(result.stderr)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("unsupported evaluation suite", error["error"])

    def test_evaluate_invalid_config_returns_machine_readable_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "bad_config.json"
            output_dir = Path(tmpdir) / "report"
            config_path.write_text('{"scenarios": []}', encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "decision_pga.cli",
                    "evaluate",
                    "--config",
                    str(config_path),
                    "--output",
                    str(output_dir),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            error = json.loads(result.stderr)

            self.assertEqual(result.returncode, 2)
            self.assertIn("error", error)
            self.assertEqual(result.stdout, "")


def _run_cli_with_payload(payload):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-m", "decision_pga.cli", "diagnose", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )


def _run_cli_with_stdin(payload):
    return subprocess.run(
        [sys.executable, "-m", "decision_pga.cli", "diagnose", "-"],
        input=json.dumps(payload),
        check=False,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    unittest.main()
