from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from orch_terminology.catalog import build_catalog_document, dump_json, validate_catalog_document


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"

    def test_build_catalog_from_repository_data(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)
        self.assertEqual(catalog, sorted(catalog, key=lambda item: (item["vendorId"], item["libraryId"], item["instrumentId"])))
        for entry in catalog:
            self.assertIn("articulations", entry)
            self.assertGreater(len(entry["articulations"]), 0)
            self.assertEqual(
                entry["articulations"],
                sorted(entry["articulations"], key=lambda item: item["articulationId"]),
            )

    def test_catalog_validation_rejects_unknown_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for filename in [
                "vendors.json",
                "libraries.json",
                "instruments.json",
                "articulations.json",
                "variants.json",
                "catalog.json",
            ]:
                dump_json(tmp_path / filename, json.loads((self.data_dir / filename).read_text(encoding="utf-8")))

            dump_json(
                tmp_path / "catalog.json",
                [
                    {
                        "vendorId": "spitfire-audio",
                        "libraryId": "bbcso",
                        "instrumentId": "trumpet",
                        "articulations": [
                            {"articulationId": "legato", "variantIds": ["unknown-variant"]}
                        ],
                    }
                ],
            )
            errors = validate_catalog_document(tmp_path)
            self.assertTrue(any("unknown variantId" in error for error in errors))

    def test_catalog_validation_rejects_duplicate_tuples(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for filename in [
                "vendors.json",
                "libraries.json",
                "instruments.json",
                "articulations.json",
                "variants.json",
                "catalog.json",
            ]:
                dump_json(tmp_path / filename, json.loads((self.data_dir / filename).read_text(encoding="utf-8")))

            dump_json(
                tmp_path / "catalog.json",
                [
                    {
                        "vendorId": "spitfire-audio",
                        "libraryId": "bbcso",
                        "instrumentId": "trumpet",
                        "articulations": [
                            {"articulationId": "legato", "variantIds": []}
                        ],
                    },
                    {
                        "vendorId": "spitfire-audio",
                        "libraryId": "bbcso",
                        "instrumentId": "trumpet",
                        "articulations": [
                            {"articulationId": "staccato", "variantIds": []}
                        ],
                    },
                ],
            )
            errors = validate_catalog_document(tmp_path)
            self.assertTrue(any("duplicate vendor/library/instrument tuple" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
