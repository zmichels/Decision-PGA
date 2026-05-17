---
id: DPGA-T009
type: task
title: Implement Baseline Metrics
status: done
parent: DPGA-S005
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [baselines, tests]
links:
  - ../../../decision_pga/baselines.py
  - ../../../tests/test_baselines.py
---

# DPGA-T009: Implement Baseline Metrics

## Description

Add entropy, margin, switching, and half-window drift metrics for non-PGA
comparison.

## Acceptance Criteria

- [x] Entropy and margin metrics match hand-computed fixtures.
- [x] Top-label switch rate is deterministic.
- [x] Jensen-Shannon and Euclidean half-window drift are exposed.
