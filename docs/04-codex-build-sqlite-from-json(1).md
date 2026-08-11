# Codex Instructions — Build SQLite Distribution from Canonical JSON

## Purpose

Build a generated SQLite database from the canonical orchestral terminology JSON files.

The JSON files remain the **authoritative source of truth**.

The SQLite database is a **generated distribution/runtime artifact** for applications such as:

- NTD Engine
- NTD Detector
- the terminology website
- internal tools
- future APIs or import/export tools

Do not manually curate terminology inside SQLite.

> **Edit JSON. Validate JSON. Generate SQLite. Consume SQLite.**

---

# Architectural Principle

The project has two clearly separated layers.

## Authoring Layer

Human- and AI-maintained canonical terminology:

```text
vendors.json
libraries.json
instruments.json
articulations.json
variants.json
catalog.json
```

These files are:

- version-controlled,
- human-readable,
- reviewable in Git,
- editable by Codex,
- the canonical source of truth.

## Runtime / Distribution Layer

Generated SQLite database:

```text
orch-terminology.db
```

This database is:

- generated from the JSON source,
- never manually edited,
- optimized for application queries,
- replaceable at any time by rebuilding from JSON.

If JSON and SQLite ever disagree:

> **JSON wins. Rebuild SQLite.**

---

# Required Build Flow

The build process must follow this order:

```text
Canonical JSON
      ↓
JSON schema validation
      ↓
semantic validation
      ↓
cross-reference validation
      ↓
normalization / deterministic ordering
      ↓
SQLite generation
      ↓
SQLite verification
      ↓
distribution artifact
```

If validation fails, do not produce a successful SQLite build.

---

# Canonical Input Files

Assume the canonical terminology is stored in files such as:

```text
vendors.json
libraries.json
instruments.json
articulations.json
variants.json
catalog.json
```

The exact project paths may differ.

Codex should inspect the repository and use the actual canonical paths.

Do not duplicate or fork these files merely for database generation.

---

# SQLite Is Generated Only

Codex MUST NOT:

- edit terminology directly inside SQLite,
- treat SQLite as the canonical store,
- write migration-only data that does not exist in JSON,
- manually patch the `.db` to fix source-data problems,
- allow applications to become dependent on undocumented SQLite-only terminology.

All terminology changes must originate in canonical JSON.

---

# Recommended SQLite Schema

The exact schema may evolve, but the database should represent the canonical terminology and catalog relationships cleanly.

A recommended starting point is:

```text
vendors
libraries
instruments
articulations
variants

catalog_entries
catalog_articulations
catalog_variants
```

Optional supporting tables may include:

```text
aliases
abbreviations
metadata
schema_info
```

Only add tables when they reflect actual canonical source concepts or useful generated indexes.

Do not invent new taxonomy merely because SQL supports it.

---

# Recommended Core Tables

## vendors

Example:

```sql
CREATE TABLE vendors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
```

Additional canonical vendor metadata may be added if it exists in JSON.

---

## libraries

Example:

```sql
CREATE TABLE libraries (
    id TEXT PRIMARY KEY,
    vendor_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);
```

If the canonical library JSON already includes a vendor relationship, preserve it.

---

## instruments

Example:

```sql
CREATE TABLE instruments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
```

This table includes solo instruments, sections, composite instruments, and ensembles if they exist canonically.

---

## articulations

Example:

```sql
CREATE TABLE articulations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
```

---

## variants

Example:

```sql
CREATE TABLE variants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
```

---

# Catalog Relationship Tables

The JSON catalog is nested for readability.

The SQLite representation should usually be normalized relationally.

Given a JSON catalog entry such as:

```json
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
    }
  ]
}
```

a normalized SQL representation is preferred.

---

## catalog_entries

One row per:

```text
vendor + library + instrument
```

Example:

