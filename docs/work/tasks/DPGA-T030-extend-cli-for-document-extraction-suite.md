---
id: DPGA-T030
type: task
title: Extend CLI For Document Extraction Suite
status: done
parent: DPGA-S013
created: 2026-05-18
completed: 2026-05-18
priority: P1
tags: [document-extraction, cli]
links:
  - ../../../decision_pga/cli.py
---

# DPGA-T030: Extend CLI For Document Extraction Suite

## Description

Add `document-extraction` routing to the evaluate command.

## Acceptance Criteria

- [x] `--suite document-extraction` returns document-extraction output.
- [x] `--suite all` includes document-extraction artifacts.
