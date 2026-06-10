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


if __name__ == "__main__":
    unittest.main()
