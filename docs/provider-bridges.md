# Provider Bridges

Provider bridges translate provider-shaped response objects into
`ModelOutputObservation` without importing provider SDKs or changing the core
Decision-PGA API.

The bridges work with plain dictionaries, lists, tuples, and simple Python
objects. Use `score_path` or `token_scores_path` to point at the data inside a
response object.

## Candidate Score Maps

Use `observation_from_provider_scores` when the provider response already
contains a mapping from candidate labels to probabilities, logprobs, or logits.

```python
from decision_pga import (
    diagnose_model_outputs,
    observation_from_provider_scores,
)

response = {
    "id": "sample-001",
    "output": {
        "scores": {
            "approve": -0.15,
            "reject": -2.30,
            "defer": -3.20,
        }
    },
}

observation = observation_from_provider_scores(
    response,
    score_path=("output", "scores"),
    candidates=["approve", "reject", "defer"],
    kind="logprobs",
    observation_id_path=("id",),
    source="example-provider",
)

result = diagnose_model_outputs([observation])
```

## Token Score Entries

Use `observation_from_token_scores` when the response contains entries such as
`{"token": "...", "logprob": ...}`.

```python
from decision_pga import observation_from_token_scores

response = {
    "top_logprobs": [
        {"token": " approve", "logprob": -0.10},
        {"token": " reject", "logprob": -2.60},
        {"token": " defer", "logprob": -3.50},
    ]
}

observation = observation_from_token_scores(
    response,
    token_scores_path=("top_logprobs",),
    candidates=["approve", "reject", "defer"],
)
```

Candidate matching normalizes whitespace, punctuation, and case. Missing
candidate scores raise by default:

```python
observation_from_token_scores(
    response,
    token_scores_path=("top_logprobs",),
    candidates=["approve", "reject", "defer"],
    missing_policy="fill",
    missing_value=-30.0,
)
```

Use `missing_policy="fill"` only when the caller has chosen an explicit floor
for absent candidates.

## Boundary

- No provider SDKs are imported.
- No network calls are made.
- Missing candidate behavior is explicit.
- The bridge output is always `ModelOutputObservation`, so downstream code can
  keep using `diagnose_model_outputs`.
