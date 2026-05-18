# Decision-PGA and the Coming Need for Decision-State Diagnostics in Agentic AI

AI systems are moving from one-shot answer generators toward embedded agents
that retrieve evidence, call tools, update plans, and make decisions with
side effects. That shift changes the role of decision uncertainty (DU). It is
no longer enough to ask whether a final answer "seems confident." A useful
agent needs to know whether the next decision is stable enough to proceed,
ambiguous enough to clarify, diffuse enough to gather more evidence, or
unstable enough to segment the problem and replan.

Decision-PGA is an early attempt to make that decision-state layer explicit.
It treats repeated model scores, sampled responses, or agent trajectory states
as a probability cloud over categorical choices. It then uses
Fisher-Rao/square-root geometry on the simplex to report not only scalar
uncertainty, but the shape of the uncertainty: tight, binary, diffuse,
boundary-sensitive, or shifting.

The claim here is deliberately measured: Decision-PGA is a promising diagnostic
scaffold, not yet validated as a production safety layer. Its value must be
earned through fixtures, baselines, and eventually real agent traces.

## Why probability-cloud diagnostics matter now

Classical uncertainty tools often aim at a final answer. Agentic systems add
several more decision points: which tool to call, what parameters to pass, what
evidence to trust, when to ask a human, when to abstain, and whether a plan has
drifted away from the original task. Each decision point can be represented as
a distribution over candidate actions or interpretations.

That representation is useful because different failure shapes imply different
next actions:

- A tight, high-margin cloud suggests proceeding.
- A cloud stretched mostly between two labels suggests a targeted
  clarification.
- A diffuse cloud suggests broader evidence gathering or task reframing.
- A cloud whose early and late means diverge suggests a regime shift or agent
  drift.

The need for these distinctions is visible across recent uncertainty work.
Semantic entropy research shows that uncertainty over meanings can matter more
than uncertainty over exact wordings in hallucination detection:
https://www.nature.com/articles/s41586-024-07421-0. Broad LLM uncertainty
surveys emphasize that LLMs introduce uncertainty sources such as input
ambiguity, reasoning-path divergence, and decoding stochasticity:
https://arxiv.org/abs/2503.15850. Agent-specific work on uncertainty
propagation argues that final-step uncertainty can miss cumulative risk across
multi-step processes: https://arxiv.org/abs/2412.01033.

## What current uncertainty tools do well

Entropy, top-1 margin, self-consistency, semantic entropy, calibration metrics,
retrieval diagnostics, verifier scores, and abstention policies are all useful.
They often answer questions like:

- Is the final answer likely to be wrong?
- Are sampled answers semantically consistent?
- Is the model calibrated on a benchmark?
- Did retrieval find relevant documents?
- Should a system refuse to answer above a threshold?

Recent function-calling uncertainty work makes this particularly concrete for
tool use: calling the wrong function can have severe consequences, and function
calling deserves its own uncertainty evaluation:
https://arxiv.org/abs/2604.22985. Structured clarification work similarly
pushes uncertainty toward tool parameters and user intent, not just final
language: https://arxiv.org/abs/2511.08798.

These are not competitors to Decision-PGA so much as necessary neighbors.
Decision-PGA needs adapters that can feed it meaningful candidate-score clouds,
and many of those adapters will come from retrieval, semantic clustering,
verifier, or tool-calling systems.

## Where current tools still leave gaps

Several recurring gaps matter for agentic integration:

- Tool/action ambiguity. Agents can appear confident while tool preferences are
  brittle. Work on tool preferences reports that LLM tool selection can be
  highly sensitive to natural-language tool descriptions:
  https://aclanthology.org/2025.emnlp-main.1060.pdf.
- Clarification and abstention. A single uncertainty score may say "do not
  proceed," but not whether the system should ask a narrow question, retrieve
  more evidence, or replan.
- RAG/evidence conflict. RAG reviews emphasize modular, policy-driven,
  provenance-aware, and uncertainty-aware pipelines, but many systems still
  lack simple diagnostics for conflicting evidence states:
  https://www.mdpi.com/2504-2289/9/12/320.
