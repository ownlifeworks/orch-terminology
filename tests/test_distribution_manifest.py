from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.build_distribution import PUBLIC_DATABASE_URL, build_manifest
from tools.build_sqlite import build_database


class DistributionManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"

    def test_sqlite_and_manifest_export_data_version_and_integrity_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            database_path = output_dir / "orch.db"
            manifest_path = output_dir / "manifest.json"
            build_database(self.data_dir, database_path)
            build_manifest(database_path, manifest_path)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            schema_document = json.loads((self.data_dir / "schema-version.json").read_text(encoding="utf-8"))
            connection = sqlite3.connect(database_path)
            try:
                schema_info = dict(connection.execute("SELECT key, value FROM schema_info"))
            finally:
                connection.close()

            self.assertEqual(schema_info["data_version"], schema_document["dataVersion"])
            self.assertEqual(manifest["formatVersion"], 1)
            self.assertEqual(manifest["dataVersion"], schema_document["dataVersion"])
            self.assertEqual(manifest["schemaVersion"], int(schema_info["schema_version"]))
            self.assertEqual(manifest["size"], database_path.stat().st_size)
            self.assertEqual(manifest["sha256"], hashlib.sha256(database_path.read_bytes()).hexdigest())
            self.assertEqual(manifest["url"], PUBLIC_DATABASE_URL)
            self.assertEqual(manifest["sourceHashes"], json.loads(schema_info["source_hashes"]))


if __name__ == "__main__":
    unittest.main()
