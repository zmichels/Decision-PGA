---
id: DPGA-T014
type: task
title: Add Tester Examples
status: done
parent: DPGA-S006
created: 2026-05-17
completed: 2026-05-17
priority: P1
tags: [examples, testers]
links:
  - ../../../examples/tester/stable_probability_cloud.json
  - ../../../examples/tester/binary_ambiguity_model_outputs.json
  - ../../../examples/tester/diffuse_probability_cloud.json
  - ../../../examples/tester/regime_shift_sampled_responses.json
  - ../../../examples/tester/provider_scores.json
---

# DPGA-T014: Add Tester Examples

## Description

Check in small JSON payloads that testers can run through `decision-pga
diagnose`.

## Acceptance Criteria

- [x] Stable, binary ambiguity, diffuse uncertainty, and regime-shift examples are included.
- [x] A provider-score-shaped example is included.
- [x] Examples do not require model credentials.
