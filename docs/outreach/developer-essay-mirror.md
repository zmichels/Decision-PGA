# Agents Need Decision-State Diagnostics, Not Just Confidence Scores

This is a developer-facing mirror draft for DEV.to, Medium, Substack, or a
project blog. It should point readers back to the canonical article and the
public repository.

## Draft

Agent workflows increasingly need to choose between actions, not just produce
answers. A useful system may need to answer now, ask a clarifying question,
retrieve more evidence, call a tool, route to review, abstain, or replan. A
single confidence score can be useful, but it often hides the difference
between decision states that should lead to different next moves.

Here is the practical version. Imagine two agent runs with similar uncertainty.
In one, almost all of the uncertainty is between two tools: search the docs or
query the database. In the other, support is scattered across many routes:
answer, retrieve, clarify, review, abstain. Both can look "uncertain." They
should not necessarily lead to the same workflow action.

Decision-PGA is a small open-source prototype that asks a narrower question:
given repeated probability-like observations over candidate decisions, what is
the shape of the cloud?

- Is the cloud tight around one action?
- Is uncertainty mostly a two-way split?
- Is support scattered across many routes?
- Is the decision sitting near a sensitive boundary?
- Did the preferred action change over the trajectory?

The prototype uses Fisher-Rao/square-root geometry on the categorical simplex
and Principal Geodesic Analysis-style dispersion metrics to produce a compact
diagnostic payload. That payload is designed for tools: a CLI, Python API, and
local stdio MCP server all return the same JSON-friendly contract.

This is not a validated safety layer. It does not call model APIs, inspect
hidden activations, or prove that an answer is correct. The value proposition is
more practical and testable: can a lightweight, model-neutral diagnostic help an
agent decide whether to proceed, clarify, retrieve, review, abstain, or replan?

Try the synthetic examples:

```bash
git clone https://github.com/zmichels/Decision-PGA.git
cd Decision-PGA
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[mcp]"
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
decision-pga diagnose --pretty examples/agent/rag_evidence_conflict.json
```

The most interesting next step is not claiming that this is the right geometry
for all agent decisions. It is collecting real workflow-shaped examples where
scalar uncertainty is too blunt, then testing whether decision-state shape adds
useful signal.

If you build agents, the most helpful feedback is concrete: show a synthetic
version of a workflow moment where the system currently has to decide whether
to proceed, clarify, retrieve, review, abstain, or replan.

Canonical article:
https://zmichels.github.io/decision-pga-pages/article/

Live demo:
https://zmichels.github.io/decision-pga-pages/demo/

Code:
https://github.com/zmichels/Decision-PGA
