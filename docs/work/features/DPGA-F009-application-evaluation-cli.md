---
id: DPGA-F009
type: feature
title: Application Evaluation CLI
status: done
parent: DPGA-E003
children:
  - DPGA-S010
created: 2026-05-18
completed: 2026-05-18
priority: P1
tags: [cli, evaluation]
---

# DPGA-F009: Application Evaluation CLI

## Description

Extend `decision-pga evaluate` with suite selection while preserving benchmark
behavior.

## Acceptance Criteria

- [x] `--suite benchmark` preserves existing benchmark output.
- [x] `--suite application` writes application-gap artifacts.
- [x] `--suite all` writes benchmark and application artifacts together.
- [x] Invalid suite names return machine-readable CLI errors.
