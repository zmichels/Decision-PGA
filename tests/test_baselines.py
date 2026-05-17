import math
import unittest

import numpy as np

from decision_pga.baselines import baseline_metrics


class TestBaselineMetrics(unittest.TestCase):
    def test_entropy_and_margin_metrics_match_hand_computed_fixture(self):
        probabilities = np.array([
            [0.8, 0.2],
            [0.5, 0.5],
        ])

        metrics = baseline_metrics(probabilities)
        payload = metrics.to_dict()

        expected_entropy = [
            -(0.8 * math.log(0.8) + 0.2 * math.log(0.2)),
            math.log(2),
        ]
        expected_margins = [0.6, 0.0]

        self.assertTrue(np.allclose(metrics.entropy, expected_entropy))
        self.assertAlmostEqual(payload["mean_entropy"], float(np.mean(expected_entropy)))
        self.assertAlmostEqual(payload["entropy_variance"], float(np.var(expected_entropy)))
        self.assertAlmostEqual(payload["mean_margin"], float(np.mean(expected_margins)))
        self.assertAlmostEqual(payload["min_margin"], 0.0)

    def test_switch_rate_and_half_window_drift_are_deterministic(self):
        probabilities = np.array([
            [0.9, 0.1],
            [0.8, 0.2],
            [0.1, 0.9],
            [0.2, 0.8],
        ])

        metrics = baseline_metrics(probabilities)

        self.assertAlmostEqual(metrics.top_label_switch_rate, 1.0 / 3.0)
        self.assertGreater(metrics.half_jensen_shannon_drift, 0.0)
        self.assertAlmostEqual(
            metrics.half_euclidean_drift,
            float(np.linalg.norm(np.array([0.85, 0.15]) - np.array([0.15, 0.85]))),
        )


if __name__ == "__main__":
    unittest.main()
