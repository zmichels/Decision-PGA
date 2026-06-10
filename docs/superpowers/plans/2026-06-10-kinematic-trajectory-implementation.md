# Kinematic Trajectory Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an integrated `kinematic_trajectory` Decision-PGA source type for multi-run, multi-step probability traces.

**Architecture:** Add a focused `decision_pga/kinematics.py` module above the existing Fisher-Rao geometry helpers. The module validates a `runs x steps x labels` tensor, computes canonical step means, geodesic velocities, approximate ambient tangent accelerations, compact dispersion summaries, and JSON-safe output. CLI routing, examples, and docs are added only after the Python API is tested.

**Tech Stack:** Python, NumPy, existing `unittest` test suite, existing `decision-pga diagnose` JSON CLI.

---

## Scope Check

The accepted spec covers one subsystem: metric-first kinematic trajectory diagnostics. MCP exposure, plotting, verbose raw vectors, parallel transport acceleration, and named kinematic states are excluded from this plan.

## File Structure

- Create `decision_pga/kinematics.py`: validation, tensor normalization, metric computation, compact dispersion summaries, JSON-safe dataclasses.
- Create `tests/test_kinematics.py`: Python API behavior and validation tests.
- Modify `decision_pga/__init__.py`: public exports for the new dataclasses and `diagnose_kinematic_trajectory`.
- Modify `decision_pga/cli.py`: route `source: "kinematic_trajectory"` payloads into the new API.
- Modify `tests/test_cli.py`: CLI smoke test for the new source type.
- Create `examples/agent/kinematic_trajectory_rag_tool_whiplash.json`: readable fixture with a final-step deflection.
- Create `docs/kinematic-trajectory.md`: short usage and interpretation guide.
- Modify `docs/agent-toolkit.md`: link and short mention of the new trajectory diagnostic.

## Task 1: API Validation Skeleton

**Files:**
- Create: `tests/test_kinematics.py`
- Create: `decision_pga/kinematics.py`

- [ ] **Step 1: Write failing validation tests**

Create `tests/test_kinematics.py` with:

```python
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
```

- [ ] **Step 2: Run validation tests and verify RED**

Run:

```bash
python -m unittest tests.test_kinematics -v
```

Expected: FAIL because `decision_pga.kinematics` does not exist.

- [ ] **Step 3: Add minimal validation implementation**

Create `decision_pga/kinematics.py` with:

```python
"""Kinematic trajectory diagnostics for multi-step Decision-PGA traces."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np

from .probability_pga import normalize_probabilities


@dataclass(frozen=True)
class KinematicTrajectoryDiagnostic:
    """JSON-friendly metric summary for observed decision-state motion."""

    label: str | None
    labels: tuple[str, ...]
    step_names: tuple[str, ...]
    normalized_runs: np.ndarray

    def to_dict(self) -> dict[str, object]:
        return {
            "source_kind": "kinematic_trajectory",
            "label": self.label,
            "labels": list(self.labels),
            "steps": list(self.step_names),
            "shape": {
                "run_count": int(self.normalized_runs.shape[0]),
                "step_count": int(self.normalized_runs.shape[1]),
                "label_count": int(self.normalized_runs.shape[2]),
            },
        }


def diagnose_kinematic_trajectory(
    runs: object,
    labels: Sequence[str] | None = None,
    step_names: Sequence[str] | None = None,
    label: str | None = None,
) -> KinematicTrajectoryDiagnostic:
    """Diagnose a run x step x label probability tensor."""

    values = np.asarray(runs, dtype=float)
    if values.ndim != 3:
        raise ValueError("runs must have shape num_runs x num_steps x num_labels.")
    run_count, step_count, label_count = values.shape
    if run_count < 1:
        raise ValueError("runs must contain at least one run.")
    if step_count < 2:
        raise ValueError("runs must contain at least two steps.")
    if label_count < 2:
        raise ValueError("runs must contain at least two labels.")

    label_tuple = _resolve_labels(labels, label_count)
    step_tuple = _resolve_step_names(step_names, step_count)
    normalized = _normalize_runs(values)
    return KinematicTrajectoryDiagnostic(
        label=label,
        labels=label_tuple,
        step_names=step_tuple,
        normalized_runs=normalized,
    )


def _resolve_labels(labels: Sequence[str] | None, label_count: int) -> tuple[str, ...]:
    if labels is None:
        return tuple(f"class_{index}" for index in range(label_count))
    label_tuple = tuple(str(item) for item in labels)
    if len(label_tuple) != label_count:
        raise ValueError("labels must match the number of probability labels.")
    return label_tuple


def _resolve_step_names(
    step_names: Sequence[str] | None,
    step_count: int,
) -> tuple[str, ...]:
    if step_names is None:
        return tuple(f"step_{index}" for index in range(step_count))
    step_tuple = tuple(str(item) for item in step_names)
    if len(step_tuple) != step_count:
        raise ValueError("step_names must match the number of trajectory steps.")
    return step_tuple


def _normalize_runs(values: np.ndarray) -> np.ndarray:
    run_count, step_count, label_count = values.shape
    normalized = normalize_probabilities(values.reshape(-1, label_count))
    return normalized.reshape(run_count, step_count, label_count)


def _json_float(value: float) -> float | None:
    scalar = float(value)
    if isfinite(scalar):
        return scalar
    return None
```

