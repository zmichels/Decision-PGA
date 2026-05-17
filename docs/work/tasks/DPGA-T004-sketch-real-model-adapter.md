---
id: DPGA-T004
type: task
title: Sketch Real Model Adapter
status: done
parent: DPGA-S002
created: 2026-05-16
completed: 2026-05-17
priority: P1
tags: [future, adapter]
links:
  - ../../../decision_pga/model_adapters.py
  - ../../../tests/test_model_adapters.py
  - ../../model-output-adapters.md
---

# DPGA-T004: Sketch Real Model Adapter

## Description

After the synthetic prototype is stable, define how real model outputs or agent
state trajectories should feed the Decision-PGA core.

## Acceptance Criteria

- [x] Adapter inputs cover output probabilities/logprobs without requiring hidden activations.
- [x] Agent-facing diagnostic states and recommendations are named.
- [x] Any API-key-dependent examples remain optional.