- Hallucination uncertainty. Semantic entropy is strong for confabulation
  detection, but a decision engine still needs to translate uncertainty into
  actions such as answer, cite, ask, retrieve, or abstain.
- Instruction-following risk. Apple research on instruction-following
  uncertainty highlights that existing uncertainty methods can struggle with
  subtle instruction errors:
  https://machinelearning.apple.com/research/estimate-uncertainty-well.
- Multi-step drift. An agent can make locally plausible steps while its overall
  trajectory moves into a different decision regime.
- Decision monitoring. Teams often monitor task accuracy, cost, and latency,
  while the shape of decision distributions changes silently underneath.

## What Decision-PGA contributes

Decision-PGA contributes a compact, model-neutral diagnostic contract:

- It accepts probability-like clouds from logits, logprobs, sampled responses,
  trajectory states, or future adapters.
- It reports shape metrics: total dispersion, PC1 fraction, anisotropy ratio,
  margin, label switching, and half-window geodesic drift.
- It maps those metrics into action-oriented states: `stable`,
  `binary_ambiguity`, `diffuse_uncertainty`, `boundary_sensitive`, and
  `regime_shift`.
- It is local and deterministic. No provider API call is required by the core
  library, CLI, or MCP server.

The distinctive bet is that geometry can separate uncertainty states that
scalar baselines blur together. Entropy can tell us a cloud is uncertain.
Decision-PGA tries to say whether that uncertainty is one coherent axis,
scattered across many alternatives, or moving over time. That shape can matter
because a decision engine should not respond to all uncertainty the same way.

## Early use-case map

The near-term application map has seven families:

- Agent tool/action selection: likely the best first deep dive because current
  provider-score adapters already map naturally to candidate actions.
- Clarification and abstention routing: promising because the current
  diagnostic states already map to different next actions.
- RAG/evidence conflict: high-impact but adapter-limited; claim and evidence
  clusters must become probability labels.
- Hallucination and confabulation triage: likely complementary to semantic
  entropy rather than a replacement.
- Instruction-following risk: important, but the hard problem is producing
  trustworthy compliance scores.
- Multi-step agent drift: promising because trajectory adapters already exist.
- Decision monitoring: useful for CI and regression reports if fixtures are
  representative.

The first two deeper tracks should be agent tool/action selection and
RAG/evidence conflict. Tool/action selection is closest to the current code.
RAG/evidence conflict is likely more important for research impact, but it
needs a careful adapter before evaluation is meaningful.

## What must be proven next

Decision-PGA should be treated as unproven until it demonstrates incremental
value over simple baselines on task-relevant fixtures. The minimum evidence
standard should be:

- Entropy and margin baselines are always reported.
- Switch-rate and drift baselines are reported for series or trajectory tasks.
- A scenario is labeled `promising` only when the current adapter contract can
  support a fair comparison.
- A scenario is labeled `needs_adapter` when the application is important but
  the inputs are not yet meaningful probability clouds.
- Reports state plainly when PGA is redundant, weak, or inconclusive.

The next benchmark layer should answer: does Decision-PGA improve routing
between proceed, clarify, gather evidence, abstain, segment, and replan on
held-out fixtures?

## Development roadmap toward agent-facing tools

1. Build a tool/action fixture set. Use candidate tools or next actions as
   labels. Compare PGA states with entropy, margin, and switch-rate baselines.
2. Add an action-routing report. Measure whether `binary_ambiguity` maps to
   better clarification and whether `diffuse_uncertainty` maps to better
   evidence gathering.
3. Define a RAG/evidence adapter. Convert retrieved passages, claim clusters,
   source groups, or answer paths into probability clouds without relying on a
   particular provider.
4. Add application reports with stable CSV, Markdown, and plot artifacts.
5. Wrap the strongest diagnostics as MCP tools so agents can call them as local
   read-only utilities.
6. Only after repeated fixture and real-trace tests should Decision-PGA be
   considered for production-like safety workflows.

Decision-PGA's opportunity is not to replace uncertainty quantification. Its
opportunity is to become a small, composable decision-state layer: one that
turns probability clouds into readable, testable, action-oriented diagnostics
for the agentic systems now being built around LLMs.
