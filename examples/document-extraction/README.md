# Document Extraction Examples

These payloads sketch how document-extraction uncertainty could be represented
as Decision-PGA candidate clouds. They are local examples only and do not call
OCR, layout, or model APIs.

Run the separate document-extraction review suite:

```bash
decision-pga evaluate --suite document-extraction --output reports/document-extraction-latest
```

Run an individual diagnostic payload:

```bash
decision-pga diagnose --pretty examples/document-extraction/field_value_ambiguity.json
```
