# Release Readiness Checklist

This checklist prepares Decision-PGA for a small public `v0.1.x` release without
publishing anything automatically.

## Fresh Clone

```bash
git clone https://github.com/zmichels/Decision-PGA.git
cd Decision-PGA
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[mcp]"
```

## GitHub Install

Confirm direct installation from the public repository:

```bash
python -m pip install "git+https://github.com/zmichels/Decision-PGA"
python -m pip install git+https://github.com/zmichels/Decision-PGA
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
```

## Local Checks

```bash
python -m unittest discover -s tests -v
python scripts/adoption_smoke.py
decision-pga diagnose --pretty examples/agent/rag_evidence_conflict.json
decision-pga evaluate --config examples/evaluation_config.json --output reports/release-check
decision-pga evaluate --suite application --output reports/release-application-check
decision-pga evaluate --suite document-extraction --output reports/release-doc-extraction-check
python scripts/work_tracker.py docs/work --summary
```

## MCP Extra Smoke Test

```bash
python -m pip install -e ".[mcp]"
python -c "from decision_pga.mcp_server import build_server; build_server(); print('mcp ok')"
npx @modelcontextprotocol/inspector decision-pga-mcp
```

## Trusted Publishing

The workflow in `.github/workflows/pypi-publish.yml` is manual-only. Before
using it:

- create the `decision-pga` project on PyPI;
- configure PyPI Trusted Publishing for this repository and workflow;
- create or approve the `pypi` GitHub environment;
- verify the package name, version, and long description;
- manually trigger the workflow only after the release is approved.

Do not publish to PyPI from this checklist without explicit approval.

## MCP Registry

`docs/mcp-registry/server.json` is draft metadata for the MCP Registry. Keep it
in the repo for review, but do not submit it until the install path is stable
and the package distribution location is final.

## Hugging Face Space

`examples/huggingface-space/` is a prepared demo scaffold. Treat it as optional:
use it if broader AI-native demo discovery is desired, but do not deploy it
until the public examples and repo links have been reviewed.

## Tagging

When the release is ready:

```bash
git tag v0.1.x
git push origin v0.1.x
```

Then create a GitHub Release that links:

- the article and live demo;
- the agent toolkit docs;
- the MCP quickstart;
- the benchmark/application reports;
- the citation metadata.
