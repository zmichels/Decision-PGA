---
id: DPGA-T007
type: task
title: Add Provider Bridges
status: done
parent: DPGA-S003
created: 2026-05-17
completed: 2026-05-17
priority: P3
tags: [future, providers, adapters]
links:
  - ../../../decision_pga/provider_bridges.py
  - ../../../tests/test_provider_bridges.py
  - ../../provider-bridges.md
---

# DPGA-T007: Add Provider Bridges

## Description

Add optional thin extractors that translate provider-specific response objects
into `ModelOutputObservation` without changing the core Decision-PGA API.

## Acceptance Criteria

- [x] Bridge code is optional and does not import provider SDKs in the core path.
- [x] Provider response objects can be converted into candidate-aligned score observations.
- [x] Missing candidate-score behavior is explicit rather than silently imputed.
