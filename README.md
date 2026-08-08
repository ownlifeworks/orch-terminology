# OwnLife Audio Terminology

Canonical terminology data and deterministic alias-resolution support shared by OwnLife Audio tools.

## Status

The first implementation slice is available: canonical seed data, JSON schemas, a deterministic Python resolver, and a validation tool. Consumer integrations and generated artifacts remain future work.

## Repository layout

- `data/` — authoritative terminology JSON files
- `schema/` — JSON Schema definitions
- `tests/` — resolver and validation fixtures
- `tools/` — validation and generation tooling

Applications such as NTD Engine and NTD Detector must consume this repository's data rather than maintaining independent terminology sources.

## Checks

From the repository root:

```powershell
python tools/validate_terminology.py
python -m unittest discover -s tests
```

The resolver normalizes separators and case, prefers contextual aliases, supports longest-match filename parsing, and reports unresolved or ambiguous terms explicitly.
