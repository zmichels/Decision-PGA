---
id: DPGA-E001
type: epic
title: Agent-Facing Decision-PGA Diagnostics
status: done
parent:
children:
  - DPGA-F001
  - DPGA-F002
  - DPGA-F003
created: 2026-05-16
completed: 2026-05-17
priority: P0
tags: [decision-pga, ai, diagnostics]
---

# DPGA-E001: Agent-Facing Decision-PGA Diagnostics

## Description

Develop Decision-PGA as a compact diagnostic method for AI agents and model
evaluators that need to detect structured uncertainty, ambiguity, boundary
sensitivity, and regime shifts in model decision states.

## Acceptance Criteria

- [x] Synthetic probability-cloud examples demonstrate stable, ambiguous, diffuse, boundary, and regime-shift cases.
- [x] A tested Python API computes Fisher-Rao/square-root PGA diagnostics.
- [x] A first notebook communicates the method without requiring model credentials.
- [x] Future work is tracked for real-model adapters and agent-tool wrapping.
- [x] A JSON-in / JSON-out process boundary lets agents call the diagnostic from outside Python.