- [ ] **Step 4: Run validation tests and verify GREEN**

Run:

```bash
python -m unittest tests.test_kinematics -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

Run:

```bash
git add decision_pga/kinematics.py tests/test_kinematics.py
git commit -m "Add kinematic trajectory validation"
```

Expected: commit succeeds.

## Task 2: Canonical Path And Zero Motion Metrics

**Files:**
- Modify: `tests/test_kinematics.py`
- Modify: `decision_pga/kinematics.py`

- [ ] **Step 1: Write failing zero-motion and JSON tests**

Append these methods inside `TestKinematicTrajectory` in `tests/test_kinematics.py`:

```python
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
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
python -m unittest tests.test_kinematics.TestKinematicTrajectory.test_identical_repeated_states_have_near_zero_motion tests.test_kinematics.TestKinematicTrajectory.test_payload_is_json_serializable -v
```

Expected: FAIL because `canonical_path_probabilities`, `systemic_kinetic_energy`, and `systemic_jerk` are not in the payload.

- [ ] **Step 3: Implement canonical path, velocities, and compact metrics**

Replace `decision_pga/kinematics.py` with:

```python
"""Kinematic trajectory diagnostics for multi-step Decision-PGA traces."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np

from .probability_pga import (
    intrinsic_mean_sphere,
    normalize_probabilities,
    sphere_log,
    sqrt_embed,
)


@dataclass(frozen=True)
class DispersionSummary:
    """Compact eigen-summary for kinematic vector dispersion."""

    tensor: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    total_dispersion: float
    pc1_fraction: float

    def to_dict(self) -> dict[str, object]:
        return {
            "tensor": _json_matrix(self.tensor),
            "eigenvalues": [_json_float(value) for value in self.eigenvalues],
            "total_dispersion": _json_float(self.total_dispersion),
            "pc1_fraction": _json_float(self.pc1_fraction),
        }


@dataclass(frozen=True)
class KinematicTrajectoryDiagnostic:
    """JSON-friendly metric summary for observed decision-state motion."""

    label: str | None
    labels: tuple[str, ...]
    step_names: tuple[str, ...]
    normalized_runs: np.ndarray
    canonical_path_probabilities: np.ndarray
    velocities: np.ndarray
    accelerations: np.ndarray
    step_kinetic_energy: np.ndarray
    step_jerk: np.ndarray
    velocity_dispersion: DispersionSummary
    acceleration_dispersion: DispersionSummary

    @property
    def systemic_kinetic_energy(self) -> float:
        if self.step_kinetic_energy.size == 0:
            return 0.0
        return float(np.mean(self.step_kinetic_energy))

    @property
    def systemic_jerk(self) -> float:
        if self.step_jerk.size == 0:
            return 0.0
        return float(np.mean(self.step_jerk))

    def to_dict(self) -> dict[str, object]:
        return {
            "source_kind": "kinematic_trajectory",
            "label": self.label,
            "labels": list(self.labels),
            "steps": list(self.step_names),
            "shape": {
                "run_count": int(self.normalized_runs.shape[0]),
                "step_count": int(self.normalized_runs.shape[1]),
                "label_count": int(self.normalized_runs.shape[2]),
            },
            "acceleration_comparison": "ambient_tangent_delta",
            "canonical_path_probabilities": _json_matrix(self.canonical_path_probabilities),
            "step_kinetic_energy": [_json_float(value) for value in self.step_kinetic_energy],
            "step_jerk": [_json_float(value) for value in self.step_jerk],
            "systemic_kinetic_energy": _json_float(self.systemic_kinetic_energy),
            "systemic_jerk": _json_float(self.systemic_jerk),
            "velocity_dispersion": self.velocity_dispersion.to_dict(),
            "acceleration_dispersion": self.acceleration_dispersion.to_dict(),
            "primary_drift_labels": _primary_drift_labels(
                self.labels,
                self.velocity_dispersion.eigenvectors,
            ),
        }


def diagnose_kinematic_trajectory(
    runs: object,
    labels: Sequence[str] | None = None,
    step_names: Sequence[str] | None = None,
    label: str | None = None,
) -> KinematicTrajectoryDiagnostic:
    """Diagnose a run x step x label probability tensor."""

    values = np.asarray(runs, dtype=float)
    if values.ndim != 3:
        raise ValueError("runs must have shape num_runs x num_steps x num_labels.")
    run_count, step_count, label_count = values.shape
    if run_count < 1:
        raise ValueError("runs must contain at least one run.")
    if step_count < 2:
        raise ValueError("runs must contain at least two steps.")
    if label_count < 2:
        raise ValueError("runs must contain at least two labels.")

    label_tuple = _resolve_labels(labels, label_count)
    step_tuple = _resolve_step_names(step_names, step_count)
    normalized = _normalize_runs(values)
    embedded = sqrt_embed(normalized.reshape(-1, label_count)).reshape(
        run_count,
        step_count,
        label_count,
    )
    canonical = _canonical_path(embedded)
    velocities = _step_velocities(embedded)
    accelerations = _ambient_accelerations(velocities)
    return KinematicTrajectoryDiagnostic(
        label=label,
        labels=label_tuple,
        step_names=step_tuple,
        normalized_runs=normalized,
        canonical_path_probabilities=canonical,
        velocities=velocities,
        accelerations=accelerations,
        step_kinetic_energy=_step_kinetic_energy(velocities),
        step_jerk=_step_jerk(accelerations),
        velocity_dispersion=_dispersion_summary(velocities.reshape(-1, label_count)),
        acceleration_dispersion=_dispersion_summary(accelerations.reshape(-1, label_count)),
    )


def _resolve_labels(labels: Sequence[str] | None, label_count: int) -> tuple[str, ...]:
    if labels is None:
        return tuple(f"class_{index}" for index in range(label_count))
    label_tuple = tuple(str(item) for item in labels)
    if len(label_tuple) != label_count:
        raise ValueError("labels must match the number of probability labels.")
    return label_tuple


def _resolve_step_names(
    step_names: Sequence[str] | None,
    step_count: int,
) -> tuple[str, ...]:
    if step_names is None:
        return tuple(f"step_{index}" for index in range(step_count))
    step_tuple = tuple(str(item) for item in step_names)
    if len(step_tuple) != step_count:
        raise ValueError("step_names must match the number of trajectory steps.")
    return step_tuple


def _normalize_runs(values: np.ndarray) -> np.ndarray:
    run_count, step_count, label_count = values.shape
    normalized = normalize_probabilities(values.reshape(-1, label_count))
    return normalized.reshape(run_count, step_count, label_count)


def _canonical_path(embedded: np.ndarray) -> np.ndarray:
    means = []
    for step_index in range(embedded.shape[1]):
        mean = intrinsic_mean_sphere(embedded[:, step_index, :])
        means.append(normalize_probabilities(mean**2)[0])
    return np.vstack(means)


def _step_velocities(embedded: np.ndarray) -> np.ndarray:
    run_count, step_count, label_count = embedded.shape
    velocities = np.zeros((run_count, step_count - 1, label_count), dtype=float)
    for run_index in range(run_count):
        for step_index in range(step_count - 1):
            velocities[run_index, step_index, :] = sphere_log(
                embedded[run_index, step_index, :],
                embedded[run_index, step_index + 1, :],
            )[0]
    return velocities


def _ambient_accelerations(velocities: np.ndarray) -> np.ndarray:
    if velocities.shape[1] < 2:
        return np.zeros((velocities.shape[0], 0, velocities.shape[2]), dtype=float)
    return velocities[:, 1:, :] - velocities[:, :-1, :]


def _step_kinetic_energy(velocities: np.ndarray) -> np.ndarray:
    speeds = np.linalg.norm(velocities, axis=2)
    return 0.5 * np.mean(speeds**2, axis=0)


def _step_jerk(accelerations: np.ndarray) -> np.ndarray:
    if accelerations.shape[1] == 0:
        return np.zeros(0, dtype=float)
    return np.mean(np.linalg.norm(accelerations, axis=2), axis=0)


def _dispersion_summary(vectors: np.ndarray) -> DispersionSummary:
    if vectors.ndim != 2:
        raise ValueError("vectors must have shape num_vectors x num_labels.")
    label_count = vectors.shape[1]
    if vectors.shape[0] <= 1:
        tensor = np.zeros((label_count, label_count), dtype=float)
    else:
        centered = vectors - np.mean(vectors, axis=0)
        tensor = centered.T @ centered / vectors.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(tensor)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.0)
    eigenvectors = eigenvectors[:, order]
    total = float(np.sum(eigenvalues))
    pc1 = float(eigenvalues[0] / total) if total > 0.0 else 0.0
    return DispersionSummary(
        tensor=tensor,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        total_dispersion=total,
        pc1_fraction=pc1,
    )


def _primary_drift_labels(
    labels: tuple[str, ...],
    eigenvectors: np.ndarray,
    limit: int = 3,
) -> list[dict[str, object]]:
    if eigenvectors.size == 0:
        return []
    primary = eigenvectors[:, 0]
    order = np.argsort(np.abs(primary))[::-1][:limit]
    return [
        {"label": labels[index], "component": _json_float(primary[index])}
        for index in order
    ]


def _json_matrix(values: np.ndarray) -> list[list[float | None]]:
    return [
        [_json_float(value) for value in row]
        for row in np.asarray(values, dtype=float)
    ]


def _json_float(value: float) -> float | None:
    scalar = float(value)
    if isfinite(scalar):
        return scalar
    return None
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python -m unittest tests.test_kinematics -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 2**

Run:

```bash
git add decision_pga/kinematics.py tests/test_kinematics.py
git commit -m "Add kinematic trajectory metrics"
```

Expected: commit succeeds.

## Task 3: Deflection/Jerk Behavior And Public Exports

**Files:**
- Modify: `tests/test_kinematics.py`
- Modify: `decision_pga/__init__.py`

- [ ] **Step 1: Write failing behavior/export tests**

Append these methods inside `TestKinematicTrajectory` in `tests/test_kinematics.py`:

```python
    def test_final_deflection_increases_final_step_jerk(self):
        smooth = np.array(
            [
                [
                    [0.70, 0.20, 0.10],
                    [0.55, 0.35, 0.10],
                    [0.40, 0.50, 0.10],
                    [0.25, 0.65, 0.10],
                ],
                [
                    [0.68, 0.22, 0.10],
                    [0.53, 0.37, 0.10],
                    [0.38, 0.52, 0.10],
                    [0.23, 0.67, 0.10],
                ],
            ]
        )
        deflected = smooth.copy()
        deflected[1, 3, :] = [0.10, 0.20, 0.70]

        smooth_payload = diagnose_kinematic_trajectory(smooth).to_dict()
        deflected_payload = diagnose_kinematic_trajectory(deflected).to_dict()

        self.assertGreater(
            deflected_payload["step_jerk"][-1],
            smooth_payload["step_jerk"][-1] * 3.0,
        )
        self.assertGreater(deflected_payload["systemic_jerk"], smooth_payload["systemic_jerk"])

    def test_primary_drift_labels_use_supplied_labels(self):
        runs = np.array(
            [
                [
                    [0.70, 0.20, 0.10],
                    [0.55, 0.35, 0.10],
                    [0.40, 0.50, 0.10],
                ],
                [
                    [0.20, 0.70, 0.10],
                    [0.35, 0.55, 0.10],
                    [0.50, 0.40, 0.10],
                ],
            ]
        )

        payload = diagnose_kinematic_trajectory(
            runs,
            labels=["retrieve", "draft", "abstain"],
        ).to_dict()

        drift_labels = {item["label"] for item in payload["primary_drift_labels"]}
        self.assertIn("retrieve", drift_labels)
        self.assertIn("draft", drift_labels)

    def test_public_package_exports_kinematic_api(self):
        import decision_pga

        self.assertTrue(hasattr(decision_pga, "diagnose_kinematic_trajectory"))
        self.assertTrue(hasattr(decision_pga, "KinematicTrajectoryDiagnostic"))
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
python -m unittest tests.test_kinematics.TestKinematicTrajectory.test_public_package_exports_kinematic_api tests.test_kinematics.TestKinematicTrajectory.test_final_deflection_increases_final_step_jerk tests.test_kinematics.TestKinematicTrajectory.test_primary_drift_labels_use_supplied_labels -v
```

Expected: FAIL because the package exports are missing. If the drift-label tests pass before the export fix, keep them as regression coverage.

- [ ] **Step 3: Export the new API**

In `decision_pga/__init__.py`, add this import block after the evaluation imports:

```python
from .kinematics import (
    DispersionSummary,
    KinematicTrajectoryDiagnostic,
    diagnose_kinematic_trajectory,
)
```

Add these names to `__all__`:

```python
    "DispersionSummary",
    "KinematicTrajectoryDiagnostic",
    "diagnose_kinematic_trajectory",
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python -m unittest tests.test_kinematics -v
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

Run:

```bash
git add decision_pga/__init__.py tests/test_kinematics.py
git commit -m "Export kinematic trajectory API"
```

Expected: commit succeeds.

## Task 4: CLI Source Routing

**Files:**
- Modify: `decision_pga/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI test**

Append this method inside `TestDecisionPGACLI` in `tests/test_cli.py`:

```python
    def test_kinematic_trajectory_payload_returns_motion_metrics(self):
        payload = {
            "source": "kinematic_trajectory",
            "label": "rag tool whiplash",
            "labels": ["retrieve", "draft", "ask_user"],
            "steps": ["input", "rag", "output"],
            "runs": [
                [
                    [0.70, 0.20, 0.10],
                    [0.45, 0.45, 0.10],
                    [0.20, 0.70, 0.10],
                ],
                [
                    [0.72, 0.18, 0.10],
                    [0.48, 0.42, 0.10],
                    [0.10, 0.20, 0.70],
                ],
            ],
        }

        result = _run_cli_with_payload(payload)
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "kinematic_trajectory")
        self.assertEqual(output["diagnostic"]["source_kind"], "kinematic_trajectory")
        self.assertEqual(output["diagnostic"]["steps"], ["input", "rag", "output"])
        self.assertGreater(output["diagnostic"]["systemic_kinetic_energy"], 0.0)
        self.assertGreater(output["diagnostic"]["systemic_jerk"], 0.0)
```

- [ ] **Step 2: Run CLI test and verify RED**

Run:

```bash
python -m unittest tests.test_cli.TestDecisionPGACLI.test_kinematic_trajectory_payload_returns_motion_metrics -v
```

Expected: FAIL with an unsupported source error.

- [ ] **Step 3: Add CLI routing**

In `decision_pga/cli.py`, add this import near the existing diagnostic imports:

```python
from .kinematics import diagnose_kinematic_trajectory
```

In `diagnose_payload`, add this branch after `trajectory_steps`:

```python
    if source == "kinematic_trajectory":
        return _diagnose_kinematic_trajectory_payload(payload)
```

Update the unsupported-source message to include `kinematic_trajectory`:

```python
    raise ValueError(
        "source must be one of 'probability_cloud', 'model_outputs', "
        "'sampled_responses', 'trajectory_steps', 'kinematic_trajectory', "
        "'provider_scores', or 'provider_token_scores'."
    )
```

Add this helper after `_diagnose_trajectory_steps_payload`:

```python
def _diagnose_kinematic_trajectory_payload(payload: Mapping[str, object]) -> dict[str, object]:
    result = diagnose_kinematic_trajectory(
        _required(payload, "runs"),
        labels=_optional_sequence(payload, "labels"),
        step_names=_optional_sequence(payload, "steps"),
        label=_optional_string(payload, "label"),
    )
    return {
        "source": "kinematic_trajectory",
        "diagnostic": result.to_dict(),
    }
```

- [ ] **Step 4: Run CLI test and verify GREEN**

Run:

```bash
python -m unittest tests.test_cli.TestDecisionPGACLI.test_kinematic_trajectory_payload_returns_motion_metrics -v
```

Expected: PASS.

- [ ] **Step 5: Run CLI and kinematics test modules**

Run:

```bash
python -m unittest tests.test_kinematics tests.test_cli -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

Run:

```bash
git add decision_pga/cli.py tests/test_cli.py
git commit -m "Route kinematic trajectory CLI payloads"
```

Expected: commit succeeds.

## Task 5: Example Fixture And Documentation

**Files:**
- Create: `examples/agent/kinematic_trajectory_rag_tool_whiplash.json`
- Create: `docs/kinematic-trajectory.md`
- Modify: `docs/agent-toolkit.md`
- Modify: `tests/test_agent_toolkit.py`

- [ ] **Step 1: Write failing example coverage test**

In `tests/test_agent_toolkit.py`, add this method to the existing test class:

```python
    def test_kinematic_trajectory_example_runs_through_cli(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "decision_pga.cli",
                "diagnose",
                "examples/agent/kinematic_trajectory_rag_tool_whiplash.json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(output["source"], "kinematic_trajectory")
        self.assertGreater(output["diagnostic"]["systemic_jerk"], 0.0)
```

If `tests/test_agent_toolkit.py` does not already import `json`, `subprocess`, or `sys`, add:

```python
import json
import subprocess
import sys
```

- [ ] **Step 2: Run example test and verify RED**

Run:

```bash
python -m unittest tests.test_agent_toolkit.TestAgentToolkitAdoptionArtifacts.test_kinematic_trajectory_example_runs_through_cli -v
```

Expected: FAIL because the example file does not exist.

- [ ] **Step 3: Add example fixture**

Create `examples/agent/kinematic_trajectory_rag_tool_whiplash.json`:

```json
{
  "source": "kinematic_trajectory",
  "label": "RAG/tool trajectory with final-step whiplash",
  "labels": ["retrieve_evidence", "draft_answer", "ask_user", "abstain"],
  "steps": ["input", "rag_context", "tool_selection", "final_output"],
  "runs": [
    [
      [0.62, 0.18, 0.12, 0.08],
      [0.44, 0.38, 0.10, 0.08],
      [0.20, 0.66, 0.08, 0.06],
      [0.12, 0.78, 0.06, 0.04]
    ],
    [
      [0.64, 0.16, 0.12, 0.08],
      [0.42, 0.40, 0.10, 0.08],
      [0.18, 0.68, 0.08, 0.06],
      [0.10, 0.80, 0.06, 0.04]
    ],
    [
      [0.60, 0.20, 0.12, 0.08],
      [0.40, 0.42, 0.10, 0.08],
      [0.20, 0.64, 0.10, 0.06],
      [0.08, 0.18, 0.68, 0.06]
    ],
    [
      [0.61, 0.19, 0.12, 0.08],
      [0.41, 0.41, 0.10, 0.08],
      [0.19, 0.65, 0.10, 0.06],
      [0.08, 0.20, 0.66, 0.06]
    ]
  ]
}
```

- [ ] **Step 4: Add docs**

Create `docs/kinematic-trajectory.md`:

```markdown
# Kinematic Trajectory Diagnostics

`kinematic_trajectory` diagnoses observed movement across multi-step agent or
application traces. It accepts a tensor shaped as `runs x steps x labels`, where
each row is a probability-like distribution over the same candidate labels.

This diagnostic reports motion in Fisher-Rao probability geometry. It does not
inspect hidden model activations or prove causal internal forces.

## Run The Example

```bash
decision-pga diagnose --pretty examples/agent/kinematic_trajectory_rag_tool_whiplash.json
```

## Reading The Output

- `canonical_path_probabilities`: the Fréchet mean decision state at each step.
- `step_kinetic_energy`: average geodesic movement for each transition.
- `step_jerk`: average change in velocity direction or magnitude between
  neighboring transitions.
- `systemic_kinetic_energy`: overall trajectory movement.
- `systemic_jerk`: overall sharp deflection.
- `velocity_dispersion`: whether runs share a similar drift axis or split into
  different directions.
- `acceleration_comparison`: the first version uses `ambient_tangent_delta`,
  an approximate comparison of neighboring velocity vectors in embedding
  coordinates.

Use low kinetic energy and low jerk as a stable-path signal. Use high jerk as a
review signal that one step sharply deflected the observed decision state.
```

In `docs/agent-toolkit.md`, add this paragraph after the list of MCP server tools:

```markdown
For multi-run traces with explicit operational steps, use
`source: "kinematic_trajectory"` instead of collapsing the trace into rolling
windows. See `docs/kinematic-trajectory.md` for the tensor contract and the
metric-first velocity/jerk output.
```

- [ ] **Step 5: Run example and docs tests**

Run:

```bash
python -m unittest tests.test_agent_toolkit -v
python -m decision_pga.cli diagnose --pretty examples/agent/kinematic_trajectory_rag_tool_whiplash.json
```

Expected: tests PASS, CLI prints JSON with `"source": "kinematic_trajectory"` and positive `systemic_jerk`.

- [ ] **Step 6: Commit Task 5**

Run:

```bash
git add examples/agent/kinematic_trajectory_rag_tool_whiplash.json docs/kinematic-trajectory.md docs/agent-toolkit.md tests/test_agent_toolkit.py
git commit -m "Document kinematic trajectory diagnostics"
```

Expected: commit succeeds.

## Task 6: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused suite**

Run:

```bash
python -m unittest tests.test_kinematics tests.test_cli tests.test_agent_toolkit -v
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

Run:

```bash
python -m unittest discover -v
```

Expected: PASS.

- [ ] **Step 3: Inspect git status**

Run:

```bash
git status --short --branch
```

Expected: clean working tree on the implementation branch after all task commits.

- [ ] **Step 4: Final summary**

Report:

```text
Implemented kinematic_trajectory diagnostics with tested Python API, CLI routing, example fixture, and docs.
Verification: python -m unittest discover -v
```

## Self-Review Notes

Spec coverage:

- Integrated source type: Task 4.
- Python API and module: Tasks 1-3.
- Tensor validation: Task 1.
- Canonical path, velocity, acceleration, kinetic energy, jerk, dispersion: Task 2.
- Public export: Task 3.
- CLI payload and example: Tasks 4-5.
- Documentation and approximation caveat: Task 5.
- TDD red/green cadence: every task starts with a failing test and verifies it.

Intentional exclusions:

- MCP exposure is not included.
- Plotting is not included.
- Parallel transport acceleration is not included.
- Named kinematic states are not included.
- Raw velocity and acceleration matrices are not returned in the JSON payload.
