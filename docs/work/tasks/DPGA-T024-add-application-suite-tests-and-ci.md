---
id: DPGA-T024
type: task
title: Add Application Suite Tests And CI
status: done
parent: DPGA-S010
created: 2026-05-18
completed: 2026-05-18
priority: P2
tags: [tests, ci]
links:
  - ../../../tests/test_application_evaluation.py
  - ../../../tests/test_cli.py
  - ../../../.github/workflows/tests.yml
---

# DPGA-T024: Add Application Suite Tests And CI

## Description

Add unit, CLI, and CI smoke coverage for the application suite.

## Acceptance Criteria

- [x] Tests cover deterministic scenarios, fit labels, gap matrix columns, article links, and report files.
- [x] CLI tests cover benchmark, application, all, and invalid suites.
- [x] CI runs an application suite smoke test.
