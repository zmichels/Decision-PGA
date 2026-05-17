---
id: DPGA-T010
type: task
title: Add Deterministic Evaluation Scenarios
status: done
parent: DPGA-S005
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [fixtures, synthetic]
links:
  - ../../../decision_pga/evaluation.py
  - ../../../examples/evaluation_config.json
---

# DPGA-T010: Add Deterministic Evaluation Scenarios

## Description

Create controlled synthetic evaluation scenarios for stable, ambiguous,
diffuse, boundary-sensitive, low-confidence, class-sweep, sample-sweep, and
regime-shift cases.

## Acceptance Criteria

- [x] Scenario generation is deterministic by seed.
- [x] Entropy-matched binary and diffuse fixtures are included.
- [x] Class-count and sample-count sweeps are included in the checked-in config.
