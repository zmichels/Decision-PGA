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
