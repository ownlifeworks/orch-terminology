# Codex Instructions — Vendor Website Terminology Ingestion

## Purpose

Use this process whenever extracting orchestral sample-library terminology from a vendor website, product page, manual, patch list, PDF, or similar source.

The goal is not to copy vendor terminology into the canonical database. The goal is to collect evidence, normalize it against the existing terminology database, surface uncertainty, ask the user when necessary, and write only approved or safely matched data.

> **Scraping gathers evidence. The terminology database decides meaning.**

## Canonical Metadata Model

```text
Vendor
Library
Instrument
Articulation
Variant (optional)
```

The UI may display `Instrument` as **Instrument / Ensemble**, but the database field remains `instrument`.

Do not introduce additional metadata levels or fields unless explicitly instructed.

# Fundamental Rules

## Never invent canonical terminology

Codex MUST NOT autonomously create canonical vendors, libraries, instruments, articulations, variants, or aliases when ingesting vendor data.

Search the existing terminology database first.

If no correct existing value can be found, the item is **UNRESOLVED**. Ask the user before adding a new canonical value or alias.

This rule is especially strict for `instrument`, `articulation`, and `variant`.

## Do not combine extraction and normalization

Never perform:

```text
website -> canonical database
```

in one uncontrolled step.

Always use the staged workflow below.

## Preserve source terminology

Vendor terminology is evidence. Never destroy or silently rewrite the original wording during extraction.

If the source says `Exp Low Lat Leg`, preserve `Exp Low Lat Leg` in the raw extraction. Normalize it later.

## Marketing language is not metadata

Words such as `lush`, `cinematic`, `beautiful`, `soaring`, `emotional`, `expressive`, `intimate`, `powerful`, or `epic` are NOT automatically articulations or variants because they occur in product copy.

Only treat a term as metadata when the source clearly associates it with a patch, preset, instrument, articulation, playing technique, variant, keyswitch, articulation list, patch list, specification, manual entry, or equivalent structured information.

> **Absence of evidence is not metadata.**

# Required Workflow

```text
PHASE 1 — DISCOVERY
        ↓
PHASE 2 — MATCHING
        ↓
PHASE 3 — CLASSIFICATION
        ↓
PHASE 4 — REVIEW
        ↓
PHASE 5 — WRITE
```

Do not skip directly to Phase 5.

# Phase 1 — Discovery

Extract what the source actually says. Do NOT normalize during this phase.

Where available, collect:

- vendor name
- product/library name
- instrument names
- ensemble/composite instrument names
- articulation names
- articulation variants
- patch/preset names
- abbreviations
- aliases explicitly shown by the source
- relevant hierarchy/context
- source URL
- source page/manual section
- useful short source context

Preserve labels verbatim.

Example:

```text
Source label: Expressive Low Latency Legato
```

Do not yet convert it to canonical fields.

# Phase 2 — Matching

For every extracted source term, search the existing terminology database.

Use this order:

```text
Exact canonical value
        ↓
Existing alias
        ↓
Existing abbreviation
        ↓
Clearly equivalent existing value
        ↓
No safe match
        ↓
UNRESOLVED
```

Do not create a new canonical value merely because wording differs.

# Phase 3 — Classification

Every proposed mapping receives one status:

```text
EXACT
ALIAS
INFERRED
UNRESOLVED
```

### EXACT

```text
Source: Legato
Canonical: legato
Status: EXACT
```

### ALIAS

```text
Source: Stac
Canonical: staccato
Status: ALIAS
```

### INFERRED

Use only when the semantic mapping is sufficiently clear.

```text
Source: Fast Legato
Articulation: legato
Variant: fast
Status: INFERRED
```

Use `INFERRED` conservatively. Do not use it to hide genuine uncertainty.

### UNRESOLVED

```text
Source: Agile Legato
Articulation: legato
Variant: UNRESOLVED
Possible candidates: fast, rapid
```

This requires user review.

# Phase 4 — Review

Before changing canonical terminology, present unresolved and genuinely ambiguous cases to the user.

Do not silently decide.

Example:

```text
UNRESOLVED VARIANT

Vendor: Example Audio
Library: Example Strings
Source patch: Agile Legato

Mapped articulation: legato
Unrecognized qualifier: Agile

Possible existing matches:
- fast
- rapid

Possible actions:
1. map "Agile" to an existing variant
2. create a new canonical variant
3. ignore the qualifier

Decision required.
```

