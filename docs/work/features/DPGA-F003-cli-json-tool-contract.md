---
id: DPGA-F003
type: feature
title: CLI JSON Tool Contract
status: done
parent: DPGA-E001
children:
  - DPGA-S004
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [cli, tool-interface, json]
---

# DPGA-F003: CLI JSON Tool Contract

## Description

Expose Decision-PGA as a deterministic JSON-in / JSON-out command-line tool so
agents, shell scripts, eval harnesses, and future services can call the
diagnostic without importing Python modules directly.

## Acceptance Criteria

- [x] The CLI accepts JSON payloads for all supported source types.
- [x] Successful diagnostics write deterministic JSON to stdout.
- [x] Input and validation errors write machine-readable JSON errors to stderr.
- [x] Example payloads document the process boundary.
