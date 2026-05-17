"""Command-line JSON interface for Decision-PGA diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import fields
from pathlib import Path
from typing import TextIO

import numpy as np

from .diagnostics import DecisionPGAConfig, diagnose_probability_cloud
from .evaluation import EvaluationConfig, run_evaluation
from .model_adapters import ModelOutputObservation, diagnose_model_outputs
from .provider_bridges import (
    observation_from_token_scores,
    observations_from_provider_scores,
)
from .reporting import write_evaluation_report
from .source_adapters import (
    SampledResponse,
    TrajectoryStep,
    diagnose_sampled_responses,
    diagnose_trajectory_steps,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Decision-PGA CLI."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "diagnose":
        return _run_diagnose(args, sys.stdin, sys.stdout, sys.stderr)
    if args.command == "evaluate":
        return _run_evaluate(args, sys.stdout, sys.stderr)
    parser.print_help(sys.stderr)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decision-pga",
        description="Decision-PGA JSON-in / JSON-out diagnostics.",
    )
    subparsers = parser.add_subparsers(dest="command")
    diagnose = subparsers.add_parser(
        "diagnose",
        help="Run a diagnostic from a JSON payload.",
    )
    diagnose.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input JSON file path, or '-' for stdin.",
    )
    diagnose.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    evaluate = subparsers.add_parser(
        "evaluate",
        help="Run deterministic Decision-PGA benchmark scenarios.",
    )
    evaluate.add_argument(
        "--config",
        default=None,
        help="Evaluation config JSON. Omit to use the default full scenario set.",
    )
    evaluate.add_argument(
        "--output",
        required=True,
        help="Directory for metrics, CSV, Markdown, and plot outputs.",
    )
    return parser


def _run_diagnose(
    args: argparse.Namespace,
    stdin: TextIO,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        payload = _read_payload(args.input, stdin)
        result = diagnose_payload(payload)
        _write_json(result, stdout, pretty=args.pretty)
        return 0
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        _write_json({"error": str(exc)}, stderr, pretty=False)
        return 2


def _run_evaluate(
    args: argparse.Namespace,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        if args.config is None:
            config = EvaluationConfig.default_full()
        else:
            config_payload = _read_payload(args.config, sys.stdin)
            config = EvaluationConfig.from_mapping(config_payload)
        report = run_evaluation(config)
        written = write_evaluation_report(report, args.output)
        _write_json(
            {
                "source": "evaluation",
                "output_dir": str(Path(args.output)),
                "written_files": [str(path) for path in written],
                "advantage": report.advantage,
            },
            stdout,
            pretty=False,
        )
        return 0
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        _write_json({"error": str(exc)}, stderr, pretty=False)
        return 2


def diagnose_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Diagnose a parsed JSON payload and return a JSON-compatible mapping."""

    if not isinstance(payload, Mapping):
        raise ValueError("input JSON must be an object.")
    source = payload.get("source")
    if not isinstance(source, str):
        raise ValueError("input JSON must include a string 'source'.")

    if source == "probability_cloud":
        return _diagnose_probability_cloud_payload(payload)
    if source == "model_outputs":
        return _diagnose_model_outputs_payload(payload)
    if source == "sampled_responses":
        return _diagnose_sampled_responses_payload(payload)
    if source == "trajectory_steps":
        return _diagnose_trajectory_steps_payload(payload)
    if source == "provider_scores":
        return _diagnose_provider_scores_payload(payload)
    if source == "provider_token_scores":
        return _diagnose_provider_token_scores_payload(payload)
    raise ValueError(
        "source must be one of 'probability_cloud', 'model_outputs', "
        "'sampled_responses', 'trajectory_steps', 'provider_scores', "
        "or 'provider_token_scores'."
    )


