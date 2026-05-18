---
id: DPGA-T023
type: task
title: Extend Evaluate CLI Suite Routing
status: done
parent: DPGA-S010
created: 2026-05-18
completed: 2026-05-18
priority: P1
tags: [cli]
links:
  - ../../../decision_pga/cli.py
---

# DPGA-T023: Extend Evaluate CLI Suite Routing

## Description

Add `--suite` routing to the evaluate command.

## Acceptance Criteria

- [x] `benchmark`, `application`, and `all` suites are supported.
- [x] Invalid suite names return JSON errors.
