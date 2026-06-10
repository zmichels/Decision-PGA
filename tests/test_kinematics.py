import unittest

import numpy as np

from decision_pga.kinematics import diagnose_kinematic_trajectory


class TestKinematicTrajectory(unittest.TestCase):
    def test_rejects_non_three_dimensional_runs(self):
        with self.assertRaisesRegex(ValueError, "runs must have shape"):
            diagnose_kinematic_trajectory([[0.5, 0.5]])

    def test_rejects_too_few_steps(self):
        runs = np.array([[[0.7, 0.3]]])

        with self.assertRaisesRegex(ValueError, "at least two steps"):
            diagnose_kinematic_trajectory(runs)

    def test_rejects_label_count_mismatch(self):
        runs = np.array(
            [
                [
                    [0.7, 0.2, 0.1],
                    [0.6, 0.3, 0.1],
                ]
            ]
        )

        with self.assertRaisesRegex(ValueError, "labels must match"):
            diagnose_kinematic_trajectory(runs, labels=["approve", "reject"])

    def test_rejects_step_name_count_mismatch(self):
        runs = np.array(
            [
                [
                    [0.7, 0.2, 0.1],
                    [0.6, 0.3, 0.1],
                ]
            ]
        )

        with self.assertRaisesRegex(ValueError, "step_names must match"):
            diagnose_kinematic_trajectory(
                runs,
                labels=["approve", "reject", "defer"],
                step_names=["input"],
            )

    def test_identical_repeated_states_have_near_zero_motion(self):
        runs = np.repeat(
            np.array([[[0.82, 0.12, 0.06], [0.82, 0.12, 0.06], [0.82, 0.12, 0.06]]]),
            repeats=4,
            axis=0,
        )

        result = diagnose_kinematic_trajectory(
            runs,
            labels=["approve", "reject", "defer"],
            step_names=["input", "rag", "output"],
            label="identical path",
        )
        payload = result.to_dict()

        self.assertEqual(payload["source_kind"], "kinematic_trajectory")
        self.assertEqual(payload["label"], "identical path")
        self.assertEqual(payload["labels"], ["approve", "reject", "defer"])
        self.assertEqual(payload["steps"], ["input", "rag", "output"])
        self.assertEqual(payload["shape"]["run_count"], 4)
        self.assertEqual(len(payload["canonical_path_probabilities"]), 3)
        self.assertLess(payload["systemic_kinetic_energy"], 1e-12)
        self.assertLess(payload["systemic_jerk"], 1e-12)

    def test_payload_is_json_serializable(self):
        runs = np.array(
            [
                [
                    [0.7, 0.2, 0.1],
                    [0.6, 0.3, 0.1],
                    [0.5, 0.4, 0.1],
                ]
            ]
        )

        payload = diagnose_kinematic_trajectory(runs).to_dict()

        import json

        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
