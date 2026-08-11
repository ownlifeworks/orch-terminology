# OwnLife Audio Terminology

Canonical terminology data and deterministic alias-resolution support shared by OwnLife Audio tools.

## Status

The first implementation slice is available: canonical seed data, JSON schemas, a deterministic Python resolver, and a validation tool. Consumer integrations and generated artifacts remain future work.

## Repository layout

- `data/` — authoritative terminology JSON files, including the generated `catalog.json`
- `schema/` — JSON Schema definitions
- `tests/` — resolver and validation fixtures
- `tools/` — validation and generation tooling

Applications such as NTD Engine and NTD Detector must consume this repository's data rather than maintaining independent terminology sources.

## Editing terminology data

Edit the canonical JSON files in `data/`. The copies in consuming applications, such as `OwnLifeAudioWebsite/src/data/terminology/`, are mirrors and can be overwritten during synchronization.

Keep entity IDs stable because libraries and `contexts.json` reference them directly. Aliases/abbreviations must never contain whitespace; use hyphens instead. Alias order matters: the first alias is used as the default abbreviation in the website's clipboard string. Avoid alias collisions within a category, preserve `schemaVersion: 1`, and keep every instrument's `iconKey` unique. When changing an ID, update all references in `libraries.json` and `contexts.json`.

The canonical vocabulary now includes `variants.json` for optional articulation qualifiers and `articulation-variant-mappings.json` for curated splits of legacy combined articulation names. Use `variant` as a separate normalized field rather than folding qualifiers back into `articulation`.

After editing, validate the data and run the tests:

```powershell
python tools/validate_terminology.py
python tools/build_catalog.py
python -m unittest discover -s tests
```

## Checks

From the repository root:

```powershell
python tools/validate_terminology.py
python tools/build_catalog.py
python -m unittest discover -s tests
```

The resolver normalizes separators and case, prefers contextual aliases, supports longest-match filename parsing, and reports unresolved or ambiguous terms explicitly. It also resolves optional articulation variants when they are present in the canonical vocabulary.