The user decides whether a new canonical term or alias should be introduced.

# Phase 5 — Write

Only write canonical database changes after:

- an EXACT match,
- an ALIAS match,
- a safe INFERRED match,
- or explicit user approval of an unresolved case.

Never write unresolved terminology into canonical fields.

# Articulation Normalization

`articulation` represents the primary normalized musical playing technique.

Examples:

```text
legato
sustain
staccato
spiccato
pizzicato
marcato
tremolo
trill
```

Vendor patch names are NOT canonical articulation names.

For example:

```text
Expressive Legato
Fast Legato
Rapid Legato
Low Latency Legato
Performance Legato
Lyrical Legato
```

must not automatically become separate articulations. Normally the articulation is `legato`, while meaningful qualifiers are evaluated separately as possible variants.

# Variant Normalization

`variant` is optional. It represents a meaningful qualifier, implementation, state, or flavor of the primary articulation.

Examples may include:

```text
expressive
fast
rapid
low latency
harmon mute
cup mute
non-vibrato
```

Example:

```text
Source: Expressive Legato
articulation = legato
variant = expressive
```

Example:

```text
Source: Harmon Mute Staccato
instrument = trumpet
articulation = staccato
variant = harmon mute
```

Variants are controlled terminology. Codex must NOT invent variants.

If a qualifier cannot be mapped correctly, set it to `UNRESOLVED` in the ingestion/review data and ask the user.

## Multiple qualifiers

Do not automatically concatenate qualifiers into a new variant.

For:

```text
Expressive Low Latency Legato
```

do NOT automatically create:

```text
variant = expressive low latency
```

unless that canonical variant already exists.

If the current schema cannot accurately represent multiple meaningful qualifiers, mark the case unresolved and ask the user. Do not change the schema autonomously.

# Instrument / Ensemble Normalization

The `instrument` field can represent:

- a solo instrument
- an instrument section
- a defined combination
- a generic ensemble

Examples:

```text
Flute
Violins
French Horns
Oboes + Clarinets
Oboes + English Horns
Low Brass
Woodwind Ensemble
Full Orchestra
```

Do not split a recorded combination into independent instruments.

If a patch contains `Oboes + Clarinets`, do not create separate Oboe and Clarinet records unless the source actually provides them independently.

## Composite naming

When the source explicitly identifies component instruments, prefer a deterministic canonical combination such as:

```text
Oboes + Clarinets
```

Alternative source forms such as `Oboes & Clarinets`, `Oboe/Clarinet`, or `Oboes and Clarinets` may be proposed as aliases, but aliases must not be added automatically.

## Generic ensembles are different

Do not assume `Oboes + Clarinets` means `Woodwinds` or `Woodwind Ensemble`.

Preserve the most specific supported meaning provided by the source.

# Vendor and Library Rules

## Vendor

Use the vendor/brand under which the product is actually distributed unless the database already defines another canonical mapping.

Do not replace it with a parent company merely because a corporate relationship exists.

## Library

`library` means the identifiable sample product containing the instrument.

A library may contain only one instrument.

Example:

```text
Vendor: Soundpaint
Library: 2001 Piccolo Shire
Instrument: Piccolo
```

Do not invent a broader collection/library merely to make grouping cleaner.

# Process One Semantic Level at a Time

Recommended order:

```text
1. Identify vendor
2. Identify library/product
3. Identify instruments/ensembles
4. Confirm instrument structure
5. Extract articulation/patch labels for each instrument
6. Normalize articulations
7. Normalize variants
8. Review unresolved terms
9. Write approved data
```

Do not issue one giant extraction-and-write operation.

# Source Reliability

Prefer structured and primary evidence:

```text
1. Official vendor manual / patch list
2. Official product documentation
3. Official product page with explicit articulation/instrument lists
4. Official walkthrough/reference material
5. Other reliable source
6. Marketing prose
```

Marketing prose alone should rarely create terminology.

If an official manual contradicts loose marketing wording, prefer the manual for taxonomy.

# Context Matters

Words such as `Long`, `Short`, `Performance`, `Core`, `Extended`, `Advanced`, `Muted`, `Soft`, `Hard`, `Solo`, `Section`, `Ensemble`, `Techniques`, and `Legato` can mean different things depending on context.

