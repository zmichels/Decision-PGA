from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


AGENT_EXAMPLES = [
    "tool_action_ambiguity.json",
    "rag_evidence_conflict.json",
    "document_extraction_routing.json",
    "multi_step_agent_drift.json",
    "abstain_defer_decision.json",
]


def main() -> int:
    for filename in AGENT_EXAMPLES:
        result = _run(
            [
                sys.executable,
                "-m",
                "decision_pga.cli",
                "diagnose",
                str(ROOT / "examples" / "agent" / filename),
            ]
        )
        payload = json.loads(result.stdout)
        print(f"{filename}: {payload['diagnostic']['state']}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "benchmark"
        _run(
            [
                sys.executable,
                "-m",
                "decision_pga.cli",
                "evaluate",
                "--config",
                str(ROOT / "examples" / "evaluation_config.json"),
                "--output",
                str(output_dir),
            ]
        )
        print(f"benchmark smoke: {output_dir / 'advantage_report.md'}")

    try:
        from decision_pga.mcp_server import build_server

        build_server()
        print("mcp smoke: ok")
    except RuntimeError as exc:
        print(f"mcp smoke: skipped ({exc})")

    return 0


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
