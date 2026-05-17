---
id: DPGA-T016
type: task
title: Implement MCP Tools
status: done
parent: DPGA-S007
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [mcp, tools]
links:
  - ../../../decision_pga/mcp_server.py
  - ../../../tests/test_mcp_server.py
---

# DPGA-T016: Implement MCP Tools

## Description

Expose the existing Decision-PGA diagnostic APIs as local read-only MCP tool
helpers.

## Acceptance Criteria

- [x] Probability-cloud, model-output, sampled-response, and trajectory tools are exposed.
- [x] MCP tool helpers return the same diagnostic dictionaries as the Python API.
- [x] Metric explanations are available as JSON-compatible context.
