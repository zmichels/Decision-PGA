# Model Output Adapter Boundary

Decision-PGA stays provider-neutral. The adapter boundary expects repeated,
candidate-aligned observations for one decision point. Each observation is one
row in the probability cloud and can arrive as probabilities, logprobs, or
logits.

## Contract

```python
from decision_pga import ModelOutputObservation, diagnose_model_outputs

observations = [
    ModelOutputObservation(
        {"approve": -0.13, "reject": -2.53, "defer": -3.10},
        kind="logprobs",
        source="model-sample-001",
    ),
    ModelOutputObservation(
        {"approve": -0.16, "reject": -2.30, "defer": -3.20},
        kind="logprobs",
        source="model-sample-002",
    ),
]

result = diagnose_model_outputs(observations)
payload = result.to_dict()
```

The payload nests the stable diagnostic contract under `diagnostic` and adapter
metadata under `adapter`:

```text
{
  "adapter": {
    "labels": [...],
    "observation_count": 2,
    "input_kinds": ["logprobs"]
  },
  "diagnostic": {
    "state": "...",
    "recommended_action": "...",
    "rationale": "...",
    "top_labels": [...],
    "metrics": {...}
  }
}
```

## Inputs

- `probabilities`: candidate probabilities that will be normalized with the
  same epsilon floor as the core PGA package.
- `logprobs`: candidate log probabilities that are softmax-normalized over the
  provided candidate set.
- `logits`: candidate scores that are softmax-normalized over the provided
  candidate set.

Inputs can be mappings keyed by candidate labels or one-dimensional arrays with
an explicit `labels` argument. Mapping inputs infer label order from the first
observation. Every observation must cover the same candidate set.

## Non-Goals

- No OpenAI API calls, local LLM calls, or provider SDK imports.
- No hidden activations, embeddings, or internal model state.
- No automatic imputation for missing top-logprob candidates. Provider-specific
  extraction code should either supply candidate-aligned scores or make an
  explicit imputation policy before calling this adapter.

## Future Adapters

- Sampled responses and agent trajectories are handled by the source adapters
  described in `docs/source-adapters.md`.
- Provider bridges are described in `docs/provider-bridges.md`; they translate
  response-shaped objects into `ModelOutputObservation` without changing the
  core Decision-PGA API.