```sql
CREATE TABLE catalog_entries (
    id INTEGER PRIMARY KEY,
    vendor_id TEXT NOT NULL,
    library_id TEXT NOT NULL,
    instrument_id TEXT NOT NULL,

    UNIQUE (vendor_id, library_id, instrument_id),

    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (library_id) REFERENCES libraries(id),
    FOREIGN KEY (instrument_id) REFERENCES instruments(id)
);
```

---

## catalog_articulations

One row per articulation available for a catalog entry.

Example:

```sql
CREATE TABLE catalog_articulations (
    id INTEGER PRIMARY KEY,
    catalog_entry_id INTEGER NOT NULL,
    articulation_id TEXT NOT NULL,

    UNIQUE (catalog_entry_id, articulation_id),

    FOREIGN KEY (catalog_entry_id) REFERENCES catalog_entries(id),
    FOREIGN KEY (articulation_id) REFERENCES articulations(id)
);
```

---

## catalog_variants

One row per variant available for a specific catalog articulation.

Example:

```sql
CREATE TABLE catalog_variants (
    catalog_articulation_id INTEGER NOT NULL,
    variant_id TEXT NOT NULL,

    PRIMARY KEY (catalog_articulation_id, variant_id),

    FOREIGN KEY (catalog_articulation_id) REFERENCES catalog_articulations(id),
    FOREIGN KEY (variant_id) REFERENCES variants(id)
);
```

An articulation with:

```json
"variantIds": []
```

simply has no rows in `catalog_variants`.

Do not create fake variants such as:

```text
default
generic
none
```

unless they exist canonically.

---

# Alias and Abbreviation Storage

If aliases and abbreviations exist in the canonical JSON, they may be normalized into generated tables.

Recommended:

```sql
CREATE TABLE aliases (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    alias TEXT NOT NULL,

    PRIMARY KEY (entity_type, entity_id, alias)
);
```

Possible `entity_type` values:

```text
vendor
library
instrument
articulation
variant
```

If abbreviations are semantically distinct from aliases in the source model, use a separate table.

Do not merge distinct canonical concepts unless the source model allows it.

---

# Generated Metadata Table

Add a small build metadata table.

Example:

```sql
CREATE TABLE schema_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

Useful generated values may include:

```text
schema_version
data_version
build_timestamp
source_commit
generator_version
```

Only populate values that can be determined reliably.

Do not invent version information.

---

# Validation Before Database Generation

The SQLite build must be blocked if canonical JSON is invalid.

Validation should include at least the following.

## JSON syntax validation

Every canonical JSON file must parse successfully.

---

## JSON schema validation

If JSON Schema files exist, validate each canonical file against its schema.

If schemas do not yet exist, Codex may propose them separately, but must not silently redefine the canonical structure during this build task.

---

## ID uniqueness

Ensure IDs are unique inside their canonical domains.

Examples:

```text
no duplicate vendor IDs
no duplicate library IDs
no duplicate instrument IDs
no duplicate articulation IDs
no duplicate variant IDs
```

---

## Referential integrity

Validate all referenced IDs before opening the SQLite write transaction.

Examples:

```text
library.vendorId exists in vendors
catalog.vendorId exists in vendors
catalog.libraryId exists in libraries
catalog.instrumentId exists in instruments
catalog.articulationId exists in articulations
catalog.variantId exists in variants
```

---

## Logical relationship validation

If `libraries.json` says:

```text
abbey-road-one-vibrant-reeds → spitfire-audio
```

then catalog data must not associate that library with another vendor.

Report conflicts.

Do not resolve them silently.

---

## Catalog uniqueness

Validate:

```text
vendorId + libraryId + instrumentId
```

is unique.

Inside each catalog entry:

```text
articulationId
```

must be unique.

Inside each articulation:

```text
variantIds
```

must be unique.

---

## No unresolved terminology

Do not generate a production SQLite database containing unresolved placeholder IDs such as:

```text
UNKNOWN
UNRESOLVED
TODO
TBD
```

unless the canonical source model explicitly defines such values.

Normally unresolved ingestion data belongs in staging/review files, not production JSON.

---

# Deterministic Builds

Given the same canonical JSON inputs, the generated logical database contents should be reproducible.

Use deterministic:

- sorting,
- insertion order,
- normalization,
- schema generation,
- index creation.

Do not depend on filesystem enumeration order.

If build timestamps are stored, they may differ, but terminology and relationships should remain logically identical.

---

# Build Strategy

Recommended implementation:

```text
1. Parse all canonical JSON
2. Validate all source data
3. Open/create a fresh SQLite database
4. Enable foreign keys
5. Create schema
6. Begin transaction
7. Insert canonical terminology
8. Insert aliases/abbreviations
9. Insert catalog entries
10. Insert catalog articulations
11. Insert catalog variants
12. Insert build metadata
13. Run verification queries
14. Commit transaction
15. Publish/replace final .db artifact
```

---

# Build Fresh, Do Not Incrementally Patch

Prefer rebuilding the SQLite database from scratch from canonical JSON.

Do not use the existing database as the authoritative base for incremental data migrations.

Recommended:

```text
delete/create temporary DB
        ↓
