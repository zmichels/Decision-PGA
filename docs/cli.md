# CLI JSON Contract

The `decision-pga` command is a JSON-in / JSON-out process boundary for agents,
shell scripts, eval harnesses, and future services.

```bash
decision-pga diagnose examples/model_outputs.json
cat examples/model_outputs.json | decision-pga diagnose -
decision-pga diagnose --pretty examples/model_outputs.json
```

Exit codes:

- `0`: diagnostic completed and JSON was written to stdout.
- `2`: input, validation, or dispatch error; JSON error payload was written to stderr.

## Output Shape

All successful commands return:

```text
{
  "source": "...",
  "diagnostic": {
    "state": "...",
    "recommended_action": "...",
    "rationale": "...",
    "top_labels": [...],
    "metrics": {...}
  },
  "adapter": {...}
}
```

`adapter` is present for model-output, sampled-response, trajectory, and
provider-bridge inputs. Raw `probability_cloud` inputs return only `source` and
`diagnostic`.

## Sources

### `probability_cloud`

```json
{
  "source": "probability_cloud",
  "labels": ["approve", "reject", "defer"],
  "probabilities": [[0.88, 0.08, 0.04], [0.86, 0.10, 0.04]]
}
```

### `model_outputs`

```json
{
  "source": "model_outputs",
  "kind": "logprobs",
  "observations": [
    {"approve": -0.13, "reject": -2.53, "defer": -3.10}
  ]
}
```

Each observation can also be an object with `values`, `kind`,
`observation_id`, `source`, and `metadata`.

### `sampled_responses`

```json
{
  "source": "sampled_responses",
  "labels": ["approve", "reject", "defer"],
  "responses": ["approve", "approve", "reject"],
  "aliases": {"approve": ["yes"], "reject": ["no"]},
  "window_size": 3,
  "step": 1
}
```

### `trajectory_steps`

```json
{
  "source": "trajectory_steps",
  "labels": ["retrieve", "analyze", "answer"],
  "steps": ["retrieve", "analyze", "answer"],
  "window_size": 3,
  "step": 1
}
```

### `provider_scores`

```json
{
  "source": "provider_scores",
  "score_path": ["output", "scores"],
  "candidates": ["approve", "reject", "defer"],
  "kind": "logprobs",
  "records": [
    {"output": {"scores": {"approve": -0.13, "reject": -2.53, "defer": -3.10}}}
  ]
}
```

### `provider_token_scores`

```json
{
  "source": "provider_token_scores",
  "token_scores_path": ["top_logprobs"],
  "candidates": ["approve", "reject", "defer"],
  "records": [
    {
      "top_logprobs": [
        {"token": " approve", "logprob": -0.13},
        {"token": " reject", "logprob": -2.53},
        {"token": " defer", "logprob": -3.10}
      ]
    }
  ]
}
```

Provider inputs raise on missing candidate scores by default. To apply an
explicit floor:

```json
{
  "missing_policy": "fill",
  "missing_value": -30.0
}
```

## Config

Any source can include a `config` object with fields from
`DecisionPGAConfig`, such as:

```json
{
  "config": {
    "stable_max_dispersion": 0.02,
    "stable_min_mean_margin": 0.45
  }
}
```
