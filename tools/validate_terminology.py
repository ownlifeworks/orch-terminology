from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orch_terminology.catalog import validate_catalog_document  # noqa: E402
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KINDS = ("vendor", "library", "instrument", "articulation", "variant")
PLURALS = {
    "vendor": "vendors",
    "library": "libraries",
    "instrument": "instruments",
    "articulation": "articulations",
    "variant": "variants",
}
LOUDNESS_CAPTURE_KINDS = ("long", "short")
EXPECTED_DYNAMIC_ANCHORS = ("pp", "mf", "fff")


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", value.lower().replace("_", " ").replace("-", " ")))


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def validate_midi_range(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: expected an object")
        return

    minimum = value.get("min")
    maximum = value.get("max")

    if not isinstance(minimum, int) or not isinstance(maximum, int):
        errors.append(f"{prefix}: min and max must be integers")
        return

    if minimum < 0 or minimum > 127 or maximum < 0 or maximum > 127:
        errors.append(f"{prefix}: min and max must be within MIDI note range 0-127")
        return

    if minimum > maximum:
        errors.append(f"{prefix}: min must not exceed max")


def validate_instrument_properties(instrument_ids: set[str]) -> list[str]:
    errors: list[str] = []
    document = load("instrument-properties.json")

    if document.get("schemaVersion") != 1:
        errors.append("instrument-properties: schemaVersion must be 1")

    loudness_reference = document.get("loudnessReference")
    if not isinstance(loudness_reference, dict):
        errors.append("instrument-properties: loudnessReference is required")
    else:
        if loudness_reference.get("version") != 1:
            errors.append("instrument-properties: loudnessReference.version must be 1")
        if loudness_reference.get("unit") != "LUFS":
            errors.append("instrument-properties: loudnessReference.unit must be LUFS")
        if loudness_reference.get("dynamicAnchors") != list(EXPECTED_DYNAMIC_ANCHORS):
            errors.append("instrument-properties: dynamicAnchors must be ['pp', 'mf', 'fff']")

    instruments = document.get("instruments")
    if not isinstance(instruments, dict):
        errors.append("instrument-properties: instruments must be an object keyed by instrument id")
        return errors

    for instrument_id, properties in instruments.items():
        prefix = f"instrument-properties[{instrument_id}]"

        if instrument_id not in instrument_ids:
            errors.append(f"{prefix}: unknown instrument id")
            continue

        if not isinstance(properties, dict):
            errors.append(f"{prefix}: expected an object")
            continue

        pitch = properties.get("pitch")
        if not isinstance(pitch, dict):
            errors.append(f"{prefix}.pitch: expected an object")
        else:
            validate_midi_range(pitch.get("range"), f"{prefix}.pitch.range", errors)
            validate_midi_range(pitch.get("measurementRange"), f"{prefix}.pitch.measurementRange", errors)

            full_range = pitch.get("range")
            measurement_range = pitch.get("measurementRange")
            if isinstance(full_range, dict) and isinstance(measurement_range, dict):
                full_min = full_range.get("min")
                full_max = full_range.get("max")
                measurement_min = measurement_range.get("min")
                measurement_max = measurement_range.get("max")

                if all(isinstance(value, int) for value in (full_min, full_max, measurement_min, measurement_max)):
                    if measurement_min < full_min or measurement_max > full_max:
                        errors.append(f"{prefix}.pitch.measurementRange: must be contained within pitch.range")

        loudness = properties.get("loudness")
        if not isinstance(loudness, dict):
            errors.append(f"{prefix}.loudness: expected an object")
            continue

        for capture_kind in LOUDNESS_CAPTURE_KINDS:
            targets = loudness.get(capture_kind)
            if not isinstance(targets, dict):
                errors.append(f"{prefix}.loudness.{capture_kind}: expected an object")
                continue

            if set(targets.keys()) != set(EXPECTED_DYNAMIC_ANCHORS):
                errors.append(f"{prefix}.loudness.{capture_kind}: keys must be pp, mf, fff")

            for anchor in EXPECTED_DYNAMIC_ANCHORS:
                if not isinstance(targets.get(anchor), (int, float)):
                    errors.append(f"{prefix}.loudness.{capture_kind}.{anchor}: must be numeric")

    return errors


def validate() -> list[str]:
    errors: list[str] = []
    entities: dict[str, list[dict]] = {}
    for kind in KINDS:
        document = load(f"{PLURALS[kind]}.json")
        entries = document.get(PLURALS[kind])
        entities[kind] = entries if isinstance(entries, list) else []
        if document.get("schemaVersion") != 1:
            errors.append(f"{kind}: schemaVersion must be 1")
        seen_ids: set[str] = set()
        aliases: dict[str, str] = {}
        for index, entity in enumerate(entities[kind]):
            prefix = f"{kind}[{index}]"
            entity_id = entity.get("id")
            if not isinstance(entity_id, str) or not ID_RE.fullmatch(entity_id):
                errors.append(f"{prefix}: invalid id")
            elif entity_id in seen_ids:
                errors.append(f"{prefix}: duplicate id {entity_id}")
            seen_ids.add(entity_id)
            if not isinstance(entity.get("name"), str) or not entity["name"].strip():
                errors.append(f"{prefix}: name is required")
            if kind == "instrument" and not isinstance(entity.get("iconKey"), str):
                errors.append(f"{prefix}: iconKey is required")
            raw_aliases = [entity.get("name", ""), entity.get("id", ""), *entity.get("aliases", [])]
            for alias in raw_aliases:
                key = normalized(alias) if isinstance(alias, str) else ""
                if not key:
                    errors.append(f"{prefix}: empty alias")
                elif key in aliases and aliases[key] != entity_id:
                    errors.append(f"{kind}: alias collision for {key}: {aliases[key]} and {entity_id}")
                else:
                    aliases[key] = entity_id

    vendor_ids = {item.get("id") for item in entities["vendor"]}
    for index, library in enumerate(entities["library"]):
        if library.get("vendorId") not in vendor_ids:
            errors.append(f"library[{index}]: unknown vendorId {library.get('vendorId')}")

    entity_ids = {kind: {item.get("id") for item in entries} for kind, entries in entities.items()}
    for index, library in enumerate(entities["library"]):
        for kind in ("instrument", "articulation"):
            for entity_id in library.get(f"{kind}Ids", []):
                if entity_id not in entity_ids[kind]:
                    errors.append(f"library[{index}]: unknown {kind}Id {entity_id}")
    errors.extend(validate_instrument_properties(entity_ids["instrument"]))
    errors.extend(validate_catalog_document(DATA))
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Terminology validation failed:")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Terminology validation passed.")
