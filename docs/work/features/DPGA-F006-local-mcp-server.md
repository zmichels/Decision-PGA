---
id: DPGA-F006
type: feature
title: Local MCP Server
status: done
parent: DPGA-E002
children:
  - DPGA-S007
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [mcp, tool-interface, agents]
---

# DPGA-F006: Local MCP Server

## Description

Expose Decision-PGA diagnostics through a local stdio MCP server while
preserving the existing Python and JSON diagnostic contracts.

## Acceptance Criteria

- [x] MCP tools expose probability-cloud, model-output, sampled-response, and trajectory diagnostics.
- [x] MCP outputs preserve the stable diagnostic payload.
- [x] The MCP server remains local, deterministic, and free of model API calls.
- [x] Docs and CI smoke tests cover server construction.
