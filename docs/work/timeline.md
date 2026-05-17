# Project Timeline

Use this file for narrative milestones. Keep canonical status in individual work item files.

## 2026-05-16

- Started Decision-PGA as a synthetic-first AI decision-state diagnostics prototype.
- Implemented the first Fisher-Rao/square-root probability-cloud PGA core.
- Added tests for normalization, sphere maps, zero dispersion, and ambiguity-vs-diffuse geometry.

## 2026-05-17

- Added the first agent-facing diagnostic policy layer with stable, binary ambiguity, diffuse uncertainty, boundary-sensitive, and regime-shift states.
- Exposed JSON-friendly diagnostic payloads for future decision-engine tool wrappers.
- Defined the provider-neutral model output adapter boundary for candidate-aligned probabilities, logprobs, and logits.
- Added sampled-response and trajectory source adapters that convert rolling windows into candidate-aligned probability clouds.
- Added provider bridge helpers for nested score maps and token-score entries without SDK imports.
- Added the `decision-pga diagnose` JSON CLI and example payloads for the first process-level tool boundary.
