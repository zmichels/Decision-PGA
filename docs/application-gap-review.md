# Decision-PGA Application Gap Review

This review turns the broad application discussion into a practical backlog.
The central question is where Decision-PGA might close a real gap in
decision-based AI tools, and where another adapter or baseline must come first.

Decision-PGA should be read as a local diagnostic layer, not a production
safety claim. It currently works best when a system can expose repeated scores
or samples over a stable set of candidate labels.

## Gap Matrix

| Gap family | Current tooling limit | Decision-PGA fit | Missing adapter | Evaluation route |
| --- | --- | --- | --- | --- |
| Tool/action ambiguity | Entropy and margin can flag uncertainty, but not always whether the ambiguity is two-way, diffuse, or drifting. | Promising; tool and action candidates are already categorical labels. | Provider/tool-score extraction for real agent traces. | Compare against entropy, margin, and switch rate on controlled tool-choice fixtures. |
| Clarification/abstention | Thresholds often decide whether to stop, but not what kind of stop is useful. | Promising; current states already map to clarify, gather evidence, inspect sensitivity, or replan. | Clarification outcome labels and cost-aware policies. | Measure whether state-aware routing asks fewer unnecessary questions while preserving task success. |
| RAG/evidence conflict | Retrieval metrics report ranking and recall, while evidence conflict can remain implicit. | Needs adapter; likely high-value if claims or source groups become labels. | Claim clustering, source-group scoring, and conflict annotations. | Build conflict fixtures with known answer/evidence structure and compare with retrieval-only diagnostics. |
| Hallucination uncertainty | Token entropy can miss semantic equivalence; semantic entropy is strong but does not by itself choose the agent action. | Needs adapter; Decision-PGA is complementary after semantic clusters exist. | Semantic claim clusters and probability estimates over clusters. | Compare state/action routing against semantic entropy and self-check baselines. |
| Instruction-following risk | Models may be confident while violating subtle constraints. | Inconclusive; the bottleneck is trustworthy compliance scoring. | Constraint verifier or rubric score cloud. | Test only after a verifier exposes stable categorical compliance labels. |
| Multi-step agent drift | Final-answer uncertainty misses cumulative uncertainty across steps. | Promising; trajectory adapters already exist. | Real or synthetic agent trace fixtures with expected drift labels. | Add sliding-window trajectory reports and compare with raw action-switch baselines. |
| Decision monitoring | Aggregate accuracy/cost/latency dashboards can hide decision-shape regressions. | Promising; deterministic CLI/MCP reports fit CI and local monitoring. | Fixture-regression expectations and acceptance thresholds. | Run checked-in fixtures over prompt/tool/model changes and track state regressions. |

## Practical Readout

The near-term development bet should be deliberately narrow:

1. Start with agent tool/action selection because it maps most cleanly onto the
   current `provider_scores`, `model_outputs`, and `probability_cloud`
   interfaces.
2. In parallel, define the RAG/evidence conflict adapter shape, but do not
   claim evaluation value until retrieved evidence can be converted into
   meaningful claim or source probability clouds.
3. Use the application suite to keep these distinctions explicit. A
   `promising` label means implementation can start now; a `needs_adapter`
   label means the application matters but the input bridge is not honest yet.

## Conservative Limits

- Decision-PGA does not verify factuality.
- Decision-PGA does not know whether a tool call is safe unless candidate
  scores and labels encode that distinction.
- Decision-PGA can inherit bias or noise from any adapter that feeds it.
- The current application suite is a structured review and report generator,
  not live model validation.

## Suggested Next Slice

The next concrete implementation slice should add an agent tool/action fixture
set:

- labels: candidate tool calls or next actions;
- inputs: provider-score shaped examples, sampled action traces, and synthetic
  controlled clouds;
- baselines: entropy, top-1 margin, top-label switch rate, and half-window
  drift;
- output: a report that measures whether Decision-PGA improves state routing
  between proceed, clarify, gather evidence, abstain, and replan.
