# Agent Example Payloads

These synthetic payloads are designed for quick intuition-building. Each one is
a complete JSON request that can be passed to the CLI:

```bash
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
```

## How to read the files

- `labels` are the candidate actions or decision routes.
- `probabilities` are repeated probability-like observations over those labels.
- `steps` are agent trajectory choices that the adapter windows into
  probability rows.
- `example_note` explains the workflow moment in human terms.

The examples do not prove that Decision-PGA is better than a baseline. They are
small fixtures for seeing the diagnostic contract in action.

## Included examples

| File | Scenario | Expected state |
| --- | --- | --- |
| `tool_action_ambiguity.json` | Planner split between docs search and database query. | `binary_ambiguity` |
| `rag_evidence_conflict.json` | Retrieved evidence supports two incompatible answer paths. | `binary_ambiguity` |
| `document_extraction_routing.json` | Missing source material scatters workflow support. | `diffuse_uncertainty` |
| `multi_step_agent_drift.json` | Agent trajectory shifts from retrieval to drafting. | `regime_shift` |
| `abstain_defer_decision.json` | Abstention is the stable top route. | `stable` |
