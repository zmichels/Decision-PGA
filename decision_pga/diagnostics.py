"""Agent-facing Decision-PGA diagnostic policy layer."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal, Sequence

import numpy as np

from .probability_pga import (
    ProbabilityPGAResult,
    intrinsic_mean_sphere,
    normalize_probabilities,
    pga_probability_cloud,
    sqrt_embed,
)


DecisionState = Literal[
    "stable",
    "binary_ambiguity",
    "diffuse_uncertainty",
    "boundary_sensitive",
    "regime_shift",
]

DecisionAction = Literal[
    "proceed",
    "clarify_between_top_labels",
    "gather_more_evidence",
    "inspect_sensitivity",
    "segment_or_replan",
]


@dataclass(frozen=True)
class DecisionPGAConfig:
    """Thresholds for mapping PGA metrics into agent-facing states."""

    stable_max_dispersion: float = 0.02
    stable_min_mean_margin: float = 0.45
    diffuse_min_dispersion: float = 0.08
    diffuse_max_pc1_fraction: float = 0.65
    ambiguity_min_pc1_fraction: float = 0.80
    ambiguity_max_mean_margin: float = 0.12
    boundary_min_pc1_fraction: float = 0.90
    boundary_max_mean_margin: float = 0.12
    boundary_min_half_distance: float = 0.15
    boundary_max_switch_rate: float = 0.20
    regime_shift_min_half_distance: float = 0.65
    regime_shift_min_sample_margin: float = 0.40


@dataclass(frozen=True)
class DecisionPGADiagnostic:
    """JSON-friendly agent diagnostic backed by a ProbabilityPGAResult."""

    state: DecisionState
    recommended_action: DecisionAction
    rationale: str
    metrics: dict[str, float]
    top_labels: tuple[str, ...]
    pga_result: ProbabilityPGAResult
    label: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable payload for agent tool wrappers."""

        return {
            "state": self.state,
            "recommended_action": self.recommended_action,
            "rationale": self.rationale,
            "label": self.label,
            "top_labels": list(self.top_labels),
            "metrics": {
                key: _json_float(value)
                for key, value in self.metrics.items()
            },
        }


def diagnose_probability_cloud(
    probs: np.ndarray,
    labels: Sequence[str] | None = None,
    config: DecisionPGAConfig | None = None,
    label: str | None = None,
) -> DecisionPGADiagnostic:
    """Map a probability cloud into an agent-facing decision state and action."""

    probabilities = normalize_probabilities(probs)
    threshold = config or DecisionPGAConfig()
    pga_result = pga_probability_cloud(probabilities, label=label)
    top_labels = _top_labels(pga_result.mean_probability, labels)
    metrics = _diagnostic_metrics(probabilities, pga_result)

    state, action, rationale = _classify(pga_result, metrics, threshold)
    return DecisionPGADiagnostic(
        state=state,
        recommended_action=action,
        rationale=rationale,
        metrics=metrics,
        top_labels=top_labels,
        pga_result=pga_result,
        label=label,
    )


def _classify(
    pga_result: ProbabilityPGAResult,
    metrics: dict[str, float],
    config: DecisionPGAConfig,
) -> tuple[DecisionState, DecisionAction, str]:
    if (
        pga_result.total_dispersion <= config.stable_max_dispersion
        and pga_result.mean_margin >= config.stable_min_mean_margin
    ):
        return (
            "stable",
            "proceed",
            "The cloud is tight and the mean decision margin is high.",
        )

    if (
        metrics["half_geodesic_distance"] >= config.regime_shift_min_half_distance
        and metrics["mean_sample_margin"] >= config.regime_shift_min_sample_margin
    ):
        return (
            "regime_shift",
            "segment_or_replan",
            "Early and late cloud means are far apart while samples remain locally decisive.",
        )

    if (
        pga_result.pc1_fraction <= config.diffuse_max_pc1_fraction
        and pga_result.total_dispersion >= config.diffuse_min_dispersion
    ):
        return (
            "diffuse_uncertainty",
            "gather_more_evidence",
            "Dispersion is broad rather than concentrated along one decision axis.",
        )

    if (
        pga_result.pc1_fraction >= config.boundary_min_pc1_fraction
        and pga_result.mean_margin <= config.boundary_max_mean_margin
        and metrics["half_geodesic_distance"] >= config.boundary_min_half_distance
        and metrics["top_label_switch_rate"] <= config.boundary_max_switch_rate
    ):
        return (
            "boundary_sensitive",
            "inspect_sensitivity",
            "Samples move coherently along a low-margin decision boundary.",
        )

    if (
        pga_result.pc1_fraction >= config.ambiguity_min_pc1_fraction
        and pga_result.mean_margin <= config.ambiguity_max_mean_margin
    ):
        return (
            "binary_ambiguity",
            "clarify_between_top_labels",
            "Most dispersion lies along one axis and the leading mean labels are close.",
        )

    return (
        "diffuse_uncertainty",
        "gather_more_evidence",
        "The cloud does not meet a stronger stable or structured-ambiguity pattern.",
    )


def _diagnostic_metrics(
    probabilities: np.ndarray,
    pga_result: ProbabilityPGAResult,
) -> dict[str, float]:
    sample_margins = _sample_margins(probabilities)
    return {
        "total_dispersion": pga_result.total_dispersion,
        "pc1_fraction": pga_result.pc1_fraction,
        "anisotropy_ratio": pga_result.anisotropy_ratio,
        "mean_margin": pga_result.mean_margin,
        "mean_sample_margin": float(np.mean(sample_margins)),
        "min_sample_margin": float(np.min(sample_margins)),
        "top_label_switch_rate": _top_label_switch_rate(probabilities),
        "half_geodesic_distance": _half_geodesic_distance(probabilities),
    }


def _sample_margins(probabilities: np.ndarray) -> np.ndarray:
    sorted_probs = np.sort(probabilities, axis=1)[:, ::-1]
    return sorted_probs[:, 0] - sorted_probs[:, 1]


def _top_label_switch_rate(probabilities: np.ndarray) -> float:
    if len(probabilities) < 2:
        return 0.0
    top_indices = np.argmax(probabilities, axis=1)
    return float(np.mean(top_indices[1:] != top_indices[:-1]))


def _half_geodesic_distance(probabilities: np.ndarray) -> float:
    if len(probabilities) < 4:
        return 0.0
    midpoint = len(probabilities) // 2
    embedded = sqrt_embed(probabilities)
    first_mean = intrinsic_mean_sphere(embedded[:midpoint])
    second_mean = intrinsic_mean_sphere(embedded[midpoint:])
    return float(np.arccos(np.clip(first_mean @ second_mean, -1.0, 1.0)))


def _top_labels(
    mean_probability: np.ndarray,
    labels: Sequence[str] | None,
) -> tuple[str, ...]:
    if labels is None:
        names = tuple(f"class_{index}" for index in range(mean_probability.shape[0]))
    else:
        names = tuple(labels)
        if len(names) != mean_probability.shape[0]:
            raise ValueError("labels must match the number of probability classes.")
    order = np.argsort(mean_probability)[::-1]
    return tuple(names[index] for index in order)


def _json_float(value: float) -> float | None:
    scalar = float(value)
    if isfinite(scalar):
        return scalar
    return None
