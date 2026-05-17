"""Scaffold a repo-native Markdown/YAML work tracker."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


DEFAULT_CONFIG = """project_prefix: {project_prefix}
project_name: {project_name}
statuses:
  - proposed
  - ready
  - active
  - blocked
  - done
  - deferred
  - superseded
priorities:
  - P0
  - P1
  - P2
  - P3
types:
  epic:
    folder: epics
    id_letter: E
    parent:
  feature:
    folder: features
    id_letter: F
    parent: epic
  story:
    folder: stories
    id_letter: S
    parent: feature
  task:
    folder: tasks
    id_letter: T
    parent: story
"""


def scaffold(root: Path, project_prefix: str, project_name: str, force: bool = False) -> None:
    if root.exists() and any(root.iterdir()) and not force:
        raise FileExistsError(f"{root} already exists and is not empty. Use --force to merge scaffold files.")

    for folder in ("epics", "features", "stories", "tasks", "diagrams"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    _write(
        root / "tracker.config.yaml",
        DEFAULT_CONFIG.format(project_prefix=project_prefix, project_name=project_name),
        force=force,
    )
    _write(root / "index.md", _index_md(project_name), force=force)
    _write(root / "tracker-guide.md", _guide_md(), force=force)
    _write(root / "timeline.md", _timeline_md(), force=force)
    _write(root / "diagrams" / "README.md", _diagrams_md(), force=force)
    for folder in ("epics", "features", "stories", "tasks"):
        _write(root / folder / ".gitkeep", "", force=force)


def _write(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _index_md(project_name: str) -> str:
    return f"""# Work Tracker

This folder tracks {project_name} work using Markdown files with YAML frontmatter.

## Commands

Validate:

```bash
python scripts/work_tracker.py docs/work
```

Summary:

```bash
python scripts/work_tracker.py docs/work --summary
```

Mermaid:

```bash
python scripts/work_tracker.py docs/work --mermaid
```
"""


def _guide_md() -> str:
    return """# Work Tracker Guide

Use `epics/`, `features/`, `stories/`, and `tasks/` to track project progress.

Every item needs YAML frontmatter, a `## Description` section, and a `## Acceptance Criteria` section with checkboxes.

Run validation before committing tracker changes:

```bash
python scripts/work_tracker.py docs/work
```
"""


def _timeline_md() -> str:
    return """# Project Timeline

Use this file for narrative milestones. Keep canonical status in individual work item files.
"""


def _diagrams_md() -> str:
    return """# Work Tracker Diagrams

Generated Mermaid diagrams can be placed here when a chart snapshot is useful. The source of truth remains the work item files.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Markdown/YAML work tracker.")
    parser.add_argument("--root", default="docs/work", help="Tracker root directory.")
    parser.add_argument("--project-prefix", default="PROJ", help="Stable ID prefix such as EMSEG or APP.")
    parser.add_argument("--project-name", default="Project", help="Human-readable project name.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold files that already exist.")
    args = parser.parse_args(argv)

    scaffold(Path(args.root), args.project_prefix, args.project_name, force=args.force)
    print(f"Scaffolded tracker at {Path(args.root)} with prefix {args.project_prefix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
