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
            "eigenvectors": _json_matrix(self.eigenvectors),
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