build complete DB
        ↓
validate
        ↓
atomically replace distribution DB
```

This prevents drift.

---

# Temporary Output

Build to a temporary path first.

Example:

```text
dist/orch-terminology.db.tmp
```

Only replace:

```text
dist/orch-terminology.db
```

after the new database passes all verification.

If generation fails, preserve the previous valid distribution artifact unless the project's build policy says otherwise.

---

# SQLite Pragmas

At minimum, enable:

```sql
PRAGMA foreign_keys = ON;
```

During generation, other pragmas may be used for build performance if they do not compromise final correctness.

Do not rely on SQLite behavior that bypasses referential integrity.

---

# Recommended Indexes

Create indexes for common application queries.

Likely examples:

```sql
CREATE INDEX idx_libraries_vendor
ON libraries(vendor_id);

CREATE INDEX idx_catalog_vendor
ON catalog_entries(vendor_id);

CREATE INDEX idx_catalog_library
ON catalog_entries(library_id);

CREATE INDEX idx_catalog_instrument
ON catalog_entries(instrument_id);

CREATE INDEX idx_catalog_articulation
ON catalog_articulations(articulation_id);

CREATE INDEX idx_catalog_variant
ON catalog_variants(variant_id);
```

Avoid excessive indexes without a query need.

---

# Cascading Selector Queries

The database should efficiently support the website/application workflow.

## Vendors

```sql
SELECT id, name
FROM vendors
ORDER BY name;
```

---

## Libraries for vendor

```sql
SELECT DISTINCT l.id, l.name
FROM libraries l
JOIN catalog_entries c
  ON c.library_id = l.id
WHERE c.vendor_id = ?
ORDER BY l.name;
```

---

## Instruments for vendor + library

```sql
SELECT DISTINCT i.id, i.name
FROM instruments i
JOIN catalog_entries c
  ON c.instrument_id = i.id
WHERE c.vendor_id = ?
  AND c.library_id = ?
ORDER BY i.name;
```

---

## Articulations for vendor + library + instrument

```sql
SELECT a.id, a.name
FROM articulations a
JOIN catalog_articulations ca
  ON ca.articulation_id = a.id
JOIN catalog_entries c
  ON c.id = ca.catalog_entry_id
WHERE c.vendor_id = ?
  AND c.library_id = ?
  AND c.instrument_id = ?
ORDER BY a.name;
```

---

## Variants for selected articulation

```sql
SELECT v.id, v.name
FROM variants v
JOIN catalog_variants cv
  ON cv.variant_id = v.id
JOIN catalog_articulations ca
  ON ca.id = cv.catalog_articulation_id
JOIN catalog_entries c
  ON c.id = ca.catalog_entry_id
WHERE c.vendor_id = ?
  AND c.library_id = ?
  AND c.instrument_id = ?
  AND ca.articulation_id = ?
ORDER BY v.name;
```

If no rows are returned, the articulation has no variant requirement.

---

# Application Consumption Contract

This is a strict architectural boundary.

There are two single sources of truth at two different stages:

```text
AUTHORING / REPOSITORY TRUTH
        │
        ▼
