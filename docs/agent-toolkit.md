# Decision-PGA Agent Toolkit

Decision-PGA is meant for a specific moment in an agent workflow: the agent has
several plausible next moves, and a plain confidence score is too blunt to say
what should happen next.

Think of a document agent that can accept an extraction, ask a person a targeted
question, retrieve another attachment, route the case for review, or defer until
the packet stops changing. Several model samples, retrieval windows, prompt
variants, rule checks, or agent steps can each produce a probability-like view
over those same actions. Decision-PGA reads that stack of rows as a cloud and
asks what shape the uncertainty has.

The output is a small diagnostic payload:

- `state`: stable, binary ambiguity, diffuse uncertainty, boundary sensitivity,
  or regime shift.
- `recommended_action`: a generic routing hint such as proceed, clarify, gather
  evidence, inspect sensitivity, or segment/replan.
- `top_labels`: the strongest domain-specific actions or labels in the mean
  cloud.
- `metrics`: dispersion, PC1 fraction, margin, switch rate, and half-cloud
  drift values that explain the routing hint.

This is a local research prototype. It is model-neutral and deterministic. It
does not call model APIs, inspect hidden activations, or validate that an answer
is correct. It is not a production safety layer. Use it as a routing hint to
inspect, test, and discuss decision states.

## Use Decision-PGA In 5 Minutes

Clone and install from GitHub:

```bash
git clone https://github.com/zmichels/Decision-PGA.git
cd Decision-PGA
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[mcp]"
```

Run a few CLI diagnoses:

```bash
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
decision-pga diagnose --pretty examples/agent/rag_evidence_conflict.json
decision-pga diagnose --pretty examples/agent/document_extraction_routing.json
decision-pga diagnose --pretty examples/agent/multi_step_agent_drift.json
decision-pga diagnose --pretty examples/agent/abstain_defer_decision.json
```

The five examples cover the first practical states an agent builder usually
wants to reason about: focused tool ambiguity, conflicting retrieved evidence,
missing document context, trajectory drift, and stable abstention.

Run the local MCP server:

```bash
decision-pga-mcp
```

Inspect it with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector decision-pga-mcp
```

## CLI diagnosis

The CLI is a JSON-in / JSON-out boundary. The simplest payload is a probability
cloud. This example describes an agent planner split between searching docs and
querying a database:

```json
{
  "source": "probability_cloud",
  "label": "agent tool-action ambiguity",
  "labels": ["search_docs", "query_database", "ask_clarifying_question", "draft_answer"],
  "probabilities": [
    [0.46, 0.42, 0.08, 0.04],
    [0.43, 0.45, 0.08, 0.04],
    [0.47, 0.40, 0.09, 0.04],
    [0.41, 0.47, 0.08, 0.04]
  ]
}
```

Each row is one repeated observation of the same decision situation. The row
values are probabilities over the labels and should sum to one. The labels can
be possible answers, tool choices, workflow actions, extraction routes, or
agent planning states.

The rows are not the document, answer, or tool result itself. They are the
workflow's repeated estimates of what it should do next. In a real integration,
the rows might come from:

- repeated model samples scored against the same action vocabulary;
- logprobs or logits over explicit candidate actions;
- a set of retrieval passages scored for competing answer routes;
- OCR/layout perturbations scored against extraction actions;
- reviewer votes or rule checks converted into candidate probabilities;
- rolling windows of agent trajectory steps.

## Python API diagnosis

Use the Python API when Decision-PGA is embedded directly in an orchestration
loop:

```python
from decision_pga import diagnose_probability_cloud

labels = ["search_docs", "query_database", "ask_clarifying_question", "draft_answer"]
probabilities = [
    [0.46, 0.42, 0.08, 0.04],
    [0.43, 0.45, 0.08, 0.04],
    [0.47, 0.40, 0.09, 0.04],
    [0.41, 0.47, 0.08, 0.04],
]

