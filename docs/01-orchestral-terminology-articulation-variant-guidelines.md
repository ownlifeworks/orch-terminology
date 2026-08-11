# Orchestral Terminology Database — Articulation and Variant Normalization

## Purpose

This document defines how orchestral library metadata should be normalized when importing or extracting data from vendor websites.

The terminology database is intended to provide a **stable, normalized vocabulary across different orchestral sample-library vendors**.

Vendor terminology must therefore not be copied blindly into canonical fields.

The database should normalize equivalent concepts while preserving vendor-specific distinctions where useful.

---

## Core Metadata Structure

The relevant hierarchy is:

```text
Vendor
└── Library
    └── Instrument
        └── Articulation
            └── Variant (optional)
```

`Variant` is optional.

Do **not** introduce additional hierarchy levels such as collection, family, ecosystem, product group, etc. unless explicitly requested.

---

## Meaning of the Fields

### Vendor

The vendor or brand under which the library is actually distributed.

Examples:

```text
Spitfire Audio
Orchestral Tools
Cinematic Studio Series
Soundpaint
VSL
EastWest
```

Do not replace the visible vendor with a parent company merely because one exists.

---

### Library

The identifiable sample product containing the instrument.

A library does not need to contain many instruments.

Single-instrument products are valid libraries.

Example:

```text
Vendor:     Soundpaint
Library:    2001 Piccolo Shire
Instrument: Piccolo
```

Do not collapse unrelated Soundpaint products into a fictional common library merely to simplify grouping.

---

### Instrument

The normalized orchestral instrument.

Examples:

```text
Flute
Piccolo
Oboe
English Horn
Clarinet
Bass Clarinet
Bassoon
Trumpet
French Horn
Trombone
Violin
Viola
Cello
Double Bass
```

Vendor-specific naming should be normalized to the canonical instrument vocabulary whenever possible.

---

## Articulation

`articulation` represents the **main normalized musical playing technique**.

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
flutter tongue
```

The articulation vocabulary should remain deliberately conservative.

### Critical Rule

**Vendor patch names are NOT canonical articulation names.**

Do not create a new articulation merely because the vendor adds descriptive wording.

Examples:

```text
Expressive Legato
Rapid Legato
Fast Legato
Low Latency Legato
Performance Legato
Lyrical Legato
```

All of these should normally map to:

```text
articulation: legato
```

The additional distinction belongs in `variant`.

---

# Variant

`variant` is an **optional, normalized qualifier** that describes a meaningful variation of the main articulation.

It is not another articulation hierarchy.

It is an orthogonal modifier.

Like `articulation`, `variant` uses a **controlled, human-curated vocabulary**. Codex must reuse existing canonical variants and aliases whenever possible and must not invent new variant values during ingestion.

Examples:

```text
articulation: legato
variant: expressive
```

```text
articulation: legato
variant: rapid
```

```text
articulation: legato
variant: low latency
```

```text
articulation: staccato
variant: harmon mute
```

```text
articulation: legato
variant: harmon mute
```

If no meaningful qualifier exists:

```text
variant: ""
```

or omit the field if the schema allows omission.

---

## Why Variant Exists

Many orchestral libraries provide several implementations of the same musical articulation.

For example:

```text
Legato
Expressive Legato
Rapid Legato
Low Latency Legato
Performance Legato
```

These should not create five unrelated canonical articulations.

They share the same normalized articulation:

```text
legato
```

but differ by variant.

Likewise, an instrument state such as a mute may apply to several articulations:

```text
Trumpet
├── Legato
│   └── Harmon mute
└── Staccato
    └── Harmon mute
```

This is better represented as:

```text
articulation: legato
variant: harmon mute
```

and:

```text
articulation: staccato
variant: harmon mute
```

rather than creating canonical articulation names such as:

```text
Harmon Muted Legato
Harmon Muted Staccato
```

---

# Normalization Philosophy

The database should answer two different questions.

`articulation` answers:

> What is the underlying musical articulation?

`variant` answers:

> What meaningful flavor, state, implementation, or vendor-specific version of that articulation is this?

---

## Canonical Articulations and Variants Must Be Stable

Both `articulation` and `variant` are controlled vocabularies that should grow slowly and intentionally.

Codex must **never automatically extend either vocabulary during vendor website ingestion**.

### Non-Invention Rule

**Never invent an articulation or a variant.**

For every extracted vendor term:

1. Search the existing canonical articulation values and their aliases.
2. Select the existing articulation that best and correctly represents the underlying musical technique.
3. If a meaningful qualifier remains, search the existing canonical variant values and their aliases.
4. Select the existing variant that best and correctly represents that qualifier.
5. Preserve the vendor's original wording in the profile name, source name, aliases, or notes as appropriate.
6. If no existing articulation or variant can be correctly mapped, **stop and ask the user**.

Do not silently create a new articulation or variant.

A new canonical articulation or variant may only be added after explicit user approval.

Codex may suggest a likely new canonical value when asking, but it must clearly identify it as a proposal rather than adding it automatically.

### Prefer Best Existing Match — But Do Not Force a Wrong Match

Codex should make a genuine semantic effort to reuse the existing vocabulary. Minor wording differences, vendor marketing language, synonyms, abbreviations, spelling differences, and descriptive modifiers are not reasons to create new values.

However, Codex must not force an incorrect match merely to avoid asking.

The decision order is:

```text
Existing exact canonical value
        ↓
Existing alias / known synonym
        ↓
Best semantically equivalent existing value
        ↓
No correct match exists
        ↓
