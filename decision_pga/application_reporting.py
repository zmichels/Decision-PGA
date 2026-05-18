"""Report writers for the Decision-PGA application-gap review."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .application_evaluation import (
    ApplicationEvaluationReport,
    GAP_MATRIX_FIELDS,
)


def write_application_evaluation_report(
    report: ApplicationEvaluationReport,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """Write JSON, CSV, Markdown, and article PDF artifacts."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    paths = (
        destination / "application_metrics.json",
        destination / "application_summary.csv",
        destination / "gap_matrix.csv",
        destination / "application_report.md",
        destination / "decision-pga-gap-review.pdf",
    )
    _write_application_metrics(report, paths[0])
    _write_application_summary(report, paths[1])
    _write_gap_matrix(report, paths[2])
    _write_application_markdown(report, paths[3])
    _write_article_pdf(paths[4])
    return paths


def _write_application_metrics(report: ApplicationEvaluationReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def _write_application_summary(report: ApplicationEvaluationReport, path: Path) -> None:
    fields = [
        "gap_family",
        "use_case",
        "touchstone",
        "fit_label",
        "implementation_difficulty",
        "baseline_reading",
        "pga_reading",
        "incremental_value",
        "recommended_next_step",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for scenario in report.scenarios:
            payload = scenario.to_dict()
            writer.writerow({field: payload[field] for field in fields})


def _write_gap_matrix(report: ApplicationEvaluationReport, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(GAP_MATRIX_FIELDS))
        writer.writeheader()
        writer.writerows(report.gap_matrix_rows())


def _write_application_markdown(report: ApplicationEvaluationReport, path: Path) -> None:
    summary = report.summary
    lines = [
        "# Decision-PGA Application Evaluation",
        "",
        "This report is a conservative application-gap readout. It does not claim that Decision-PGA is a production safety layer; it identifies where the current local diagnostic contract is ready for deeper testing and where adapters are still missing.",
        "",
        "## Summary",
        "",
        str(summary["claim"]),
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    fit_counts = summary.get("fit_counts", {})
    if isinstance(fit_counts, dict):
        for label, count in fit_counts.items():
            lines.append(f"| `{label}` | {count} |")

    lines.extend(
        [
            "",
            "## Recommended deep dives",
            "",
            "1. **agent tool/action selection**: build fixtures where candidate tools and next actions are the decision labels, then compare Decision-PGA against entropy, margin, and switch-rate baselines.",
            "2. **RAG/evidence conflict**: define an adapter from retrieved evidence and claim clusters into probability clouds before making any stronger performance claim.",
            "",
            "## Gap matrix",
            "",
            "| Gap family | Fit | Current failure mode | Decision-PGA contribution | Next step |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for scenario in report.scenarios:
        lines.append(
            "| "
            + " | ".join(
                [
                    scenario.gap_family,
                    scenario.fit_label,
                    scenario.current_failure_mode,
                    scenario.decision_pga_contribution,
                    scenario.recommended_next_step,
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## What this tells a tester",
            "",
            "Use this report to pick the next fixture family. A `promising` label means the current Decision-PGA interfaces can probably support a fair comparison now. A `needs_adapter` label means the use case matters, but the missing adapter is the honest next step.",
            "",
            "## What this does not prove",
            "",
            "This suite is a structured review, not live model validation. It does not measure real-agent task success, factuality, human preference, or safety outcomes.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_article_pdf(path: Path) -> None:
    article_path = Path("docs/articles/decision-pga-gap-review.md")
    if article_path.exists():
        text = article_path.read_text(encoding="utf-8")
    else:
        text = "# Decision-PGA Gap Review\n\nArticle Markdown was not found in this checkout."

    pages = _markdown_to_pdf_pages(text)
    with PdfPages(path) as pdf:
        for page in pages:
            fig = plt.figure(figsize=(8.5, 11))
            fig.patch.set_facecolor("white")
            fig.text(
                0.08,
                0.95,
                page,
                ha="left",
                va="top",
                fontsize=9,
                family="DejaVu Sans",
                linespacing=1.32,
            )
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def _markdown_to_pdf_pages(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("# "):
            lines.append(stripped[2:])
            lines.append("")
        elif stripped.startswith("## "):
            lines.append("")
            lines.append(stripped[3:])
        elif stripped.startswith("### "):
            lines.append("")
            lines.append(stripped[4:])
        elif stripped.startswith("- "):
            wrapped = textwrap.wrap(stripped[2:], width=92)
            if wrapped:
                lines.append("- " + wrapped[0])
                lines.extend("  " + line for line in wrapped[1:])
            else:
                lines.append("-")
        elif stripped:
            lines.extend(textwrap.wrap(stripped, width=96))
        else:
            lines.append("")

    pages: list[str] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= 64:
            pages.append("\n".join(current))
            current = []
    if current:
        pages.append("\n".join(current))
    return pages or [""]
