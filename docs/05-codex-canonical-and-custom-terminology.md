# Codex Instructions — Canonical Terminology and Custom Profile Values

## Purpose

NTD Engine and other profile-authoring applications use the shared `orch-terminology` database for canonical metadata.

At the same time, users must remain free to enter terminology that does not yet exist in the canonical database.

This document defines the strict boundary between:

```text
Canonical terminology
```

and:

```text
User-defined custom terminology
```

The goal is to preserve both:

- a single shared canonical terminology system,
- user freedom to describe unsupported or unusual libraries and patches.

---

# Core Principle

> **Canonical terminology is curated. Custom terminology is local to the profile.**

A user may enter a custom value.

A custom value must never automatically become canonical terminology.

The terminology database and the user's profile metadata are different authorities.

---

# Relationship to `orch-terminology`

The generated SQLite database:

```text
orch-terminology.db
```

is the **single runtime source of truth for canonical terminology**.

Applications such as:

- NTD Engine
- NTD Detector
- the terminology website
- future profile tools

must use this database when presenting or resolving canonical:

```text
Vendor
Library
Instrument / Ensemble
Articulation
Variant
```

However, the SQLite database is not required to contain every possible value a user may ever need.

---

# Why Custom Values Must Remain Supported

The terminology database can never be assumed to contain every:

- new sample library,
- obscure sample library,
- private sample collection,
- custom Kontakt instrument,
- user-created patch,
- experimental instrument,
- unusual ensemble,
- proprietary articulation,
- newly released product,
- personal naming convention.

Therefore NTD Engine must not prevent profile creation merely because canonical terminology is unavailable.

The terminology system should guide the user, not trap the user.

---

# Metadata Value Model

Each terminology field conceptually has two possible states:

```text
CANONICAL
```

or:

```text
CUSTOM
```

These states must remain distinguishable.

---

# Canonical Value

A canonical value references a stable ID from `orch-terminology.db`.

Example:

```text
Instrument / Ensemble:
Trumpet
```

Internal representation:

```json
{
  "instrumentId": "trumpet",
  "instrumentCustom": null
}
```

The display name should be resolved from the terminology database rather than treated as the identity.

---

# Custom Value

A custom value is literal user-owned text.

Example:

```text
Instrument / Ensemble:
3 Trumpets + Garden Hose
```

Internal representation:

```json
{
  "instrumentId": null,
  "instrumentCustom": "3 Trumpets + Garden Hose"
}
```

The custom text belongs to the profile.

It does not belong to the canonical terminology database.

---

# Required Rule

For every terminology-backed profile field:

```text
canonical ID XOR custom value
```

Normally exactly one representation is active.

Examples:

```json
{
  "articulationId": "legato",
  "articulationCustom": null
}
```

or:

```json
{
  "articulationId": null,
  "articulationCustom": "Feathered Performance Legato"
}
```

Do not store both as competing active identities.

---

# Fields

The same concept may apply to:

```text
Vendor
Library
Instrument / Ensemble
Articulation
Variant
```

Example profile metadata:

```json
{
  "vendorId": "spitfire-audio",
  "vendorCustom": null,

  "libraryId": "abbey-road-one-vibrant-reeds",
  "libraryCustom": null,

  "instrumentId": "oboes-clarinets",
  "instrumentCustom": null,

  "articulationId": "legato",
  "articulationCustom": null,

  "variantId": null,
  "variantCustom": "Experimental Transition"
}
```

This example intentionally mixes canonical and custom metadata.

That is allowed.

---

# Do Not Use Display Names as Identity

Avoid storing only:

```json
{
  "instrument": "Trumpet"
}
```

for canonical terminology.

A canonical selection should reference:

```json
{
  "instrumentId": "trumpet"
}
```

The visible label comes from `orch-terminology.db`.

This allows canonical terminology display names to evolve without breaking profiles.

---

# Custom Values Are Literal

Custom values should preserve what the user typed.

Do not automatically:

- normalize them,
- rename them,
- map them,
- spell-correct them,
- create aliases from them,
- upload them,
- insert them into canonical terminology.

A user-owned custom value is profile data.

---

# UI Behavior

Terminology-backed controls should primarily encourage canonical selection.

Recommended interaction:

```text
Instrument / Ensemble

[ Trumpet                         ▼ ]
```

The selector is populated from the canonical terminology database and reduced according to the catalog where appropriate.

The user must also have an explicit escape hatch:

```text
Custom…
```

Selecting it enables free text.

Example:

```text
Instrument / Ensemble

[ Custom…                         ]

[ 3 Trumpets + Garden Hose        ]
```

The exact visual design may differ.

The semantic distinction must remain.

---

# Canonical First

When entering metadata, canonical terminology should be the normal/default path.

Recommended priority:

```text
1. Search/select canonical value
2. If unavailable, use Custom…
```

Do not make custom text the primary path if a canonical value exists.