def _diagnose_probability_cloud_payload(payload: Mapping[str, object]) -> dict[str, object]:
    probabilities = _required(payload, "probabilities")
    diagnostic = diagnose_probability_cloud(
        np.asarray(probabilities, dtype=float),
        labels=_optional_sequence(payload, "labels"),
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return {
        "source": "probability_cloud",
        "diagnostic": diagnostic.to_dict(),
    }


def _diagnose_model_outputs_payload(payload: Mapping[str, object]) -> dict[str, object]:
    observations = [
        _model_output_observation(item, default_kind=str(payload.get("kind", "logprobs")))
        for item in _required_sequence(payload, "observations")
    ]
    result = diagnose_model_outputs(
        observations,
        labels=_optional_sequence(payload, "labels"),
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return _with_source("model_outputs", result.to_dict())


def _diagnose_sampled_responses_payload(payload: Mapping[str, object]) -> dict[str, object]:
    responses = [
        _sampled_response(item)
        for item in _required_sequence(payload, "responses")
    ]
    result = diagnose_sampled_responses(
        responses,
        labels=_required_sequence(payload, "labels"),
        aliases=_optional_mapping(payload, "aliases"),
        window_size=int(payload.get("window_size", 5)),
        step=int(payload.get("step", 1)),
        unknown_policy=str(payload.get("unknown_policy", "ignore")),
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return _with_source("sampled_responses", result.to_dict())


def _diagnose_trajectory_steps_payload(payload: Mapping[str, object]) -> dict[str, object]:
    steps = [
        _trajectory_step(item)
        for item in _required_sequence(payload, "steps")
    ]
    result = diagnose_trajectory_steps(
        steps,
        labels=_optional_sequence(payload, "labels"),
        window_size=int(payload.get("window_size", 5)),
        step=int(payload.get("step", 1)),
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return _with_source("trajectory_steps", result.to_dict())


def _diagnose_provider_scores_payload(payload: Mapping[str, object]) -> dict[str, object]:
    records = _provider_records(payload)
    observations = observations_from_provider_scores(
        records,
        score_path=_required_sequence(payload, "score_path"),
        candidates=_required_sequence(payload, "candidates"),
        kind=str(payload.get("kind", "logprobs")),
        missing_policy=str(payload.get("missing_policy", "raise")),
        missing_value=payload.get("missing_value"),
        observation_id_path=_optional_sequence(payload, "observation_id_path"),
        source=_optional_string(payload, "provider"),
        metadata=_optional_mapping(payload, "metadata"),
    )
    result = diagnose_model_outputs(
        observations,
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return _with_source("provider_scores", result.to_dict())


def _diagnose_provider_token_scores_payload(payload: Mapping[str, object]) -> dict[str, object]:
    observations = tuple(
        observation_from_token_scores(
            record,
            token_scores_path=_required_sequence(payload, "token_scores_path"),
            candidates=_required_sequence(payload, "candidates"),
            token_key=str(payload.get("token_key", "token")),
            score_key=str(payload.get("score_key", "logprob")),
            kind=str(payload.get("kind", "logprobs")),
            missing_policy=str(payload.get("missing_policy", "raise")),
            missing_value=payload.get("missing_value"),
            observation_id_path=_optional_sequence(payload, "observation_id_path"),
            source=_optional_string(payload, "provider"),
            metadata=_optional_mapping(payload, "metadata"),
        )
        for record in _provider_records(payload)
    )
    result = diagnose_model_outputs(
        observations,
        config=_config_from_payload(payload),
        label=_optional_string(payload, "label"),
    )
    return _with_source("provider_token_scores", result.to_dict())


def _read_payload(path: str, stdin: TextIO) -> Mapping[str, object]:
    text = stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    value = json.loads(text)
    if not isinstance(value, Mapping):
        raise ValueError("input JSON must be an object.")
    return value


def _write_json(payload: Mapping[str, object], stream: TextIO, pretty: bool) -> None:
    if pretty:
        stream.write(json.dumps(payload, indent=2, sort_keys=True))
    else:
        stream.write(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    stream.write("\n")


def _with_source(source: str, payload: Mapping[str, object]) -> dict[str, object]:
    result = {"source": source}
    result.update(payload)
    return result


def _config_from_payload(payload: Mapping[str, object]) -> DecisionPGAConfig | None:
    raw = payload.get("config")
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise ValueError("config must be an object.")
    allowed = {field.name for field in fields(DecisionPGAConfig)}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"unknown config fields: {unknown}")
    return DecisionPGAConfig(**raw)


def _model_output_observation(item: object, default_kind: str) -> ModelOutputObservation:
    if isinstance(item, Mapping) and "values" in item:
        return ModelOutputObservation(
            values=item["values"],
            kind=str(item.get("kind", default_kind)),
            observation_id=_string_or_none(item.get("observation_id")),
            source=_string_or_none(item.get("source")),
            metadata=_mapping_or_none(item.get("metadata")),
        )
    return ModelOutputObservation(values=item, kind=default_kind)


def _sampled_response(item: object) -> SampledResponse:
    if isinstance(item, Mapping):
        return SampledResponse(
            text=str(_required(item, "text")),
            response_id=_string_or_none(item.get("response_id")),
            source=_string_or_none(item.get("source")),
            metadata=_mapping_or_none(item.get("metadata")),
        )
    return SampledResponse(str(item))


def _trajectory_step(item: object) -> TrajectoryStep:
    if isinstance(item, Mapping):
        return TrajectoryStep(
            choice=str(_required(item, "choice")),
            step_id=_string_or_none(item.get("step_id")),
            source=_string_or_none(item.get("source")),
            metadata=_mapping_or_none(item.get("metadata")),
        )
    return TrajectoryStep(str(item))


def _provider_records(payload: Mapping[str, object]) -> Sequence[object]:
    if "records" in payload:
        return _required_sequence(payload, "records")
    if "record" in payload:
        return (payload["record"],)
    raise ValueError("provider payloads must include 'records' or 'record'.")


def _required(payload: Mapping[str, object], key: str) -> object:
    if key not in payload:
        raise ValueError(f"input JSON is missing required field {key!r}.")
    return payload[key]


def _required_sequence(payload: Mapping[str, object], key: str) -> Sequence[object]:
    value = _required(payload, key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{key} must be an array.")
    return value


def _optional_sequence(payload: Mapping[str, object], key: str) -> Sequence[object] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{key} must be an array.")
    return value


def _optional_mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object] | None:
    return _mapping_or_none(payload.get(key))


def _mapping_or_none(value: object) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("metadata/config-style fields must be objects.")
    return value


def _optional_string(payload: Mapping[str, object], key: str) -> str | None:
    return _string_or_none(payload.get(key))


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
