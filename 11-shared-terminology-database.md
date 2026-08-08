# Shared Terminology Database

## Purpose

Introduce one shared, canonical terminology database for the OwnLife Audio ecosystem.

The same terminology and alias-resolution logic must be usable by:

- NTD Detector
- NTD Engine
- import/conversion tools
- filename parsers
- Dave Kudell database lookup
- future `.ntdpack` tooling
- profile editors
- future website/community tooling

The goal is to avoid each application inventing its own names and aliases for vendors, libraries, instruments, and articulations.

There must be exactly one authoritative source of terminology.

---

## Core Concept

The terminology database defines canonical identities for four main metadata dimensions:

1. Vendor
2. Library
3. Instrument
4. Articulation

Each canonical entity has:

- a stable machine-readable ID
- a human-readable display name
- zero or more aliases

Example:

```json
{
  "id": "trumpet",
  "name": "Trumpet",
  "aliases": [
    "tpt",
    "trp",
    "trpt",
    "trumpet"
  ]
}
```

All applications should use canonical IDs internally wherever possible.

Aliases exist only to interpret external or loosely structured input.

Examples of external input:

- `bbc_tpt_marcato_v10.wav`
- `BBCSO Trumpet Marc`
- metadata imported from another source
- Dave Kudell spreadsheet labels
- user-entered profile metadata
- community profile packages

The resolver translates these variants into canonical terminology.

Example:

```text
bbc + tpt + marc
```

resolves to:

```json
{
  "vendor": "spitfire-audio",
  "library": "bbcso-core",
  "instrument": "trumpet",
  "articulation": "marcato"
}
```

---

# Design Goals

The implementation should prioritize:

- predictability
- maintainability
- explicit aliases
- easy manual editing
- shared use across languages and applications
- stable canonical identifiers
- no unnecessary fuzzy/AI matching
- transparent matching behavior

The system should not try to infer musical equivalence.

For example:

```text
short != staccato
```

unless a specific library explicitly defines that alias.

Aliases mean:

> another spelling, abbreviation, naming convention, or known equivalent label for the same canonical entity

They do not mean:

> musically similar articulation

---

# Suggested Repository Layout

Use one shared source directory.

Suggested structure:

```text
shared/
  terminology/
    vendors.json
    libraries.json
    instruments.json
    articulations.json
    schema-version.json
```

Alternative naming is acceptable if the repository already has an established shared-data location.

The important requirement is:

> NTD Detector and NTD Engine must not maintain independent copies of terminology data.

If build/runtime requirements make direct sharing difficult, generated copies may be produced during build or packaging, but they must originate from the same authoritative source files.

---

# Canonical IDs

Canonical IDs must be:

- lowercase
- stable
- machine-readable
- independent of display-name changes
- preferably kebab-case

Examples:

```text
spitfire-audio
bbcso-core
trumpet
trumpets-a3
horn
horns-a4
marcato
long-cuivre
staccato
```

Do not use display names as persistent identifiers.

Good:

```json
{
  "id": "bbcso-core",
  "name": "BBC Symphony Orchestra Core"
}
```

Bad:

```json
{
  "id": "BBC Symphony Orchestra Core"
}
```

The display name may change later without breaking references.

---

# Vendor Schema

Example:

```json
{
  "schemaVersion": 1,
  "vendors": [
    {
      "id": "spitfire-audio",
      "name": "Spitfire Audio",
      "aliases": [
        "spitfire",
        "spitfireaudio",
        "sa"
      ]
    },
    {
      "id": "cinematic-studio-series",
      "name": "Cinematic Studio Series",
      "aliases": [
        "cinematic studio",
        "cinematicstudio",
        "css"
      ]
    }
  ]
}
```

---

# Library Schema

Libraries belong to vendors.

Example:

```json
{
  "schemaVersion": 1,
  "libraries": [
    {
      "id": "bbcso-core",
      "name": "BBC Symphony Orchestra Core",
      "vendorId": "spitfire-audio",
      "aliases": [
        "bbc",
        "bbcso",
        "bbc core",
        "bbcso core",
        "bbc symphony orchestra",
        "bbc symphony orchestra core"
      ]
    }
  ]
}
```

The resolver should be able to infer the vendor from a resolved library.

