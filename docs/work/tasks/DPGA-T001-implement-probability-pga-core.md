---
id: DPGA-T001
type: task
title: Implement Probability PGA Core
status: done
parent: DPGA-S001
created: 2026-05-16
completed: 2026-05-16
priority: P0
tags: [python, core]
links:
  - ../../../decision_pga/probability_pga.py
---

# DPGA-T001: Implement Probability PGA Core

## Description

Implement Fisher-Rao/square-root PGA helpers for categorical probability
clouds.

## Acceptance Criteria

- [x] Probability vectors are normalized with a positive epsilon floor.
- [x] Square-root embeddings lie on the positive unit sphere.
- [x] Intrinsic mean, sphere log, and sphere exp are implemented.
- [x] PGA returns mean probability, tangent vectors, tensor, eigenvalues, eigenvectors, total dispersion, PC1 fraction, anisotropy ratio, and mean margin.
