from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.build_distribution import CONSUMER_TARGETS, NTD_ENGINE_ICON_SIZE, export_reduced_icons
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

    def test_missing_icon_file_is_reported_as_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_icon_dir = Path(tmp) / "instrument-icons"
            shutil.copytree(self.icon_dir, tmp_icon_dir)
            (tmp_icon_dir / "tpt.png").unlink()

            errors = validator_module.validate_instrument_icon_assets(self.instruments, tmp_icon_dir)
            warnings = validator_module.missing_instrument_icon_warnings(self.instruments, tmp_icon_dir)

        self.assertEqual(errors, [])
        self.assertTrue(any("missing tpt.png" in warning for warning in warnings))

    def test_ntd_engine_icons_are_reduced_for_embedding(self):
        from PIL import Image

        self.assertEqual(CONSUMER_TARGETS["ntd-engine"].icon_max_size, NTD_ENGINE_ICON_SIZE)
        masters = sorted(self.icon_dir.glob("*.png"))[:3]
        # Export targets must stay inside the workspace, so the scratch folder lives in the repository.
        with tempfile.TemporaryDirectory(dir=self.repo_root) as tmp:
            source = Path(tmp) / "masters"
            source.mkdir()
            for master in masters:
                shutil.copy2(master, source / master.name)

            count = export_reduced_icons(source, Path(tmp) / "reduced", NTD_ENGINE_ICON_SIZE)

            self.assertEqual(count, len(masters))
            for master in masters:
                reduced_path = Path(tmp) / "reduced" / master.name
                with Image.open(reduced_path) as reduced:
                    self.assertLessEqual(max(reduced.size), NTD_ENGINE_ICON_SIZE)
                    self.assertEqual(reduced.mode, "P")
                self.assertLess(reduced_path.stat().st_size, master.stat().st_size)


if __name__ == "__main__":
    unittest.main()
