import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import build_distribution


class DistributionCatalogTests(unittest.TestCase):
    def test_build_regenerates_catalog_before_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            data.mkdir()
            (data / "catalog.json").write_text("[]", encoding="utf-8")
            catalog = [{"instrumentId": "updated"}]
            report = SimpleNamespace(source_files=1, validation_errors=())

            def check_database_input(data_dir, _output):
                self.assertEqual(json.loads((data_dir / "catalog.json").read_text(encoding="utf-8")), catalog)
                return object()

            with patch.object(build_distribution, "ROOT", root), \
                 patch.object(build_distribution, "DIST_DIR", root / "dist"), \
                 patch.object(build_distribution, "build_catalog_document", return_value=(catalog, report)), \
                 patch.object(build_distribution, "validate", return_value=[]), \
                 patch.object(build_distribution, "build_database", side_effect=check_database_input), \
                 patch.object(build_distribution, "build_manifest"), \
                 patch.object(build_distribution, "replace_directory", return_value=0):
                build_distribution.build_dist()


if __name__ == "__main__":
    unittest.main()