Do not classify a heading from the word alone. Determine what the source is actually grouping.

For example, `Performance` might be a patch-name component, folder, playback mode, articulation qualifier, or marketing category.

# Technical Terms Are Not Articulations

Do not turn sampling/playback terms into articulations or variants.

Examples:

```text
RR
Round Robin
RRx4
DXF
Dynamic Crossfade
Keyswitch
KS
Velocity
Velocity Layer
Mic
Close
Tree
Ambient
Dry
Wet
Kontakt
NKI
Patch
Preset
```

Preserve them as source context if useful, but do not insert them into canonical articulation/variant fields.

# Abbreviations

Never guess an abbreviation expansion solely from appearance.

First search:

- existing terminology aliases
- existing abbreviation tables
- vendor documentation
- surrounding patch/context information

`Leg` may safely map to `legato` if supported by aliases/context.

Ambiguous abbreviations such as `Perf` must remain unresolved unless the context establishes the meaning.

# Evidence Requirement

Every imported concept should be traceable during ingestion.

Maintain at least:

```text
sourceLabel
sourceUrl
sourceContext
proposedCanonicalValue
status
```

Example:

```json
{
  "sourceLabel": "Exp Legato",
  "sourceUrl": "https://example.com/product",
  "sourceContext": "Articulations > Legato patches",
  "proposedCanonicalValue": {
    "articulation": "legato",
    "variant": "expressive"
  },
  "status": "ALIAS"
}
```

This evidence may live only in ingestion/review data and does not have to become part of the production schema.

# Required Pre-Write Review Report

Before modifying canonical data, produce a concise report such as:

```text
INGESTION REVIEW
================

Vendor:
Spitfire Audio

Library:
Example Library

CONFIDENT MATCHES
-----------------
Instruments: 12
Articulations: 47
Variants: 18

INFERRED MATCHES
----------------
3
- "Exp Leg" -> legato / expressive
- ...

UNRESOLVED INSTRUMENTS
----------------------
2
- Oboes + Clarinets
- Horns + Wagner Tubas

UNRESOLVED ARTICULATIONS
------------------------
1
- Feathered Runs

UNRESOLVED VARIANTS
-------------------
3
- Agile
- Intimate
- Immediate

IGNORED TECHNICAL/MARKETING TERMS
---------------------------------
- RRx4
- Close Mic
- Cinematic
- Soaring
```

The exact formatting may vary, but these categories must remain clear.

# Database Mutation Safety

## Codex MAY

- extract source evidence
- search existing terminology
- use existing aliases and abbreviations
- propose mappings
- identify likely matches
- flag uncertainty
- ask the user
- write approved/safe mappings

## Codex MUST NOT

- invent canonical articulations
- invent canonical variants
- invent canonical instruments
- invent aliases
- silently broaden the schema
- infer metadata from marketing adjectives
- split recorded ensembles into fictional independent instruments
- overwrite canonical terminology based only on vendor wording
- hide uncertainty behind a confident guess

# When to Ask

Ask the user when:

- no existing canonical value fits
- multiple existing values are plausible
- a new articulation appears necessary
- a new variant appears necessary
- a new instrument/ensemble appears necessary
- an abbreviation is ambiguous
- the source hierarchy is unclear
- multiple meaningful qualifiers cannot fit the current schema
- classification would require changing the schema
- vendor documentation is contradictory

Do NOT ask merely because wording differs if an existing alias or semantic mapping is clearly correct.

# Preferred User Question Style

Good:

```text
The patch "Agile Legato" clearly maps to articulation `legato`,
but `agile` does not match an existing variant.

Existing candidates:
- fast
- rapid

Should I map it to one of these, add `agile`, or ignore the qualifier?
```

Bad:

```text
What should I do with this?
```

Always show the source term, context, proposed mapping, reason for uncertainty, and relevant existing candidates.

# Final Principle

The terminology database exists to **normalize vendor chaos, not reproduce it**.

Vendor terminology is input evidence. Canonical terminology is curated data.

Codex's job is to make the best possible mapping to the existing vocabulary while preserving evidence and surfacing uncertainty.

When a correct mapping exists:

> **Use it.**

When no correct mapping exists:

> **Ask.**

When tempted to invent:

> **Do not.**
