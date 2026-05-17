---
id: DPGA-T008
type: task
title: Implement CLI JSON Contract
status: done
parent: DPGA-S004
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [cli, tests, examples]
links:
  - ../../../decision_pga/cli.py
  - ../../../tests/test_cli.py
  - ../../cli.md
  - ../../../examples/model_outputs.json
---

# DPGA-T008: Implement CLI JSON Contract

## Description

Implement the command-line interface, package console script, example payloads,
and focused tests for the JSON tool boundary.

## Acceptance Criteria

- [x] CLI tests cover file input, stdin input, provider score input, sampled responses, and error output.
- [x] `pyproject.toml` exposes the `decision-pga` console script.
- [x] Example JSON payloads are present under `examples/`.
- [x] CLI documentation records source shapes, output shape, and exit codes.