Canonical JSON files
        │
        │ validate + build
        ▼
orch-terminology.db
        │
        ▼
RUNTIME / CONSUMPTION TRUTH
        │
        ├── NTD Engine
        ├── NTD Detector
        ├── terminology website
        ├── import/export tooling
        └── future consuming applications
```

## Authoring source of truth

The canonical JSON files are the **single source of truth for authoring, reviewing, correcting, and extending the terminology dataset**.

All terminology changes originate there.

## Runtime source of truth

The generated `orch-terminology.db` SQLite database is the **single source of truth for all consuming applications**.

This is mandatory, not a preference.

NTD Engine, NTD Detector, the terminology website, and every other runtime consumer MUST obtain canonical terminology and catalog relationships from the generated SQLite database.

Consuming applications MUST NOT:

- independently load the canonical JSON files for normal runtime terminology lookup,
- maintain their own copies of vendor/library/instrument/articulation/variant vocabularies,
- implement independent normalization rules,
- reinterpret aliases independently,
- duplicate the catalog relationship logic,
- introduce application-specific canonical terminology,
- silently supplement SQLite with locally invented terminology,
- treat hard-coded terminology lists as authoritative.

The intended architecture is:

```text
Codex / human curation
        ↓
Canonical JSON
        ↓
validation
        ↓
SQLite generator
        ↓
orch-terminology.db
        ↓
ALL consuming applications
```

The JSON files define what gets built.

The SQLite database defines what consumers see.

## No divergent consumer vocabularies

A consuming application may cache or index SQLite data internally for performance, but that data must remain derived from `orch-terminology.db`.

A consumer must not become an independent terminology authority.

For example, NTD Engine must not maintain its own articulation vocabulary while NTD Detector maintains another.

Both must resolve terminology from the same generated database.

If terminology is missing or incorrect:

```text
DO NOT fix it in NTD Engine.
DO NOT fix it in NTD Detector.
DO NOT fix it in the website.
DO NOT patch the SQLite database manually.

Fix the canonical JSON.
Validate.
Rebuild SQLite.
Distribute the updated SQLite database.
```

This guarantees that every consumer sees the same canonical terminology and relationships.

## Consumer schema access

Consumers may query the SQLite schema directly or through a shared terminology access library/API.

A shared access layer is encouraged if it prevents query logic from being duplicated across applications.

However, such a library is an access mechanism only.

The authority remains:

```text
orch-terminology.db
```

for runtime consumption.

## Runtime availability

A consuming application should treat the terminology database as a versioned application resource.

If the required SQLite database cannot be loaded or is incompatible with the consumer's supported schema version, the application must handle that explicitly.

It must not silently fall back to an independent embedded terminology vocabulary unless such fallback behavior has been deliberately designed and approved.

## Architectural invariant

The following invariant must remain true:

```text
ONE editable canonical dataset
        ↓
ONE generated runtime representation
        ↓
MANY consumers
```

Never allow this architecture to degrade into:

```text
                ┌─ NTD Engine terminology
Canonical data ─┼─ NTD Detector terminology
                ├─ Website terminology
                └─ Other app terminology
```

The entire purpose of `orch-terminology` is to provide one shared terminology system.

Therefore:

> **Canonical JSON is the single authoring source of truth.**

> **Generated SQLite is the single runtime source of truth.**

> **Consuming applications do not own terminology. They consume it.**


---

# Version Control Guidance

Recommended:

- commit canonical JSON,
- commit schema/build scripts,
- commit tests,
- optionally commit the generated SQLite distribution if applications need a ready-to-use artifact.

Do not treat changes to the binary SQLite file as sufficient review evidence.

The meaningful review remains the JSON diff.

If the `.db` is committed, it must be reproducibly generated from the committed source JSON.

---

# CI / Build Pipeline

Recommended automated pipeline:

```text
validate JSON
      ↓
run semantic validation
      ↓
