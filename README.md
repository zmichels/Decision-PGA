# Decision-PGA

Decision-PGA is a synthetic-first prototype for agent-facing diagnostics on
model decision states. Version 1 analyzes clouds of categorical probability
vectors with Fisher-Rao/square-root geometry:

```text
probabilities -> sqrt embedding on the positive sphere -> intrinsic mean
-> tangent vectors -> principal geodesic dispersion tensor
```

The immediate goal is to distinguish decision geometries that ordinary entropy
summaries blur together:

- stable confident decisions;
- coherent binary ambiguity;
- diffuse uncertainty;
- perturbation-sensitive boundary cases;
- sliding-window regime shifts.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run the JSON CLI:

```bash
decision-pga diagnose examples/model_outputs.json
cat examples/model_outputs.json | decision-pga diagnose -
decision-pga diagnose --pretty examples/provider_scores.json
decision-pga evaluate --config examples/evaluation_config.json --output reports/latest
```

Open or execute:

```text
notebooks/01_fisher_rao_probability_clouds.ipynb
```

## Minimal API

```python
from decision_pga import (
    diagnose_probability_cloud,
    diagnose_model_outputs,
    diagnose_sampled_responses,
    ModelOutputObservation,
    observation_from_provider_scores,
    SampledResponse,
    pga_probability_cloud,
    synthetic_probability_cloud,
)

probs = synthetic_probability_cloud("binary_ambiguity", 80, 5, seed=7)
result = pga_probability_cloud(probs, label="binary ambiguity")

print(result.pc1_fraction)
print(result.anisotropy_ratio)
print(result.mean_margin)

diagnostic = diagnose_probability_cloud(
    probs,
    labels=["alpha", "beta", "gamma", "delta", "epsilon"],
)

print(diagnostic.state)
print(diagnostic.recommended_action)
print(diagnostic.to_dict())

observations = [
    ModelOutputObservation([0.88, 0.08, 0.04], kind="probabilities"),
    ModelOutputObservation([0.86, 0.10, 0.04], kind="probabilities"),
    ModelOutputObservation([0.89, 0.07, 0.04], kind="probabilities"),
    ModelOutputObservation([0.87, 0.09, 0.04], kind="probabilities"),
]

model_result = diagnose_model_outputs(
    observations,
    labels=["approve", "reject", "defer"],
)

print(model_result.to_dict())

sampled_result = diagnose_sampled_responses(
    [
        SampledResponse("approve"),
        SampledResponse("approve"),
        SampledResponse("reject"),
        SampledResponse("reject"),
    ],
    labels=["approve", "reject", "defer"],
    window_size=2,
)

print(sampled_result.to_dict())

provider_observation = observation_from_provider_scores(
    {
        "output": {
            "scores": {
                "approve": -0.13,
                "reject": -2.53,
                "defer": -3.10,
            }
        }
    },
    score_path=("output", "scores"),
    candidates=["approve", "reject", "defer"],
    kind="logprobs",
)
```

The first agent-facing diagnostic states and recommended actions are:

| State | Recommended action |
| --- | --- |
| `stable` | `proceed` |
| `binary_ambiguity` | `clarify_between_top_labels` |
| `diffuse_uncertainty` | `gather_more_evidence` |
| `boundary_sensitive` | `inspect_sensitivity` |
| `regime_shift` | `segment_or_replan` |

See `docs/model-output-adapters.md` for the provider-neutral model output
adapter boundary and `docs/source-adapters.md` for sampled-response and
trajectory adapters. Provider-shaped response extraction is documented in
`docs/provider-bridges.md`. The process-level JSON contract is documented in
`docs/cli.md`. The synthetic benchmark harness is documented in
`docs/evaluation.md`.

## Local MCP Server

Install the optional MCP dependency and launch the local stdio server:

```bash
python -m pip install -e ".[mcp]"
decision-pga-mcp
```

The MCP server is local, deterministic, and read-only. It exposes the same
diagnostic contract as the Python API and CLI. See `docs/mcp-server.md`.

## Tester Path

For a short private-repo trial, start with `docs/tester-guide.md` and capture
comments with `docs/tester-feedback-template.md`.

## Notes

This prototype is deliberately model-free. It does not call the OpenAI API, run
a local LLM, or inspect hidden activations. Real model adapters should come
after the synthetic geometry is stable and tested.
