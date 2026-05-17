---
id: DPGA-S007
type: story
title: Add Local MCP Server
status: done
parent: DPGA-F006
children:
  - DPGA-T016
  - DPGA-T017
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [mcp, stdio]
---

# DPGA-S007: Add Local MCP Server

## Description

Wrap the existing Decision-PGA diagnostic functions as read-only local MCP
tools.

## Acceptance Criteria

- [x] MCP tool helpers match the existing Python API payloads.
- [x] A `decision-pga-mcp` console script is declared.
- [x] MCP docs explain install, stdio launch, and example payloads.
- [x] CI installs the MCP extra and constructs the server.
