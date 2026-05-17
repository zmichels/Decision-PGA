"""Adapters from sampled responses and agent trajectories to probability clouds."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Mapping, Sequence

import numpy as np

from .diagnostics import (
    DecisionPGAConfig,
    DecisionPGADiagnostic,
    diagnose_probability_cloud,
)
from .probability_pga import normalize_probabilities


UnknownPolicy = Literal["ignore", "raise"]


@dataclass(frozen=True)
class SampledResponse:
    """One free-form sampled model response."""

    text: str
    response_id: str | None = None
    source: str | None = None
    metadata: Mapping[str, object] | None = None


@dataclass(frozen=True)
class TrajectoryStep:
    """One agent trajectory step with a candidate-aligned choice."""

    choice: str
    step_id: str | None = None
    source: str | None = None
    metadata: Mapping[str, object] | None = None


@dataclass(frozen=True)
class SourceAdapterDiagnostic:
    """Diagnostic result for sampled-response or trajectory adapters."""

    probabilities: np.ndarray
    labels: tuple[str, ...]
    diagnostic: DecisionPGADiagnostic
    source_kind: str
    observation_count: int
    window_size: int
    step: int
    mapped_count: int
    unmapped_count: int = 0

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable payload for agent tool wrappers."""

        return {
            "adapter": {
                "source_kind": self.source_kind,
                "labels": list(self.labels),
                "observation_count": self.observation_count,
                "window_size": self.window_size,
                "step": self.step,
                "mapped_count": self.mapped_count,
                "unmapped_count": self.unmapped_count,
                "row_count": int(self.probabilities.shape[0]),
            },
            "diagnostic": self.diagnostic.to_dict(),
        }


