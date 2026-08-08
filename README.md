# OwnLife Audio Terminology

Canonical terminology data and deterministic alias-resolution support shared by OwnLife Audio tools.

## Status

The repository is initialized from [the shared terminology specification](11-shared-terminology-database.md). Canonical data and resolver implementation are not populated yet.

## Repository layout

- `data/` — authoritative terminology JSON files
- `schema/` — JSON Schema definitions
- `tests/` — resolver and validation fixtures
- `tools/` — validation and generation tooling

Applications such as NTD Engine and NTD Detector must consume this repository's data rather than maintaining independent terminology sources.
