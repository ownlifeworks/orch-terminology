# OwnLife Audio Terminology

Canonical terminology data and deterministic alias-resolution support shared by OwnLife Audio tools.

## Status

The first implementation slice is available: canonical seed data, JSON schemas, a deterministic Python resolver, and a validation tool. Consumer integrations and generated artifacts remain future work.

## Repository layout

- `data/` — authoritative terminology JSON files, including the generated `catalog.json`
- `data/instrument-properties.json` — canonical per-instrument pitch and loudness-reference properties for `orch.db` consumers such as SymphonicBalance
- `data/catalog/` — per-library catalog source files that are combined into `catalog.json`
- `schema/` — JSON Schema definitions
- `tests/` — resolver and validation fixtures
- `tools/` — validation and generation tooling

Applications such as NTD Engine and NTD Detector must consume this repository's data rather than maintaining independent terminology sources. Applications that need canonical instrument pitch or loudness-reference metadata, such as SymphonicBalance, must consume the generated `orch.db` representation of `instrument-properties.json` rather than creating an independent authority.

```mermaid
flowchart TD
    subgraph Canonical["Canonical Terminology Source"]
        Vendors["data/vendors.json"]
        Libraries["data/libraries.json"]
        Instruments["data/instruments.json"]
        InstrumentProps["data/instrument-properties.json"]
        Articulations["data/articulations.json"]
        Variants["data/variants.json"]
        CatalogSources["data/catalog/*.json"]
    end

    Build["tools/build_catalog.ps1<br/>or build_catalog.py"]
    Aggregate["data/catalog.json"]
    Validate["tools/validate_terminology.py"]
    Resolver["orch_terminology/resolver.py"]
    Tests["python -m unittest discover -s tests"]

    subgraph Consumers["Consumer Applications and Mirrors"]
        Website["OwnLifeAudioWebsite"]
        Detector["NTD Detector"]
        Engine["NTD Engine"]
        SymphonicBalance["SymphonicBalance"]
    end

    CatalogSources --> Build --> Aggregate
    Vendors --> Validate
    Libraries --> Validate
    Instruments --> Validate
    InstrumentProps --> Validate
    Articulations --> Validate
    Variants --> Validate
    Aggregate --> Validate

    Vendors --> Resolver
    Libraries --> Resolver
    Instruments --> Resolver
    Articulations --> Resolver
    Variants --> Resolver
    Aggregate --> Resolver

    Validate --> Tests
    Resolver --> Tests

    Aggregate --> Website
    Aggregate --> Detector
    Aggregate --> Engine
    InstrumentProps --> SymphonicBalance
    Aggregate --> SymphonicBalance
    Vendors --> Website
    Libraries --> Website
    Instruments --> Website
    Articulations --> Website
    Variants --> Website
```

## Editing terminology data

Edit the canonical JSON files in `data/`. The copies in consuming applications, such as `OwnLifeAudioWebsite/src/data/terminology/`, are mirrors and can be overwritten during synchronization.

For catalog relationships, edit the per-library source files in `data/catalog/` and then run `pwsh -File tools/build_catalog.ps1` to regenerate the aggregate `data/catalog.json`.

Keep entity IDs stable because libraries and `contexts.json` reference them directly. Aliases/abbreviations must never contain whitespace; use hyphens instead. Alias order matters: the first alias is used as the default abbreviation in the website's clipboard string. Avoid alias collisions within a category, preserve `schemaVersion: 1`, and keep every instrument's `iconKey` unique. When changing an ID, update all references in `libraries.json` and `contexts.json`.

The canonical vocabulary now includes `variants.json` for optional articulation qualifiers. Use `variant` as a separate normalized field rather than folding qualifiers back into `articulation`.

`instrument-properties.json` is keyed by instrument ID from `instruments.json`. It currently supports pitch range, recommended measurement range, and factory loudness-reference targets for `long` and `short` capture modes. Treat it as canonical source data that is exported into `orch.db` for consumer applications.

After editing, validate the data and run the tests:

```powershell
python tools/validate_terminology.py
pwsh -File tools/build_catalog.ps1
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
