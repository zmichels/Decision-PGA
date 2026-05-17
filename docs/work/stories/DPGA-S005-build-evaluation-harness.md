---
id: DPGA-S005
type: story
title: Build Evaluation Harness
status: done
parent: DPGA-F004
children:
  - DPGA-T009
  - DPGA-T010
  - DPGA-T011
  - DPGA-T012
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [evaluation, reports]
---

# DPGA-S005: Build Evaluation Harness

## Description

Provide a repeatable way to compare Decision-PGA state inference with simpler
entropy, margin, and drift baselines.

## Acceptance Criteria

- [x] Baseline metrics are tested against hand-computed fixtures.
- [x] Synthetic evaluation scenarios are deterministic by seed.
- [x] Evaluation reports include machine-readable and human-readable artifacts.
- [x] The CLI can run benchmark configs and report errors as JSON.
