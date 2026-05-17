---
id: DPGA-S002
type: story
title: Plan Agent Tool Wrapper
status: done
parent: DPGA-F002
children:
  - DPGA-T004
  - DPGA-T005
created: 2026-05-16
completed: 2026-05-17
priority: P1
tags: [future, tool-interface]
---

# DPGA-S002: Plan Agent Tool Wrapper

## Description

Define the later agent-facing shape for Decision-PGA diagnostics once the
synthetic core has been validated.

## Acceptance Criteria

- [x] Inputs and outputs for an agent-callable diagnostic are specified.
- [x] The wrapper distinguishes proceed, clarify, gather-evidence, inspect, and segment/replan recommendations.
- [x] Real-model adapter assumptions are separated from core probability-cloud math.
