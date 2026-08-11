from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orch_terminology.catalog import build_catalog_document, dump_json  # noqa: E402


def main() -> int:
    data_dir = ROOT / "data"
    catalog, report = build_catalog_document(data_dir)
    if report.validation_errors:
        print("CATALOG BUILD BLOCKED")
        print("\n".join(f"- {error}" for error in report.validation_errors))
        return 1

    dump_json(data_dir / "catalog.json", catalog)
    print("CATALOG UPDATE REVIEW")
    print(f"New catalog entries: {report.new_catalog_entries}")
    print(f"Existing entries updated: {report.existing_entries_updated}")
    print(f"New articulation relationships: {report.new_articulation_relationships}")
    print(f"New variant relationships: {report.new_variant_relationships}")
    print(f"Duplicates removed: {report.duplicates_removed}")
    print(f"Unresolved references: {len(report.unresolved_references)}")
    print("Validation errors: 0")
    print(f"Output: {data_dir / 'catalog.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
