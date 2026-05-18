"""Report writers for the Decision-PGA document-extraction gap review."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .document_extraction_evaluation import (
    DOCUMENT_EXTRACTION_GAP_MATRIX_FIELDS,
    DocumentExtractionEvaluationReport,
)


def write_document_extraction_evaluation_report(
    report: DocumentExtractionEvaluationReport,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """Write JSON, CSV, Markdown, and article PDF artifacts."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    paths = (
        destination / "document_extraction_metrics.json",
        destination / "document_extraction_summary.csv",
        destination / "document_extraction_gap_matrix.csv",
        destination / "document_extraction_report.md",
        destination / "decision-pga-document-extraction-gap-review.pdf",
    )
    _write_metrics(report, paths[0])
    _write_summary_csv(report, paths[1])
    _write_gap_matrix(report, paths[2])
    _write_markdown(report, paths[3])
    _write_article_pdf(paths[4])
    return paths


def _write_metrics(report: DocumentExtractionEvaluationReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def _write_summary_csv(report: DocumentExtractionEvaluationReport, path: Path) -> None:
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


def _write_gap_matrix(report: DocumentExtractionEvaluationReport, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DOCUMENT_EXTRACTION_GAP_MATRIX_FIELDS))
        writer.writeheader()
        writer.writerows(report.gap_matrix_rows())


def _write_markdown(report: DocumentExtractionEvaluationReport, path: Path) -> None:
    summary = report.summary
    lines = [
        "# Decision-PGA Document Extraction Evaluation",
        "",
        "This report is a separate document-extraction gap readout. It does not replace the broader application-gap report and does not claim that Decision-PGA can parse documents by itself.",
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
            "1. **field-value candidate extraction**: build fixtures where extracted values, spans, and alternates are candidate labels, then compare Decision-PGA against confidence, entropy, margin, and agreement baselines.",
            "2. **table and line-item extraction**: define row, column, and item-assignment candidate clouds so PGA can be tested on structured table ambiguity rather than generic extraction confidence.",
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
            "Use this report to choose extraction fixtures. A `promising` label means the current Decision-PGA contract can plausibly evaluate candidate-cloud diagnostics once examples are available. A `needs_adapter` label means the document problem matters, but the candidate labels are not yet defined well enough for a fair test.",
            "",
            "## What this does not prove",
            "",
            "This suite is a structured review, not an OCR, layout, document parsing, or extraction benchmark. It does not measure field accuracy, table F1, provenance correctness, or human-review savings.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_article_pdf(path: Path) -> None:
    article_path = Path("docs/articles/decision-pga-document-extraction-gap-review.md")
    if article_path.exists():
        text = article_path.read_text(encoding="utf-8")
    else:
        text = "# Decision-PGA Document Extraction Gap Review\n\nArticle Markdown was not found in this checkout."

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
