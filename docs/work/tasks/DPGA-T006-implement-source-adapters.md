---
id: DPGA-T006
type: task
title: Implement Source Adapters
status: done
parent: DPGA-S003
created: 2026-05-17
completed: 2026-05-17
priority: P2
tags: [adapters, sampled-responses, trajectories]
links:
  - ../../../decision_pga/source_adapters.py
  - ../../../tests/test_source_adapters.py
  - ../../source-adapters.md
---

# DPGA-T006: Implement Source Adapters

## Description

Add provider-neutral adapters that convert sampled free-form responses and
agent trajectory steps into candidate-aligned rolling probability clouds.

## Acceptance Criteria

- [x] Sampled responses can be mapped with explicit label aliases.
- [x] Sampled responses can be diagnosed through the existing Decision-PGA policy layer.
- [x] Trajectory choices can be converted into rolling empirical probability rows.
- [x] Trajectory diagnostics are JSON-serializable for agent tool callers.
