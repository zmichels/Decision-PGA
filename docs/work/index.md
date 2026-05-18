# Work Tracker

This folder tracks Decision-PGA work using Markdown files with YAML frontmatter.

Start with `DPGA-E004` for the current document-extraction gap bridge.
`DPGA-E003` covers the broader application-gap review, article, and
application-suite bridge. `DPGA-E002` covers evidence, tester-readiness, and
MCP work. `DPGA-E001` captures the accepted prototype history.

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
