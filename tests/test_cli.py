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

    def test_invalid_source_returns_machine_readable_error(self):
        payload = {"source": "unknown"}

        result = _run_cli_with_stdin(payload)
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
