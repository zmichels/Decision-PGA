import json
import math
import unittest

import numpy as np

from decision_pga import (
    ModelOutputObservation,
    diagnose_model_outputs,
    probability_cloud_from_observations,
    synthetic_probability_cloud,
)


class TestModelOutputAdapters(unittest.TestCase):
    def test_logprob_observations_convert_to_candidate_probability_cloud(self):
        observations = [
            ModelOutputObservation(
                {"accept": math.log(0.82), "reject": math.log(0.12), "defer": math.log(0.06)},
                kind="logprobs",
            ),
            ModelOutputObservation(
                {"accept": math.log(0.79), "reject": math.log(0.15), "defer": math.log(0.06)},
                kind="logprobs",
            ),
        ]

        probs, labels = probability_cloud_from_observations(observations)

        self.assertEqual(labels, ("accept", "reject", "defer"))
        np.testing.assert_allclose(np.sum(probs, axis=1), np.ones(2), atol=1e-12)
        np.testing.assert_allclose(probs[0], [0.82, 0.12, 0.06], atol=1e-12)

    def test_probability_observations_feed_the_diagnostic_contract(self):
        observations = [
            ModelOutputObservation([0.88, 0.08, 0.04], kind="probabilities"),
            ModelOutputObservation([0.86, 0.10, 0.04], kind="probabilities"),
            ModelOutputObservation([0.89, 0.07, 0.04], kind="probabilities"),
            ModelOutputObservation([0.87, 0.09, 0.04], kind="probabilities"),
        ]

        result = diagnose_model_outputs(
            observations,
            labels=["approve", "reject", "defer"],
            label="approval-check",
        )

        self.assertEqual(result.labels, ("approve", "reject", "defer"))
        self.assertEqual(result.diagnostic.state, "stable")
        self.assertEqual(result.diagnostic.recommended_action, "proceed")
        self.assertEqual(result.observation_count, 4)

    def test_logprob_adapter_preserves_binary_ambiguity_signal(self):
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        probs = synthetic_probability_cloud("binary_ambiguity", 120, 5, seed=42)
        observations = [
            ModelOutputObservation(dict(zip(labels, np.log(row))), kind="logprobs")
            for row in probs
        ]

        result = diagnose_model_outputs(observations)

        self.assertEqual(result.diagnostic.state, "binary_ambiguity")
        self.assertEqual(result.diagnostic.recommended_action, "clarify_between_top_labels")
        self.assertEqual(set(result.diagnostic.top_labels[:2]), {"alpha", "beta"})

    def test_adapter_result_is_json_serializable_for_tool_callers(self):
        observations = [
            ModelOutputObservation([0.88, 0.08, 0.04], kind="probabilities"),
            ModelOutputObservation([0.86, 0.10, 0.04], kind="probabilities"),
            ModelOutputObservation([0.89, 0.07, 0.04], kind="probabilities"),
            ModelOutputObservation([0.87, 0.09, 0.04], kind="probabilities"),
        ]

        payload = diagnose_model_outputs(
            observations,
            labels=["approve", "reject", "defer"],
        ).to_dict()

        json.dumps(payload)
        self.assertEqual(payload["adapter"]["labels"], ["approve", "reject", "defer"])
        self.assertEqual(payload["adapter"]["observation_count"], 4)
        self.assertEqual(payload["adapter"]["input_kinds"], ["probabilities"])
        self.assertEqual(payload["diagnostic"]["state"], "stable")

    def test_hidden_activation_payload_kind_is_rejected(self):
        observations = [
            ModelOutputObservation([0.1, 0.2, 0.3], kind="hidden_activations"),
        ]

        with self.assertRaisesRegex(ValueError, "kind must be"):
            probability_cloud_from_observations(
                observations,
                labels=["a", "b", "c"],
            )


if __name__ == "__main__":
    unittest.main()
