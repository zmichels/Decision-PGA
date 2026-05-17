---
id: DPGA-T017
type: task
title: Add MCP Docs And Smoke Tests
status: done
parent: DPGA-S007
created: 2026-05-17
completed: 2026-05-17
priority: P2
tags: [mcp, docs, ci]
links:
  - ../../../docs/mcp-server.md
  - ../../../.github/workflows/tests.yml
---

# DPGA-T017: Add MCP Docs And Smoke Tests

## Description

Document MCP setup and ensure CI can install the optional MCP extra and build
the server.

## Acceptance Criteria

- [x] MCP docs include install, stdio launch, and example tool payloads.
- [x] CI installs `.[mcp]`.
- [x] CI constructs the MCP server without launching a long-running stdio session.
