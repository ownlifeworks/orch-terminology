from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.build_sqlite import build_database
from tools.validate_terminology import validate_library_weblinks


class LibraryMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"
        document = json.loads((cls.data_dir / "libraries.json").read_text(encoding="utf-8"))
        cls.libraries = document["libraries"]

    def test_repository_library_weblinks_validate(self):
        self.assertEqual(validate_library_weblinks(self.libraries), [])

    def test_every_concrete_library_has_a_weblink(self):
        missing = [item["id"] for item in self.libraries if item["id"] != "other" and not item.get("weblink")]
        self.assertEqual(missing, [])

    def test_validation_rejects_non_http_weblink(self):
        errors = validate_library_weblinks(
            [{"id": "example", "name": "Example", "vendorId": "vendor", "weblink": "ftp://example.com/library"}]
        )
        self.assertTrue(any("HTTP(S) URL" in error for error in errors))

    def test_sqlite_build_exports_library_weblink(self):
        expected = {
            item["id"]: item.get("weblink")
            for item in self.libraries
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "orch.db"
            build_database(self.data_dir, output_path)
            connection = sqlite3.connect(output_path)
            try:
                actual = dict(connection.execute("SELECT id, weblink FROM libraries"))
            finally:
                connection.close()

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
