from __future__ import annotations

from dataclasses import dataclass
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_FILENAMES = {
    "vendor": "vendors.json",
    "library": "libraries.json",
    "instrument": "instruments.json",
    "articulation": "articulations.json",
    "variant": "variants.json",
}
PLURALS = {
    "vendor": "vendors",
    "library": "libraries",
    "instrument": "instruments",
    "articulation": "articulations",
    "variant": "variants",
}
SOURCE_FILES = [
    "vendors.json",
    "libraries.json",
    "instruments.json",
    "instrument-properties.json",
    "articulations.json",
    "variants.json",
    "catalog.json",
    "schema-version.json",
]


@dataclass(frozen=True)
class BuildReport:
    vendors: int
    libraries: int
    instruments: int
    instrument_properties: int
    instrument_loudness_targets: int
    articulations: int
    variants: int
    catalog_entries: int
    catalog_articulations: int
    catalog_variants: int


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def entity_items(document: dict[str, Any], plural: str) -> list[dict[str, Any]]:
    items = document.get(plural, [])
    if not isinstance(items, list):
        raise ValueError(f"{plural}: expected an array")
    return [item for item in items if isinstance(item, dict)]


def index_entities(document: dict[str, Any], plural: str) -> dict[str, dict[str, Any]]:
    items = entity_items(document, plural)
    index: dict[str, dict[str, Any]] = {}
    for item in items:
        entity_id = item.get("id")
        if isinstance(entity_id, str):
            if entity_id in index:
                raise ValueError(f"duplicate {plural[:-1]} id: {entity_id}")
            index[entity_id] = item
    return index


def sorted_aliases(entity: dict[str, Any]) -> list[str]:
    aliases = entity.get("aliases", [])
    if not isinstance(aliases, list):
        raise ValueError(f"{entity.get('id', '<unknown>')}: aliases must be an array")
    if any(not isinstance(alias, str) for alias in aliases):
        raise ValueError(f"{entity.get('id', '<unknown>')}: aliases must contain strings only")
    return sorted({alias for alias in aliases if alias})


