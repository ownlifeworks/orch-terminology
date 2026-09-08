---
name: instrument-icon-creation
description: Create dedicated instrument icon PNGs for this repository while preserving its realistic cutout style, translucent backdrop treatment, and catalog wiring.
---

# Instrument Icon Creation

Use this skill when the user asks for a new or replacement instrument icon for this repository.

## Visual Direction

- Create a realistic studio/product-style rendering of the instrument, isolated and centered on a square canvas.
- Match the existing icon family: crisp detailed materials, strong readable silhouette, and the instrument filling most of the 300x300 frame.
- Use a genuinely transparent background with a restrained translucent warm-cream geometric wash behind the subject. The wash may be a soft wedge or abstract shape, but must not become an opaque full-canvas background.
- Do not include text, labels, logos, watermarks, people, hands, cases, or unrelated instruments.
- Choose an instrument-specific angle and material treatment that makes the identity immediately legible at icon size.

## Generation Workflow

1. Inspect several existing similar icons in `assets/instrument-icons/` before generating. Useful references include `ob.png`, `hn.png`, `piano.png`, `soldbs.png`, `hrp.png`, and `vlnII.png`.
2. Use the built-in image generation tool by default. Generate one distinct asset per instrument; do not use a single generic result for multiple instrument IDs.
3. Prompt for a transparent output and repeat the visual constraints above. Treat the existing icons as style references, not as assets to overwrite.
4. Inspect each generated image visually before accepting it. Reject results with incorrect instrument identity, visible text, opaque backgrounds, distracting artifacts, or a weak silhouette.
5. Save the final asset under `assets/instrument-icons/<instrument-id>.png`.
6. Normalize every final file to exactly 300x300 PNG with alpha preserved. Verify the dimensions and that a transparent corner remains transparent.

## Catalog Integration

- Set the matching instrument's `iconKey` in `data/instruments.json` to the dedicated filename.
- Do not create a new instrument entity merely to obtain an icon; confirm the canonical instrument ID first.
- Preserve existing assets unless the user explicitly requests replacement.
- Run `python tools/validate_terminology.py` and `python -m unittest discover -s tests` after updating the catalog.
- Run `python tools/build_distribution.py --skip-sync` when the runtime distribution needs refreshing.

## Prompt Template

Use this as a starting point and customize the subject description:

```text
Use case: stylized-concept.
Asset type: orchestral terminology instrument icon.
Primary request: a photorealistic isolated <instrument> cutout, viewed at a clear three-quarter angle, centered and filling most of a square canvas.
Style/medium: realistic studio product rendering with crisp detailed materials and a readable silhouette.
Scene/backdrop: genuinely transparent background with a very subtle translucent warm-cream geometric wash behind the instrument, such as a soft abstract wedge; keep the outer canvas transparent.
Constraints: no text, labels, logos, watermark, people, hands, cases, or extra instruments; suitable for a 300x300 transparent PNG icon.
```
