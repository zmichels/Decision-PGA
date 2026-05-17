# Evaluation Harness

Decision-PGA includes a deterministic synthetic benchmark for checking whether
PGA geometry adds signal beyond entropy, margins, and simple drift metrics.

Run the default checked-in benchmark:

```bash
decision-pga evaluate --config examples/evaluation_config.json --output reports/latest
```

The command writes:

- `metrics.json`: complete machine-readable report.
- `summary.csv`: one row per scenario.
- `confusion_matrix.csv`: expected vs PGA-predicted states.
- `advantage_report.md`: concise human-readable interpretation.
- `separability.png`, `confusion_matrix.png`, `pga_vs_baseline_deltas.png`.

The conservative advantage claim is intentionally modest. PGA is treated as
useful only when it improves separability or state classification over
entropy/margin baselines on held-out deterministic fixtures. If it does not,
the generated report says so.

No benchmark scenario calls a model API. The fixture set is synthetic-first so
that class count, sample count, ambiguity, diffusion, and regime-shift behavior
can be tested without provider variance.
