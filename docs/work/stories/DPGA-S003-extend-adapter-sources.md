---
id: DPGA-S003
type: story
title: Extend Adapter Sources
status: done
parent: DPGA-F002
children:
  - DPGA-T006
  - DPGA-T007
created: 2026-05-17
completed: 2026-05-17
priority: P2
tags: [future, adapters, trajectories]
---

# DPGA-S003: Extend Adapter Sources

## Description

Build on the provider-neutral model-output adapter by adding optional source
adapters for sampled responses, agent trajectories, and provider-specific
response objects.

## Acceptance Criteria

- [x] Sampled free-form responses can be mapped to candidate labels or semantic clusters.
- [x] Agent trajectories can be windowed into candidate-aligned probability clouds.
- [x] Provider bridges translate response objects into `ModelOutputObservation` without changing the core PGA API.
