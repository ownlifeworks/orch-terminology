# Insanity Samples — NEO STRINGS - Solo String Ensemble

Source: https://insanitysamples.com/collections/neo-series-update/products/neo-strings-solo-string-ensemble

Reviewed on 2026-09-29. The source lists Violin, Viola, Cello, Double Bass, and an Ensemble Patch. The Ensemble Patch is mapped to the existing `strings-ensemble` instrument with the common main articulation set. `Col Legno` is absent only for Violin, as explicitly stated by the source.

## Normalization decisions

- `Static Longs - Vibrato & Non-Vibrato` and both `Expressive Longs` labels → `long` with the existing `expressive`, `vibrato`, and `non-vibrato` variants.
- `Ornaments` → curator-approved `various`, consistent with the other NEO libraries.
- `Trills` → `trills` with `minor-2nd` and `wholetone`; `Tremolo (With accented start)` → `tremolo` with `acc`.
- `Sforzando Decrescendo` → existing `sforzando`.
- `Harmonics` maps directly to the existing articulation. The remaining extended techniques and FX (`Extreme Sul Pont`, `Pont-Tasto Cycles`, `Extreme Sul Tasto`, `Behind the Bridge FX`, `Sul Pont Erratic Trems`, and `Erratic Vibrato`) map to `various`, because their qualifiers are unsupported or composite in the current relationship model.
