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


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", value.lower().replace("_", " ").replace("-", " ")))


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


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
    instrument_icon_keys: dict[str, str] = {}
    for index, instrument in enumerate(entities["instrument"]):
        icon_key = instrument.get("iconKey")
        if isinstance(icon_key, str):
            if icon_key in instrument_icon_keys:
                errors.append(f"instrument: duplicate iconKey {icon_key}: {instrument_icon_keys[icon_key]} and {instrument.get('id')}")
            else:
                instrument_icon_keys[icon_key] = instrument.get("id", f"instrument[{index}]")
    for index, library in enumerate(entities["library"]):
        if library.get("vendorId") not in vendor_ids:
            errors.append(f"library[{index}]: unknown vendorId {library.get('vendorId')}")

    entity_ids = {kind: {item.get("id") for item in entries} for kind, entries in entities.items()}
    for index, library in enumerate(entities["library"]):
        for kind in ("instrument", "articulation"):
            for entity_id in library.get(f"{kind}Ids", []):
                if entity_id not in entity_ids[kind]:
                    errors.append(f"library[{index}]: unknown {kind}Id {entity_id}")
    errors.extend(validate_catalog_document(DATA))
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Terminology validation failed:")
        print("\n".join(f"- {problem}" for problem in problems))
        sys.exit(1)
    print("Terminology validation passed.")