For example:

```text
bbc
```

can resolve directly to:

```json
{
  "libraryId": "bbcso-core",
  "vendorId": "spitfire-audio"
}
```

The filename does not need to contain both vendor and library.

---

# Instrument Schema

Instrument terminology should distinguish materially different sampled entities.

For example:

```json
{
  "schemaVersion": 1,
  "instruments": [
    {
      "id": "trumpet",
      "name": "Trumpet",
      "aliases": [
        "tpt",
        "trp",
        "trpt",
        "trumpet"
      ]
    },
    {
      "id": "trumpets-a3",
      "name": "Trumpets A3",
      "aliases": [
        "tpts",
        "3tpt",
        "3tpts",
        "trumpets3",
        "trumpets a3",
        "tpt a3"
      ]
    },
    {
      "id": "horn",
      "name": "Horn",
      "aliases": [
        "hn",
        "fh",
        "french horn",
        "horn"
      ]
    },
    {
      "id": "horns-a4",
      "name": "Horns A4",
      "aliases": [
        "hns",
        "4hn",
        "4hns",
        "horns4",
        "horns a4"
      ]
    }
  ]
}
```

Do not collapse solo and ensemble instruments unless they are genuinely represented as the same sampled instrument in the relevant ecosystem.

---

# Articulation Schema

Example:

```json
{
  "schemaVersion": 1,
  "articulations": [
    {
      "id": "long",
      "name": "Long",
      "aliases": [
        "long",
        "sus",
        "sustain",
        "sustained"
      ]
    },
    {
      "id": "staccato",
      "name": "Staccato",
      "aliases": [
        "stac",
        "stacc",
        "staccato"
      ]
    },
    {
      "id": "marcato",
      "name": "Marcato",
      "aliases": [
        "marc",
        "marcato"
      ]
    },
    {
      "id": "long-cuivre",
      "name": "Long Cuivre",
      "aliases": [
        "cuivre",
        "long cuivre",
        "longcuivre",
        "long-cuivre"
      ]
    }
  ]
}
```

Again, aliases must describe naming variants, not broad musical similarity.

Do not globally define things such as:

```text
short -> staccato
```

unless that is intentionally true for all consumers.

---

# Context-Specific Aliases

Global aliases are not always sufficient.

Some libraries use unusual abbreviations or names that would be ambiguous globally.

The terminology system must therefore support contextual aliases.

Suggested precedence:

```text
library-specific alias
    >
vendor-specific alias
    >
global alias
```

Example concept:

```json
{
  "libraryId": "bbcso-core",
  "instrumentAliases": {
    "hn": "horn",
    "hns": "horns-a4",
    "4hn": "horns-a4"
  },
  "articulationAliases": {
    "cuiv": "long-cuivre"
  }
}
```

These contextual aliases may either live:

- in a dedicated `contexts.json`
- or inside the relevant library definition

Choose whichever produces the cleanest implementation.

The important behavior is deterministic precedence.

---

# Normalization Rules

Before alias lookup, normalize textual input.

At minimum:

1. Trim whitespace.
2. Convert to lowercase.
3. Treat underscores and hyphens as token separators where appropriate.
4. Collapse repeated whitespace.
5. Ignore file extension for filename parsing.
6. Match aliases case-insensitively.

These should resolve identically:

```text
BBC_TPT_MARCATO_V10.wav
bbc_tpt_marcato_v10.wav
Bbc-Tpt-Marcato-V10.WAV
```

Be careful not to destroy meaningful multiword aliases.

For example:

```text
long cuivre
```

must still be recognizable as one articulation.

A longest-match-first strategy is appropriate for multi-token aliases.

---

# Filename Parsing

NTD Detector already interprets filenames such as:

```text
bbc_tpt_marcato_v10.wav
```

The shared terminology system should become the canonical parser dependency for this metadata interpretation.

Expected result:

```json
{
  "vendorId": "spitfire-audio",
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato",
  "velocity": 10
}
```

Velocity is not part of the terminology database.

The filename parser should handle non-terminology markers separately.

Examples:

```text
v10
v64
v127
```

Terminology parsing and measurement metadata parsing should remain separate concepts.

---

# Resolver API

