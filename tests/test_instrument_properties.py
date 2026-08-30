from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import tools.validate_terminology as validator_module
from tools.build_sqlite import build_database


class InstrumentPropertiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).parents[1]
        cls.data_dir = cls.repo_root / "data"
        instruments_doc = json.loads((cls.data_dir / "instruments.json").read_text(encoding="utf-8"))
        cls.instrument_ids = {entry["id"] for entry in instruments_doc["instruments"]}

    def test_repository_instrument_properties_validate(self):
        self.assertEqual(validator_module.validate_instrument_properties(self.instrument_ids), [])

    def test_validation_rejects_unknown_instrument_id(self):
        document = json.loads((self.data_dir / "instrument-properties.json").read_text(encoding="utf-8"))
        document["instruments"]["unknown-instrument"] = document["instruments"]["trumpet"]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "instrument-properties.json").write_text(json.dumps(document, indent=2), encoding="utf-8")

            previous_data = validator_module.DATA
            try:
                validator_module.DATA = tmp_path
                errors = validator_module.validate_instrument_properties(self.instrument_ids)
            finally:
                validator_module.DATA = previous_data

        self.assertTrue(any("unknown instrument id" in error for error in errors))

    def test_sqlite_build_exports_instrument_properties(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "orch.db"
            report = build_database(self.data_dir, output_path)

            self.assertEqual(report.instrument_properties, 1)
            self.assertEqual(report.instrument_loudness_targets, 6)

            connection = sqlite3.connect(output_path)
            try:
                row = connection.execute(
                    """
                    SELECT range_min, range_max, measurement_range_min, measurement_range_max
                    FROM instrument_properties
                    WHERE instrument_id = ?
                    """,
                    ("trumpet",),
                ).fetchone()
                self.assertEqual(row, (54, 82, 60, 72))

                targets = connection.execute(
                    """
                    SELECT capture_kind, dynamic_anchor, lufs
                    FROM instrument_loudness_targets
                    WHERE instrument_id = ?
                    ORDER BY capture_kind, dynamic_anchor
                    """,
                    ("trumpet",),
                ).fetchall()
                self.assertEqual(
                    targets,
                    [
                        ("long", "fff", -22.0),
                        ("long", "mf", -31.0),
                        ("long", "pp", -40.0),
                        ("short", "fff", -20.0),
                        ("short", "mf", -29.0),
                        ("short", "pp", -38.0),
                    ],
                )
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
