# Work Tracker Guide

Use `epics/`, `features/`, `stories/`, and `tasks/` to track project progress.

Every item needs YAML frontmatter, a `## Description` section, and a `## Acceptance Criteria` section with checkboxes.

Run validation before committing tracker changes:

```bash
python scripts/work_tracker.py docs/work
```