Create a reusable terminology resolver.

The concrete language-specific API may differ, but conceptually it should expose functionality similar to:

```text
resolveVendor(text)
resolveLibrary(text)
resolveInstrument(text, optionalContext)
resolveArticulation(text, optionalContext)
```

and ideally:

```text
resolveMetadata(textOrTokens, optionalContext)
```

Example conceptual result:

```json
{
  "vendor": {
    "id": "spitfire-audio",
    "name": "Spitfire Audio"
  },
  "library": {
    "id": "bbcso-core",
    "name": "BBC Symphony Orchestra Core"
  },
  "instrument": {
    "id": "trumpet",
    "name": "Trumpet"
  },
  "articulation": {
    "id": "marcato",
    "name": "Marcato"
  }
}
```

No confidence score is required.

The system should return:

- resolved entity
- unresolved
- ambiguous

where appropriate.

Do not silently guess when two aliases genuinely collide.

---

# Ambiguity Handling

If the same normalized alias can resolve to multiple canonical entities in the same context, treat this as a terminology-data problem.

Do not arbitrarily choose one.

Example result:

```json
{
  "status": "ambiguous",
  "input": "short",
  "matches": [
    "staccato",
    "short",
    "short-tight"
  ]
}
```

Prefer fixing the terminology data with context-specific aliases rather than adding fuzzy heuristics.

---

# Dave Kudell Database Integration

Dave Kudell's database should be treated as a separate reference dataset.

Do not put Dave's timing values into the terminology database.

Architecture:

```text
Shared Terminology Database
        |
        v
Filename / Metadata Resolver
        |
        v
Canonical metadata IDs
        |
        v
Dave Kudell Reference Database
        |
        v
Reference timing recommendation
```

Example:

```text
bbc_tpt_marcato_v10.wav
```

resolves to:

```json
{
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato"
}
```

The Dave database can then be queried using canonical identifiers.

Example normalized Dave record:

```json
{
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato",
  "delayMs": 70,
  "source": "Dave Kudell NTD Database"
}
```

The recommendation is informational only.

NTD Detector's own audio analysis remains independent.

---

# Dave Database Conversion

The original Google Sheet should not be parsed dynamically by NTD Detector.

Instead create a one-time or repeatable import/conversion process:

```text
Dave Google Sheet export
        |
        v
conversion/import script
        |
        v
terminology resolver
        |
        v
manual cleanup when required
        |
        v
normalized Dave JSON
```

The normalized Dave dataset should use canonical IDs from the shared terminology database.

It is useful to retain the original source labels for debugging:

```json
{
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato",
  "delayMs": 70,
  "sourceLabels": {
    "library": "BBC Symphony Orchestra",
    "instrument": "Trumpet",
    "articulation": "Marcato"
  }
}
```

---

# NTD Detector Usage

NTD Detector should use the shared terminology system for:

- parsing WAV filenames
- identifying library
- identifying instrument
- identifying articulation
- finding Dave Kudell reference entries
- pre-filling metadata
- future batch-analysis workflows

Example UI behavior:

```text
Filename:
bbc_tpt_marcato_v10.wav

Resolved:
BBC Symphony Orchestra Core
Trumpet
Marcato
Velocity 10

NTD Detector:
56 ms

Dave Kudell reference:
53 ms
```

The UI should display which canonical Dave record was matched.

Do not present Dave's value as a confidence mechanism for the audio analysis.

---

# NTD Engine Usage

NTD Engine should use the same canonical terminology for:

- profile metadata
- profile creation
- import/export
- `.ntdpack` files
- library browser
- articulation editor
- future community packages
- future online profile distribution

Where possible, profiles should store stable IDs rather than arbitrary free-text strings.

Preferred:

```json
{
  "vendorId": "spitfire-audio",
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato"
}
```

Display names come from the terminology database.

If backward compatibility requires existing display-name fields, canonical IDs should be added without immediately removing the old fields.

Example transition structure:

```json
{
  "vendorId": "spitfire-audio",
  "vendor": "Spitfire Audio",

  "libraryId": "bbcso-core",
  "library": "BBC Symphony Orchestra Core",

  "instrumentId": "trumpet",
  "instrument": "Trumpet",

  "articulationId": "marcato",
  "articulation": "Marcato"
}
```

