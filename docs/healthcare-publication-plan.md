# Healthcare Publication Plan

This plan is for publishing a no-cost, open-source article about Decision-PGA
and healthcare AI decision-state diagnostics within roughly one week.

## Recommended Route

### 1. Canonical public version

Use GitHub Pages or repository Markdown as the canonical open-source home.

Why:

- full control over wording, updates, diagrams, and links;
- natural connection to the prototype code;
- easy to revise as feedback arrives;
- no publishing cost;
- no arXiv endorsement delay.

Canonical article:

```text
docs/articles/decision-pga-healthcare-decision-state-diagnostics.md
```

### 2. Readable mirror

Mirror a lightly edited version on Substack or Medium.

Why:

- better for healthcare, AI, and developer readers who will not browse a repo;
- supports narrative framing and discussion;
- good place to invite feedback.

### 3. Citable archive after the first feedback pass

Use OSF Preprints if the piece remains mostly a position article. Use Zenodo
when the code, article, and examples are ready for a versioned open-source
snapshot.

OSF Preprints:

- easiest serious archive route;
- good fit for interdisciplinary exploratory work;
- useful if arXiv endorsement or category fit slows the process.

Zenodo:

- best once there is a GitHub release;
- gives a DOI to a versioned code/article bundle;
- good for reproducibility and open-source citation.

### 4. Later arXiv version

arXiv is attractive once the manuscript becomes more paper-like, with a clearer
method section, benchmark results, and diagrams. Do not make arXiv the blocker
for next week's publication.

## One-week publication path

Day 1:

- finalize article title, thesis, and healthcare scope;
- confirm caveats around institutional independence, patient data, and clinical
  validation.

Day 2:

- revise article for readability and source support;
- keep the article as a personal technical perspective, not institutional
  communication.

Day 3:

- add one or two simple diagrams;
- verify that all claims are measured and no clinical-readiness implication is
  present.

Day 4:

- ask two or three trusted reviewers for comments;
- ideally include one technical reviewer and one healthcare-workflow reader.

Day 5:

- publish the canonical GitHub Markdown or GitHub Pages version;
- publish the Substack or Medium mirror.

Day 6:

- make small wording fixes from early comments;
- avoid changing the core claim unless a serious issue is found.

Day 7:

- decide whether to archive v1 on OSF Preprints immediately or wait for one
  more code/demo pass.

## Article Guardrails

- Do not wait for clinical-grade code.
- Do not claim clinical validation.
- Do not include patient data, private workflow details, or protected health
  information.
- Do not imply institutional endorsement or deployment.
- Do not describe Decision-PGA as a medical device, diagnosis tool, treatment
  recommendation system, or clinical decision support product.
- Do state that the code is a research prototype and diagnostic scaffold.
- Do state that healthcare deployment would require governance, validation,
  usability, privacy, regulatory, and safety review.

## Suggested Publication Stack

| Purpose | Venue | Timing |
| --- | --- | --- |
| Canonical open-source version | GitHub Pages or repository Markdown | Week 1 |
| Readable essay | Substack or Medium | Week 1 |
| Citable exploratory preprint | OSF Preprints | After first feedback pass |
| Versioned code/article bundle | Zenodo | After tagged GitHub release |
| Academic manuscript | arXiv | After benchmark/demo maturity |

## Short Abstract

Healthcare AI systems are beginning to participate in workflows where they
retrieve evidence, extract data, route messages, and recommend next actions.
These systems need more than confidence scores. They need diagnostics that can
distinguish stable decisions, structured ambiguity, diffuse uncertainty,
boundary sensitivity, and decision-state drift. Decision-PGA is a prototype
framework for analyzing probability clouds over candidate decisions using
Fisher-Rao/square-root geometry. This article argues that decision-state
diagnostics could become a useful observability layer for high-accountability
healthcare AI workflows, while emphasizing that the current implementation is a
research scaffold and not clinical validation.
