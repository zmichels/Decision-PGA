---
id: DPGA-T005
type: task
title: Implement Agent Diagnostic Policy
status: done
parent: DPGA-S002
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [tool-interface, diagnostics, policy]
links:
  - ../../../decision_pga/diagnostics.py
  - ../../../tests/test_diagnostics.py
---

# DPGA-T005: Implement Agent Diagnostic Policy

## Description

Add the first agent-facing Decision-PGA policy layer that maps probability-cloud
geometry into diagnostic states and recommended actions.

## Acceptance Criteria

- [x] Stable clouds map to `stable` with `proceed`.
- [x] Binary ambiguity maps to `binary_ambiguity` with `clarify_between_top_labels`.
- [x] Diffuse uncertainty maps to `diffuse_uncertainty` with `gather_more_evidence`.
- [x] Boundary-sensitive clouds map to `boundary_sensitive` with `inspect_sensitivity`.
- [x] Regime-shift clouds map to `regime_shift` with `segment_or_replan`.
- [x] Diagnostic results expose JSON-serializable state, action, rationale, labels, and metrics.
