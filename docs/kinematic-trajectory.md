# Kinematic Trajectory Diagnostics

`kinematic_trajectory` diagnoses observed movement across multi-step agent or
application traces. It accepts a tensor shaped as `runs x steps x labels`, where
each row is a probability-like distribution over the same candidate labels.

This diagnostic reports motion in Fisher-Rao probability geometry. It does not
inspect hidden model activations or prove causal internal forces.

## Run The Example

```bash
decision-pga diagnose --pretty examples/agent/kinematic_trajectory_rag_tool_whiplash.json
```

## Reading The Output

- `canonical_path_probabilities`: the Fréchet mean decision state at each step.
- `step_kinetic_energy`: average geodesic movement for each transition.
- `step_jerk`: average change in velocity direction or magnitude between
  neighboring transitions.
- `systemic_kinetic_energy`: overall trajectory movement.
- `systemic_jerk`: overall sharp deflection.
- `velocity_dispersion`: whether runs share a similar drift axis or split into
  different directions.
- `acceleration_comparison`: the first version uses `ambient_tangent_delta`,
  an approximate comparison of neighboring velocity vectors in embedding
  coordinates.

Use low kinetic energy and low jerk as a stable-path signal. Use high jerk as a
review signal that one step sharply deflected the observed decision state.
