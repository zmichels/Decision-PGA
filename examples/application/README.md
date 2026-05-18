# Application Examples

These examples are lightweight payloads for the application-gap bridge. They do
not call model APIs. The first files are shaped so future tests can use them as
seed fixtures for tool/action and RAG/evidence-conflict deep dives.

Run the application review suite:

```bash
decision-pga evaluate --suite application --output reports/application-latest
```

Run an individual diagnostic payload:

```bash
decision-pga diagnose --pretty examples/application/tool_action_binary_ambiguity.json
```