diagnostic = diagnose_probability_cloud(probabilities, labels=labels)
print(diagnostic.to_dict())
```

## Local MCP server

The MCP server exposes the same diagnostic contract to MCP-compatible agent
clients. Start with local stdio because it is deterministic, private to the
machine, and does not introduce network services:

```bash
python -m pip install -e ".[mcp]"
decision-pga-mcp
```

The server tools include:

- `diagnose_probability_cloud`
- `diagnose_model_outputs`
- `diagnose_sampled_responses`
- `diagnose_trajectory_steps`
- `explain_decision_pga_metrics`

## What the input means

Decision-PGA does not require a specific model provider. The required structure
is simply a repeated set of comparable observations:

- fixed candidate labels;
- one probability-like row per sample, perturbation, retrieved context, tool
  evaluation, reviewer vote, or trajectory window;
- rows aligned to the same candidate labels;
- no private data or credentials in the payload.

If a provider gives logprobs or logits instead of probabilities, use the
`model_outputs`, `provider_scores`, or `provider_token_scores` sources documented
in `docs/cli.md`.

## Calling from an agent loop

Use Decision-PGA after an agent has generated several comparable candidate
scores and before it commits to an irreversible workflow action:

```python
diagnostic = diagnose_probability_cloud(probabilities, labels=actions).to_dict()

state = diagnostic["state"]
recommended = diagnostic["recommended_action"]
top_action = diagnostic["top_labels"][0]

if recommended == "proceed":
    run_action(top_action)
elif recommended == "clarify_between_top_labels":
    ask_targeted_question(diagnostic["top_labels"][:2])
elif recommended == "gather_more_evidence":
    retrieve_more_context()
elif recommended == "inspect_sensitivity":
    route_to_review(top_action, diagnostic["metrics"])
elif recommended == "segment_or_replan":
    replan_or_split_trace()
```

In practice, keep the domain action vocabulary separate from Decision-PGA's
generic routing hint. If the top domain label is `abstain` and the generic
recommendation is `proceed`, the workflow should proceed with abstention, not
override the abstention.

## Interpreting states and actions

| State | Generic action | Practical reading |
| --- | --- | --- |
| `stable` | `proceed` | The cloud is tight and the top label has a clear margin. Proceed with the top label. |
| `binary_ambiguity` | `clarify_between_top_labels` | Most uncertainty lies between two choices. Ask a targeted question or resolve that pair. |
| `diffuse_uncertainty` | `gather_more_evidence` | Support is scattered across several options. Retrieve context, inspect missing inputs, or widen evidence. |
| `boundary_sensitive` | `inspect_sensitivity` | Small changes can flip the result. Review thresholds, perturbations, or policy context. |
| `regime_shift` | `segment_or_replan` | Early and late observations disagree. Split the trace or replan instead of averaging. |

`recommended_action` is a diagnostic hint about what to do next. It is not a
claim that the top label is correct. For example, if the top label is
`abstain` and the state is `stable`, then `proceed` means proceed with the
abstention route.

## Prime examples

These examples are intentionally small. They are meant to be readable enough
that a developer can look at the rows, guess the state, then run the diagnostic
and compare.

| Example | Human situation | Expected reading |
| --- | --- | --- |
| `examples/agent/tool_action_ambiguity.json` | A planner is split between searching docs and querying a database. | Focused two-way ambiguity. Clarify or choose between the top routes. |
| `examples/agent/rag_evidence_conflict.json` | Two retrieved snippets support incompatible answer paths. | Focused evidence conflict. Resolve the conflicting evidence before answering. |
| `examples/agent/document_extraction_routing.json` | A document extraction packet references a source that is not available. | Diffuse uncertainty. Retrieve more context rather than asking a narrow question. |
| `examples/agent/multi_step_agent_drift.json` | Early trajectory windows retrieve evidence, later windows start drafting. | Regime shift. Segment the trace or replan. |
| `examples/agent/abstain_defer_decision.json` | The agent repeatedly favors abstention. | Stable abstention. Proceed with the abstain route. |

## What makes a good new example

A useful Decision-PGA example needs only three pieces:

- a fixed action vocabulary;
- several comparable rows over that vocabulary;
- a short note explaining the human workflow moment.

The strongest examples are not the most dramatic ones. They are the everyday
cases where a team can immediately say: "Yes, those two states both look
uncertain, but we would handle them differently."
