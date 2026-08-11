# Codex Instructions — Build `catalog.json`

## Purpose

Build and maintain a relationship catalog that connects the canonical orchestral terminology datasets.

The canonical terminology files define **which values exist**.

The catalog defines **which combinations actually occur in real sample libraries**.

The catalog must support cascading UI selectors such as:

```text
Vendor
→ Library
→ Instrument / Ensemble
→ Articulation
→ Variant
```

The catalog is a relationship layer only. It must not become a second terminology database.

---

# Canonical Terminology Sources

Assume separate canonical JSON files exist for:

```text
vendors.json
libraries.json
instruments.json
articulations.json
variants.json
```

These files are authoritative for names, IDs, aliases, abbreviations, notes, and other terminology metadata.

`catalog.json` must reference canonical entries by stable ID.

Do not duplicate canonical display names unless explicitly required.

---

# Core Principle

> **Terminology files define values. `catalog.json` defines valid relationships.**

The catalog must never invent:

- vendor IDs
- library IDs
- instrument IDs
- articulation IDs
- variant IDs

Every referenced ID must already exist in the corresponding canonical terminology file.

If a required canonical term does not exist, stop and ask the user or follow the project's unresolved-term workflow.

Do not silently create terminology while building the catalog.

---

# Required Catalog Granularity

Use **one catalog entry per Vendor + Library + Instrument / Ensemble combination**.

Within that entry, list all available articulations.

Within each articulation, list the variants that exist for that articulation.

Conceptually:

```text
catalog entry
├── vendorId
├── libraryId
├── instrumentId
└── articulations[]
    ├── articulationId
    └── variantIds[]
```

---

# Required JSON Shape

Preferred structure:

```json
[
  {
    "vendorId": "spitfire-audio",
    "libraryId": "abbey-road-one-vibrant-reeds",
    "instrumentId": "oboes-clarinets",
    "articulations": [
      {
        "articulationId": "sustain",
        "variantIds": []
      },
      {
        "articulationId": "staccato",
        "variantIds": []
      },
      {
        "articulationId": "legato",
        "variantIds": [
          "expressive",
          "fast"
        ]
      }
    ]
  }
]
```

---

# Why the Catalog Is Nested This Way

Do NOT use this lossy structure:

```json
{
  "instrumentId": "trumpet",
  "articulations": [
    "legato",
    "staccato"
  ],
  "variants": [
    "harmon-mute",
    "expressive"
  ]
}
```

This destroys the relationship between articulation and variant.

For example, it becomes impossible to know whether:

```text
expressive
```

belongs to:

```text
legato
```

or:

```text
staccato
```

or both.

Instead use:

```json
{
  "instrumentId": "trumpet",
  "articulations": [
    {
      "articulationId": "legato",
      "variantIds": [
        "expressive",
        "harmon-mute"
      ]
    },
    {
      "articulationId": "staccato",
      "variantIds": [
        "harmon-mute"
      ]
    }
  ]
}
```

This preserves the exact relationship.

---

# Empty Variant Lists

An articulation with no variant must use:

```json
"variantIds": []
```

Example:

```json
{
  "articulationId": "staccato",
  "variantIds": []
}
```

An empty variant list means:

> This articulation exists for this instrument/library combination without a defined variant.

Do not:

- omit the articulation,
- invent a `"default"` variant,
- invent a `"generic"` variant,
- use `null` unless the schema is explicitly changed.

Prefer the explicit empty array.

---

# Variant Relationship Rule

Variants are attached to articulations, not globally to instruments or libraries.

Correct:

```text
Trumpet
├── Legato
│   ├── Expressive
│   └── Harmon Mute
└── Staccato
    └── Harmon Mute
```

Incorrect:

```text
Trumpet
├── Articulations
│   ├── Legato
│   └── Staccato
└── Variants
    ├── Expressive
    └── Harmon Mute
```

The second structure loses information.

---

# Instrument / Ensemble Rule

`instrumentId` may refer to:

- solo instruments
- instrument sections
- explicit instrument combinations
- generic ensembles

Examples:

```text
flute
violins
french-horns
oboes-clarinets
low-brass
woodwind-ensemble
full-orchestra
```

The canonical instrument terminology file remains authoritative.

Do not split a sampled ensemble combination into multiple independent catalog entries unless the source library actually provides those instruments independently.

For example:

```text
Oboes + Clarinets
```

should normally be one `instrumentId`.

Do not turn it into separate Oboe and Clarinet catalog entries if the patch is a combined recording.

---

# Stable IDs Only

Use IDs in `catalog.json`.

Preferred:

```json
{
  "vendorId": "spitfire-audio",
  "libraryId": "abbey-road-one-vibrant-reeds",
  "instrumentId": "oboes-clarinets"
}
```

Avoid:

```json
{
  "vendor": "Spitfire Audio",
  "library": "Abbey Road One: Vibrant Reeds",
  "instrument": "Oboes + Clarinets"
}
```

Display names can change.

Stable IDs should preserve relationships even if the visible terminology is later renamed.

---

