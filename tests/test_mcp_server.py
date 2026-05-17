import unittest

from decision_pga import diagnose_probability_cloud
from decision_pga.mcp_server import (
    diagnose_model_outputs_tool,
    diagnose_probability_cloud_tool,
    diagnose_sampled_responses_tool,
    diagnose_trajectory_steps_tool,
    explain_decision_pga_metrics,
)


class TestDecisionPGAMCPTools(unittest.TestCase):
    def test_probability_cloud_tool_matches_python_api_contract(self):
        probabilities = [
            [0.88, 0.08, 0.04],
            [0.86, 0.10, 0.04],
            [0.89, 0.07, 0.04],
            [0.87, 0.09, 0.04],
        ]
        labels = ["approve", "reject", "defer"]

        tool_payload = diagnose_probability_cloud_tool(probabilities, labels=labels)
        api_payload = diagnose_probability_cloud(probabilities, labels=labels).to_dict()

        self.assertEqual(tool_payload["diagnostic"], api_payload)
        self.assertEqual(tool_payload["source"], "probability_cloud")

    def test_other_mcp_tools_preserve_existing_payload_shapes(self):
        model_payload = diagnose_model_outputs_tool(
            observations=[
                {"values": {"approve": -0.13, "reject": -2.53, "defer": -3.10}, "kind": "logprobs"},
                {"values": {"approve": -0.16, "reject": -2.30, "defer": -3.20}, "kind": "logprobs"},
            ]
        )
        sampled_payload = diagnose_sampled_responses_tool(
            responses=["approve"] * 6 + ["reject"] * 6,
            labels=["approve", "reject", "defer"],
            window_size=3,
            step=3,
        )
        trajectory_payload = diagnose_trajectory_steps_tool(
            steps=["retrieve", "retrieve", "answer", "answer"],
            labels=["retrieve", "answer"],
            window_size=2,
            step=2,
        )

        self.assertEqual(model_payload["source"], "model_outputs")
        self.assertIn("adapter", model_payload)
        self.assertEqual(sampled_payload["source"], "sampled_responses")
        self.assertIn("adapter", sampled_payload)
        self.assertEqual(trajectory_payload["source"], "trajectory_steps")
        self.assertIn("adapter", trajectory_payload)

    def test_metric_explanation_is_plain_json_compatible_context(self):
        explanation = explain_decision_pga_metrics()

        self.assertIn("pc1_fraction", explanation)
        self.assertIn("total_dispersion", explanation)
        self.assertIn("mean_margin", explanation)


if __name__ == "__main__":
    unittest.main()
