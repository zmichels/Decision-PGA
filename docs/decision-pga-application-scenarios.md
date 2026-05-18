# Decision-PGA Application Scenarios

This scenario backlog mirrors the application evaluation suite. It is meant to
help testers and future implementers choose where Decision-PGA should grow
next.

Run the current suite:

```bash
decision-pga evaluate --suite application --output reports/application-latest
```

The command writes `application_metrics.json`, `application_summary.csv`,
`gap_matrix.csv`, `application_report.md`, and a generated
`decision-pga-gap-review.pdf`.

## Selected Deep Dives

### 1. Agent Tool/Action Selection

Use candidate tools or next actions as labels. Feed probability clouds from
provider scores, sampled action choices, or synthetic fixtures into
Decision-PGA.

Why it is compelling:

- It connects directly to the current adapter shape.
- Wrong tool calls can have immediate side effects.
- Recent work on function-calling UQ and tool-preference unreliability makes
  the gap timely.

What to test:

- Can PGA separate two-tool ambiguity from diffuse action uncertainty at
  comparable entropy?
- Does `binary_ambiguity` lead to better clarification behavior than an
  entropy-only stop rule?
- Do state changes catch prompt/tool-description regressions?

### 2. RAG/Evidence Conflict

Use retrieved evidence groups, claim clusters, or answer paths as labels. This
requires an adapter before the comparison is fair.

Why it is compelling:

- RAG workflows are becoming modular and policy-driven.
- Evidence conflict often needs a control action, not just a score.
- PGA may help distinguish one dominant conflict axis from a broad evidence
  failure.

What to test:

- Can a claim/evidence adapter produce stable probability clouds?
- Does PGA add value over retrieval overlap, source count, entropy, or
  evidence-score variance?
- Do reports make conflict states readable to testers?

### 3. Multi-Step Agent Drift

Use agent step sequences as labels or windowed probability clouds. This is the
closest Decision-PGA analogue to the series-reporting bridge built in SO3-PGA.

Why it is compelling:

- Final-answer uncertainty can miss accumulated drift.
- The current `trajectory_steps` adapter already provides a starting point.
- Drift states naturally map to segmenting, replanning, or asking for help.

What to test:

- Can half-window geodesic distance catch known trajectory shifts?
- Does PGA distinguish coherent regime shifts from high action churn?
- Can static series plots make the diagnostic story obvious to testers?

## Full Backlog

| Gap family | Use case | Current failure mode | Decision-PGA contribution | Baseline comparison | Difficulty | Recommended next step |
| --- | --- | --- | --- | --- | --- | --- |
| Tool/action ambiguity | Agent tool/action selection | Tool choice can be fragile under shallow score differences or tool descriptions. | Shape-aware action-state routing. | Entropy, margin, switch rate. | Medium | Build the first real fixture set. |
| Clarification/abstention | Ask/proceed/gather evidence decisions | Stop thresholds rarely explain what to do next. | Maps uncertainty shapes to different actions. | Entropy and fixed abstention thresholds. | Medium | Add clarification outcome fixtures. |
| RAG/evidence conflict | Conflicting retrieval support | Retrieval quality and answer confidence are often monitored separately. | Potential claim/source conflict geometry. | Retrieval metrics, entropy, source counts. | High | Define a claim/evidence adapter. |
| Hallucination uncertainty | Confabulation triage | Surface wording variation can hide semantic stability or instability. | Possible shape layer after semantic clustering. | Semantic entropy, self-checking. | High | Prototype semantic-cluster input only. |
| Instruction-following risk | Constraint compliance | Confidence may stay high despite subtle violations. | Possible compliance-cloud diagnostic. | Verifier confidence, rule failure rates. | High | Defer until verifier labels are trustworthy. |
| Multi-step agent drift | Plan and trajectory monitoring | Final output metrics miss cumulative process uncertainty. | Windowed drift/state diagnostics. | Final entropy, switch rate, step-count heuristics. | Medium | Add trajectory series reports. |
| Decision monitoring | CI and regression checks | Aggregate metrics hide distribution-shape changes. | Deterministic state regression reports. | Accuracy, entropy, margin thresholds. | Low | Add fixture-regression expected states. |