# Do Not Duplicate Canonical Metadata

The catalog should not repeat:

- display names
- aliases
- abbreviations
- descriptions
- notes
- family names
- normalization information

unless there is a specific relationship-level reason.

The catalog should stay compact and relational.

Canonical metadata belongs in the terminology files.

---

# One Entry Per Vendor + Library + Instrument

The tuple:

```text
vendorId
libraryId
instrumentId
```

must be unique.

Do not create:

```json
{
  "vendorId": "x",
  "libraryId": "y",
  "instrumentId": "z",
  "articulations": [...]
}
```

twice.

If additional articulations are discovered later, merge them into the existing entry.

---

# One Articulation Per Catalog Entry

Within one catalog entry, each:

```text
articulationId
```

must occur only once.

Incorrect:

```json
"articulations": [
  {
    "articulationId": "legato",
    "variantIds": ["expressive"]
  },
  {
    "articulationId": "legato",
    "variantIds": ["fast"]
  }
]
```

Correct:

```json
"articulations": [
  {
    "articulationId": "legato",
    "variantIds": [
      "expressive",
      "fast"
    ]
  }
]
```

Merge duplicate articulation records.

---

# Variant Deduplication

Within one articulation:

```text
variantIds
```

must contain unique IDs.

Incorrect:

```json
"variantIds": [
  "expressive",
  "expressive"
]
```

Correct:

```json
"variantIds": [
  "expressive"
]
```

---

# Sorting

Keep `catalog.json` deterministic and easy to diff.

Preferred sort order:

```text
vendorId
libraryId
instrumentId
articulationId
variantId
```

Within each catalog entry:

1. sort articulations by `articulationId`,
2. sort `variantIds` lexically by ID.

If the project already defines a canonical display/order field, that may be used instead, but sorting must remain deterministic.

---

# Catalog Construction Workflow

Use this sequence.

## Step 1 — Load canonical terminology

Load the current canonical files:

```text
vendors.json
libraries.json
instruments.json
articulations.json
variants.json
```

Build lookup maps by ID.

---

## Step 2 — Load normalized source/library data

Use only data that has already passed the terminology ingestion and review process.

The catalog-building step must not re-scrape vendor websites and independently reinterpret terminology unless explicitly instructed.

Prefer normalized/approved relationships such as:

```text
vendorId
libraryId
instrumentId
articulationId
variantId
```

---

## Step 3 — Validate all IDs

Before adding a relationship, verify:

```text
vendorId       exists in vendors.json
libraryId      exists in libraries.json
instrumentId   exists in instruments.json
articulationId exists in articulations.json
variantId      exists in variants.json, if present
```

If any ID is missing:

```text
STOP
```

Do not invent the missing term.

Report the unresolved reference.

---

## Step 4 — Group relationships

Group normalized rows by:

```text
vendorId + libraryId + instrumentId
```

For each group, group again by:

```text
articulationId
```

Collect the valid variant IDs for that articulation.

---

## Step 5 — Build nested catalog entries

Transform grouped relationships into:

```json
{
  "vendorId": "...",
  "libraryId": "...",
  "instrumentId": "...",
  "articulations": [
    {
      "articulationId": "...",
      "variantIds": []
    }
  ]
}
```

---

## Step 6 — Merge with existing catalog

If `catalog.json` already exists:

- preserve existing valid mappings,
- add newly discovered mappings,
- merge duplicate articulations,
- merge variant lists,
- remove exact duplicates,
- do not remove mappings merely because a newly scraped source did not mention them.

Absence from one source is not proof that an existing catalog relationship is invalid.

Only remove catalog relationships when explicitly instructed or when there is strong reviewed evidence that they are incorrect.

---

## Step 7 — Validate the finished catalog

Before writing, validate all constraints in this document.

---

# Required Validation Rules

Codex must validate that:

1. every `vendorId` exists,
2. every `libraryId` exists,
3. every `instrumentId` exists,
4. every `articulationId` exists,
5. every non-empty `variantId` exists,
6. every Vendor + Library + Instrument tuple is unique,
7. every articulation occurs only once per catalog entry,
8. every variant occurs only once per articulation,
9. `variantIds` is always an array,
10. `articulations` is always a non-empty array,
11. no canonical display names are accidentally used where IDs are required,
12. the resulting JSON is deterministic and consistently sorted.

---

# Referential Consistency

Where possible, also validate logical parent relationships already encoded elsewhere.

For example, if `libraries.json` contains a canonical vendor relationship:

```json
{
  "id": "abbey-road-one-vibrant-reeds",
  "vendorId": "spitfire-audio"
}
```

then a catalog entry must not claim:

```json
{
  "vendorId": "different-vendor",
  "libraryId": "abbey-road-one-vibrant-reeds"
}
```

If this conflict occurs, report it rather than choosing one silently.

---

# No Cartesian Products

Never assume that every instrument supports every articulation in a library.

Never assume that every articulation supports every variant.

Do not generate relationships from broad lists using a Cartesian product.

For example, given:

```text
Instruments:
Trumpet
Horn

Articulations:
Legato
Staccato

Variants:
Harmon Mute
Expressive
```

do NOT generate all possible combinations.

Only store relationships supported by normalized source evidence.

---

# Source Evidence

When building the production `catalog.json`, the catalog itself may remain compact.

However, if ingestion/review evidence exists, preserve it in a separate staging or review file when useful.

For example:

```json
{
  "vendorId": "spitfire-audio",
  "libraryId": "example-library",
  "instrumentId": "trumpet",
  "articulationId": "legato",
  "variantId": "expressive",
  "sourceLabel": "Exp Leg",
  "sourceUrl": "https://...",
  "status": "ALIAS"
}
```

Do not necessarily copy this evidence into production `catalog.json`.

The catalog should remain focused on valid relationships.

---

# Website Cascading Selector Behavior

The catalog is intended to support queries like:

## Vendor selected

Given:

```text
vendorId = spitfire-audio
```

derive only libraries present in catalog entries with that vendor.

## Library selected

Given:

```text
vendorId = spitfire-audio
libraryId = abbey-road-one-vibrant-reeds
```

derive only instruments present in matching catalog entries.

## Instrument selected

Given:

```text
vendorId
libraryId
instrumentId
```

derive only articulations in that catalog entry.

## Articulation selected

Given:

```text
vendorId
libraryId
instrumentId
articulationId
```

derive only the `variantIds` for that articulation.

If:

```json
"variantIds": []
```

the UI should understand that no variant selection is required.

---

# Example

Canonical terminology might contain:

```text
Vendor:
spitfire-audio

Library:
abbey-road-one-vibrant-reeds

Instruments:
oboes-clarinets
oboes-english-horns

Articulations:
legato
staccato
sustain

Variants:
expressive
fast
```

A catalog may then contain:

```json
[
  {
    "vendorId": "spitfire-audio",
    "libraryId": "abbey-road-one-vibrant-reeds",
    "instrumentId": "oboes-clarinets",
    "articulations": [
      {
        "articulationId": "legato",
        "variantIds": [
          "expressive",
          "fast"
        ]
      },
      {
        "articulationId": "staccato",
        "variantIds": []
      },
      {
        "articulationId": "sustain",
        "variantIds": []
      }
    ]
  },
  {
    "vendorId": "spitfire-audio",
    "libraryId": "abbey-road-one-vibrant-reeds",
    "instrumentId": "oboes-english-horns",
    "articulations": [
      {
        "articulationId": "legato",
        "variantIds": []
      },
      {
        "articulationId": "sustain",
        "variantIds": []
      }
    ]
  }
]
```

This means the UI can reduce each subsequent selector without losing articulation-to-variant relationships.

---

# Update Behavior

When new approved data is ingested:

### Existing instrument + existing articulation + new variant

Add the variant to the existing articulation's `variantIds`.

### Existing instrument + new articulation

Add a new articulation object to the existing catalog entry.

### New instrument in an existing library

Add a new Vendor + Library + Instrument catalog entry.

### New library

Add catalog entries for its approved instruments and articulation relationships.

### Terminology rename

If stable IDs remain unchanged, no catalog migration should be required.

### Canonical ID change

Treat this as a deliberate migration and update all references consistently.

---

# Error Handling

If Codex encounters:

```text
unknown vendor ID
unknown library ID
unknown instrument ID
unknown articulation ID
unknown variant ID
conflicting library/vendor relationship
ambiguous normalized mapping
```

do not guess.

Report the problem clearly.

Example:

```text
CATALOG BUILD BLOCKED

Source relationship:
Spitfire Audio / Example Library / Trumpet / Agile Legato

Resolved:
vendorId       = spitfire-audio
libraryId      = example-library
instrumentId   = trumpet
articulationId = legato

Unresolved:
variant = agile

No canonical variant ID exists.

catalog.json was not updated with this unresolved relationship.
```

---

# Recommended Review Output

Before writing a substantial catalog update, summarize:

```text
CATALOG UPDATE REVIEW

New catalog entries: 8
Existing entries updated: 14
New articulation relationships: 23
New variant relationships: 11
Duplicates removed: 4
Unresolved references: 2
Validation errors: 0
```

List unresolved references explicitly.

---

# What Codex Must Not Do

Codex MUST NOT:

- create new canonical terminology while building the catalog,
- put display names in place of IDs,
- flatten variants away from their articulations,
- generate Cartesian products,
- split recorded composite instruments without evidence,
- create duplicate Vendor + Library + Instrument entries,
- create duplicate articulation objects,
- create duplicate variant IDs,
- treat missing source evidence as permission to remove existing mappings,
- silently repair ambiguous terminology.

---

# Final Rule

`catalog.json` is the authoritative map of **which canonical terms are valid together**.

It should answer:

> For this vendor and library, which instruments exist?

> For this instrument, which articulations exist?

> For this articulation, which variants exist?

It should not answer:

> What does this terminology mean?

That belongs in the canonical terminology files.

Keep the distinction strict:

```text
Canonical JSONs = vocabulary
catalog.json    = relationships
```
