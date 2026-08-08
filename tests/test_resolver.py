import unittest
from pathlib import Path

from orch_terminology.resolver import TerminologyResolver, normalize_text


class ResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = TerminologyResolver(Path(__file__).parents[1] / "data")

    def test_normalization_and_alias_resolution(self):
        self.assertEqual(normalize_text(" BBC_TPT-MARCATO "), "bbc tpt marcato")
        result = self.resolver.resolve_library("BBC_SYMPHONY_ORCHESTRA")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "bbcso")

    def test_filename_metadata_resolution(self):
        result = self.resolver.resolve_filename("bbc_tpt_marcato_v10.wav")
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["vendor"]["id"], "spitfire-audio")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "marcato")
        self.assertEqual(result["velocity"], 10)

    def test_library_infers_vendor(self):
        result = self.resolver.resolve_library("bbc")
        self.assertEqual(result.entity["vendor"]["id"], "spitfire-audio")

    def test_contextual_alias_overrides_global_alias(self):
        result = self.resolver.resolve_articulation("cuiv", context="bbcso")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "long-cuivre")

    def test_unknown_term_is_unresolved(self):
        result = self.resolver.resolve_articulation("short")
        self.assertEqual(result.status, "unresolved")

    def test_berlin_symphonic_strings_filename(self):
        result = self.resolver.resolve_filename(
            "berlin_symphonic_strings_vln_i_marcato_long.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-symphonic-strings")
        self.assertEqual(result["instrument"]["id"], "violins-i")
        self.assertEqual(result["articulation"]["id"], "marcato-long")

    def test_berlin_brass_filename(self):
        result = self.resolver.resolve_filename(
            "berlin_brass_tpt1_marcato_long.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-brass")
        self.assertEqual(result["instrument"]["id"], "trumpet-1")
        self.assertEqual(result["articulation"]["id"], "marcato-long")

    def test_duplicate_alias_is_ambiguous(self):
        self.resolver._entities["articulation"].append(
            {"id": "long-alt", "name": "Long Alternative", "aliases": ["long"]}
        )
        result = self.resolver.resolve_articulation("long")
        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(len(result.matches), 2)


if __name__ == "__main__":
    unittest.main()
