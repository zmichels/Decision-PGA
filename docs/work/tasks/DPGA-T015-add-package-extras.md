---
id: DPGA-T015
type: task
title: Add Package Extras
status: done
parent: DPGA-S006
created: 2026-05-17
completed: 2026-05-17
priority: P2
tags: [packaging]
links:
  - ../../../pyproject.toml
  - ../../../tests/test_packaging.py
---

# DPGA-T015: Add Package Extras

## Description

Declare optional package extras for development and MCP usage.

## Acceptance Criteria

- [x] `dev` extra is declared.
- [x] `mcp` extra installs the official MCP Python package.
- [x] `decision-pga-mcp` console script is declared.