This improves consistency across profiles.

---

# Cascading Selectors

Canonical values participate in the `catalog.json` / SQLite relationship model.

For example:

```text
Vendor
→ Library
→ Instrument / Ensemble
→ Articulation
→ Variant
```

Selecting canonical values allows the next selector to be reduced to known valid relationships.

---

# Custom Values and Cascading

A custom value breaks the canonical relationship chain at that point unless a deliberate fallback behavior exists.

Example:

```text
Vendor:
Spitfire Audio          [canonical]

Library:
My Modified Library     [custom]
```

The canonical catalog cannot reliably determine which instruments belong to:

```text
My Modified Library
```

Therefore subsequent fields must not pretend that the catalog has authoritative relationship data for that custom branch.

The UI may still allow the user to:

- select canonical terminology independently,
- enter further custom values,
- search the global canonical vocabulary,

but it must not falsely claim that these are catalog-validated relationships.

---

# Important Distinction

There are two different concepts:

```text
Canonical term exists
```

and:

```text
Canonical relationship exists
```

For example, after a custom library is entered, the user might still choose the canonical instrument:

```text
Trumpet
```

That is valid profile metadata.

However, the application must understand:

> `Trumpet` is canonical terminology, but its relationship to this custom library is not established by the canonical catalog.

Do not silently add that relationship to `orch-terminology`.

---

# Custom Values Must Not Contaminate `orch-terminology`

This is a hard rule.

NTD Engine MUST NOT:

- insert custom values into SQLite,
- modify canonical JSON,
- create canonical IDs from custom text,
- add catalog relationships from custom profile metadata,
- create aliases from custom profile metadata,
- publish custom values as official terminology.

The same rule applies to all consuming applications.

---

# No Runtime Canonical Mutation

Recall the architecture:

```text
Canonical JSON
        ↓
validated build
        ↓
orch-terminology.db
        ↓
NTD Engine / Detector / Website
```

Consumers read canonical terminology.

They do not author canonical terminology.

Custom profile values do not change this architecture.

---

# Profile Portability

Custom values must be stored directly in the profile so the profile remains understandable and portable without requiring a local custom terminology database.

Example:

```json
{
  "instrumentId": null,
  "instrumentCustom": "DIY Flugelhorn Section"
}
```

Do not store a local pseudo-ID such as:

```text
custom-instrument-48372
```

unless the application has a separate deliberate custom-entity architecture.

For ordinary profile metadata, literal custom text is preferred.

---

# Missing Canonical IDs

A profile may reference a canonical ID that is unavailable in the currently installed terminology database.

Example:

```json
{
  "instrumentId": "contrabass-flugelhorn",
  "instrumentCustom": null
}
```

but the installed database does not contain:

```text
contrabass-flugelhorn
```

Do not silently convert this into a custom value.

Treat it as a missing canonical reference.

Possible causes include:

- outdated terminology database,
- incompatible database version,
- corrupted profile,
- removed/renamed canonical ID.

Handle this explicitly.

---

# Optional Stored Display Fallback

If profile portability requires readable metadata even when the terminology DB is unavailable, the profile format MAY additionally cache the canonical display label.

Example:

```json
{
  "instrumentId": "trumpet",
  "instrumentLabel": "Trumpet",
  "instrumentCustom": null
}
```

If used:

- `instrumentId` remains authoritative,
- `instrumentLabel` is only a cached/fallback display value,
- the current SQLite terminology wins when available.

Do not confuse cached labels with custom values.

Only introduce this mechanism if the application actually needs it.

---

# Future Canonical Match for a Custom Value

A custom value may later become representable by canonical terminology.

Example profile:

```text
Custom library:
Spitfire Symphonic Brass
```

Later, `orch-terminology.db` contains the correct canonical library.

The application may offer:

```text
Custom value:
Spitfire Symphonic Brass

Canonical match available:
Spitfire Audio
→ Spitfire Symphonic Brass

[Use canonical value]
```

This conversion must be user-approved unless the migration is provably safe and explicitly designed as an automatic migration.

---

# Converting Custom to Canonical

After approval:

Before:

```json
{
  "libraryId": null,
  "libraryCustom": "Spitfire Symphonic Brass"
}
```

After:

```json
{
  "libraryId": "spitfire-symphonic-brass",
  "libraryCustom": null
}
```

Do not retain the custom value as a second competing identity.

---

# Profile Migration

When migrating older NTD profiles that stored plain text metadata, do not assume every text value is custom.

Attempt to resolve it against canonical terminology.

Recommended process:

```text
Old text value
      ↓
exact canonical match?
      ↓
existing alias?
      ↓
safe normalized match?
      ↓
YES → canonical ID
NO  → preserve as custom value
```

Do not discard information.

Do not invent canonical mappings.

Ambiguous migration cases should remain custom or be flagged for review.

---

# Example Migration

Old profile:

