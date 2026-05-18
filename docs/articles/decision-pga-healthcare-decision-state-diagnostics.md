# Decision-State Diagnostics for Healthcare AI

## Why Agentic Clinical Systems Need More Than Confidence Scores

Healthcare AI is moving quickly from passive summarization toward systems that
retrieve evidence, extract structured data, triage messages, recommend next
steps, and coordinate work across clinical and administrative settings. That
shift changes the uncertainty problem. It is no longer enough to ask whether a
model is confident in a final answer. A healthcare workflow often needs to ask
what kind of decision state the system is in.

Is the next action stable enough to proceed? Is the uncertainty concentrated
between two plausible choices? Is it diffuse across many alternatives? Is the
system sensitive to a boundary condition? Has the decision state shifted over a
multi-step trajectory?

Decision-PGA is a prototype framework for studying those questions. It analyzes
clouds of categorical probability vectors on the probability simplex using
Fisher-Rao/square-root geometry, then maps the resulting dispersion shape into
states such as stable, binary ambiguity, diffuse uncertainty, boundary
sensitivity, and regime shift. In plain language: it tries to describe the
shape of uncertainty around a decision, not merely the size of that
uncertainty.

This article is a personal technical perspective, not an institutional statement.
It is motivated by high-accountability healthcare environments, including
academic medical centers such as Mayo Clinic, where AI is actively being
explored for clinical, operational, and research workflows. It does not
represent Mayo Clinic policy or endorsement. The work described here uses no patient data, is not clinical validation, and is not a medical device or clinical decision support product.

## Why healthcare is a natural stress test

Healthcare is full of decisions that are too consequential for a single opaque
confidence score:

- A patient-message assistant must decide whether to answer, clarify, route to
  a nurse, route to a physician, retrieve chart context, or escalate.
- A guideline or policy assistant must decide whether the retrieved evidence is
  coherent, stale, conflicting, or insufficient.
- A document-extraction system must decide whether a medication dose, prior
  authorization field, referral detail, lab value, or discharge instruction is
  stable enough to enter a structured record.
- A clinical trial matching workflow must decide whether eligibility criteria
  are clearly met, clearly unmet, ambiguous, or missing.
- A coding or revenue-cycle assistant must decide whether extracted evidence
  supports a code, conflicts with another source, or needs human review.
- A care-management agent must decide whether to proceed with a plan step,
  gather more evidence, ask a clarifying question, or replan.

These are not all clinical diagnosis tasks. Many are operational or
administrative. But they share a common structure: a system is choosing among
candidate actions, labels, sources, or extracted values under uncertainty. That
is exactly the space where a decision-state diagnostic can be useful.

## The regulatory and governance backdrop

Healthcare AI is not an abstract future category. The FDA maintains a public
resource of AI-enabled medical devices authorized for marketing in the United
States:
https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices.
The FDA also has guidance on Clinical Decision Support software and how some
software functions fit within or outside device regulation:
https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs.

The ONC HTI-1 final rule adds transparency requirements for predictive
decision support interventions in certified health IT:
https://healthit.gov/regulations/hti-rules/hti-1-final-rule/. The WHO has
published guidance on ethics and governance of AI for health:
https://www.who.int/publications/i/item/9789240029200.

Healthcare institutions are also visibly building AI capacity. Public Mayo
Clinic pages describe AI as a major area of medical innovation:
https://www.mayoclinic.org/giving-to-mayo-clinic/our-priorities/artificial-intelligence.
The Mayo Clinic Platform page describes work around secure, de-identified
clinical data and digital health innovation:
https://www.mayoclinic.org/giving-to-mayo-clinic/our-priorities/mayo-clinic-platform.

These sources point in the same direction: healthcare AI needs transparency,
validation, governance, and practical control surfaces. Decision-PGA is not a
regulatory framework. But it aims at a technical gap underneath many governance
questions: how can an AI workflow expose the state of its own decisions in a
readable, testable way?

## Confidence is not enough

Suppose a system must choose between several next actions:

- answer now;
- ask a clarifying question;
- retrieve more evidence;
- route to a clinician;
- abstain;
- replan.

Two cases can have similar entropy but require different responses. In one
case, almost all uncertainty may lie between two options, such as answer now
versus ask one specific clarifying question. In another, the probability mass
may be scattered across many actions, suggesting that the system does not have
enough context to know what kind of move is appropriate.

A scalar confidence score may say "uncertain" in both cases. A decision-state
diagnostic tries to say more:

- tight cloud: proceed may be reasonable;
- elongated two-label cloud: clarify between top options;
- diffuse cloud: gather more evidence;
- boundary-sensitive cloud: inspect assumptions or sensitivity;
- drifting cloud: segment the task or replan.

This distinction matters in healthcare because the next action is part of the
safety case. The same uncertainty score should not always produce the same
workflow response.

## What Decision-PGA does

Decision-PGA starts with repeated probability-like observations over candidate
labels. Those labels might be actions, extracted field values, evidence
clusters, review outcomes, or routing decisions. The current prototype then:

