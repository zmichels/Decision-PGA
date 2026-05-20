# Contributing

Decision-PGA is an early research prototype. Contributions are welcome when
they keep the project small, reproducible, and clear about its limits.

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[mcp]"
python -m unittest discover -s tests -v
```

## Contribution Guidelines

- Keep examples synthetic or explicitly public.
- Do not add patient data, private documents, credentials, or provider API
  responses that contain sensitive content.
- Keep model/provider adapters optional and local-first.
- Include tests for public behavior.
- Keep diagnostic claims conservative: show what the method measures and where
  it is not yet validated.

## Example Datasets And Scenarios

The most useful early contributions are small, human-readable decision
scenarios. Good examples include:

- a fixed set of candidate actions or labels;
- 4-20 repeated probability-like observations;
- a short note explaining what the rows mean;
- an expected diagnostic state and why entropy or margin alone may be too blunt.

Use `examples/agent/` as the shape reference. Please keep examples synthetic,
public, or anonymized. If a real workflow inspired the example, remove names,
private text, user data, credentials, and proprietary payloads before opening an
issue or pull request.

## Before Opening A Pull Request

```bash
python -m unittest discover -s tests -v
python scripts/work_tracker.py docs/work --summary
decision-pga evaluate --config examples/evaluation_config.json --output reports/latest
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
```

Generated reports under `reports/` are ignored by git.
