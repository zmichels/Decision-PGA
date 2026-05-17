import math
import unittest

from decision_pga import (
    diagnose_model_outputs,
    observation_from_provider_scores,
    observation_from_token_scores,
    observations_from_provider_scores,
)


class ProviderChoice:
    def __init__(self, token_scores):
        self.token_scores = token_scores


class ProviderResponse:
    def __init__(self, response_id, token_scores):
        self.response_id = response_id
        self.choice = ProviderChoice(token_scores)


class TestProviderBridges(unittest.TestCase):
    def test_nested_provider_score_mapping_becomes_model_output_observation(self):
        response = {
            "id": "sample-001",
            "output": {
                "scores": {
                    "approve": math.log(0.86),
                    "reject": math.log(0.10),
                    "defer": math.log(0.04),
                }
            },
        }

        observation = observation_from_provider_scores(
            response,
            score_path=("output", "scores"),
            candidates=["approve", "reject", "defer"],
            kind="logprobs",
            observation_id_path=("id",),
            source="dict-provider",
        )

        self.assertEqual(observation.kind, "logprobs")
        self.assertEqual(observation.observation_id, "sample-001")
        self.assertEqual(observation.source, "dict-provider")
        self.assertEqual(set(observation.values), {"approve", "reject", "defer"})

    def test_provider_score_observations_feed_existing_diagnostic_contract(self):
        responses = [
            {"scores": {"approve": math.log(0.88), "reject": math.log(0.08), "defer": math.log(0.04)}},
            {"scores": {"approve": math.log(0.86), "reject": math.log(0.10), "defer": math.log(0.04)}},
            {"scores": {"approve": math.log(0.89), "reject": math.log(0.07), "defer": math.log(0.04)}},
            {"scores": {"approve": math.log(0.87), "reject": math.log(0.09), "defer": math.log(0.04)}},
        ]

        observations = observations_from_provider_scores(
            responses,
            score_path=("scores",),
            candidates=["approve", "reject", "defer"],
            kind="logprobs",
            source="dict-provider",
        )
        diagnostic = diagnose_model_outputs(observations)

        self.assertEqual(diagnostic.diagnostic.state, "stable")
        self.assertEqual(diagnostic.diagnostic.recommended_action, "proceed")

    def test_token_score_entries_can_be_extracted_from_object_paths(self):
        response = ProviderResponse(
            "sample-002",
            [
                {"token": " approve", "logprob": math.log(0.90)},
                {"token": " reject", "logprob": math.log(0.07)},
                {"token": " defer", "logprob": math.log(0.03)},
            ],
        )

        observation = observation_from_token_scores(
            response,
            token_scores_path=("choice", "token_scores"),
            candidates=["approve", "reject", "defer"],
            observation_id_path=("response_id",),
            source="object-provider",
        )

        self.assertEqual(observation.observation_id, "sample-002")
        self.assertEqual(observation.values["approve"], math.log(0.90))
        self.assertEqual(observation.values["reject"], math.log(0.07))
        self.assertEqual(observation.values["defer"], math.log(0.03))

    def test_missing_candidate_score_can_be_filled_explicitly(self):
        response = {
            "top_logprobs": [
                {"token": "approve", "logprob": math.log(0.91)},
                {"token": "reject", "logprob": math.log(0.09)},
            ]
        }

        observation = observation_from_token_scores(
            response,
            token_scores_path=("top_logprobs",),
            candidates=["approve", "reject", "defer"],
            missing_policy="fill",
            missing_value=-30.0,
        )

        self.assertEqual(observation.values["defer"], -30.0)

    def test_missing_candidate_score_raises_by_default(self):
        response = {
            "scores": {
                "approve": math.log(0.91),
                "reject": math.log(0.09),
            }
        }

        with self.assertRaisesRegex(ValueError, "missing candidate scores"):
            observation_from_provider_scores(
                response,
                score_path=("scores",),
                candidates=["approve", "reject", "defer"],
            )


if __name__ == "__main__":
    unittest.main()
