import json
import unittest

import numpy as np

from decision_pga import (
    SampledResponse,
    TrajectoryStep,
    diagnose_sampled_responses,
    diagnose_trajectory_steps,
    probability_cloud_from_sampled_responses,
    probability_cloud_from_trajectory_steps,
)


class TestSourceAdapters(unittest.TestCase):
    def test_sampled_responses_map_aliases_to_rolling_probability_rows(self):
        responses = [
            SampledResponse("Yes, approve the request."),
            SampledResponse("I would accept this."),
            SampledResponse("Approved."),
            SampledResponse("No, reject it."),
            SampledResponse("I would decline."),
            SampledResponse("Rejected."),
        ]

        probs, labels = probability_cloud_from_sampled_responses(
            responses,
            labels=["approve", "reject", "defer"],
            aliases={
                "approve": ["yes", "accept", "approved"],
                "reject": ["no", "decline", "rejected"],
                "defer": ["unclear", "unsure"],
            },
            window_size=3,
            step=3,
        )

        self.assertEqual(labels, ("approve", "reject", "defer"))
        self.assertEqual(probs.shape, (2, 3))
        np.testing.assert_allclose(probs[0], [1.0, 0.0, 0.0], atol=1e-9)
        np.testing.assert_allclose(probs[1], [0.0, 1.0, 0.0], atol=1e-9)

    def test_sampled_response_diagnostic_detects_windowed_regime_shift(self):
        responses = [
            SampledResponse("approve")
            for _ in range(12)
        ] + [
            SampledResponse("reject")
            for _ in range(12)
        ]

        result = diagnose_sampled_responses(
            responses,
            labels=["approve", "reject", "defer"],
            window_size=6,
            step=6,
        )

        self.assertEqual(result.source_kind, "sampled_responses")
        self.assertEqual(result.diagnostic.state, "regime_shift")
        self.assertEqual(result.diagnostic.recommended_action, "segment_or_replan")

    def test_trajectory_steps_window_into_candidate_probability_rows(self):
        steps = [
            TrajectoryStep("retrieve"),
            TrajectoryStep("retrieve"),
            TrajectoryStep("analyze"),
            TrajectoryStep("analyze"),
            TrajectoryStep("answer"),
            TrajectoryStep("answer"),
        ]

        probs, labels = probability_cloud_from_trajectory_steps(
            steps,
            labels=["retrieve", "analyze", "answer"],
            window_size=2,
            step=2,
        )

        self.assertEqual(labels, ("retrieve", "analyze", "answer"))
        self.assertEqual(probs.shape, (3, 3))
        np.testing.assert_allclose(probs[0], [1.0, 0.0, 0.0], atol=1e-9)
        np.testing.assert_allclose(probs[1], [0.0, 1.0, 0.0], atol=1e-9)
        np.testing.assert_allclose(probs[2], [0.0, 0.0, 1.0], atol=1e-9)

    def test_trajectory_diagnostic_result_is_json_serializable(self):
        steps = [
            TrajectoryStep("retrieve")
            for _ in range(8)
        ] + [
            TrajectoryStep("answer")
            for _ in range(8)
        ]

        result = diagnose_trajectory_steps(
            steps,
            labels=["retrieve", "analyze", "answer"],
            window_size=4,
            step=4,
        )
        payload = result.to_dict()

        json.dumps(payload)
        self.assertEqual(payload["adapter"]["source_kind"], "trajectory_steps")
        self.assertEqual(payload["adapter"]["window_size"], 4)
        self.assertEqual(payload["diagnostic"]["state"], "regime_shift")

    def test_unmapped_sampled_response_can_raise(self):
        responses = [SampledResponse("this does not match a candidate")]

        with self.assertRaisesRegex(ValueError, "could not map sampled response"):
            probability_cloud_from_sampled_responses(
                responses,
                labels=["approve", "reject"],
                unknown_policy="raise",
            )


if __name__ == "__main__":
    unittest.main()
