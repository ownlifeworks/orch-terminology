from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import os
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_SOURCE_DIRNAME = "catalog"
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
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class CatalogBuildReport:
    source_files: int
    new_catalog_entries: int
    existing_entries_updated: int
    new_articulation_relationships: int
    new_variant_relationships: int
    duplicates_removed: int
    unresolved_references: tuple[str, ...]
    validation_errors: tuple[str, ...]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=Path(tempfile.gettempdir()),
        prefix=f".{path.stem}.",
        suffix=".tmp",
    ) as handle:
        handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        temp_path = Path(handle.name)
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        raise RuntimeError("PowerShell is required to write catalog files in this environment")
    command = (
        f"$content = Get-Content -Raw -LiteralPath '{str(temp_path)}'; "
        f"Set-Content -LiteralPath '{str(path)}' -Value $content -Encoding utf8; "
        f"Remove-Item -LiteralPath '{str(temp_path)}'"
    )
    subprocess.run([shell, "-NoProfile", "-Command", command], check=True)


def load_canonical_documents(data_dir: Path) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for kind, filename in DATA_FILENAMES.items():
        documents[kind] = load_json(data_dir / filename)
    return documents


def _load_catalog_sources(data_dir: Path) -> tuple[list[dict[str, Any]], tuple[str, ...], int]:
    source_dir = data_dir / CATALOG_SOURCE_DIRNAME
    if not source_dir.exists():
        return [], (), 0

    source_files = sorted(path for path in source_dir.rglob("*.json") if path.is_file())
    if not source_files:
        return [], (f"{CATALOG_SOURCE_DIRNAME}: no source JSON files found",), 0

    catalog: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in source_files:
        relative = path.relative_to(data_dir)
        payload = load_json(path)
        if not isinstance(payload, list):
            errors.append(f"{relative}: must be a JSON array")
            continue
        for index, entry in enumerate(payload):
            if not isinstance(entry, dict):
                errors.append(f"{relative}[{index}]: must be an object")
                continue
            catalog.append(entry)

    return catalog, tuple(errors), len(source_files)


def _entity_index(document: dict[str, Any], plural: str) -> dict[str, dict[str, Any]]:
    entities = document.get(plural, [])
    return {
        entity["id"]: entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("id"), str)
    }


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    articulations = []
    for articulation in sorted(entry["articulations"].items(), key=lambda item: item[0]):
        articulation_id, variant_ids = articulation
        articulations.append(
            {
                "articulationId": articulation_id,
                "variantIds": sorted(variant_ids),
            }
        )
    return {
        "vendorId": entry["vendorId"],
        "libraryId": entry["libraryId"],
        "instrumentId": entry["instrumentId"],
        "articulations": articulations,
    }


