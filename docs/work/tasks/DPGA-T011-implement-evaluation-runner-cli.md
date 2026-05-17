---
id: DPGA-T011
type: task
title: Implement Evaluation Runner CLI
status: done
parent: DPGA-S005
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [cli, evaluation]
links:
  - ../../../decision_pga/evaluation.py
  - ../../../decision_pga/cli.py
  - ../../../tests/test_evaluation.py
  - ../../../tests/test_cli.py
---

# DPGA-T011: Implement Evaluation Runner CLI

## Description

Add `decision-pga evaluate` for benchmark configs and machine-readable error
handling.

## Acceptance Criteria

- [x] The CLI accepts `--config` and `--output`.
- [x] Successful runs emit JSON listing report files.
- [x] Invalid configs return JSON errors on stderr.
