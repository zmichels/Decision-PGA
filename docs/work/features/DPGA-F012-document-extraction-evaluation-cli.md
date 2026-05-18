---
id: DPGA-F012
type: feature
title: Document Extraction Evaluation CLI
status: done
parent: DPGA-E004
children:
  - DPGA-S013
created: 2026-05-18
completed: 2026-05-18
priority: P1
tags: [document-extraction, cli]
---

# DPGA-F012: Document Extraction Evaluation CLI

## Description

Expose the document-extraction review through the existing evaluation CLI as a
separate suite.

## Acceptance Criteria

- [x] `--suite document-extraction` writes separate artifacts.
- [x] `--suite all` includes document-extraction artifacts without changing benchmark and application outputs.
- [x] CLI and CI cover the new suite.
