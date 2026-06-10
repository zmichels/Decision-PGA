# Kinematic Trajectory Diagnostics Design

Date: 2026-06-10
Status: draft for review

## Purpose

Decision-PGA already diagnoses the shape of repeated probability-like observations
over a fixed label set. This feature makes multi-step agent and application traces
first-class by adding a `kinematic_trajectory` source type.

The goal is to describe how observed decision states move across operational
steps, such as input, retrieval, tool selection, validation, and output. The
feature should report geodesic velocity, acceleration, jerk-like instability,
and dominant drift directions while staying within the existing Fisher-Rao
probability geometry.

This is an observed decision-state diagnostic. It does not inspect hidden model
activations, infer causal internal physics, or claim that the model literally has
mechanical forces. Kinematic language is used as a disciplined geometric analogy
for movement across probability states.

## Recommended Approach

Implement the feature inside the existing `Decision-PGA` package as an integrated
source type rather than creating a sibling package.

Reasons:

- The existing `probability_pga.py` module is already the geometry authority.
- The current source adapters already support agent trajectories, but only by
  collapsing steps into rolling probability clouds.
- A new source type can reuse the CLI, MCP, examples, and JSON boundary that
  testers already have.
- Keeping this in-tree reduces the chance of a second, inconsistent PGA math
  implementation.

## Input Contract

Add support for a JSON payload with this shape:

```json
{
  "source": "kinematic_trajectory",
  "label": "agent rag/tool trajectory",
  "labels": ["retrieve_evidence", "draft_answer", "ask_user", "abstain"],
  "steps": ["input", "rag", "tool", "output"],
  "runs": [
    [
      [0.60, 0.20, 0.10, 0.10],
      [0.40, 0.40, 0.10, 0.10],
      [0.20, 0.65, 0.10, 0.05],
      [0.15, 0.70, 0.10, 0.05]
    ],
    [
      [0.62, 0.18, 0.10, 0.10],
      [0.35, 0.45, 0.10, 0.10],
      [0.18, 0.62, 0.10, 0.10],
      [0.05, 0.20, 0.65, 0.10]
    ]
  ]
}
```

`runs` must have shape `num_runs x num_steps x num_labels`.

Rows are probability-like candidate distributions and should be normalized by
the same probability handling used elsewhere in Decision-PGA. Labels must match
the final tensor dimension. Step names are optional, but if present they must
match the step dimension.

## Proposed Python API

Add a new module:

```text
decision_pga/kinematics.py
```

Expose a public function:

```python
diagnose_kinematic_trajectory(
    runs,
    labels=None,
    step_names=None,
    label=None,
)
```

The implementation should reuse existing geometry helpers:

- `normalize_probabilities`
- `sqrt_embed`
- `intrinsic_mean_sphere`
- `sphere_log`
- `sphere_exp`
- `pga_probability_cloud`

It should not duplicate logarithmic-map or exponential-map math.

## Diagnostic Payload

Return a JSON-friendly result with:

- `source_kind`: `kinematic_trajectory`
- `label`
- `labels`
- `steps`
- `shape`: run count, step count, label count
- `canonical_path_probabilities`: Fréchet mean probability at each step
- `step_kinetic_energy`: average geodesic velocity energy for each transition
- `step_jerk`: average acceleration norm for each second-order transition
- `systemic_kinetic_energy`: average kinetic energy across all transitions
- `systemic_jerk`: average acceleration norm across all second-order transitions
- `velocity_dispersion`: compact tensor and eigenvalue summaries
- `acceleration_dispersion`: compact tensor and eigenvalue summaries
- `primary_drift_labels`: label components most involved in the first velocity
  dispersion axis

The first version should avoid returning huge raw vector matrices by default.
Raw vectors can be added later behind an explicit verbose flag if needed.

## Data Flow

1. Validate the tensor as `runs x steps x labels`.
2. Normalize each probability row.
3. Square-root embed each row onto the positive unit sphere.
4. Compute the canonical trajectory by taking the intrinsic mean across runs at
   each step.
5. Compute step velocities for each run using `sphere_log(base, target)`.
6. Transport or approximate velocity comparison in a documented first version.
   The first slice may compare velocities in the ambient embedding coordinates
   after projection, provided the limitation is documented in the output.
7. Compute accelerations as changes between consecutive velocities.
8. Run dispersion summaries over velocity and acceleration vectors.
9. Emit a deterministic JSON payload and route it through the CLI after the
   Python API is stable. MCP exposure can follow in a later slice.

## Classification Policy

Do not add a new high-level state classifier in the first implementation.

The initial output should be metric-first:

- low kinetic energy, low jerk: stable path
- high kinetic energy, low jerk: smooth systematic drift
- high jerk: sharp step-local deflection
- high velocity dispersion: different runs follow different drift axes

A later slice can map those profiles into named states such as
`smooth_drift`, `boundary_turbulence`, or `stiff_inconsistency` after examples
and thresholds are exercised.

## Error Handling

Raise clear `ValueError` messages for:

- tensors that are not three-dimensional;
- fewer than one run, fewer than two steps, or fewer than two labels;
- non-finite values;
- negative probability values;
- label count mismatches;
- step-name count mismatches.

Use existing probability normalization behavior for zero-like and unnormalized
rows wherever possible.

## Testing Strategy

Use test-driven development for each behavior. No production implementation
should be added before a failing test is observed.

Initial tests:

1. Rejects tensors that are not `runs x steps x labels`.
2. Rejects label and step-name dimension mismatches.
3. Returns near-zero kinetic energy and jerk for identical repeated states.
4. Reports higher final-step jerk when half the runs sharply deflect at output.
5. Returns a canonical path with one probability vector per step.
6. Emits JSON-safe output with no NumPy scalars or arrays leaking through.
7. Routes a `source: kinematic_trajectory` CLI payload into the new diagnostic.

Secondary tests after the Python API:

- Example fixture coverage under `examples/agent/`.
- MCP tool payload smoke test if the CLI shape proves stable.
- Documentation examples that run through the same CLI path.

## First Implementation Slice

The smallest useful implementation should include:

- `decision_pga/kinematics.py`
- Python API tests
- `__init__.py` export
- CLI source routing
- one checked-in example payload
- one short docs section in `docs/agent-toolkit.md` or a dedicated
  `docs/kinematic-trajectory.md`

MCP exposure, plotting, and threshold-based named kinematic states should wait
until the core payload is tested and readable.

## Open Decisions

- Whether to include raw velocity and acceleration vectors by default or only in
  verbose output.
- Whether the first acceleration comparison should use approximate ambient
  tangent differences or implement parallel transport along each geodesic.
- Whether to name high-level kinematic states in v1 or keep the first release
  metric-first.

For the first slice, choose compact summaries, document the acceleration
approximation, and avoid new high-level state names.
