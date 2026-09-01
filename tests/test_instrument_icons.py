from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import tools.validate_terminology as validator_module


class InstrumentIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).parents[1]
        cls.data_dir = cls.repo_root / "data"
        cls.icon_dir = cls.repo_root / "assets" / "instrument-icons"
        instruments_doc = json.loads((cls.data_dir / "instruments.json").read_text(encoding="utf-8"))
        cls.instruments = instruments_doc["instruments"]

    def test_repository_icon_assets_validate(self):
        self.assertEqual(validator_module.validate_instrument_icon_assets(self.instruments, self.icon_dir), [])

    def test_validation_rejects_missing_icon_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_icon_dir = Path(tmp) / "instrument-icons"
            shutil.copytree(self.icon_dir, tmp_icon_dir)
            (tmp_icon_dir / "tpt.png").unlink()

            errors = validator_module.validate_instrument_icon_assets(self.instruments, tmp_icon_dir)

        self.assertTrue(any("missing tpt.png" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
