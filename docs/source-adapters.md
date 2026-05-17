# Source Adapters

Source adapters convert higher-level agent artifacts into candidate-aligned
probability clouds before they enter Decision-PGA.

## Sampled Responses

Free-form sampled responses are mapped to labels with literal label matching
plus optional aliases. Rows are empirical label frequencies over rolling
windows.

```python
from decision_pga import SampledResponse, diagnose_sampled_responses

responses = [
    SampledResponse("Yes, approve the request."),
    SampledResponse("I would accept this."),
    SampledResponse("No, reject it."),
    SampledResponse("Rejected."),
]

result = diagnose_sampled_responses(
    responses,
    labels=["approve", "reject", "defer"],
    aliases={
        "approve": ["yes", "accept"],
        "reject": ["no", "rejected"],
        "defer": ["unsure"],
    },
    window_size=2,
    step=1,
)

payload = result.to_dict()
```

Unmapped responses are ignored by default. Pass `unknown_policy="raise"` when a
strict candidate mapping is required.

## Agent Trajectories

Trajectory steps are candidate choices such as routes, tools, actions, or
planning modes. Rolling windows become empirical choice distributions.

```python
from decision_pga import TrajectoryStep, diagnose_trajectory_steps

steps = [
    TrajectoryStep("retrieve"),
    TrajectoryStep("retrieve"),
    TrajectoryStep("analyze"),
    TrajectoryStep("answer"),
]

result = diagnose_trajectory_steps(
    steps,
    labels=["retrieve", "analyze", "answer"],
    window_size=2,
    step=1,
)
```

The resulting `SourceAdapterDiagnostic` nests the same stable diagnostic payload
under `diagnostic` and adapter metadata under `adapter`.

## Boundary

These adapters do not call models or embed text. Alias maps are explicit and
local. Semantic clustering can be layered on later by assigning each sampled
response to a label or cluster before calling this adapter.
