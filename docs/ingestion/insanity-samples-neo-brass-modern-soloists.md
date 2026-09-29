# Insanity Samples — NEO BRASS - Modern Soloists

Source: https://insanitysamples.com/collections/neo-series/products/neo-brass-modern-soloists

Reviewed on 2026-09-29. The source lists Trumpet, Flugelhorn, French Horn, Trombone, Euphonium, Tuba, and an Ensemble Patch. The existing `horn` alias covers French Horn and `tenor-trombone` alias covers Trombone. The Ensemble Patch is mapped to `brass-ensemble`, using the source's all-instrument basic articulation set.

## Normalization decisions

- `Expressive Longs (poco vib)` → `long` with `expressive` and `vibrato`.
- `Triple Tongue` → existing `multitongue`.
- `Falls`, `Flutter Tongue`, and `Shakes` map to their existing canonical articulations.
- `Muted Flutter Tongue` → `flutter` with the existing `muted` variant.
- `Flutter Tongue Crescendo`, `Comic Whaps`, `Muted Double Whap`, `Chatter`, and `Xslide` map to the curator-approved `various` articulation because the catalog cannot represent their composite or otherwise unsupported technique semantics without adding terms.
