import unittest

import numpy as np

from decision_pga import (
    intrinsic_mean_sphere,
    normalize_probabilities,
    pga_probability_cloud,
    sphere_exp,
    sphere_log,
    sqrt_embed,
    synthetic_probability_cloud,
)


class TestProbabilityPGA(unittest.TestCase):
    def test_normalize_probabilities_returns_positive_rows_summing_to_one(self):
        probs = normalize_probabilities(np.array([[0.0, 2.0, 3.0], [4.0, 0.0, 1.0]]))

        self.assertEqual(probs.shape, (2, 3))
        self.assertTrue(np.all(probs > 0.0))
        np.testing.assert_allclose(np.sum(probs, axis=1), np.ones(2), atol=1e-12)

    def test_sqrt_embedding_has_unit_norm(self):
        probs = normalize_probabilities(np.array([[0.8, 0.1, 0.1], [0.2, 0.3, 0.5]]))

        embedded = sqrt_embed(probs)

        np.testing.assert_allclose(np.linalg.norm(embedded, axis=1), np.ones(2), atol=1e-12)
        self.assertTrue(np.all(embedded >= 0.0))

    def test_sphere_exp_log_round_trips_localized_samples(self):
        points = sqrt_embed(
            np.array(
                [
                    [0.70, 0.20, 0.10],
                    [0.68, 0.22, 0.10],
                    [0.72, 0.18, 0.10],
                ]
            )
        )
        mean = intrinsic_mean_sphere(points)

        tangents = sphere_log(mean, points)
        reconstructed = sphere_exp(mean, tangents)

        np.testing.assert_allclose(reconstructed, points, atol=1e-10)

    def test_identical_distributions_have_near_zero_dispersion(self):
        probs = np.repeat([[0.85, 0.10, 0.05]], repeats=12, axis=0)

        result = pga_probability_cloud(probs)

        self.assertLess(result.total_dispersion, 1e-12)
        self.assertLess(np.max(np.abs(result.tangent_vectors)), 1e-10)
        np.testing.assert_allclose(result.mean_probability, probs[0], atol=1e-10)

    def test_binary_ambiguity_has_high_pc1_fraction(self):
        probs = synthetic_probability_cloud(
            "binary_ambiguity",
            n_samples=80,
            n_classes=5,
            seed=7,
        )

        result = pga_probability_cloud(probs)

        self.assertGreater(result.pc1_fraction, 0.80)
        self.assertGreater(result.anisotropy_ratio, 4.0)

    def test_diffuse_uncertainty_has_lower_pc1_fraction_than_binary_at_comparable_entropy(self):
        binary = synthetic_probability_cloud("binary_ambiguity", 120, 5, seed=11)
        diffuse = synthetic_probability_cloud("diffuse_uncertainty", 120, 5, seed=11)

        binary_result = pga_probability_cloud(binary)
        diffuse_result = pga_probability_cloud(diffuse)

        binary_entropy = _mean_entropy(binary)
        diffuse_entropy = _mean_entropy(diffuse)

        self.assertLess(abs(binary_entropy - diffuse_entropy), 0.35)
        self.assertLess(diffuse_result.pc1_fraction, binary_result.pc1_fraction)
        self.assertLess(diffuse_result.anisotropy_ratio, binary_result.anisotropy_ratio)


def _mean_entropy(probs):
    probs = np.asarray(probs, dtype=float)
    return float(np.mean(-np.sum(probs * np.log(probs), axis=1)))


if __name__ == "__main__":
    unittest.main()
