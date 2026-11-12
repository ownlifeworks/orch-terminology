# Terminology synchronization checklist

Use this checklist whenever the canonical terminology data or canonical instrument icons change. The authoritative sources are `data/` and `assets/instrument-icons/` in this repository. Never treat a consumer copy as authoritative.

## Consumers that must be checked

- `OwnLifeAudioWebsite/src/data/terminology/orch.db`
- `OwnLifeAudioWebsite/public/orchdb/orch.db`
- `OwnLifeAudioWebsite/public/orchdb/manifest.json`
- `NtdEngine/Source/Assets/terminology/orch.db`
- `NtdEngine/Source/Assets/inst/`
- `NtdEngine/tools/NtdDetector/backend/assets/terminology/`
- `NtdEngine/tools/NtdDetector/frontend/public/terminology/`
- `SymphonicBalance/Resources/orch.db`
- `SymphonicBalance/Resources/instrument-icons/`

## Required workflow

1. Edit only the canonical files in `data/` and `assets/instrument-icons/`.
2. Keep IDs stable. Update all `libraries.json` and `contexts.json` references when an ID changes.
3. Increment `data/schema-version.json` `dataVersion` for every published data change. Change `schemaVersion` only when the SQLite contract changes.
4. Run the distribution build. It regenerates `data/catalog.json` from the per-library sources before validating and building the database:

   ```powershell
   python tools/build_distribution.py
   python -m unittest discover -s tests
   ```

5. If only one consumer needs to be refreshed, rerun `python tools/build_distribution.py --targets <consumer-key>`.
6. Verify that the website's public OrchDB database and manifest match the generated distribution.
7. Verify that NTD Engine's embedded terminology resource and instrument PNG resources match the synchronized mirrors, then rebuild it. The sync writes NTD Engine's icons reduced to 160 px with a 256-colour palette (this needs Pillow), so they intentionally differ from the masters; never copy the full-size masters into `NtdEngine/Source/Assets/inst/` by hand, because NTD Engine's CMake configure rejects icons larger than 160 px.
8. Verify that NTDDetector uses the synchronized `orch.db` mirrors in both backend and frontend paths. Do not mirror instrument icons there unless the detector UI starts rendering them.
9. Build the affected websites and applications.
10. Inspect `git diff` and `git status` in every affected repository.
11. Commit and push the canonical data plus all synchronized consumer changes together, or clearly record any consumer that is blocked.

## Current implementation warning

`python tools/build_distribution.py` is the canonical sync entry point. Never report terminology work as complete until each affected consumer above has either been synchronized by that script or explicitly marked blocked.
