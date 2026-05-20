# Launch Post Drafts

These drafts are intentionally careful. They invite feedback without implying
production validation.

## LinkedIn / Team-Facing

I have been exploring a small open-source prototype called Decision-PGA: a
decision-state diagnostic for AI workflows.

The idea is simple to state. Many AI systems are starting to choose between
workflow actions: answer, clarify, retrieve more evidence, route to review,
abstain, or replan. Two cases can both look "uncertain" by a scalar score, but
the next useful action may be very different. Decision-PGA looks at repeated
probability-like observations as a cloud and asks whether that cloud is stable,
two-way ambiguous, diffuse, boundary-sensitive, or drifting.

The practical question is not "can this prove the model is right?" It cannot.
The question is whether a lightweight diagnostic can help an agent decide what
kind of next step is appropriate before it acts.

It is early, local, model-neutral, and synthetic-first. It is not a validated
safety layer. But I think the diagnostic contract may be useful for agent
builders who need lightweight routing hints before a workflow acts.

Article, demo, and toolkit:
https://zmichels.github.io/decision-pga-pages/article/
https://zmichels.github.io/decision-pga-pages/toolkit/

Code:
https://github.com/zmichels/Decision-PGA

## Developer-Facing

Decision-PGA now has a small agent toolkit: CLI, Python API, local stdio MCP
server, and copy-paste JSON examples for tool ambiguity, RAG evidence conflict,
document extraction routing, agent drift, and stable abstention.

Try:

```bash
git clone https://github.com/zmichels/Decision-PGA.git
cd Decision-PGA
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[mcp]"
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
```

What I am looking for: agent workflow examples where entropy/confidence is too
blunt, and the shape of uncertainty might help decide whether to proceed,
clarify, retrieve, review, abstain, or replan.

Toolkit page:
https://zmichels.github.io/decision-pga-pages/toolkit/

## Research-Facing

Decision-PGA is an early prototype exploring Principal Geodesic Analysis-style
diagnostics for probability clouds on the categorical simplex.

The research question is deliberately modest: when repeated model or workflow
observations produce a probability cloud over candidate decisions, do
Fisher-Rao/square-root dispersion metrics add useful structure beyond entropy,
margin, and drift baselines?

The current release is synthetic-first and model-neutral. It includes a package,
CLI, benchmark harness, application gap reviews, and a local MCP server. The
next useful critique is where the geometry is redundant, where it adds
interpretive value, and what real adapter fixtures would make the evaluation
more convincing.

Article:
https://zmichels.github.io/decision-pga-pages/article/

Repository:
https://github.com/zmichels/Decision-PGA