def probability_cloud_from_sampled_responses(
    responses: Sequence[SampledResponse | str],
    labels: Sequence[str],
    aliases: Mapping[str, Sequence[str]] | None = None,
    window_size: int = 5,
    step: int = 1,
    unknown_policy: UnknownPolicy = "ignore",
    eps: float = 1e-12,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Map free-form sampled responses into rolling empirical probabilities."""

    items = tuple(_coerce_response(item) for item in responses)
    label_tuple = _validate_labels(labels)
    assignments = _sampled_response_assignments(
        items,
        label_tuple,
        aliases or {},
        unknown_policy,
    )
    return _rolling_probability_rows(assignments, label_tuple, window_size, step, eps), label_tuple


def diagnose_sampled_responses(
    responses: Sequence[SampledResponse | str],
    labels: Sequence[str],
    aliases: Mapping[str, Sequence[str]] | None = None,
    window_size: int = 5,
    step: int = 1,
    unknown_policy: UnknownPolicy = "ignore",
    config: DecisionPGAConfig | None = None,
    label: str | None = None,
    eps: float = 1e-12,
) -> SourceAdapterDiagnostic:
    """Diagnose rolling free-form response clusters with Decision-PGA."""

    items = tuple(_coerce_response(item) for item in responses)
    label_tuple = _validate_labels(labels)
    assignments = _sampled_response_assignments(
        items,
        label_tuple,
        aliases or {},
        unknown_policy,
    )
    probabilities = _rolling_probability_rows(assignments, label_tuple, window_size, step, eps)
    diagnostic = diagnose_probability_cloud(
        probabilities,
        labels=label_tuple,
        config=config,
        label=label,
    )
    mapped_count = sum(index is not None for index in assignments)
    return SourceAdapterDiagnostic(
        probabilities=probabilities,
        labels=label_tuple,
        diagnostic=diagnostic,
        source_kind="sampled_responses",
        observation_count=len(items),
        window_size=_effective_window_size(len(items), window_size),
        step=step,
        mapped_count=mapped_count,
        unmapped_count=len(assignments) - mapped_count,
    )


def probability_cloud_from_trajectory_steps(
    steps: Sequence[TrajectoryStep | str],
    labels: Sequence[str] | None = None,
    window_size: int = 5,
    step: int = 1,
    eps: float = 1e-12,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Map agent trajectory choices into rolling empirical probabilities."""

    items = tuple(_coerce_step(item) for item in steps)
    label_tuple = _resolve_trajectory_labels(items, labels)
    assignments = [_label_index(item.choice, label_tuple) for item in items]
    return _rolling_probability_rows(assignments, label_tuple, window_size, step, eps), label_tuple


def diagnose_trajectory_steps(
    steps: Sequence[TrajectoryStep | str],
    labels: Sequence[str] | None = None,
    window_size: int = 5,
    step: int = 1,
    config: DecisionPGAConfig | None = None,
    label: str | None = None,
    eps: float = 1e-12,
) -> SourceAdapterDiagnostic:
    """Diagnose rolling agent trajectory choices with Decision-PGA."""

    items = tuple(_coerce_step(item) for item in steps)
    label_tuple = _resolve_trajectory_labels(items, labels)
    assignments = [_label_index(item.choice, label_tuple) for item in items]
    probabilities = _rolling_probability_rows(assignments, label_tuple, window_size, step, eps)
    diagnostic = diagnose_probability_cloud(
        probabilities,
        labels=label_tuple,
        config=config,
        label=label,
    )
    return SourceAdapterDiagnostic(
        probabilities=probabilities,
        labels=label_tuple,
        diagnostic=diagnostic,
        source_kind="trajectory_steps",
        observation_count=len(items),
        window_size=_effective_window_size(len(items), window_size),
        step=step,
        mapped_count=len(assignments),
    )


def _sampled_response_assignments(
    responses: tuple[SampledResponse, ...],
    labels: tuple[str, ...],
    aliases: Mapping[str, Sequence[str]],
    unknown_policy: UnknownPolicy,
) -> list[int | None]:
    if unknown_policy not in {"ignore", "raise"}:
        raise ValueError("unknown_policy must be 'ignore' or 'raise'.")
    match_terms = _match_terms(labels, aliases)
    assignments: list[int | None] = []
    for response in responses:
        matched = _match_response(response.text, labels, match_terms)
        if matched is None and unknown_policy == "raise":
            raise ValueError(f"could not map sampled response: {response.text!r}")
        assignments.append(matched)
    return assignments


def _rolling_probability_rows(
    assignments: Sequence[int | None],
    labels: tuple[str, ...],
    window_size: int,
    step: int,
    eps: float,
) -> np.ndarray:
    if not assignments:
        raise ValueError("at least one observation is required.")
    if window_size <= 0:
        raise ValueError("window_size must be positive.")
    if step <= 0:
        raise ValueError("step must be positive.")

    width = len(labels)
    effective_window = _effective_window_size(len(assignments), window_size)
    rows = []
    for start in range(0, len(assignments) - effective_window + 1, step):
        counts = np.zeros(width, dtype=float)
        for index in assignments[start:start + effective_window]:
            if index is not None:
                counts[index] += 1.0
        if np.sum(counts) <= 0.0:
            counts += 1.0
        rows.append(normalize_probabilities(counts, eps=eps)[0])
    return np.vstack(rows)


def _effective_window_size(observation_count: int, window_size: int) -> int:
    return min(observation_count, window_size)


def _match_terms(
    labels: tuple[str, ...],
    aliases: Mapping[str, Sequence[str]],
) -> dict[str, tuple[str, ...]]:
    terms = {}
    for label in labels:
        label_aliases = aliases.get(label, ())
        terms[label] = tuple(_normalize_text(term) for term in (label, *label_aliases))
    return terms


def _match_response(
    text: str,
    labels: tuple[str, ...],
    match_terms: Mapping[str, tuple[str, ...]],
) -> int | None:
    normalized = _normalize_text(text)
    haystack = f" {normalized} "
    for index, label in enumerate(labels):
        if any(term and f" {term} " in haystack for term in match_terms[label]):
            return index
    return None


def _normalize_text(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(text).lower()).split())


def _label_index(choice: str, labels: tuple[str, ...]) -> int:
    normalized = _normalize_text(choice)
    for index, label in enumerate(labels):
        if normalized == _normalize_text(label):
            return index
    raise ValueError(f"trajectory choice {choice!r} is not in labels.")


def _resolve_trajectory_labels(
    steps: tuple[TrajectoryStep, ...],
    labels: Sequence[str] | None,
) -> tuple[str, ...]:
    if not steps:
        raise ValueError("steps must contain at least one item.")
    if labels is not None:
        return _validate_labels(labels)

    ordered = tuple(dict.fromkeys(item.choice for item in steps))
    return _validate_labels(ordered)


def _validate_labels(labels: Sequence[str]) -> tuple[str, ...]:
    label_tuple = tuple(str(label) for label in labels)
    if len(label_tuple) < 2:
        raise ValueError("labels must contain at least two candidates.")
    if len(set(_normalize_text(label) for label in label_tuple)) != len(label_tuple):
        raise ValueError("labels must be unique after normalization.")
    return label_tuple


def _coerce_response(item: SampledResponse | str) -> SampledResponse:
    if isinstance(item, SampledResponse):
        return item
    return SampledResponse(str(item))


def _coerce_step(item: TrajectoryStep | str) -> TrajectoryStep:
    if isinstance(item, TrajectoryStep):
        return item
    return TrajectoryStep(str(item))
