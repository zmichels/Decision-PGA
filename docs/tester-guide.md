# Tester Guide

This is the short path for trying Decision-PGA from a public GitHub clone. It
should take about 20 minutes on a machine with Python 3.10, 3.11, or 3.12.

## Setup

```bash
git clone https://github.com/zmichels/Decision-PGA.git
cd Decision-PGA
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Check The Install

```bash
python -m unittest discover -s tests -v
python scripts/work_tracker.py docs/work --summary
```

## Try The Diagnostic CLI

```bash
decision-pga diagnose --pretty examples/tester/stable_probability_cloud.json
decision-pga diagnose --pretty examples/tester/binary_ambiguity_model_outputs.json
decision-pga diagnose --pretty examples/tester/diffuse_probability_cloud.json
decision-pga diagnose --pretty examples/tester/regime_shift_sampled_responses.json
decision-pga diagnose --pretty examples/tester/provider_scores.json
```

## Try The Agent Toolkit Examples

```bash
decision-pga diagnose --pretty examples/agent/tool_action_ambiguity.json
decision-pga diagnose --pretty examples/agent/rag_evidence_conflict.json
decision-pga diagnose --pretty examples/agent/document_extraction_routing.json
decision-pga diagnose --pretty examples/agent/multi_step_agent_drift.json
decision-pga diagnose --pretty examples/agent/abstain_defer_decision.json
open docs/agent-toolkit.md
```

These examples are synthetic. They are designed to show how an agent-facing
tool might route tool selection ambiguity, RAG evidence conflict, missing
document context, trajectory drift, and stable abstention.

## Run The Benchmark

```bash
decision-pga evaluate --config examples/evaluation_config.json --output reports/latest
open reports/latest/advantage_report.md
```

The benchmark is synthetic and local. It does not call OpenAI, local LLMs, or
provider APIs.

## Read The Application Gap Review

```bash
decision-pga evaluate --suite application --output reports/application-latest
open reports/application-latest/application_report.md
open docs/articles/decision-pga-gap-review.md
```

The application suite is not a live model benchmark. It is a structured review
of where Decision-PGA is likely useful now, where adapters are missing, and
which two deeper tracks should be tested first.

## Read The Document Extraction Gap Review

```bash
decision-pga evaluate --suite document-extraction --output reports/document-extraction-latest
open reports/document-extraction-latest/document_extraction_report.md
open docs/articles/decision-pga-document-extraction-gap-review.md
```

This suite is separate from the broader application suite. It focuses on data
extraction from documents and does not call OCR, layout, model, or provider
APIs.

## Optional MCP Smoke Test

```bash
python -m pip install -e ".[mcp]"
decision-pga-mcp
```

The MCP command starts a local stdio server. It is meant to be launched by an
MCP client or inspector rather than used as a normal terminal command.

For MCP Inspector:

```bash
npx @modelcontextprotocol/inspector decision-pga-mcp
```
