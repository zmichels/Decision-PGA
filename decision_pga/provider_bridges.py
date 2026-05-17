"""Thin provider-object bridges into ModelOutputObservation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Literal

from .model_adapters import ModelOutputObservation, ObservationKind


PathPart = str | int
MissingScorePolicy = Literal["raise", "fill"]


def observation_from_provider_scores(
    record: object,
    score_path: Sequence[PathPart],
    candidates: Sequence[str],
    kind: ObservationKind = "logprobs",
    missing_policy: MissingScorePolicy = "raise",
    missing_value: float | None = None,
    observation_id_path: Sequence[PathPart] | None = None,
    source: str | None = None,
    metadata: Mapping[str, object] | None = None,
) -> ModelOutputObservation:
    """Extract candidate score mapping from a provider-shaped object."""

    candidate_tuple = _validate_candidates(candidates)
    scores = _extract_path(record, score_path)
    if not isinstance(scores, Mapping):
        raise ValueError("score_path must resolve to a mapping of candidate scores.")

    values = _candidate_scores(
        scores,
        candidate_tuple,
        missing_policy,
        missing_value,
    )
    return ModelOutputObservation(
        values=values,
        kind=kind,
        observation_id=_extract_optional_text(record, observation_id_path),
        source=source,
        metadata=metadata,
    )


def observations_from_provider_scores(
    records: Sequence[object],
    score_path: Sequence[PathPart],
    candidates: Sequence[str],
    kind: ObservationKind = "logprobs",
    missing_policy: MissingScorePolicy = "raise",
    missing_value: float | None = None,
    observation_id_path: Sequence[PathPart] | None = None,
    source: str | None = None,
    metadata: Mapping[str, object] | None = None,
) -> tuple[ModelOutputObservation, ...]:
    """Extract multiple provider records into model-output observations."""

    return tuple(
        observation_from_provider_scores(
            record,
            score_path=score_path,
            candidates=candidates,
            kind=kind,
            missing_policy=missing_policy,
            missing_value=missing_value,
            observation_id_path=observation_id_path,
            source=source,
            metadata=metadata,
        )
        for record in records
    )


def observation_from_token_scores(
    record: object,
    token_scores_path: Sequence[PathPart],
    candidates: Sequence[str],
    token_key: str = "token",
    score_key: str = "logprob",
    kind: ObservationKind = "logprobs",
    missing_policy: MissingScorePolicy = "raise",
    missing_value: float | None = None,
    observation_id_path: Sequence[PathPart] | None = None,
    source: str | None = None,
    metadata: Mapping[str, object] | None = None,
) -> ModelOutputObservation:
    """Extract token-score entries into a candidate-aligned observation."""

    candidate_tuple = _validate_candidates(candidates)
    entries = _extract_path(record, token_scores_path)
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise ValueError("token_scores_path must resolve to a sequence of token score entries.")

    token_scores = _token_score_mapping(entries, token_key, score_key)
    values = _candidate_scores(
        token_scores,
        candidate_tuple,
        missing_policy,
        missing_value,
    )
    return ModelOutputObservation(
        values=values,
        kind=kind,
        observation_id=_extract_optional_text(record, observation_id_path),
        source=source,
        metadata=metadata,
    )


def _candidate_scores(
    scores: Mapping[object, object],
    candidates: tuple[str, ...],
    missing_policy: MissingScorePolicy,
    missing_value: float | None,
) -> dict[str, float]:
    if missing_policy not in {"raise", "fill"}:
        raise ValueError("missing_policy must be 'raise' or 'fill'.")
    normalized_scores = {_normalize_token(key): value for key, value in scores.items()}
    values: dict[str, float] = {}
    missing = []
    for candidate in candidates:
        normalized_candidate = _normalize_token(candidate)
        if normalized_candidate in normalized_scores:
            values[candidate] = float(normalized_scores[normalized_candidate])
        else:
            missing.append(candidate)

    if missing:
        if missing_policy == "raise":
            raise ValueError(f"missing candidate scores: {missing}")
        if missing_value is None:
            raise ValueError("missing_value is required when missing_policy='fill'.")
        for candidate in missing:
            values[candidate] = float(missing_value)
    return values


def _token_score_mapping(
    entries: Sequence[object],
    token_key: str,
    score_key: str,
) -> dict[str, float]:
    values = {}
    for entry in entries:
        token = _field(entry, token_key)
        score = _field(entry, score_key)
        values[_normalize_token(token)] = float(score)
    return values


def _extract_path(record: object, path: Sequence[PathPart]) -> object:
    if not path:
        raise ValueError("path must contain at least one part.")
    current = record
    for part in path:
        current = _field(current, part)
    return current


def _field(record: object, part: PathPart) -> object:
    if isinstance(record, Mapping):
        try:
            return record[part]
        except KeyError as exc:
            raise ValueError(f"path part {part!r} was not found.") from exc
    if isinstance(record, Sequence) and not isinstance(record, (str, bytes)):
        if not isinstance(part, int):
            raise ValueError("sequence path parts must be integers.")
        try:
            return record[part]
        except IndexError as exc:
            raise ValueError(f"path index {part!r} was not found.") from exc
    if isinstance(part, str) and hasattr(record, part):
        return getattr(record, part)
    raise ValueError(f"path part {part!r} was not found.")


def _extract_optional_text(
    record: object,
    path: Sequence[PathPart] | None,
) -> str | None:
    if path is None:
        return None
    value = _extract_path(record, path)
    return str(value)


def _validate_candidates(candidates: Sequence[str]) -> tuple[str, ...]:
    values = tuple(str(candidate) for candidate in candidates)
    if len(values) < 2:
        raise ValueError("candidates must contain at least two labels.")
    if len({_normalize_token(candidate) for candidate in values}) != len(values):
        raise ValueError("candidates must be unique after normalization.")
    return values


def _normalize_token(value: object) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value).lower()).split())