```json
{
  "instrument": "Tpt",
  "articulation": "Exp Leg"
}
```

If terminology aliases establish:

```text
Tpt     → trumpet
Exp Leg → legato + expressive
```

migration may produce:

```json
{
  "instrumentId": "trumpet",
  "instrumentCustom": null,

  "articulationId": "legato",
  "articulationCustom": null,

  "variantId": "expressive",
  "variantCustom": null
}
```

If `Exp Leg` cannot be safely resolved, preserve the source meaning rather than guessing.

---

# Search Behavior

When the user types into a terminology control, search canonical terminology first.

Search may include:

- canonical names,
- aliases,
- abbreviations.

If no suitable canonical result exists, offer:

```text
Use "typed value" as Custom
```

Do not automatically turn an unmatched search string into a canonical value.

---

# Visual Distinction

Custom values should be distinguishable without making them look erroneous.

Possible UI treatments:

```text
DIY Flugelhorn Section   Custom
```

or a small custom indicator/icon.

Do not use warning/error styling merely because a value is custom.

Custom is supported behavior, not invalid data.

---

# Validation

Profile validation should accept:

```text
valid canonical ID
```

or:

```text
non-empty custom value
```

for fields where custom values are supported.

Reject invalid states such as:

```json
{
  "instrumentId": "trumpet",
  "instrumentCustom": "Flute"
}
```

unless a clearly defined migration state temporarily permits both.

---

# Recommended Helper Model

Avoid scattering canonical/custom resolution logic throughout the application.

Prefer a reusable conceptual type such as:

```text
TerminologyValue
```

with semantics similar to:

```text
canonicalId: optional
customValue: optional
```

and invariants enforcing:

```text
canonical OR custom
```

This does not require a specific programming-language implementation.

Use the architecture appropriate to the codebase.

---

# Shared Resolution Logic

Where practical, centralize behavior for:

- displaying canonical values,
- displaying custom values,
- resolving IDs,
- searching aliases,
- handling missing IDs,
- converting custom → canonical,
- validating canonical/custom state.

Do not independently reimplement these rules for every metadata field.

---

# Example Complete Profile Metadata

Canonical profile:

```json
{
  "vendorId": "spitfire-audio",
  "vendorCustom": null,

  "libraryId": "abbey-road-one-vibrant-reeds",
  "libraryCustom": null,

  "instrumentId": "oboes-clarinets",
  "instrumentCustom": null,

  "articulationId": "legato",
  "articulationCustom": null,

  "variantId": "expressive",
  "variantCustom": null
}
```

Mixed canonical/custom profile:

```json
{
  "vendorId": null,
  "vendorCustom": "Danny's Samples",

  "libraryId": null,
  "libraryCustom": "Weird Brass Experiments",

  "instrumentId": null,
  "instrumentCustom": "3 Trumpets + Garden Hose",

  "articulationId": "staccato",
  "articulationCustom": null,

  "variantId": null,
  "variantCustom": "Extra Evil"
}
```

Both are valid.

Only the first is fully catalog-backed.

---

# What Codex Must Preserve

When implementing this model, preserve these invariants:

1. Canonical terminology comes only from `orch-terminology.db`.
2. Custom terminology belongs only to user/profile data.
3. Custom values never mutate canonical terminology.
4. Canonical values use stable IDs.
5. Custom values preserve literal user text.
6. Canonical and custom identities remain distinguishable.
7. A custom branch must not create fictional catalog relationships.
8. Missing canonical IDs are not silently converted to custom values.
9. Old profile metadata is migrated conservatively.
10. Users remain able to create profiles even when terminology is incomplete.

---

# What Codex Must Not Do

Codex MUST NOT implement behavior that:

- removes free-text support entirely,
- treats every typed value as canonical,
- inserts custom terms into SQLite,
- modifies canonical JSON from NTD Engine,
- generates canonical IDs from arbitrary user strings,
- silently maps ambiguous custom values,
- creates catalog relationships from user profiles,
- hard-codes fallback terminology in consuming applications,
- makes custom terminology appear to be officially curated terminology.

---

# Architectural Summary

```text
                ORCH TERMINOLOGY
                       │
                       │ canonical
                       ▼
             orch-terminology.db
                       │
                       ▼
                  NTD Engine
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Canonical selection    Custom entry
             │                   │
             │                   │
             ▼                   ▼
      canonical stable ID    literal profile text
             │                   │
             └─────────┬─────────┘
                       ▼
                   NTD profile
```

The two paths meet in the profile, but they do not have the same authority.

---

# Final Principle

The shared terminology database provides:

> **Consistency where possible.**

Custom profile values provide:

> **Freedom where necessary.**

Do not sacrifice one for the other.

The final contract is:

```text
orch-terminology
    = curated shared language

custom profile values
    = user-owned local language
```

And the hard boundary is:

> **Custom values may use the terminology system, but they may never silently become part of it.**
