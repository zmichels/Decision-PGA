# Local MCP Server

Decision-PGA can run as a local stdio MCP server. The server is deterministic,
read-only, and local. It does not call model APIs, inspect hidden activations,
write files, or connect to external services.

## Why MCP

Decision-PGA is most useful when it is close to the agent loop. An agent can
sample possible actions, compare retrieved evidence, perturb a document
extraction, or window its own trajectory, then call this server before taking
the next workflow step.

The returned payload does not say "the answer is true." It says something more
operational: the decision cloud looks stable, two-way ambiguous, diffuse,
boundary-sensitive, or drifting. That is the kind of signal an agent can use to
decide whether to proceed, clarify, retrieve, review, abstain, or replan.

The MCP server is intentionally narrow: local stdio first, no remote service,
and no hidden network calls.

## Quickstart

Install the optional MCP dependency:

```bash
python -m pip install -e ".[mcp]"
```

Launch the stdio server:

```bash
decision-pga-mcp
```

Open the server in MCP Inspector:

```bash
npx @modelcontextprotocol/inspector decision-pga-mcp
```

For Inspector workflows, run the command from an environment where
`decision-pga-mcp` is installed. The server exposes these tools:

- `diagnose_probability_cloud`
- `diagnose_model_outputs`
- `diagnose_sampled_responses`
- `diagnose_trajectory_steps`
- `explain_decision_pga_metrics`

Example probability-cloud arguments:

```json
{
  "probabilities": [
    [0.88, 0.08, 0.04],
    [0.86, 0.10, 0.04],
    [0.89, 0.07, 0.04],
    [0.87, 0.09, 0.04]
  ],
  "labels": ["approve", "reject", "defer"]
}
```

Tool results preserve the existing diagnostic payload:

```json
{
  "source": "probability_cloud",
  "diagnostic": {
    "state": "stable",
    "recommended_action": "proceed",
    "rationale": "...",
    "top_labels": ["approve", "reject", "defer"],
    "metrics": {}
  }
}
```

For stdio MCP servers, avoid writing logs to stdout because stdout carries the
JSON-RPC protocol stream.

## Example Tool Calls

### Tool/action ambiguity

`diagnose_probability_cloud` accepts the same rows as the CLI:

```json
{
  "probabilities": [
    [0.46, 0.42, 0.08, 0.04],
    [0.43, 0.45, 0.08, 0.04],
    [0.47, 0.40, 0.09, 0.04],
    [0.41, 0.47, 0.08, 0.04]
  ],
  "labels": [
    "search_docs",
    "query_database",
    "ask_clarifying_question",
    "draft_answer"
  ],
  "label": "agent tool-action ambiguity"
}
```

Expected output is a JSON object with `source` and `diagnostic`. In this
example, the diagnostic state is `binary_ambiguity` and the recommended action
is `clarify_between_top_labels`, because the planner is mostly split between
the first two tools.

### Trajectory drift

`diagnose_trajectory_steps` is useful when an agent trace can be windowed into
candidate actions:

```json
{
  "steps": [
    "retrieve_evidence",
    "retrieve_evidence",
    "retrieve_evidence",
    "retrieve_evidence",
    "retrieve_evidence",
    "retrieve_evidence",
    "draft_answer",
    "draft_answer",
    "draft_answer",
    "draft_answer",
    "draft_answer",
    "draft_answer"
  ],
  "labels": [
    "retrieve_evidence",
    "draft_answer",
    "ask_user",
    "abstain"
  ],
  "window_size": 3,
  "step": 3
}
```

Expected output is a `regime_shift` diagnostic because the early and late
windows prefer different actions.

## Draft MCP Registry Metadata

Draft metadata lives at `docs/mcp-registry/server.json`.

The metadata is prepared but not submitted. Submit it only after the package
distribution path is final and the public install path is stable.
