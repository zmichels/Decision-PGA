---
id: DPGA-S004
type: story
title: Build CLI Process Boundary
status: done
parent: DPGA-F003
children:
  - DPGA-T008
created: 2026-05-17
completed: 2026-05-17
priority: P0
tags: [cli, json, agents]
---

# DPGA-S004: Build CLI Process Boundary

## Description

Add a `decision-pga diagnose` command that dispatches JSON payloads into the
existing probability-cloud, model-output, sampled-response, trajectory, and
provider-bridge adapters.

## Acceptance Criteria

- [x] `probability_cloud` payloads call the core diagnostic API.
- [x] `model_outputs`, `sampled_responses`, `trajectory_steps`, `provider_scores`, and `provider_token_scores` payloads call their adapters.
- [x] CLI output uses a stable JSON envelope with `source` and `diagnostic`.
- [x] Stdin and file input are both supported.
