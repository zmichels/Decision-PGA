---
id: DPGA-F004
type: feature
title: Robust Evaluation Harness
status: done
parent: DPGA-E002
children:
  - DPGA-S005
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [evaluation, baselines, reporting]
---

# DPGA-F004: Robust Evaluation Harness

## Description

Add deterministic synthetic benchmark tooling that compares Decision-PGA
diagnostics with entropy, margin, switch-rate, and drift baselines.

## Acceptance Criteria

- [x] Baseline metrics include entropy, margin, label switching, Jensen-Shannon drift, and Euclidean drift.
- [x] Evaluation scenarios include ambiguity, diffuse uncertainty, boundary sensitivity, regime shift, and sweeps.
- [x] Reports include JSON, CSV, Markdown, and plot artifacts.
- [x] CLI and CI can run the benchmark from a checked-in config.
