# Changelog

## 0.1.0 - 2026-05-19

Initial public release candidate.

- Added Fisher-Rao/square-root probability-cloud PGA core.
- Added diagnostic states for stable, binary ambiguity, diffuse uncertainty,
  boundary sensitivity, and regime shift.
- Added JSON CLI and examples for probability clouds, model outputs, sampled
  responses, trajectories, and provider-shaped score payloads.
- Added deterministic synthetic benchmark reports with entropy, margin, drift,
  and PGA comparisons.
- Added local stdio MCP server helpers.
- Added application and document-extraction review/evaluation suites.

This release is a research prototype. It uses synthetic examples and local
diagnostics only; it does not call model APIs and is not a production safety or
clinical decision-support system.