Eventually the ID should be authoritative.

---

# `.ntdpack` Usage

Future or existing `.ntdpack` packages should use canonical terminology IDs wherever practical.

This prevents community packages from fragmenting metadata into variants such as:

```text
Trumpet
trumpet
TPT
Tpt.
Trumpets
Trumpet Solo
```

The terminology database provides one canonical vocabulary while still accepting common aliases during import.

---

# Generated Consumer Artifacts

The authoritative terminology should remain human-maintainable.

If NTD Engine and NTD Detector need different optimized structures, generate them from the shared source.

Example:

```text
shared/terminology/*
        |
        v
generate-terminology
        |
        +--> detector terminology JSON
        |
        +--> engine terminology JSON/resources
        |
        +--> importer lookup JSON
```

Generated files must never become separately maintained sources of truth.

---

# Versioning

The terminology dataset should have its own schema version.

Example:

```json
{
  "schemaVersion": 1
}
```

Consider also adding a terminology-data version later:

```json
{
  "schemaVersion": 1,
  "dataVersion": "2026.08.1"
}
```

Schema version describes structure.

Data version describes terminology content.

Do not over-engineer migration handling initially, but leave room for it.

---

# Validation

Add validation tooling/tests.

At minimum validate:

- canonical IDs are unique
- aliases within one resolution scope do not collide unexpectedly
- referenced vendor IDs exist
- referenced library IDs exist
- contextual aliases point to existing canonical IDs
- canonical IDs follow naming rules
- empty aliases are rejected
- aliases are normalized consistently

A small validation script should run in CI.

---

# Tests

Add unit tests covering common cases.

Examples:

```text
bbc -> bbcso-core
BBC -> bbcso-core
bbcso -> bbcso-core
bbc_core -> bbcso-core

tpt -> trumpet
trp -> trumpet
TRPT -> trumpet

marc -> marcato
Marcato -> marcato
long_cuivre -> long-cuivre
Long-Cuivre -> long-cuivre
```

Filename example:

```text
bbc_tpt_marcato_v10.wav
```

must resolve to:

```json
{
  "vendorId": "spitfire-audio",
  "libraryId": "bbcso-core",
  "instrumentId": "trumpet",
  "articulationId": "marcato",
  "velocity": 10
}
```

Also test ambiguity and unknown values.

---

# Initial Scope

Do not attempt to catalog the entire orchestral sample-library ecosystem immediately.

Start with terminology required by current work.

Recommended first content:

- vendors/libraries currently supported by NTD Engine
- BBC Symphony Orchestra Core
- instruments found in those libraries
- articulations currently being measured
- aliases needed for existing WAV filenames
- aliases required to normalize Dave Kudell database entries

Grow the registry organically.

---

# Implementation Order

Recommended sequence:

## 1. Create shared terminology files

Create canonical JSON files and schemas.

## 2. Implement resolver

Implement deterministic normalization and alias lookup.

## 3. Add automated validation

Catch ID and alias collisions.

## 4. Integrate NTD Detector

Replace Detector-local terminology/alias logic with the shared resolver.

## 5. Convert Dave database

Normalize Dave's source labels through the terminology resolver.

## 6. Integrate NTD Engine

Use canonical IDs for profile metadata while preserving backward compatibility.

## 7. Reuse in package/import tooling

Make `.ntdpack` and other importers use the same resolver.

---

# Important Non-Goals

Do not implement:

- AI-based terminology matching
- confidence scores
- aggressive fuzzy matching
- semantic guesses such as "short probably means staccato"
- automatic musical-equivalence mapping
- separate alias databases for each application

The design should remain simple and explicit.

---

# Guiding Principle

The terminology database should become the vocabulary layer for OwnLife Audio.

Applications should not need to know whether:

```text
bbc
bbcso
BBC Symphony Orchestra
BBCSO Core
```

were used by a user or source dataset.

They should receive:

```text
bbcso-core
```

Likewise:

```text
tpt
trp
trpt
Trumpet
```

should resolve to:

```text
trumpet
```

The canonical terminology layer should sit between messy external naming and clean internal metadata.

That single responsibility is the main architectural goal.