def normalize_catalog(catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in catalog:
        articulations = entry.get("articulations", [])
        if not isinstance(articulations, list):
            raise ValueError("catalog entry articulations must be an array")
        art_rows = []
        for articulation in articulations:
            articulation_id = articulation.get("articulationId")
            variant_ids = articulation.get("variantIds", [])
            if not isinstance(articulation_id, str):
                raise ValueError("catalog articulation missing articulationId")
            if not isinstance(variant_ids, list):
                raise ValueError("catalog articulation variantIds must be an array")
            art_rows.append(
                {
                    "articulationId": articulation_id,
                    "variantIds": sorted({variant_id for variant_id in variant_ids if isinstance(variant_id, str)}),
                }
            )
        normalized.append(
            {
                "vendorId": entry["vendorId"],
                "libraryId": entry["libraryId"],
                "instrumentId": entry["instrumentId"],
                "articulations": sorted(art_rows, key=lambda item: item["articulationId"]),
            }
        )
    return sorted(normalized, key=lambda item: (item["vendorId"], item["libraryId"], item["instrumentId"]))


def validate_sources(
    vendors: dict[str, dict[str, Any]],
    libraries: dict[str, dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    articulations: dict[str, dict[str, Any]],
    variants: dict[str, dict[str, Any]],
    catalog: list[dict[str, Any]],
) -> None:
    for library_id, library in libraries.items():
        vendor_id = library.get("vendorId")
        if vendor_id not in vendors:
            raise ValueError(f"library {library_id} references unknown vendorId {vendor_id}")

    seen_entries: set[tuple[str, str, str]] = set()
    for entry in catalog:
        vendor_id = entry.get("vendorId")
        library_id = entry.get("libraryId")
        instrument_id = entry.get("instrumentId")
        articulations_value = entry.get("articulations", [])

        if vendor_id not in vendors:
            raise ValueError(f"catalog entry references unknown vendorId {vendor_id}")
        if library_id not in libraries:
            raise ValueError(f"catalog entry references unknown libraryId {library_id}")
        if instrument_id not in instruments:
            raise ValueError(f"catalog entry references unknown instrumentId {instrument_id}")
        if libraries[library_id].get("vendorId") != vendor_id:
            raise ValueError(f"catalog entry {vendor_id}/{library_id}/{instrument_id} has mismatched vendor/library relationship")

        key = (vendor_id, library_id, instrument_id)
        if key in seen_entries:
            raise ValueError(f"duplicate catalog entry {key}")
        seen_entries.add(key)

        seen_articulations: set[str] = set()
        if not articulations_value:
            raise ValueError(f"catalog entry {key} must contain at least one articulation")
        for articulation in articulations_value:
            articulation_id = articulation.get("articulationId")
            variant_ids = articulation.get("variantIds", [])
            if articulation_id not in articulations:
                raise ValueError(f"catalog entry {key} references unknown articulationId {articulation_id}")
            if articulation_id in seen_articulations:
                raise ValueError(f"catalog entry {key} contains duplicate articulationId {articulation_id}")
            seen_articulations.add(articulation_id)

            seen_variants: set[str] = set()
            for variant_id in variant_ids:
                if variant_id not in variants:
                    raise ValueError(f"catalog entry {key} references unknown variantId {variant_id}")
                if variant_id in seen_variants:
                    raise ValueError(f"catalog entry {key} contains duplicate variantId {variant_id}")
                seen_variants.add(variant_id)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_database(data_dir: Path, output_path: Path) -> BuildReport:
    documents = {
        kind: load_json(data_dir / filename)
        for kind, filename in DATA_FILENAMES.items()
    }
    schema_version_doc = load_json(data_dir / "schema-version.json")
    instrument_properties_doc = load_json(data_dir / "instrument-properties.json")
    catalog = load_json(data_dir / "catalog.json")

    vendors = index_entities(documents["vendor"], "vendors")
    libraries = index_entities(documents["library"], "libraries")
    instruments = index_entities(documents["instrument"], "instruments")
    articulations = index_entities(documents["articulation"], "articulations")
    variants = index_entities(documents["variant"], "variants")

    if not isinstance(catalog, list):
        raise ValueError("catalog.json must be an array")

    normalized_catalog = normalize_catalog(catalog)
    validate_sources(vendors, libraries, instruments, articulations, variants, normalized_catalog)

    loudness_reference = instrument_properties_doc.get("loudnessReference", {})
    instrument_properties = instrument_properties_doc.get("instruments", {})
    if not isinstance(loudness_reference, dict):
        raise ValueError("instrument-properties.json: loudnessReference must be an object")
    if not isinstance(instrument_properties, dict):
        raise ValueError("instrument-properties.json: instruments must be an object")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    connection = sqlite3.connect(output_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.executescript(
            """
            CREATE TABLE schema_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE vendors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE vendor_aliases (
                vendor_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                PRIMARY KEY (vendor_id, alias),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id)
            );

            CREATE TABLE libraries (
                id TEXT PRIMARY KEY,
                vendor_id TEXT NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id)
            );

            CREATE TABLE library_aliases (
                library_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                PRIMARY KEY (library_id, alias),
                FOREIGN KEY (library_id) REFERENCES libraries(id)
            );

            CREATE TABLE instruments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                icon_key TEXT
            );

            CREATE TABLE instrument_aliases (
                instrument_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                PRIMARY KEY (instrument_id, alias),
                FOREIGN KEY (instrument_id) REFERENCES instruments(id)
            );

            CREATE TABLE loudness_reference_info (
                version INTEGER NOT NULL,
                unit TEXT NOT NULL
            );

            CREATE TABLE loudness_reference_dynamic_anchors (
                anchor TEXT PRIMARY KEY,
                sort_order INTEGER NOT NULL UNIQUE
            );

            CREATE TABLE instrument_properties (
                instrument_id TEXT PRIMARY KEY,
                range_min INTEGER NOT NULL,
                range_max INTEGER NOT NULL,
                measurement_range_min INTEGER NOT NULL,
                measurement_range_max INTEGER NOT NULL,
                FOREIGN KEY (instrument_id) REFERENCES instruments(id)
            );

            CREATE TABLE instrument_loudness_targets (
                instrument_id TEXT NOT NULL,
                capture_kind TEXT NOT NULL,
                dynamic_anchor TEXT NOT NULL,
                lufs REAL NOT NULL,
                PRIMARY KEY (instrument_id, capture_kind, dynamic_anchor),
                FOREIGN KEY (instrument_id) REFERENCES instruments(id),
                FOREIGN KEY (dynamic_anchor) REFERENCES loudness_reference_dynamic_anchors(anchor)
            );

            CREATE TABLE articulations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE articulation_aliases (
                articulation_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                PRIMARY KEY (articulation_id, alias),
                FOREIGN KEY (articulation_id) REFERENCES articulations(id)
            );

            CREATE TABLE variants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE variant_aliases (
                variant_id TEXT NOT NULL,
                alias TEXT NOT NULL,
                PRIMARY KEY (variant_id, alias),
                FOREIGN KEY (variant_id) REFERENCES variants(id)
            );

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

            CREATE TABLE catalog_articulations (
                id INTEGER PRIMARY KEY,
                catalog_entry_id INTEGER NOT NULL,
                articulation_id TEXT NOT NULL,
                UNIQUE (catalog_entry_id, articulation_id),
                FOREIGN KEY (catalog_entry_id) REFERENCES catalog_entries(id),
                FOREIGN KEY (articulation_id) REFERENCES articulations(id)
            );

            CREATE TABLE catalog_variants (
                catalog_articulation_id INTEGER NOT NULL,
                variant_id TEXT NOT NULL,
                PRIMARY KEY (catalog_articulation_id, variant_id),
                FOREIGN KEY (catalog_articulation_id) REFERENCES catalog_articulations(id),
                FOREIGN KEY (variant_id) REFERENCES variants(id)
            );

            CREATE INDEX idx_libraries_vendor ON libraries(vendor_id);
            CREATE INDEX idx_catalog_vendor ON catalog_entries(vendor_id);
            CREATE INDEX idx_catalog_library ON catalog_entries(library_id);
            CREATE INDEX idx_catalog_instrument ON catalog_entries(instrument_id);
            CREATE INDEX idx_catalog_articulation ON catalog_articulations(articulation_id);
            CREATE INDEX idx_catalog_variant ON catalog_variants(variant_id);
            CREATE INDEX idx_instrument_loudness_targets_instrument ON instrument_loudness_targets(instrument_id);
            """
        )

        def insert_entities(table: str, entities: dict[str, dict[str, Any]]) -> None:
            for entity_id in sorted(entities):
                entity = entities[entity_id]
                if table == "vendors":
                    connection.execute("INSERT INTO vendors (id, name) VALUES (?, ?)", (entity_id, entity["name"]))
                elif table == "libraries":
                    connection.execute(
                        "INSERT INTO libraries (id, vendor_id, name) VALUES (?, ?, ?)",
                        (entity_id, entity["vendorId"], entity["name"]),
                    )
                elif table == "instruments":
                    connection.execute(
                        "INSERT INTO instruments (id, name, icon_key) VALUES (?, ?, ?)",
                        (entity_id, entity["name"], entity.get("iconKey")),
                    )
                elif table == "articulations":
                    connection.execute("INSERT INTO articulations (id, name) VALUES (?, ?)", (entity_id, entity["name"]))
                elif table == "variants":
                    connection.execute("INSERT INTO variants (id, name) VALUES (?, ?)", (entity_id, entity["name"]))
                else:
                    raise ValueError(f"unknown entity table: {table}")
                for alias in sorted_aliases(entity):
                    connection.execute(
                        {
                            "vendors": "INSERT INTO vendor_aliases (vendor_id, alias) VALUES (?, ?)",
                            "libraries": "INSERT INTO library_aliases (library_id, alias) VALUES (?, ?)",
                            "instruments": "INSERT INTO instrument_aliases (instrument_id, alias) VALUES (?, ?)",
                            "articulations": "INSERT INTO articulation_aliases (articulation_id, alias) VALUES (?, ?)",
                            "variants": "INSERT INTO variant_aliases (variant_id, alias) VALUES (?, ?)",
                        }[table],
                        (entity_id, alias),
                    )

        insert_entities("vendors", vendors)
        insert_entities("libraries", libraries)
        insert_entities("instruments", instruments)
        dynamic_anchors = loudness_reference.get("dynamicAnchors", [])
        if not isinstance(dynamic_anchors, list):
            raise ValueError("instrument-properties.json: loudnessReference.dynamicAnchors must be an array")
        connection.execute(
            "INSERT INTO loudness_reference_info (version, unit) VALUES (?, ?)",
            (int(loudness_reference.get("version", 0)), str(loudness_reference.get("unit", ""))),
        )
        for sort_order, anchor in enumerate(dynamic_anchors):
            if not isinstance(anchor, str):
                raise ValueError("instrument-properties.json: dynamic anchors must be strings")
            connection.execute(
                "INSERT INTO loudness_reference_dynamic_anchors (anchor, sort_order) VALUES (?, ?)",
                (anchor, sort_order),
            )
        for instrument_id in sorted(instrument_properties):
            properties = instrument_properties[instrument_id]
            if instrument_id not in instruments:
                raise ValueError(f"instrument-properties.json references unknown instrument id: {instrument_id}")
            if not isinstance(properties, dict):
                raise ValueError(f"instrument-properties.json: {instrument_id} must be an object")

            pitch = properties.get("pitch", {})
            full_range = pitch.get("range", {}) if isinstance(pitch, dict) else {}
            measurement_range = pitch.get("measurementRange", {}) if isinstance(pitch, dict) else {}
            if not isinstance(full_range, dict) or not isinstance(measurement_range, dict):
                raise ValueError(f"instrument-properties.json: {instrument_id}.pitch ranges must be objects")

            connection.execute(
                """
                INSERT INTO instrument_properties (
                    instrument_id,
                    range_min,
                    range_max,
                    measurement_range_min,
                    measurement_range_max
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    instrument_id,
                    int(full_range["min"]),
                    int(full_range["max"]),
                    int(measurement_range["min"]),
                    int(measurement_range["max"]),
                ),
            )

            loudness = properties.get("loudness", {})
            if not isinstance(loudness, dict):
                raise ValueError(f"instrument-properties.json: {instrument_id}.loudness must be an object")
            for capture_kind in ("long", "short"):
                targets = loudness.get(capture_kind)
                if not isinstance(targets, dict):
                    raise ValueError(f"instrument-properties.json: {instrument_id}.loudness.{capture_kind} must be an object")
                for anchor in dynamic_anchors:
                    if anchor not in targets:
                        raise ValueError(f"instrument-properties.json: {instrument_id}.loudness.{capture_kind} missing {anchor}")
                    connection.execute(
                        """
                        INSERT INTO instrument_loudness_targets (
                            instrument_id,
                            capture_kind,
                            dynamic_anchor,
                            lufs
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (instrument_id, capture_kind, anchor, float(targets[anchor])),
                    )
        insert_entities("articulations", articulations)
        insert_entities("variants", variants)

        catalog_entry_id = 0
        catalog_articulation_id = 0
        for entry in normalized_catalog:
            cursor = connection.execute(
                "INSERT INTO catalog_entries (vendor_id, library_id, instrument_id) VALUES (?, ?, ?)",
                (entry["vendorId"], entry["libraryId"], entry["instrumentId"]),
            )
            catalog_entry_id = cursor.lastrowid
            for articulation in entry["articulations"]:
                cursor = connection.execute(
                    "INSERT INTO catalog_articulations (catalog_entry_id, articulation_id) VALUES (?, ?)",
                    (catalog_entry_id, articulation["articulationId"]),
                )
                catalog_articulation_id = cursor.lastrowid
                for variant_id in articulation["variantIds"]:
                    connection.execute(
                        "INSERT INTO catalog_variants (catalog_articulation_id, variant_id) VALUES (?, ?)",
                        (catalog_articulation_id, variant_id),
                    )

        source_hashes = {filename: sha256_of(data_dir / filename) for filename in SOURCE_FILES if (data_dir / filename).exists()}
        connection.executemany(
            "INSERT INTO schema_info (key, value) VALUES (?, ?)",
            [
                ("schema_version", str(schema_version_doc.get("schemaVersion", ""))),
                ("source_format", "canonical-json"),
                ("source_files", ",".join(sorted(source_hashes))),
                ("source_hashes", json.dumps(source_hashes, sort_keys=True)),
                ("generator", "tools/build_sqlite.py"),
            ],
        )

        connection.commit()

        foreign_key_errors = connection.execute("PRAGMA foreign_key_check;").fetchall()
        if foreign_key_errors:
            raise ValueError(f"foreign_key_check failed: {foreign_key_errors[:5]}")
        integrity_result = connection.execute("PRAGMA integrity_check;").fetchone()
        if not integrity_result or integrity_result[0] != "ok":
            raise ValueError(f"integrity_check failed: {integrity_result}")

        report = BuildReport(
            vendors=connection.execute("SELECT COUNT(*) FROM vendors").fetchone()[0],
            libraries=connection.execute("SELECT COUNT(*) FROM libraries").fetchone()[0],
            instruments=connection.execute("SELECT COUNT(*) FROM instruments").fetchone()[0],
            instrument_properties=connection.execute("SELECT COUNT(*) FROM instrument_properties").fetchone()[0],
            instrument_loudness_targets=connection.execute("SELECT COUNT(*) FROM instrument_loudness_targets").fetchone()[0],
            articulations=connection.execute("SELECT COUNT(*) FROM articulations").fetchone()[0],
            variants=connection.execute("SELECT COUNT(*) FROM variants").fetchone()[0],
            catalog_entries=connection.execute("SELECT COUNT(*) FROM catalog_entries").fetchone()[0],
            catalog_articulations=connection.execute("SELECT COUNT(*) FROM catalog_articulations").fetchone()[0],
            catalog_variants=connection.execute("SELECT COUNT(*) FROM catalog_variants").fetchone()[0],
        )
    finally:
        connection.close()

    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build orch-terminology.db from canonical JSON.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "orch.db")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    temp_output = args.output.with_suffix(args.output.suffix + ".tmp")
    if temp_output.exists():
        temp_output.unlink()

    try:
        report = build_database(args.data_dir, temp_output)
    except Exception as exc:
        if temp_output.exists():
            temp_output.unlink()
        print("SQLITE BUILD BLOCKED")
        print(str(exc))
        return 1

    shutil.move(str(temp_output), str(args.output))
    print("ORCH TERMINOLOGY SQLITE BUILD")
    print(f"Vendors: {report.vendors}")
    print(f"Libraries: {report.libraries}")
    print(f"Instruments: {report.instruments}")
    print(f"Instrument properties: {report.instrument_properties}")
    print(f"Instrument loudness targets: {report.instrument_loudness_targets}")
    print(f"Articulations: {report.articulations}")
    print(f"Variants: {report.variants}")
    print(f"Catalog entries: {report.catalog_entries}")
    print(f"Catalog articulations: {report.catalog_articulations}")
    print(f"Catalog variants: {report.catalog_variants}")
    print("Foreign key check: OK")
    print("Integrity check: OK")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
