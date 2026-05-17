---
id: DPGA-F002
type: feature
title: Real Model And Agent Adapters
status: done
parent: DPGA-E001
children:
  - DPGA-S002
  - DPGA-S003
created: 2026-05-16
completed: 2026-05-17
priority: P1
tags: [future, agents, adapters]
---

# DPGA-F002: Real Model And Agent Adapters

## Description

Extend the synthetic Decision-PGA method to real model outputs and agent-state
trajectories after the probability-cloud geometry is stable.

## Acceptance Criteria

- [x] Adapter boundaries are documented for model logprobs, sampled responses, and agent trajectories.
- [x] Real-model work remains optional and does not block the synthetic prototype.
- [x] Agent-facing output fields are mapped from the core PGA result object.
- [x] Provider bridges, sampled-response adapters, and trajectory-window adapters remain separated from the core PGA math.
