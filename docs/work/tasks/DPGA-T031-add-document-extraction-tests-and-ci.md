---
id: DPGA-T031
type: task
title: Add Document Extraction Tests And CI
status: done
parent: DPGA-S013
created: 2026-05-18
completed: 2026-05-18
priority: P2
tags: [document-extraction, tests, ci]
links:
  - ../../../tests/test_document_extraction_evaluation.py
  - ../../../tests/test_cli.py
  - ../../../.github/workflows/tests.yml
---

# DPGA-T031: Add Document Extraction Tests And CI

## Description

Add unit, CLI, and CI smoke coverage for the document-extraction suite.

## Acceptance Criteria

- [x] Tests cover deterministic scenarios, fit labels, gap matrix columns, article links, and report files.
- [x] CLI tests cover separate suite output and `all` bundle inclusion.
- [x] CI runs a document-extraction suite smoke test.