def _catalog_index(catalog: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in catalog:
        key = (entry["vendorId"], entry["libraryId"], entry["instrumentId"])
        bucket = index.setdefault(
            key,
            {
                "vendorId": entry["vendorId"],
                "libraryId": entry["libraryId"],
                "instrumentId": entry["instrumentId"],
                "articulations": defaultdict(set),
            },
        )
        for articulation in entry.get("articulations", []):
            bucket["articulations"][articulation["articulationId"]].update(articulation.get("variantIds", []))
    return index


def _catalog_index_to_list(index: dict[tuple[str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key in sorted(index):
        entry = index[key]
        items.append(_normalize_entry(entry))
    return items


def _validate_catalog_entry(
    entry: dict[str, Any],
    *,
    vendors: dict[str, dict[str, Any]],
    libraries: dict[str, dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    articulations: dict[str, dict[str, Any]],
    variants: dict[str, dict[str, Any]],
    seen_entries: set[tuple[str, str, str]],
    errors: list[str],
    prefix: str,
) -> None:
    vendor_id = entry.get("vendorId")
    library_id = entry.get("libraryId")
    instrument_id = entry.get("instrumentId")
    articulations_value = entry.get("articulations")

    if not isinstance(vendor_id, str) or not ID_RE.fullmatch(vendor_id):
        errors.append(f"{prefix}: invalid vendorId")
    elif vendor_id not in vendors:
        errors.append(f"{prefix}: unknown vendorId {vendor_id}")

    if not isinstance(library_id, str) or not ID_RE.fullmatch(library_id):
        errors.append(f"{prefix}: invalid libraryId")
    elif library_id not in libraries:
        errors.append(f"{prefix}: unknown libraryId {library_id}")
    elif isinstance(vendor_id, str) and vendor_id in vendors:
        library_vendor_id = libraries[library_id].get("vendorId")
        if library_vendor_id != vendor_id:
            errors.append(
                f"{prefix}: conflicting library/vendor relationship for {library_id}: "
                f"expected {library_vendor_id}, got {vendor_id}"
            )

    if not isinstance(instrument_id, str) or not ID_RE.fullmatch(instrument_id):
        errors.append(f"{prefix}: invalid instrumentId")
    elif instrument_id not in instruments:
        errors.append(f"{prefix}: unknown instrumentId {instrument_id}")

    key = (vendor_id, library_id, instrument_id)
    if key in seen_entries:
        errors.append(f"{prefix}: duplicate vendor/library/instrument tuple {key}")
    else:
        seen_entries.add(key)

    if not isinstance(articulations_value, list) or not articulations_value:
        errors.append(f"{prefix}: articulations must be a non-empty array")
        return

    seen_articulations: set[str] = set()
    for art_index, articulation in enumerate(articulations_value):
        art_prefix = f"{prefix}.articulations[{art_index}]"
        articulation_id = articulation.get("articulationId")
        variant_ids = articulation.get("variantIds")

        if not isinstance(articulation_id, str) or not ID_RE.fullmatch(articulation_id):
            errors.append(f"{art_prefix}: invalid articulationId")
        elif articulation_id not in articulations:
            errors.append(f"{art_prefix}: unknown articulationId {articulation_id}")
        elif articulation_id in seen_articulations:
            errors.append(f"{art_prefix}: duplicate articulationId {articulation_id}")
        else:
            seen_articulations.add(articulation_id)

        if not isinstance(variant_ids, list):
            errors.append(f"{art_prefix}: variantIds must be an array")
            continue

        seen_variants: set[str] = set()
        for variant_index, variant_id in enumerate(variant_ids):
            variant_prefix = f"{art_prefix}.variantIds[{variant_index}]"
            if not isinstance(variant_id, str) or not ID_RE.fullmatch(variant_id):
                errors.append(f"{variant_prefix}: invalid variantId")
            elif variant_id not in variants:
                errors.append(f"{variant_prefix}: unknown variantId {variant_id}")
            elif variant_id in seen_variants:
                errors.append(f"{art_prefix}: duplicate variantId {variant_id}")
            else:
                seen_variants.add(variant_id)

        if variant_ids != sorted(variant_ids):
            errors.append(f"{art_prefix}: variantIds must be sorted")


def _validate_catalog_payload(
    catalog: Any,
    *,
    vendors: dict[str, dict[str, Any]],
    libraries: dict[str, dict[str, Any]],
    instruments: dict[str, dict[str, Any]],
    articulations: dict[str, dict[str, Any]],
    variants: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(catalog, list):
        return ["catalog: must be a JSON array"]

    seen_entries: set[tuple[str, str, str]] = set()
    for index, entry in enumerate(catalog):
        if not isinstance(entry, dict):
            errors.append(f"catalog[{index}]: must be an object")
            continue
        _validate_catalog_entry(
            entry,
            vendors=vendors,
            libraries=libraries,
            instruments=instruments,
            articulations=articulations,
            variants=variants,
            seen_entries=seen_entries,
            errors=errors,
            prefix=f"catalog[{index}]",
        )

    if all(isinstance(entry, dict) for entry in catalog):
        sort_key = lambda item: (item.get("vendorId", ""), item.get("libraryId", ""), item.get("instrumentId", ""))
        if catalog != sorted(catalog, key=sort_key):
            errors.append("catalog: entries must be sorted by vendorId, libraryId, instrumentId")

    return errors


def validate_catalog_document(data_dir: Path) -> list[str]:
    documents = load_canonical_documents(data_dir)
    vendors = _entity_index(documents["vendor"], "vendors")
    libraries = _entity_index(documents["library"], "libraries")
    instruments = _entity_index(documents["instrument"], "instruments")
    articulations = _entity_index(documents["articulation"], "articulations")
    variants = _entity_index(documents["variant"], "variants")

    catalog_path = data_dir / "catalog.json"
    if not catalog_path.exists():
        return []

    catalog = load_json(catalog_path)
    return _validate_catalog_payload(
        catalog,
        vendors=vendors,
        libraries=libraries,
        instruments=instruments,
        articulations=articulations,
        variants=variants,
    )


def build_catalog_document(data_dir: Path) -> tuple[list[dict[str, Any]], CatalogBuildReport]:
    documents = load_canonical_documents(data_dir)
    vendors = _entity_index(documents["vendor"], "vendors")
    libraries = _entity_index(documents["library"], "libraries")
    instruments = _entity_index(documents["instrument"], "instruments")
    articulations = _entity_index(documents["articulation"], "articulations")
    variants = _entity_index(documents["variant"], "variants")

    validation_errors: list[str] = []
    source_catalog, source_errors, source_file_count = _load_catalog_sources(data_dir)
    validation_errors.extend(source_errors)
    if source_file_count:
        catalog_input = source_catalog
    else:
        existing_path = data_dir / "catalog.json"
        if not existing_path.exists():
            catalog_input = []
            validation_errors.append("catalog source directory is missing and catalog.json does not exist")
        else:
            catalog_input = load_json(existing_path)
            if not isinstance(catalog_input, list):
                validation_errors.append("catalog.json must be an array when present")
                catalog_input = []

    new_catalog_entries = 0
    existing_entries_updated = 0
    new_articulation_relationships = 0
    new_variant_relationships = 0
    duplicates_removed = 0

    merged_index = _catalog_index(catalog_input)
    catalog = _catalog_index_to_list(merged_index)
    new_catalog_entries = len(catalog)
    for entry in catalog:
        articulation_count = len(entry["articulations"])
        unique_articulation_count = len({item["articulationId"] for item in entry["articulations"]})
        duplicates_removed += articulation_count - unique_articulation_count
        for articulation in entry["articulations"]:
            unique_variant_count = len(set(articulation["variantIds"]))
            duplicates_removed += len(articulation["variantIds"]) - unique_variant_count
            new_variant_relationships += len(articulation["variantIds"])
        new_articulation_relationships += articulation_count

    validation_errors.extend(
        _validate_catalog_payload(
            catalog,
            vendors=vendors,
            libraries=libraries,
            instruments=instruments,
            articulations=articulations,
            variants=variants,
        )
    )

    report = CatalogBuildReport(
        source_files=source_file_count,
        new_catalog_entries=new_catalog_entries,
        existing_entries_updated=existing_entries_updated,
        new_articulation_relationships=new_articulation_relationships,
        new_variant_relationships=new_variant_relationships,
        duplicates_removed=duplicates_removed,
        unresolved_references=(),
        validation_errors=tuple(validation_errors),
    )
    return catalog, report
