# Work Tracker

This folder tracks Decision-PGA work using Markdown files with YAML frontmatter.

Start with `DPGA-E002` for current evidence, tester-readiness, and MCP work.
`DPGA-E001` captures the accepted prototype history.

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
