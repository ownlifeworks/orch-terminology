# Terminology synchronization checklist

Use this checklist whenever the canonical terminology database changes. The canonical source is `data/` in this repository. Never treat a consumer copy as authoritative.

## Consumers that must be checked

- `OwnLifeAudioWebsite/src/data/terminology/`
- `website/data/` (the Orch Terminology browser)
- `NtdEngine/Source/Assets/terminology/instruments.json`
- `python_ntd` / NTDDetector terminology integration

## Required workflow

1. Edit only the canonical files in `data/`.
2. Keep IDs stable. Update all `libraries.json` and `contexts.json` references when an ID changes.
3. Run:

   ```powershell
   python tools/validate_terminology.py
   python -m unittest discover -s tests
   ```

4. Synchronize every consumer mirror from the canonical data. Do not update only the website.
5. Verify that NTD Engine's embedded terminology resource contains the same relevant instrument names and aliases, then rebuild it.
6. Verify that NTDDetector uses the same terminology source or generated artifact. If it does not, fix the integration before proceeding.
7. Build the affected websites and applications.
8. Inspect `git diff` and `git status` in every affected repository.
9. Commit and push the canonical data plus all synchronized consumer changes together, or clearly record any consumer that is blocked.

## Current implementation warning

There is not yet a fully automatic synchronization generator. Website mirrors and NTD Engine data may therefore drift unless they are explicitly updated during the same task. Never report terminology work as complete until each consumer above has been checked.
