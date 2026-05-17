"""Report writers for Decision-PGA evaluation runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .evaluation import EvaluationReport


def write_evaluation_report(report: EvaluationReport, output_dir: str | Path) -> tuple[Path, ...]:
    """Write JSON, CSV, Markdown, and plot artifacts for an evaluation report."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    paths = (
        destination / "metrics.json",
        destination / "summary.csv",
        destination / "confusion_matrix.csv",
        destination / "advantage_report.md",
        destination / "separability.png",
        destination / "confusion_matrix.png",
        destination / "pga_vs_baseline_deltas.png",
    )

    _write_metrics_json(report, paths[0])
    _write_summary_csv(report, paths[1])
    _write_confusion_csv(report, paths[2])
    _write_markdown(report, paths[3])
    _write_separability_plot(report, paths[4])
    _write_confusion_plot(report, paths[5])
    _write_delta_plot(report, paths[6])
    return paths


def _write_metrics_json(report: EvaluationReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def _write_summary_csv(report: EvaluationReport, path: Path) -> None:
    fields = [
        "name",
        "kind",
        "expected_state",
        "pga_state",
        "baseline_state",
        "pga_correct",
        "baseline_correct",
        "mean_entropy",
        "mean_margin",
        "pc1_fraction",
        "total_dispersion",
        "half_jensen_shannon_drift",
        "half_geodesic_distance",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in report.scenarios:
            payload = result.to_dict()
            baseline = payload["baseline_metrics"]
            pga = payload["pga_metrics"]
            writer.writerow(
                {
                    "name": payload["name"],
                    "kind": payload["kind"],
                    "expected_state": payload["expected_state"],
                    "pga_state": payload["pga_state"],
                    "baseline_state": payload["baseline_state"],
                    "pga_correct": payload["pga_correct"],
                    "baseline_correct": payload["baseline_correct"],
                    "mean_entropy": baseline["mean_entropy"],
                    "mean_margin": baseline["mean_margin"],
                    "pc1_fraction": pga["pc1_fraction"],
                    "total_dispersion": pga["total_dispersion"],
                    "half_jensen_shannon_drift": baseline["half_jensen_shannon_drift"],
                    "half_geodesic_distance": pga["half_geodesic_distance"],
                }
            )


def _write_confusion_csv(report: EvaluationReport, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["expected/predicted", *report.states])
        for state, row in zip(report.states, report.confusion_matrix, strict=True):
            writer.writerow([state, *row])


def _write_markdown(report: EvaluationReport, path: Path) -> None:
    advantage = report.advantage
    lines = [
        "# Decision-PGA Evaluation Report",
        "",
        "## Conservative advantage readout",
        "",
        str(advantage["claim"]),
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| PGA accuracy | {advantage['pga_accuracy']} |",
        f"| Baseline accuracy | {advantage['baseline_accuracy']} |",
        f"| Entropy binary/diffuse gap | {advantage['entropy_binary_diffuse_gap']} |",
        f"| PGA PC1 binary/diffuse gap | {advantage['pga_binary_diffuse_gap']} |",
        "",
        "## Scenario summary",
        "",
        "| Scenario | Expected | PGA | Baseline |",
        "| --- | --- | --- | --- |",
    ]
    for result in report.scenarios:
        lines.append(
            f"| {result.spec.name} | {result.spec.expected_state} | "
            f"{result.diagnostic.state} | {result.baseline_state} |"
        )
    lines.append("")
    lines.append(
        "This report is generated from deterministic synthetic fixtures and does not call external model APIs."
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_separability_plot(report: EvaluationReport, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for result in report.scenarios:
        ax.scatter(
            result.baselines.mean_entropy,
            result.diagnostic.metrics["pc1_fraction"],
            label=result.spec.expected_state,
            s=52,
        )
        ax.annotate(result.spec.name, (result.baselines.mean_entropy, result.diagnostic.metrics["pc1_fraction"]), fontsize=7)
    ax.set_xlabel("Mean entropy")
    ax.set_ylabel("PGA PC1 fraction")
    ax.set_title("Entropy vs PGA geometry")
    ax.grid(alpha=0.25)
    _deduplicate_legend(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_confusion_plot(report: EvaluationReport, path: Path) -> None:
    matrix = np.array(report.confusion_matrix)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks(range(len(report.states)), report.states, rotation=35, ha="right")
    ax.set_yticks(range(len(report.states)), report.states)
    ax.set_xlabel("Predicted state")
    ax.set_ylabel("Expected state")
    ax.set_title("Decision-PGA confusion matrix")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            ax.text(column, row, str(matrix[row, column]), ha="center", va="center")
    fig.colorbar(image, ax=ax, shrink=0.75)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_delta_plot(report: EvaluationReport, path: Path) -> None:
    advantage = report.advantage
    labels = ["accuracy", "binary/diffuse gap"]
    pga = [
        float(advantage["pga_accuracy"]),
        float(advantage["pga_binary_diffuse_gap"]),
    ]
    baseline = [
        float(advantage["baseline_accuracy"]),
        float(advantage["entropy_binary_diffuse_gap"]),
    ]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(x - width / 2, baseline, width, label="baseline")
    ax.bar(x + width / 2, pga, width, label="PGA")
    ax.set_xticks(x, labels)
    ax.set_title("PGA vs baseline readouts")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _deduplicate_legend(ax: plt.Axes) -> None:
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles, strict=False))
    ax.legend(unique.values(), unique.keys(), fontsize=8)
