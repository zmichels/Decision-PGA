---
id: DPGA-T012
type: task
title: Generate Evaluation Reports
status: done
parent: DPGA-S005
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [reports, plots]
links:
  - ../../../decision_pga/reporting.py
  - ../../../docs/evaluation.md
---

# DPGA-T012: Generate Evaluation Reports

## Description

Write reproducible report artifacts for evaluation runs.

## Acceptance Criteria

- [x] Reports include `metrics.json`, `summary.csv`, `confusion_matrix.csv`, and `advantage_report.md`.
- [x] Reports include separability, confusion, and PGA-vs-baseline plots.
- [x] The advantage report states conservative claims plainly.
