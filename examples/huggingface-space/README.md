# Decision-PGA Hugging Face Space Scaffold

This folder is a ready-to-copy scaffold for an optional public Hugging Face
Space. It is not deployed by the repository.

Suggested Space settings:

```yaml
---
title: Decision-PGA Agent Diagnostic Demo
emoji: D
colorFrom: teal
colorTo: gray
sdk: gradio
app_file: app.py
---
```

The Space would let visitors choose a synthetic agent scenario, run
Decision-PGA locally inside the Space runtime, and inspect the diagnostic JSON.
It should link back to:

- https://zmichels.github.io/decision-pga-pages/article/
- https://zmichels.github.io/decision-pga-pages/demo/
- https://github.com/zmichels/Decision-PGA

Keep the same guardrails: synthetic examples only, no credentials, no private
documents, no clinical validation claims.