run catalog validation
      ↓
generate SQLite
      ↓
verify SQLite
      ↓
run tests
      ↓
publish artifact
```

A validation failure must fail the build.

---

# Verification After Generation

After creating the database, run checks such as:

```sql
PRAGMA foreign_key_check;
PRAGMA integrity_check;
```

The build must fail if these checks report errors.

Also compare expected source counts to generated table counts where appropriate.

Examples:

```text
vendors.json count      == vendors row count
libraries.json count    == libraries row count
instruments.json count  == instruments row count
articulations.json count == articulations row count
variants.json count     == variants row count
```

For nested catalog data, verify generated relationship counts against independently computed expected counts.

---

# Suggested Build Report

After a successful build, print a concise report such as:

```text
ORCH TERMINOLOGY SQLITE BUILD

Vendors: 18
Libraries: 143
Instruments / Ensembles: 96
Articulations: 72
Variants: 31

Catalog entries: 487
Catalog articulations: 3,912
Catalog variants: 1,284

Foreign key check: OK
Integrity check: OK

Output:
dist/orch-terminology.db
```

If errors occur, report the exact source IDs and relationships involved.

---

# Error Handling

Example:

```text
SQLITE BUILD BLOCKED

catalog.json references unknown variant:

vendorId: spitfire-audio
libraryId: example-library
instrumentId: trumpet
articulationId: legato
variantId: agile

No canonical variant with ID "agile" exists.

Fix the canonical JSON or approve/add the terminology first.
SQLite database was not regenerated.
```

Do not automatically invent or insert the missing term.

---

# Schema Evolution

The generated SQLite schema may evolve over time.

When it changes:

- update the generator,
- update application queries as needed,
- update a schema version value,
- rebuild the database from canonical JSON.

Do not introduce Liquibase or migration history merely to preserve the generated DB unless a future runtime requirement genuinely needs in-place database upgrades.

Because SQLite is generated from canonical JSON, rebuilding from scratch is normally preferred over migrating old generated databases.

---

# Liquibase Policy

Liquibase is not the primary mechanism for terminology authoring.

Do not use Liquibase changelogs as the source of truth for terminology values.

Liquibase may become useful in the future only if the project moves to a persistent server-side relational database that must be upgraded in place.

For the current architecture:

```text
JSON = source of truth
SQLite = generated artifact
```

A deterministic generator is preferred over database migration scripts.

---

# Recommended Project Structure

One possible layout:

```text
data/
  vendors.json
  libraries.json
  instruments.json
  articulations.json
  variants.json
  catalog.json

schemas/
  vendors.schema.json
  libraries.schema.json
  instruments.schema.json
  articulations.schema.json
  variants.schema.json
  catalog.schema.json

scripts/
  validate_terminology.*
  build_sqlite.*

dist/
  orch-terminology.db

tests/
  ...
```

Use the repository's existing conventions if they differ.

Do not reorganize the project unnecessarily.

---

# Testing Requirements

Add automated tests for at least:

- duplicate canonical IDs,
- missing references,
- invalid library/vendor links,
- invalid catalog articulation references,
- invalid variant references,
- duplicate catalog entries,
- duplicate articulations,
- duplicate variants,
- successful SQLite generation,
- foreign-key integrity,
- key cascading-selector queries.

If practical, include a test that rebuilds the database twice from identical inputs and verifies logically identical contents.

---

# Final Principle

The database pipeline must preserve this separation:

```text
Canonical JSON
    = SINGLE SOURCE OF TRUTH FOR AUTHORING

Validation
    = quality gate

SQLite
    = SINGLE SOURCE OF TRUTH FOR ALL RUNTIME CONSUMERS
```

Never fix the generated database directly.

Never let SQLite-specific state become terminology truth.

When data changes:

> **Change JSON and rebuild.**

When validation fails:

> **Fix JSON and rebuild.**

When application queries need improvement:

> **Change the generator/schema/query layer, not the canonical terminology model unless the data model truly requires it.**
