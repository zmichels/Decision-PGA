"""Provider-neutral adapters from model outputs to Decision-PGA diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Sequence

import numpy as np

from .diagnostics import (
    DecisionPGAConfig,
    DecisionPGADiagnostic,
    diagnose_probability_cloud,
)
from .probability_pga import normalize_probabilities


ObservationKind = Literal["probabilities", "logprobs", "logits"]


@dataclass(frozen=True)
class ModelOutputObservation:
    """One candidate-aligned model observation for a decision point."""

    values: Mapping[str, float] | Sequence[float]
    kind: ObservationKind = "logprobs"
    observation_id: str | None = None
    source: str | None = None
    metadata: Mapping[str, object] | None = None


@dataclass(frozen=True)
class ModelOutputDiagnostic:
    """Adapter result that feeds the stable Decision-PGA diagnostic contract."""

    probabilities: np.ndarray
    labels: tuple[str, ...]
    diagnostic: DecisionPGADiagnostic
    observation_count: int
    input_kinds: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable payload for tool wrappers."""

        return {
            "adapter": {
                "labels": list(self.labels),
                "observation_count": self.observation_count,
                "input_kinds": list(self.input_kinds),
            },
            "diagnostic": self.diagnostic.to_dict(),
        }


def probability_cloud_from_observations(
    observations: Sequence[ModelOutputObservation],
    labels: Sequence[str] | None = None,
    eps: float = 1e-12,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Convert candidate-aligned model observations into a probability cloud."""

    items = tuple(observations)
    if not items:
        raise ValueError("observations must contain at least one item.")

    label_tuple = _resolve_labels(items, labels)
    rows = [
        _observation_to_probability_row(item, label_tuple, eps)
        for item in items
    ]
    return np.vstack(rows), label_tuple


def diagnose_model_outputs(
    observations: Sequence[ModelOutputObservation],
    labels: Sequence[str] | None = None,
    config: DecisionPGAConfig | None = None,
    label: str | None = None,
    eps: float = 1e-12,
) -> ModelOutputDiagnostic:
    """Diagnose model output observations through the Decision-PGA policy layer."""

    items = tuple(observations)
    probabilities, label_tuple = probability_cloud_from_observations(items, labels, eps)
    diagnostic = diagnose_probability_cloud(
        probabilities,
        labels=label_tuple,
        config=config,
        label=label,
    )
    input_kinds = tuple(dict.fromkeys(item.kind for item in items))
    return ModelOutputDiagnostic(
        probabilities=probabilities,
        labels=label_tuple,
        diagnostic=diagnostic,
        observation_count=len(items),
        input_kinds=input_kinds,
    )


def _observation_to_probability_row(
    observation: ModelOutputObservation,
    labels: tuple[str, ...],
    eps: float,
) -> np.ndarray:
    values = _values_for_labels(observation.values, labels)
    if observation.kind == "probabilities":
        return normalize_probabilities(values, eps=eps)[0]
    if observation.kind in {"logprobs", "logits"}:
        return _softmax(values, eps)
    raise ValueError("kind must be one of 'probabilities', 'logprobs', or 'logits'.")


def _resolve_labels(
    observations: tuple[ModelOutputObservation, ...],
    labels: Sequence[str] | None,
) -> tuple[str, ...]:
    if labels is not None:
        label_tuple = tuple(labels)
        if len(label_tuple) < 2:
            raise ValueError("labels must contain at least two candidates.")
        return label_tuple

    first_values = observations[0].values
    if isinstance(first_values, Mapping):
        label_tuple = tuple(first_values.keys())
        if len(label_tuple) < 2:
            raise ValueError("mapping observations must contain at least two candidates.")
        return label_tuple

    width = len(first_values)
    if width < 2:
        raise ValueError("array observations must contain at least two candidates.")
    return tuple(f"class_{index}" for index in range(width))


def _values_for_labels(
    values: Mapping[str, float] | Sequence[float],
    labels: tuple[str, ...],
) -> np.ndarray:
    if isinstance(values, Mapping):
        missing = [label for label in labels if label not in values]
        if missing:
            raise ValueError(f"observation is missing candidate labels: {missing}")
        vector = np.array([values[label] for label in labels], dtype=float)
    else:
        vector = np.asarray(values, dtype=float)
        if vector.ndim != 1:
            raise ValueError("observation values must be a one-dimensional vector.")
        if vector.shape[0] != len(labels):
            raise ValueError("observation values must match the number of labels.")

    if np.any(np.isnan(vector)) or np.any(np.isposinf(vector)):
        raise ValueError("observation values cannot contain NaN or positive infinity.")
    return vector


def _softmax(scores: np.ndarray, eps: float) -> np.ndarray:
    if np.all(np.isneginf(scores)):
        raise ValueError("at least one log score must be finite.")
    shifted = scores - np.max(scores)
    weights = np.exp(shifted)
    return normalize_probabilities(weights, eps=eps)[0]
