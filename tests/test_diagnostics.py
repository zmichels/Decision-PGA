import json
import unittest

from decision_pga import diagnose_probability_cloud, synthetic_probability_cloud


class TestDecisionPGADiagnostics(unittest.TestCase):
    def test_stable_cloud_recommends_proceed(self):
        probs = synthetic_probability_cloud("stable", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs)

        self.assertEqual(diagnostic.state, "stable")
        self.assertEqual(diagnostic.recommended_action, "proceed")

    def test_binary_ambiguity_recommends_clarifying_between_top_labels(self):
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        probs = synthetic_probability_cloud("binary_ambiguity", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs, labels=labels)

        self.assertEqual(diagnostic.state, "binary_ambiguity")
        self.assertEqual(diagnostic.recommended_action, "clarify_between_top_labels")
        self.assertEqual(set(diagnostic.top_labels[:2]), {"alpha", "beta"})

    def test_diffuse_uncertainty_recommends_gathering_more_evidence(self):
        probs = synthetic_probability_cloud("diffuse_uncertainty", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs)

        self.assertEqual(diagnostic.state, "diffuse_uncertainty")
        self.assertEqual(diagnostic.recommended_action, "gather_more_evidence")

    def test_boundary_sensitive_cloud_recommends_sensitivity_inspection(self):
        probs = synthetic_probability_cloud("boundary", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs)

        self.assertEqual(diagnostic.state, "boundary_sensitive")
        self.assertEqual(diagnostic.recommended_action, "inspect_sensitivity")

    def test_regime_shift_cloud_recommends_segmentation_or_replanning(self):
        probs = synthetic_probability_cloud("regime_shift", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs)

        self.assertEqual(diagnostic.state, "regime_shift")
        self.assertEqual(diagnostic.recommended_action, "segment_or_replan")

    def test_diagnostic_can_be_serialized_for_agent_tooling(self):
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        probs = synthetic_probability_cloud("binary_ambiguity", 120, 5, seed=42)

        diagnostic = diagnose_probability_cloud(probs, labels=labels)
        payload = diagnostic.to_dict()

        json.dumps(payload)
        self.assertEqual(payload["state"], "binary_ambiguity")
        self.assertEqual(payload["recommended_action"], "clarify_between_top_labels")
        self.assertIn("pc1_fraction", payload["metrics"])
        self.assertEqual(set(payload["top_labels"][:2]), {"alpha", "beta"})


if __name__ == "__main__":
    unittest.main()
