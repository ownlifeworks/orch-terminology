# Terminology synchronization checklist

Use this checklist whenever the canonical terminology data or canonical instrument icons change. The authoritative sources are `data/` and `assets/instrument-icons/` in this repository. Never treat a consumer copy as authoritative.

## Consumers that must be checked

- `OwnLifeAudioWebsite/src/data/terminology/orch.db`
- `NtdEngine/Source/Assets/terminology/orch.db`
- `NtdEngine/Source/Assets/inst/`
- `NtdEngine/tools/NtdDetector/backend/assets/terminology/`
- `NtdEngine/tools/NtdDetector/frontend/public/terminology/`
- `SymphonicBalance/Resources/orch.db`
- `SymphonicBalance/Resources/instrument-icons/`

## Required workflow

1. Edit only the canonical files in `data/` and `assets/instrument-icons/`.
2. Keep IDs stable. Update all `libraries.json` and `contexts.json` references when an ID changes.
3. Run:

   ```powershell
   python tools/build_distribution.py
   python -m unittest discover -s tests
   ```

4. If only one consumer needs to be refreshed, rerun `python tools/build_distribution.py --targets <consumer-key>`.
5. Verify that NTD Engine's embedded terminology resource and instrument PNG resources match the synchronized mirrors, then rebuild it.
6. Verify that NTDDetector uses the synchronized `orch.db` mirrors in both backend and frontend paths. Do not mirror instrument icons there unless the detector UI starts rendering them.
7. Build the affected websites and applications.
8. Inspect `git diff` and `git status` in every affected repository.
9. Commit and push the canonical data plus all synchronized consumer changes together, or clearly record any consumer that is blocked.

## Current implementation warning

`python tools/build_distribution.py` is the canonical sync entry point. Never report terminology work as complete until each affected consumer above has either been synchronized by that script or explicitly marked blocked.
