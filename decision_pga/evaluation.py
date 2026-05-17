"""Reproducible evaluation harness for Decision-PGA scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

import numpy as np

from .baselines import BaselineMetrics, baseline_metrics
from .diagnostics import DecisionPGADiagnostic, DecisionState, diagnose_probability_cloud
from .probability_pga import normalize_probabilities, synthetic_probability_cloud


@dataclass(frozen=True)
class ScenarioSpec:
    """One deterministic evaluation scenario."""

    name: str
    kind: str
    expected_state: DecisionState
    n_samples: int
    n_classes: int
    seed: int | None = None
    labels: tuple[str, ...] | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, object], default_seed: int) -> "ScenarioSpec":
        seed = value.get("seed")
        return cls(
            name=_required_string(value, "name"),
            kind=_required_string(value, "kind"),
            expected_state=_required_string(value, "expected_state"),  # type: ignore[arg-type]
            n_samples=int(value.get("n_samples", 96)),
            n_classes=int(value.get("n_classes", 5)),
            seed=default_seed if seed is None else int(seed),
            labels=_optional_string_tuple(value.get("labels")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "expected_state": self.expected_state,
            "n_samples": self.n_samples,
            "n_classes": self.n_classes,
            "seed": self.seed,
            "labels": list(self.labels) if self.labels is not None else None,
        }


@dataclass(frozen=True)
class EvaluationConfig:
    """Scenario set and seed for a Decision-PGA evaluation run."""

    seed: int = 20260517
    scenarios: tuple[ScenarioSpec, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "EvaluationConfig":
        seed = int(value.get("seed", 20260517))
        raw_scenarios = value.get("scenarios")
        if not isinstance(raw_scenarios, Sequence) or isinstance(raw_scenarios, (str, bytes)):
            raise ValueError("evaluation config must include a non-empty 'scenarios' array.")
        scenarios = tuple(
            ScenarioSpec.from_mapping(_mapping(item), seed + index)
            for index, item in enumerate(raw_scenarios)
        )
        if not scenarios:
            raise ValueError("evaluation config must include at least one scenario.")
        return cls(seed=seed, scenarios=scenarios)

    @classmethod
    def default_smoke(cls, seed: int = 20260517) -> "EvaluationConfig":
        return cls(
            seed=seed,
            scenarios=(
                ScenarioSpec("stable_confident", "stable", "stable", 72, 5, seed + 1),
                ScenarioSpec("entropy_matched_binary", "entropy_matched_binary", "binary_ambiguity", 96, 5, seed + 2),
                ScenarioSpec("entropy_matched_diffuse", "entropy_matched_diffuse", "diffuse_uncertainty", 96, 5, seed + 3),
                ScenarioSpec("boundary_sensitive", "boundary", "boundary_sensitive", 96, 5, seed + 4),
                ScenarioSpec("regime_shift", "regime_shift", "regime_shift", 96, 5, seed + 5),
            ),
        )

    @classmethod
    def default_full(cls, seed: int = 20260517) -> "EvaluationConfig":
        return cls(
            seed=seed,
            scenarios=(
                *cls.default_smoke(seed).scenarios,
                ScenarioSpec("stable_low_confidence", "stable_low_confidence", "diffuse_uncertainty", 96, 5, seed + 6),
                ScenarioSpec("class_sweep_3_binary", "entropy_matched_binary", "binary_ambiguity", 96, 3, seed + 7),
                ScenarioSpec("class_sweep_8_diffuse", "entropy_matched_diffuse", "diffuse_uncertainty", 96, 8, seed + 8),
                ScenarioSpec("sample_sweep_24_boundary", "boundary", "boundary_sensitive", 24, 5, seed + 9),
                ScenarioSpec("sample_sweep_160_regime", "regime_shift", "regime_shift", 160, 5, seed + 10),
            ),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
        }


@dataclass(frozen=True)
class ScenarioResult:
    """Evaluation result for one scenario."""

    spec: ScenarioSpec
    diagnostic: DecisionPGADiagnostic
    baselines: BaselineMetrics
    baseline_state: DecisionState

    @property
    def pga_correct(self) -> bool:
        return self.diagnostic.state == self.spec.expected_state

    @property
    def baseline_correct(self) -> bool:
        return self.baseline_state == self.spec.expected_state

    def to_dict(self) -> dict[str, object]:
        diagnostic = self.diagnostic.to_dict()
        return {
            "name": self.spec.name,
            "kind": self.spec.kind,
            "expected_state": self.spec.expected_state,
            "pga_state": self.diagnostic.state,
            "baseline_state": self.baseline_state,
            "pga_correct": self.pga_correct,
            "baseline_correct": self.baseline_correct,
            "top_labels": diagnostic["top_labels"],
            "pga_metrics": diagnostic["metrics"],
            "baseline_metrics": self.baselines.to_dict(),
        }


@dataclass(frozen=True)
class EvaluationReport:
    """Complete benchmark result."""

    config: EvaluationConfig
    scenarios: tuple[ScenarioResult, ...]
    states: tuple[str, ...]
    confusion_matrix: tuple[tuple[int, ...], ...]
    baseline_confusion_matrix: tuple[tuple[int, ...], ...]
    advantage: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "config": self.config.to_dict(),
            "states": list(self.states),
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "confusion_matrix": _matrix_to_dict(self.states, self.confusion_matrix),
            "baseline_confusion_matrix": _matrix_to_dict(self.states, self.baseline_confusion_matrix),
            "advantage": self.advantage,
        }


def run_evaluation(config: EvaluationConfig | None = None) -> EvaluationReport:
    """Run Decision-PGA and baseline classifiers over a deterministic scenario set."""

    evaluation_config = config or EvaluationConfig.default_full()
    if not evaluation_config.scenarios:
        raise ValueError("evaluation config must include at least one scenario.")

    results = []
    for spec in evaluation_config.scenarios:
        probabilities = scenario_probability_cloud(spec)
        labels = spec.labels or tuple(f"class_{index}" for index in range(spec.n_classes))
        baselines = baseline_metrics(probabilities)
        diagnostic = diagnose_probability_cloud(probabilities, labels=labels, label=spec.name)
        results.append(
            ScenarioResult(
                spec=spec,
                diagnostic=diagnostic,
                baselines=baselines,
                baseline_state=classify_with_baselines(baselines, spec.n_classes),
            )
        )

    states = tuple(sorted(
        {result.spec.expected_state for result in results}
        | {result.diagnostic.state for result in results}
        | {result.baseline_state for result in results}
    ))
    confusion = _confusion_matrix(results, states, predictor="pga")
    baseline_confusion = _confusion_matrix(results, states, predictor="baseline")
    return EvaluationReport(
        config=evaluation_config,
        scenarios=tuple(results),
        states=states,
        confusion_matrix=confusion,
        baseline_confusion_matrix=baseline_confusion,
        advantage=_advantage_summary(results),
    )


def scenario_probability_cloud(spec: ScenarioSpec) -> np.ndarray:
    """Generate the probability cloud for an evaluation scenario."""

    if spec.n_samples <= 0:
        raise ValueError("n_samples must be positive.")
    if spec.n_classes < 3:
        raise ValueError("n_classes must be at least 3.")

    seed = 0 if spec.seed is None else spec.seed
    rng = np.random.default_rng(seed)
    kind = spec.kind.lower()
    if kind in {"stable", "binary_ambiguity", "diffuse_uncertainty", "boundary", "regime_shift"}:
        return synthetic_probability_cloud(kind, spec.n_samples, spec.n_classes, seed=seed)
    if kind == "entropy_matched_binary":
        return _entropy_matched_binary(spec.n_samples, spec.n_classes, rng)
    if kind == "entropy_matched_diffuse":
        return _entropy_matched_diffuse(spec.n_samples, spec.n_classes, rng)
    if kind == "stable_low_confidence":
        center = _low_confidence_center(spec.n_classes)
        return rng.dirichlet(180.0 * center, size=spec.n_samples)
    raise ValueError(f"unknown scenario kind: {spec.kind}")


def classify_with_baselines(metrics: BaselineMetrics, n_classes: int) -> DecisionState:
    """A deliberately simple entropy/margin/drift baseline classifier."""

    uniform_entropy = float(np.log(n_classes))
    if metrics.half_jensen_shannon_drift >= 0.30 and metrics.mean_margin >= 0.35:
        return "regime_shift"
    if metrics.mean_entropy <= 0.55 * uniform_entropy and metrics.mean_margin >= 0.45:
        return "stable"
    if metrics.mean_margin <= 0.12 and metrics.top_label_switch_rate <= 0.35:
        return "boundary_sensitive"
    if metrics.mean_margin <= 0.12:
        return "binary_ambiguity"
    return "diffuse_uncertainty"


def _entropy_matched_binary(n_samples: int, n_classes: int, rng: np.random.Generator) -> np.ndarray:
    axis = rng.beta(0.7, 0.7, size=n_samples)
    top_pair_mass = 0.88
    cloud = np.full((n_samples, n_classes), (1.0 - top_pair_mass) / (n_classes - 2))
    cloud[:, 0] = 0.44 + 0.28 * (axis - 0.5)
    cloud[:, 1] = top_pair_mass - cloud[:, 0]
    noise = rng.dirichlet(np.full(n_classes, 18.0), size=n_samples)
    return normalize_probabilities(0.94 * cloud + 0.06 * noise)


def _entropy_matched_diffuse(n_samples: int, n_classes: int, rng: np.random.Generator) -> np.ndarray:
    raw = rng.dirichlet(np.full(n_classes, 0.42), size=n_samples)
    softened = 0.82 * raw + 0.18 / n_classes
    return normalize_probabilities(softened)


def _low_confidence_center(n_classes: int) -> np.ndarray:
    values = np.full(n_classes, (1.0 - 0.42 - 0.30) / (n_classes - 2))
    values[0] = 0.42
    values[1] = 0.30
    return normalize_probabilities(values)[0]


def _confusion_matrix(
    results: Sequence[ScenarioResult],
    states: tuple[str, ...],
    predictor: str,
) -> tuple[tuple[int, ...], ...]:
    index = {state: position for position, state in enumerate(states)}
    matrix = np.zeros((len(states), len(states)), dtype=int)
    for result in results:
        predicted = result.diagnostic.state if predictor == "pga" else result.baseline_state
        matrix[index[result.spec.expected_state], index[predicted]] += 1
    return tuple(tuple(int(value) for value in row) for row in matrix)


def _advantage_summary(results: Sequence[ScenarioResult]) -> dict[str, object]:
    pga_accuracy = float(np.mean([result.pga_correct for result in results]))
    baseline_accuracy = float(np.mean([result.baseline_correct for result in results]))
    binary = _find_result(results, "entropy_matched_binary")
    diffuse = _find_result(results, "entropy_matched_diffuse")
    entropy_gap = 0.0
    pga_gap = 0.0
    if binary is not None and diffuse is not None:
        entropy_gap = abs(binary.baselines.mean_entropy - diffuse.baselines.mean_entropy)
        pga_gap = abs(
            binary.diagnostic.metrics["pc1_fraction"]
            - diffuse.diagnostic.metrics["pc1_fraction"]
        )

    if pga_accuracy > baseline_accuracy or pga_gap > entropy_gap:
        claim = (
            "PGA shows a conservative advantage on this fixture set: it exposes "
            "geometry that entropy/margin summaries compress."
        )
    else:
        claim = (
            "No conservative PGA advantage is established on this fixture set; "
            "baseline summaries explain the tested states as well as PGA."
        )

    return {
        "pga_accuracy": _json_float(pga_accuracy),
        "baseline_accuracy": _json_float(baseline_accuracy),
        "entropy_binary_diffuse_gap": _json_float(entropy_gap),
        "pga_binary_diffuse_gap": _json_float(pga_gap),
        "claim": claim,
    }


def _find_result(results: Sequence[ScenarioResult], name: str) -> ScenarioResult | None:
    for result in results:
        if result.spec.name == name:
            return result
    return None


def _matrix_to_dict(
    states: tuple[str, ...],
    matrix: tuple[tuple[int, ...], ...],
) -> dict[str, object]:
    return {
        "states": list(states),
        "rows": [
            {"expected": state, "counts": dict(zip(states, row, strict=True))}
            for state, row in zip(states, matrix, strict=True)
        ],
    }


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("scenario entries must be objects.")
    return value


def _required_string(value: Mapping[str, object], key: str) -> str:
    raw = value.get(key)
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"scenario must include a non-empty string '{key}'.")
    return raw


def _optional_string_tuple(value: object) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("labels must be an array of strings.")
    labels = tuple(str(item) for item in value)
    if len(labels) < 2:
        raise ValueError("labels must contain at least two entries.")
    return labels


def _json_float(value: float) -> float | None:
    scalar = float(value)
    return scalar if isfinite(scalar) else None