1. Normalizes probability vectors.
2. Maps them to the positive unit sphere with the square-root transform.
3. Computes an intrinsic mean.
4. Log-maps samples into a tangent space.
5. Computes a dispersion tensor and eigensystem.
6. Reports shape metrics such as total dispersion, PC1 fraction, anisotropy
   ratio, margin, label-switching, and half-window geodesic drift.

The practical output is not just a metric table. It is an action-oriented
diagnostic contract:

| State | Possible workflow interpretation |
| --- | --- |
| Stable | Proceed, assuming the task is within scope. |
| Binary ambiguity | Ask a targeted question or compare the top candidates. |
| Diffuse uncertainty | Gather more evidence or broaden context. |
| Boundary sensitive | Inspect sensitivity, constraints, or assumptions. |
| Regime shift | Segment the task, replan, or escalate. |

This is still a research scaffold. It must be tested against baselines such as
entropy, margin, switch rate, agreement, and task-specific accuracy. But the
core idea is simple: if healthcare AI systems are going to act in workflows,
they need diagnostics for the state of their decisions.

## Healthcare use cases worth studying first

### Patient-message and inbox triage

Many healthcare workflows begin with a message. The candidate decisions may be
answer, ask for clarification, route to nurse, route to physician, schedule,
retrieve chart context, or escalate. Decision-PGA could help distinguish a
stable routing decision from a two-route ambiguity or diffuse uncertainty.

### Guideline and policy retrieval

RAG-style systems can retrieve evidence that is relevant but not coherent. The
system may face conflicts between guidelines, local policies, patient-specific
constraints, or outdated sources. A diagnostic over candidate evidence clusters
could help decide whether to answer, retrieve more, cite uncertainty, or route
to human review.

### Medical document extraction

Healthcare uses enormous volumes of forms, referrals, notes, faxes, PDFs,
prior authorizations, medication lists, and discharge documents. Extraction
uncertainty is often not just "low confidence." It may be a two-value dispute,
a source-span ambiguity, a table-row association problem, or OCR sensitivity.
Decision-PGA could sit downstream of extraction candidates and help triage the
kind of review needed.

### Clinical trial matching

Eligibility matching requires structured decisions over inclusion and
exclusion criteria. Some fields are stable; some are missing; some conflict
across notes or reports. Decision-state diagnostics could help separate clear
matches from missing-evidence cases and true ambiguity.

### Care-management and operational agents

Agentic systems may coordinate multi-step workflows: gather context, check
criteria, prepare documentation, route work, and monitor follow-up. A final
confidence score misses drift across the trajectory. Sliding-window
decision-state diagnostics could help identify when the agent's plan has moved
into a different regime.

## What this does not claim

Decision-PGA is not clinical validation. It is not a substitute for model
evaluation, usability testing, bias assessment, safety review, regulatory
analysis, or clinical governance. It does not determine truth. It does not
decide whether a diagnosis, treatment, or recommendation is correct. It only
analyzes the shape of probability-like observations over candidate decisions.

That limitation is important. In healthcare, a tool that describes uncertainty
can still be useful, but only if it is surrounded by validation, human
oversight, workflow design, and governance appropriate to the use case.

The prototype should therefore be evaluated first on synthetic and
retrospective fixtures:

- controlled action-selection examples;
- document-extraction candidate fixtures;
- evidence-conflict examples;
- simulated agent trajectories;
- benchmark comparisons against entropy and margin.

Only after those tests should anyone consider prospective workflow studies,
and only with the appropriate institutional, regulatory, privacy, and ethics
review.

## Why publish now

The timing is useful because the healthcare AI conversation is shifting from
"can models answer questions?" to "how do AI systems participate in workflows
responsibly?" That shift requires technical vocabulary for states between
confidence and failure.

Decision-PGA gives one possible vocabulary:

- stable decisions;
- structured ambiguity;
- diffuse uncertainty;
- sensitivity near a boundary;
- decision-state drift.

It is not the final answer. It is a proposal for a measurement layer that can
be made explicit, tested, criticized, and improved.

## A near-term open-source path

The most practical next step is not to overclaim the method. It is to publish a
clear article, release the prototype openly, and invite technical feedback.

The first open-source package should focus on:

- probability-cloud diagnostics;
- reproducible synthetic benchmarks;
- document-extraction and healthcare-flavored examples that use no patient
  data;
- local CLI and MCP-style tool interfaces;
- readable Markdown/PDF reports;
- clear limitations.

The strongest early healthcare-facing benchmark would not require clinical
data. It could use synthetic fixtures that mimic common workflow decisions:
two plausible extracted values, conflicting evidence clusters, routing
ambiguity, and multi-step drift.

## Conclusion

Healthcare AI will need more than confident answers. It will need systems that
can expose when they are stable, ambiguous, diffuse, sensitive, or drifting.

Decision-PGA is a small attempt to formalize that layer. By analyzing
probability clouds on the simplex, it asks whether the geometry of a decision
state can help route AI workflows toward better next actions: proceed, clarify,
gather evidence, inspect sensitivity, segment, replan, or escalate.

That question is worth studying now, before agentic healthcare systems become
routine infrastructure. The right goal is not to claim that Decision-PGA is
ready for clinical deployment. The right goal is to make decision-state
diagnostics visible enough that they can be tested before they are needed at
scale.
