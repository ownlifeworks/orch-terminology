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

    def test_contextless_alias_is_unresolved(self):
        result = self.resolver.resolve_articulation("cuiv")
        self.assertEqual(result.status, "unresolved")

    def test_unknown_term_is_unresolved(self):
        result = self.resolver.resolve_articulation("short")
        self.assertEqual(result.status, "unresolved")

    def test_shorts_articulation_resolution(self):
        result = self.resolver.resolve_articulation("shorts")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "shorts")

    def test_variant_resolution(self):
        result = self.resolver.resolve_variant("Low Latency")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "low-latency")

    def test_senza_sordino_variant_resolution(self):
        result = self.resolver.resolve_variant("senza sordino")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "senza-sordino")

    def test_standalone_articulation_resolution(self):
        result = self.resolver.resolve_articulation("sul ponticello")
        self.assertEqual(result.status, "unresolved")

    def test_berlin_symphonic_strings_filename(self):
        result = self.resolver.resolve_filename(
            "berlin_symphonic_strings_vln_i_marcato_long.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-symphonic-strings")
        self.assertEqual(result["instrument"]["id"], "violins-i")
        self.assertEqual(result["articulation"]["id"], "marcato")
        self.assertEqual(result["variant"]["id"], "long")

    def test_variant_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_expressive_legato_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "legato")
        self.assertEqual(result["variant"]["id"], "expressive")
        self.assertEqual(result["velocity"], 10)

    def test_pattern_legato_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_pattern_legato_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "legato")
        self.assertEqual(result["variant"]["id"], "pattern")
        self.assertEqual(result["velocity"], 10)

    def test_melodic_legato_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_melodic_legato_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "legato")
        self.assertEqual(result["variant"]["id"], "melodic")
        self.assertEqual(result["velocity"], 10)

    def test_long_cs_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_long_cs_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "long")
        self.assertEqual(result["variant"]["id"], "con-sordino")
        self.assertEqual(result["velocity"], 10)

    def test_long_flautando_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_long_flautando_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "long")
        self.assertEqual(result["variant"]["id"], "flautando")
        self.assertEqual(result["velocity"], 10)

    def test_long_cuivre_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_long_cuivre_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "long")
        self.assertEqual(result["variant"]["id"], "cuivre")
        self.assertEqual(result["velocity"], 10)

    def test_glissandi_pentatonic_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "berlin_symphonic_strings_hrp_glissandi_pentatonic.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-symphonic-strings")
        self.assertEqual(result["instrument"]["id"], "harp")
        self.assertEqual(result["articulation"]["id"], "glissandi")
        self.assertEqual(result["variant"]["id"], "pentatonic")

    def test_glissandi_major_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "berlin_symphonic_strings_hrp_glissandi_major.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-symphonic-strings")
        self.assertEqual(result["instrument"]["id"], "harp")
        self.assertEqual(result["articulation"]["id"], "glissandi")
        self.assertEqual(result["variant"]["id"], "major")

    def test_glissandi_harmonic_minor_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "berlin_symphonic_strings_hrp_glissandi_harmonic_minor.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "berlin-symphonic-strings")
        self.assertEqual(result["instrument"]["id"], "harp")
        self.assertEqual(result["articulation"]["id"], "glissandi")
        self.assertEqual(result["variant"]["id"], "harmonic-minor")

    def test_repetitions_phrase_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_repetitions_16th_phrase_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "repetitions")
        self.assertEqual(result["variant"]["id"], "16th-phrase")
        self.assertEqual(result["velocity"], 10)

    def test_short_spiccato_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_short_spiccato_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "spiccato")
        self.assertEqual(result["variant"]["id"], "short")
        self.assertEqual(result["velocity"], 10)

    def test_long_harmonics_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_long_harmonics_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "harmonics")
        self.assertEqual(result["variant"]["id"], "long")
        self.assertEqual(result["velocity"], 10)

    def test_short_pizzicato_bartok_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_short_pizzicato_bartok_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "bartok")
        self.assertEqual(result["variant"]["id"], "short")
        self.assertEqual(result["velocity"], 10)

    def test_sul_ponticello_filename_resolution(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_sul_ponticello_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "long")
        self.assertEqual(result["variant"]["id"], "sul-ponticello")
        self.assertEqual(result["velocity"], 10)

    def test_berlin_brass_filename(self):
        result = self.resolver.resolve_filename(
            "berlin_brass_tpt1_marcato_long.wav"
        )
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["library"]["id"], "berlin-brass")
        self.assertIsNone(result["instrument"])
        self.assertEqual(result["articulation"]["id"], "marcato")
        self.assertIsNone(result["variant"])

    def test_synchron_prime_woodwinds_filename(self):
        result = self.resolver.resolve_filename(
            "synchron_prime_woodwinds_fl1_sus_vib.wav"
        )
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["library"]["id"], "synchron-prime-woodwinds")
        self.assertIsNone(result["instrument"])
        self.assertIsNone(result["articulation"])
        self.assertEqual(result["variant"]["id"], "vibrato")

    def test_synchron_prime_strings_i_library_resolution(self):
        result = self.resolver.resolve_library("Synchron Prime Strings I")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "synchron-prime-strings-1")
        self.assertEqual(result.entity["vendor"]["id"], "vienna-symphonic-library")

    def test_synchron_prime_strings_ii_library_resolution(self):
        result = self.resolver.resolve_library("Synchron Prime Strings II")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "synchron-prime-strings-2")
        self.assertEqual(result.entity["vendor"]["id"], "vienna-symphonic-library")

    def test_new_percussion_instrument_resolution(self):
        result = self.resolver.resolve_instrument("Concert Toms")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "concert-toms")

        result = self.resolver.resolve_instrument("Taiko")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "taiko")

        result = self.resolver.resolve_instrument("Suspended Cymbals")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "suspended-cymbals")

        result = self.resolver.resolve_instrument("Woodblocks")
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.entity["id"], "woodblocks")

    def test_harmon_mute_variant_filename(self):
        result = self.resolver.resolve_filename(
            "bbc_tpt_harmon_mute_staccato_v10.wav"
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["library"]["id"], "bbcso")
        self.assertEqual(result["instrument"]["id"], "trumpet")
        self.assertEqual(result["articulation"]["id"], "staccato")
        self.assertEqual(result["variant"]["id"], "harmon-mute")

    def test_duplicate_alias_is_ambiguous(self):
        resolver = TerminologyResolver(Path(__file__).parents[1] / "data")
        resolver._entities["articulation"].append(
            {"id": "long-alt", "name": "Long Alternative", "aliases": ["long"]}
        )
        result = resolver.resolve_articulation("long")
        self.assertEqual(result.status, "ambiguous")
        self.assertEqual(len(result.matches), 2)


if __name__ == "__main__":
    unittest.main()
