"""Entropy, margin, and drift baselines for Decision-PGA evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np

from .probability_pga import normalize_probabilities


@dataclass(frozen=True)
class BaselineMetrics:
    """Baseline summaries for a categorical probability cloud."""

    entropy: np.ndarray
    margin: np.ndarray
    mean_entropy: float
    entropy_variance: float
    mean_margin: float
    min_margin: float
    top_label_switch_rate: float
    half_jensen_shannon_drift: float
    half_euclidean_drift: float

    def to_dict(self) -> dict[str, object]:
        return {
            "entropy": [_json_float(value) for value in self.entropy],
            "margin": [_json_float(value) for value in self.margin],
            "mean_entropy": _json_float(self.mean_entropy),
            "entropy_variance": _json_float(self.entropy_variance),
            "mean_margin": _json_float(self.mean_margin),
            "min_margin": _json_float(self.min_margin),
            "top_label_switch_rate": _json_float(self.top_label_switch_rate),
            "half_jensen_shannon_drift": _json_float(self.half_jensen_shannon_drift),
            "half_euclidean_drift": _json_float(self.half_euclidean_drift),
        }


def baseline_metrics(probs: np.ndarray, eps: float = 1e-12) -> BaselineMetrics:
    """Compute non-PGA baseline metrics for a probability cloud."""

    probabilities = normalize_probabilities(probs, eps=eps)
    entropy = -np.sum(probabilities * np.log(probabilities), axis=1)
    sorted_probs = np.sort(probabilities, axis=1)[:, ::-1]
    margin = sorted_probs[:, 0] - sorted_probs[:, 1]
    first_mean, second_mean = _half_window_means(probabilities)

    return BaselineMetrics(
        entropy=entropy,
        margin=margin,
        mean_entropy=float(np.mean(entropy)),
        entropy_variance=float(np.var(entropy)),
        mean_margin=float(np.mean(margin)),
        min_margin=float(np.min(margin)),
        top_label_switch_rate=_top_label_switch_rate(probabilities),
        half_jensen_shannon_drift=_jensen_shannon_divergence(first_mean, second_mean),
        half_euclidean_drift=float(np.linalg.norm(first_mean - second_mean)),
    )


def _half_window_means(probabilities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(probabilities) < 4:
        mean = np.mean(probabilities, axis=0)
        return mean, mean
    midpoint = len(probabilities) // 2
    return (
        np.mean(probabilities[:midpoint], axis=0),
        np.mean(probabilities[midpoint:], axis=0),
    )


def _top_label_switch_rate(probabilities: np.ndarray) -> float:
    if len(probabilities) < 2:
        return 0.0
    top_indices = np.argmax(probabilities, axis=1)
    return float(np.mean(top_indices[1:] != top_indices[:-1]))


def _jensen_shannon_divergence(first: np.ndarray, second: np.ndarray) -> float:
    midpoint = 0.5 * (first + second)
    return float(0.5 * _kl_divergence(first, midpoint) + 0.5 * _kl_divergence(second, midpoint))


def _kl_divergence(values: np.ndarray, reference: np.ndarray) -> float:
    mask = values > 0
    return float(np.sum(values[mask] * np.log(values[mask] / reference[mask])))


def _json_float(value: float) -> float | None:
    scalar = float(value)
    return scalar if isfinite(scalar) else None
