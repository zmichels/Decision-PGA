---
id: DPGA-T002
type: task
title: Add Synthetic Cloud Tests
status: done
parent: DPGA-S001
created: 2026-05-16
completed: 2026-05-16
priority: P0
tags: [tests, synthetic]
links:
  - ../../../tests/test_probability_pga.py
---

# DPGA-T002: Add Synthetic Cloud Tests

## Description

Add unit tests that pin down the first Decision-PGA probability-cloud behavior.

## Acceptance Criteria

- [x] Identical distributions produce near-zero dispersion.
- [x] Normalized probabilities sum to one and remain positive.
- [x] Square-root embeddings have unit norm.
- [x] Sphere exp/log round-trips localized samples.
- [x] Binary ambiguity has high PC1 fraction.
- [x] Diffuse uncertainty has lower PC1 fraction than binary ambiguity at comparable entropy.
