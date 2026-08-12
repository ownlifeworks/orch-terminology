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

    def test_vsl_synchron_prime_woodwinds_catalog_entry(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)

        flute_entry = next(
            entry
            for entry in catalog
            if entry["vendorId"] == "vienna-symphonic-library"
            and entry["libraryId"] == "synchron-prime-woodwinds"
            and entry["instrumentId"] == "flute"
        )

        self.assertEqual(
            flute_entry["articulations"],
            [
                {"articulationId": "legato", "variantIds": ["performance", "vibrato"]},
                {"articulationId": "long", "variantIds": ["non-vibrato", "vibrato"]},
                {"articulationId": "portato", "variantIds": ["bold", "rapid"]},
                {"articulationId": "sforzando", "variantIds": ["non-vibrato", "vibrato"]},
                {"articulationId": "sforzatissimo", "variantIds": ["non-vibrato", "vibrato"]},
                {"articulationId": "staccato", "variantIds": ["bold", "rapid"]},
            ],
        )

    def test_vsl_synchron_prime_strings_1_catalog_entry(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)

        ensemble_entry = next(
            entry
            for entry in catalog
            if entry["vendorId"] == "vienna-symphonic-library"
            and entry["libraryId"] == "synchron-prime-strings-1"
            and entry["instrumentId"] == "strings-ensemble"
        )

        self.assertEqual(
            ensemble_entry["articulations"],
            [
                {"articulationId": "bartok", "variantIds": []},
                {"articulationId": "legato", "variantIds": ["soft"]},
                {"articulationId": "long", "variantIds": ["soft"]},
                {"articulationId": "marcato", "variantIds": []},
                {"articulationId": "pizzicato", "variantIds": []},
                {"articulationId": "sforzando", "variantIds": []},
                {"articulationId": "staccato", "variantIds": ["bold", "rapid"]},
                {"articulationId": "tremolo", "variantIds": []},
            ],
        )

    def test_vsl_synchron_prime_strings_2_catalog_entry(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)

        ensemble_entry = next(
            entry
            for entry in catalog
            if entry["vendorId"] == "vienna-symphonic-library"
            and entry["libraryId"] == "synchron-prime-strings-2"
            and entry["instrumentId"] == "strings-ensemble"
        )

        self.assertEqual(
            ensemble_entry["articulations"],
            [
                {"articulationId": "bartok", "variantIds": []},
                {"articulationId": "legato", "variantIds": ["soft"]},
                {"articulationId": "long", "variantIds": ["soft"]},
                {"articulationId": "marcato", "variantIds": []},
                {"articulationId": "pizzicato", "variantIds": []},
                {"articulationId": "sforzando", "variantIds": []},
                {"articulationId": "staccato", "variantIds": ["bold", "rapid"]},
                {"articulationId": "tremolo", "variantIds": []},
            ],
        )

    def test_vsl_synchron_prime_brass_catalog_entry(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)

        trumpet_entry = next(
            entry
            for entry in catalog
            if entry["vendorId"] == "vienna-symphonic-library"
            and entry["libraryId"] == "synchron-prime-brass"
            and entry["instrumentId"] == "trumpet"
        )

        self.assertEqual(
            trumpet_entry["articulations"],
            [
                {"articulationId": "legato", "variantIds": ["non-vibrato", "vibrato"]},
                {"articulationId": "long", "variantIds": ["non-vibrato", "vibrato"]},
                {"articulationId": "portato", "variantIds": ["bold", "rapid"]},
                {"articulationId": "sforzando", "variantIds": []},
                {"articulationId": "sforzatissimo", "variantIds": []},
                {"articulationId": "staccato", "variantIds": ["bold", "rapid"]},
            ],
        )

    def test_vsl_synchron_prime_percussion_catalog_entry(self):
        catalog, report = build_catalog_document(self.data_dir)
        self.assertFalse(report.validation_errors)

        taiko_entry = next(
            entry
            for entry in catalog
            if entry["vendorId"] == "vienna-symphonic-library"
            and entry["libraryId"] == "synchron-prime-percussion"
            and entry["instrumentId"] == "taiko"
        )

        self.assertEqual(
            taiko_entry["articulations"],
            [
                {"articulationId": "hits", "variantIds": ["hard", "soft"]},
            ],
        )

    def test_build_catalog_from_split_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for filename in [
                "vendors.json",
                "libraries.json",
                "instruments.json",
                "articulations.json",
                "variants.json",
            ]:
                dump_json(tmp_path / filename, json.loads((self.data_dir / filename).read_text(encoding="utf-8")))

            source_dir = tmp_path / "catalog" / "spitfire-audio"
            source_dir.mkdir(parents=True, exist_ok=True)
            dump_json(
                source_dir / "bbcso.json",
                [
                    {
                        "vendorId": "spitfire-audio",
                        "libraryId": "bbcso",
                        "instrumentId": "trumpet",
                        "articulations": [
                            {"articulationId": "legato", "variantIds": []}
                        ],
                    }
                ],
            )
            dump_json(
                source_dir / "bbcso-extra.json",
                [
                    {
                        "vendorId": "spitfire-audio",
                        "libraryId": "bbcso",
                        "instrumentId": "horn",
                        "articulations": [
                            {"articulationId": "staccato", "variantIds": []}
                        ],
                    }
                ],
            )

            catalog, report = build_catalog_document(tmp_path)
            self.assertFalse(report.validation_errors)
            self.assertEqual(report.source_files, 2)
            self.assertEqual(
                [(entry["instrumentId"], entry["articulations"][0]["articulationId"]) for entry in catalog],
                [("horn", "staccato"), ("trumpet", "legato")],
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
