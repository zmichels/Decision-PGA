"""Local stdio MCP server for Decision-PGA diagnostics."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields
from typing import Any

import numpy as np

from .diagnostics import DecisionPGAConfig, diagnose_probability_cloud
from .model_adapters import ModelOutputObservation, diagnose_model_outputs
from .source_adapters import (
    diagnose_sampled_responses,
    diagnose_trajectory_steps,
)


def diagnose_probability_cloud_tool(
    probabilities: Sequence[Sequence[float]],
    labels: Sequence[str] | None = None,
    config: Mapping[str, float] | None = None,
    label: str | None = None,
) -> dict[str, object]:
    """Diagnose a candidate probability cloud."""

    diagnostic = diagnose_probability_cloud(
        np.asarray(probabilities, dtype=float),
        labels=labels,
        config=_config(config),
        label=label,
    )
    return {
        "source": "probability_cloud",
        "diagnostic": diagnostic.to_dict(),
    }


def diagnose_model_outputs_tool(
    observations: Sequence[object],
    labels: Sequence[str] | None = None,
    kind: str = "logprobs",
    config: Mapping[str, float] | None = None,
    label: str | None = None,
) -> dict[str, object]:
    """Diagnose candidate-aligned probabilities, logprobs, or logits."""

    result = diagnose_model_outputs(
        [_model_output_observation(item, kind) for item in observations],
        labels=labels,
        config=_config(config),
        label=label,
    )
    payload = {"source": "model_outputs"}
    payload.update(result.to_dict())
    return payload


def diagnose_sampled_responses_tool(
    responses: Sequence[str],
    labels: Sequence[str],
    aliases: Mapping[str, Sequence[str]] | None = None,
    window_size: int = 5,
    step: int = 1,
    unknown_policy: str = "ignore",
    config: Mapping[str, float] | None = None,
    label: str | None = None,
) -> dict[str, object]:
    """Diagnose rolling windows of sampled free-form responses."""

    result = diagnose_sampled_responses(
        responses,
        labels=labels,
        aliases=aliases,
        window_size=window_size,
        step=step,
        unknown_policy=unknown_policy,  # type: ignore[arg-type]
        config=_config(config),
        label=label,
    )
    payload = {"source": "sampled_responses"}
    payload.update(result.to_dict())
    return payload


def diagnose_trajectory_steps_tool(
    steps: Sequence[str],
    labels: Sequence[str] | None = None,
    window_size: int = 5,
    step: int = 1,
    config: Mapping[str, float] | None = None,
    label: str | None = None,
) -> dict[str, object]:
    """Diagnose rolling windows of agent trajectory choices."""

    result = diagnose_trajectory_steps(
        steps,
        labels=labels,
        window_size=window_size,
        step=step,
        config=_config(config),
        label=label,
    )
    payload = {"source": "trajectory_steps"}
    payload.update(result.to_dict())
    return payload


def explain_decision_pga_metrics() -> dict[str, str]:
    """Return short descriptions of stable Decision-PGA output metrics."""

    return {
        "total_dispersion": "Total tangent-space dispersion of the probability cloud on the Fisher-Rao sphere.",
        "pc1_fraction": "Fraction of dispersion explained by the first principal geodesic direction.",
        "anisotropy_ratio": "Ratio of first to second tangent dispersion eigenvalues.",
        "mean_margin": "Gap between the top two labels in the intrinsic mean probability.",
        "mean_sample_margin": "Average top-two margin across individual probability samples.",
        "top_label_switch_rate": "Fraction of adjacent samples whose top label changes.",
        "half_geodesic_distance": "Fisher-Rao/square-root geodesic distance between first-half and second-half cloud means.",
    }


def build_server() -> Any:
    """Build the FastMCP server. Requires installing the `mcp` extra."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The MCP server requires the optional dependency: "
            "python -m pip install -e '.[mcp]'"
        ) from exc

    mcp = FastMCP("decision-pga")

    mcp.tool(name="diagnose_probability_cloud")(diagnose_probability_cloud_tool)
    mcp.tool(name="diagnose_model_outputs")(diagnose_model_outputs_tool)
    mcp.tool(name="diagnose_sampled_responses")(diagnose_sampled_responses_tool)
    mcp.tool(name="diagnose_trajectory_steps")(diagnose_trajectory_steps_tool)
    mcp.tool()(explain_decision_pga_metrics)
    return mcp


def main() -> None:
    """Run the local stdio MCP server."""

    build_server().run()


def _model_output_observation(item: object, default_kind: str) -> ModelOutputObservation:
    if isinstance(item, Mapping) and "values" in item:
        return ModelOutputObservation(
            values=item["values"],  # type: ignore[arg-type]
            kind=str(item.get("kind", default_kind)),  # type: ignore[arg-type]
            observation_id=_string_or_none(item.get("observation_id")),
            source=_string_or_none(item.get("source")),
            metadata=_mapping_or_none(item.get("metadata")),
        )
    return ModelOutputObservation(values=item, kind=default_kind)  # type: ignore[arg-type]


def _config(value: Mapping[str, float] | None) -> DecisionPGAConfig | None:
    if value is None:
        return None
    allowed = {field.name for field in fields(DecisionPGAConfig)}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unknown config fields: {unknown}")
    return DecisionPGAConfig(**value)


def _string_or_none(value: object) -> str | None:
    return None if value is None else str(value)


def _mapping_or_none(value: object) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("metadata must be an object.")
    return value


if __name__ == "__main__":
    main()
