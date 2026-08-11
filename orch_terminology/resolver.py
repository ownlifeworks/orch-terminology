from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Iterable


KINDS = ("vendor", "library", "instrument", "articulation", "variant")
PLURALS = {
    "vendor": "vendors",
    "library": "libraries",
    "instrument": "instruments",
    "articulation": "articulations",
    "variant": "variants",
}
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)
_VELOCITY_RE = re.compile(r"^v(\d{1,3})$", re.IGNORECASE)


def normalize_text(value: str) -> str:
    """Normalize an alias without applying fuzzy or semantic matching."""
    if not isinstance(value, str):
        return ""
    return " ".join(_TOKEN_RE.findall(value.lower().replace("_", " ").replace("-", " ")))


def _tokens(value: str) -> list[str]:
    return normalize_text(value).split()


@dataclass(frozen=True)
class Resolution:
    status: str
    input: str
    entity: dict[str, Any] | None = None
    matches: tuple[dict[str, Any], ...] = ()


class TerminologyResolver:
    def __init__(self, data_directory: Path):
        self.data_directory = Path(data_directory)
        self._entities: dict[str, list[dict[str, Any]]] = {}
        self._contexts: list[dict[str, Any]] = []
        self._load()

    @classmethod
    def from_directory(cls, data_directory: str | Path) -> "TerminologyResolver":
        return cls(Path(data_directory))

    def _load(self) -> None:
        filenames = {
            "vendor": "vendors.json",
            "library": "libraries.json",
            "instrument": "instruments.json",
            "articulation": "articulations.json",
            "variant": "variants.json",
        }
        for kind, filename in filenames.items():
            document = json.loads((self.data_directory / filename).read_text(encoding="utf-8"))
            self._entities[kind] = list(document[PLURALS[kind]])

        context_file = self.data_directory / "contexts.json"
        if context_file.exists():
            self._contexts = list(json.loads(context_file.read_text(encoding="utf-8"))["contexts"])
        else:
            self._contexts = []

    def resolve_vendor(self, value: str) -> Resolution:
        return self._resolve_exact("vendor", value)

    def resolve_library(self, value: str) -> Resolution:
        result = self._resolve_exact("library", value)
        if result.status == "resolved":
            entity = dict(result.entity or {})
            vendor_id = entity.get("vendorId")
            if vendor_id:
                entity["vendor"] = self._entity_by_id("vendor", vendor_id)
            return Resolution(result.status, result.input, entity, result.matches)
        return result

    def resolve_instrument(self, value: str, context: str | dict[str, Any] | None = None) -> Resolution:
        return self._resolve_exact("instrument", value, context)

    def resolve_articulation(self, value: str, context: str | dict[str, Any] | None = None) -> Resolution:
        return self._resolve_exact("articulation", value, context)

    def resolve_variant(self, value: str, context: str | dict[str, Any] | None = None) -> Resolution:
        return self._resolve_exact("variant", value, context)

    def resolve_metadata(self, value: str, context: str | dict[str, Any] | None = None) -> dict[str, Any]:
        tokens = _tokens(value)
        velocity = None
        terminology_tokens = []
        for token in tokens:
            match = _VELOCITY_RE.match(token)
            if match:
                velocity = int(match.group(1))
            else:
                terminology_tokens.append(token)

        library_result, library_span = self._resolve_tokens("library", terminology_tokens, context)
        library = library_result.entity if library_result.status == "resolved" else None
        effective_context: str | dict[str, Any] | None = library or context
        vendor = None
        if library and library.get("vendorId"):
            vendor = self._entity_by_id("vendor", library["vendorId"])
        else:
            vendor_result, _ = self._resolve_tokens("vendor", terminology_tokens, context)
            if vendor_result.status == "resolved":
                vendor = vendor_result.entity

        remaining = [token for index, token in enumerate(terminology_tokens)
                     if library_span is None or not library_span[0] <= index < library_span[1]]
        instrument_result, instrument_span = self._resolve_tokens("instrument", remaining, effective_context)
        articulation_result, articulation_span = self._resolve_tokens("articulation", remaining, effective_context)
        used_indexes = set()
        if instrument_span is not None:
            used_indexes.update(range(instrument_span[0], instrument_span[1]))
        if articulation_span is not None:
            used_indexes.update(range(articulation_span[0], articulation_span[1]))
        variant_tokens = [token for index, token in enumerate(remaining) if index not in used_indexes]
        if variant_tokens:
            variant_result, _ = self._resolve_tokens("variant", variant_tokens, effective_context)
        else:
            variant_result = Resolution("absent", "")

        statuses = {
            "vendor": "resolved" if vendor else "unresolved",
            "library": library_result.status,
            "instrument": instrument_result.status,
            "articulation": articulation_result.status,
            "variant": variant_result.status,
        }
        required_statuses = [statuses["vendor"], statuses["library"], statuses["instrument"], statuses["articulation"]]
        return {
            "status": "ambiguous" if "ambiguous" in statuses.values() else
                      ("resolved" if all(status == "resolved" for status in required_statuses) and
                       variant_result.status in {"resolved", "absent"} else "partial"),
            "vendor": vendor,
            "library": library,
            "instrument": instrument_result.entity if instrument_result.status == "resolved" else None,
            "articulation": articulation_result.entity if articulation_result.status == "resolved" else None,
            "variant": variant_result.entity if variant_result.status == "resolved" else None,
            "velocity": velocity,
            "statuses": statuses,
        }

    def resolve_filename(self, filename: str, context: str | dict[str, Any] | None = None) -> dict[str, Any]:
        return self.resolve_metadata(Path(filename).stem, context)

    def _resolve_exact(self, kind: str, value: str, context: str | dict[str, Any] | None = None) -> Resolution:
        normalized = normalize_text(value)
        candidates = self._candidates(kind, normalized, context)
        return self._make_resolution(value, candidates)

    def _resolve_tokens(self, kind: str, tokens: list[str], context: str | dict[str, Any] | None) -> tuple[Resolution, tuple[int, int] | None]:
        matches: list[tuple[int, int, dict[str, Any]]] = []
        for start in range(len(tokens)):
            for end in range(len(tokens), start, -1):
                normalized = " ".join(tokens[start:end])
                candidates = self._candidates(kind, normalized, context)
                for candidate in candidates:
                    matches.append((start, end, candidate))

        if not matches:
            return Resolution("unresolved", " ".join(tokens)), None

        longest = max(end - start for start, end, _ in matches)
        longest_matches = [(start, end, entity) for start, end, entity in matches if end - start == longest]
        unique = {entity["id"]: (start, end, entity) for start, end, entity in longest_matches}
        result = self._make_resolution(" ".join(tokens), [item[2] for item in unique.values()])
        if result.status == "resolved":
            item = next(iter(unique.values()))
            return result, (item[0], item[1])
        return result, None

    def _candidates(self, kind: str, normalized: str, context: str | dict[str, Any] | None) -> list[dict[str, Any]]:
        if not normalized:
            return []

        contextual = self._context_aliases(kind, context)
        if normalized in contextual:
            ids = contextual[normalized]
            return [self._entity_by_id(kind, entity_id) for entity_id in ids]

        candidates = []
        for entity in self._entities[kind]:
            aliases = {entity["id"], entity["name"], *entity.get("aliases", [])}
            if normalized in {normalize_text(alias) for alias in aliases}:
                candidates.append(entity)
        return candidates

    def _context_aliases(self, kind: str, context: str | dict[str, Any] | None) -> dict[str, list[str]]:
        if context is None:
            return {}
        context_id = context.get("id") if isinstance(context, dict) else context
        selected = next((item for item in self._contexts if item.get("libraryId") == context_id), None)
        if selected is None:
            return {}
        aliases = selected.get(f"{kind}Aliases", {})
        return {normalize_text(alias): ([target] if isinstance(target, str) else list(target))
                for alias, target in aliases.items()}

    def _entity_by_id(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        return next((entity for entity in self._entities[kind] if entity["id"] == entity_id), None)

    @staticmethod
    def _make_resolution(value: str, candidates: Iterable[dict[str, Any]]) -> Resolution:
        unique = {candidate["id"]: candidate for candidate in candidates if candidate is not None}
        if not unique:
            return Resolution("unresolved", value)
        if len(unique) > 1:
            return Resolution("ambiguous", value, matches=tuple(unique.values()))
        return Resolution("resolved", value, entity=next(iter(unique.values())))
