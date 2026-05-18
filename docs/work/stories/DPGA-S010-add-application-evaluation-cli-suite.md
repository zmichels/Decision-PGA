---
id: DPGA-S010
type: story
title: Add Application Evaluation CLI Suite
status: done
parent: DPGA-F009
children:
  - DPGA-T022
  - DPGA-T023
  - DPGA-T024
created: 2026-05-18
completed: 2026-05-18
priority: P1
tags: [cli, tests]
---

# DPGA-S010: Add Application Evaluation CLI Suite

## Description

Expose application evaluation through the existing CLI without breaking the
benchmark behavior.

## Acceptance Criteria

- [x] Suite routing supports benchmark, application, and all.
- [x] Tests cover output artifacts and invalid suite errors.
- [x] CI includes an application suite smoke test.
