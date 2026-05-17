# Local MCP Server

Decision-PGA can run as a local stdio MCP server. The server is deterministic,
read-only, and local. It does not call model APIs, inspect hidden activations,
write files, or connect to external services.

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