ASK THE USER
```

The same rule applies independently to both `articulation` and `variant`.

---

# Website Extraction Rules

When reading vendor websites, patch lists, manuals, product pages, PDFs, or presets:

## Step 1 — Preserve the source label

Example source:

```text
Expressive Low Latency Legato
```

Preserve this exact phrase somewhere appropriate, such as:

```text
name
sourceName
aliases
notes
```

depending on the current schema.

Do not lose the vendor's original terminology.

---

## Step 2 — Identify the base articulation

From:

```text
Expressive Low Latency Legato
```

extract:

```text
articulation: legato
```

---

## Step 3 — Map meaningful qualifiers to an existing variant

Do **not** copy the remaining words directly into `variant`.

Search the existing canonical variant vocabulary and aliases and choose the best correct match.

For example, if the source says:

```text
Expressive Legato
```

and the canonical variant vocabulary already contains:

```text
expressive
```

use:

```text
articulation: legato
variant: expressive
```

If the source contains a qualifier for which no existing canonical variant or alias is a correct match, **ask the user** instead of creating one.

---

## Step 4 — Reuse canonical values

Before assigning an articulation or variant, search the existing terminology database.

Prefer existing normalized values whenever they accurately represent the source terminology.

Neither `articulation` nor `variant` may be extended automatically.

---

# Examples

## Example 1 — Expressive Legato

Vendor label:

```text
Expressive Legato
```

Correct:

```text
articulation: legato
variant: expressive
```

Incorrect:

```text
articulation: expressive legato
```

---

## Example 2 — Rapid Legato

Vendor label:

```text
Rapid Legato
```

Correct:

```text
articulation: legato
variant: rapid
```

Incorrect:

```text
articulation: rapid legato
```

---

## Example 3 — Low Latency Legato

Vendor label:

```text
Low Latency Legato
```

Correct:

```text
articulation: legato
variant: low latency
```

---

## Example 4 — Harmon Mute Staccato

Vendor label:

```text
Harmon Mute Staccato
```

Correct:

```text
instrument: trumpet
articulation: staccato
variant: harmon mute
```

Incorrect:

```text
articulation: harmon mute staccato
```

---

## Example 5 — Harmon Mute Legato

Vendor label:

```text
Harmon Mute Legato
```

Correct:

```text
instrument: trumpet
articulation: legato
variant: harmon mute
```

---

## Example 6 — Plain Legato

Vendor label:

```text
Legato
```

Correct:

```text
articulation: legato
variant: ""
```

---

# Important Ambiguity Rule

Some terms can be interpreted either as an articulation or as a variant.

Examples may include:

```text
con sordino
sul ponticello
flutter tongue
measured tremolo
muted
```

Do not attempt to solve these philosophically.

Use the existing database vocabulary and project conventions.

The practical rule is:

> `articulation` is the primary normalized technique used for cross-library matching.
>
> `variant` is an optional qualifier that distinguishes meaningful versions of that articulation.

If the existing terminology database already treats a term as an articulation, continue using it that way.

Consistency across the database is more important than theoretically perfect classification.

---

# Ingestion Safety Rules

Codex must follow these rules when importing metadata:

1. **Never blindly copy vendor patch names into `articulation`.**
2. **Never create a new canonical articulation solely because wording differs.**
3. **Always search existing canonical articulations before proposing a new one.**
4. **Use `variant` for meaningful qualifiers and alternate implementations.**
5. **Preserve the original vendor wording elsewhere.**
6. **Prefer broader existing canonical articulations over unnecessary fragmentation.**
7. **Never invent a canonical variant.**
8. **When no correct existing articulation or variant can be found, stop and ask the user.**
9. **A new articulation or variant requires explicit user approval.**
10. **Do not create additional metadata hierarchy levels without explicit instruction.**

---

# Desired Behavior

The goal is not to reproduce vendor terminology.

The goal is to normalize it.

Vendor websites may contain:

```text
Performance Legato
Agile Legato
Expressive Legato
Low Latency Legato
Lyrical Legato
Fast Legato
```

The terminology database should understand these primarily as:

```text
legato
```

with optional variants such as:

```text
performance
agile
expressive
low latency
lyrical
fast
```

**only where those variants already exist in the controlled vocabulary or have been explicitly approved by the user.**

If, for example, `agile` is encountered on a vendor website but no canonical `agile` variant or suitable alias/mapping exists, Codex must ask whether it should be added or mapped to another existing variant.

This allows cross-vendor matching while still preserving meaningful product-specific distinctions without allowing uncontrolled vocabulary growth.

---

# Key Principle

**The terminology database should reduce vendor terminology chaos, not reproduce it.**

Canonical fields should remain stable and reusable.

Vendor-specific detail should be preserved, but placed in the appropriate field.


---

# Mandatory Decision Rule for Codex

When ingesting orchestral terminology, use this rule without exception:

```text
ARTICULATION

Can the vendor term be mapped correctly to an existing
canonical articulation or articulation alias?

YES → Use that canonical articulation.
NO  → ASK THE USER. Do not invent one.


VARIANT

Is there a meaningful qualifier?

NO  → Leave variant empty.

YES → Can it be mapped correctly to an existing
      canonical variant or variant alias?

      YES → Use that canonical variant.
      NO  → ASK THE USER. Do not invent one.
```

The purpose of AI-assisted ingestion is to make the **best possible normalization decision using the existing terminology database**, not to expand the vocabulary autonomously.

When asking the user, provide enough context to make the decision easy. For example:

```text
Unrecognized variant from vendor source: "Agile"

Source patch: "Agile Legato"
Mapped articulation: legato

I could not find an existing canonical variant or alias that
correctly represents "Agile".

Possible action:
- map it to an existing variant
- add "agile" as a new canonical variant
- ignore the qualifier and leave variant empty

Please decide.
```

**When in doubt, ask. Never invent.**
