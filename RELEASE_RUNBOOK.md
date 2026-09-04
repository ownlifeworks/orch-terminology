# Orchestral Terminology Release Runbook

Use this runbook whenever canonical terminology, catalog relationships, instrument properties, or canonical instrument icons change. `data/` and `assets/instrument-icons/` are authoritative. Every `orch.db` and icon copy outside this repository is a generated consumer mirror.

## Release sequence

1. Edit canonical source data only.

   - Update canonical JSON under `data/`.
   - Update per-library catalog sources under `data/catalog/`.
   - Update canonical PNG icons under `assets/instrument-icons/`.
   - Preserve stable IDs. If an ID must change, update all references in `libraries.json` and `contexts.json` in the same change.

2. Regenerate the aggregate catalog if a per-library catalog source changed.

   ```powershell
   pwsh -File tools/build_catalog.ps1
   ```

3. Run a validation-only distribution build before overwriting consumers.

   ```powershell
   python tools/build_distribution.py --skip-sync
   python -m unittest discover -s tests
   ```

   Stop and fix canonical inputs if either command fails. Do not patch `dist/orch.db` directly; rebuild it from JSON.

4. Generate the distribution and synchronize all consumers.

   ```powershell
   python tools/build_distribution.py
   python -m unittest discover -s tests
   ```

   The command validates first, creates `dist/orch.db` and `dist/instrument-icons/`, and replaces the following mirrors:

   - `C:\dev\OwnLifeAudioWebsite\src\data\terminology\orch.db`
   - `C:\dev\OwnLifeAudioWebsite\public\terminology\instrument-icons\`
   - `C:\dev\NtdEngine\Source\Assets\terminology\orch.db`
   - `C:\dev\NtdEngine\Source\Assets\inst\`
   - `C:\dev\NtdEngine\tools\NtdDetector\backend\assets\terminology\orch.db`
   - `C:\dev\NtdEngine\tools\NtdDetector\frontend\public\terminology\orch.db`
   - `C:\dev\SymphonicBalance\Resources\orch.db`
   - `C:\dev\SymphonicBalance\Resources\instrument-icons\`

5. If only a specific consumer must be refreshed, use `--targets website`, `--targets ntd-engine`, `--targets ntd-detector`, or `--targets symphonic-balance`. Run the complete sync before a coordinated terminology release unless a consumer is explicitly blocked.

6. Review `git diff` and `git status` in this repository and every affected consumer. The detector consumes database mirrors only; it intentionally does not receive icons.

7. Hand off to consumer release builds.

   - Rebuild and test the website before its Render deployment.
   - Rebuild NTD Engine because it embeds the database and icon resources.
   - Build/test NTD Detector if its terminology UI or backend lookup is being released.
   - Rebuild Symphonic Balance because it embeds the database and icon resources.

8. Commit and push this canonical repository and the changed consumer mirrors together where possible. Do not describe a terminology release as complete while an affected consumer still has an unsynchronized mirror.

## Fast checks

```powershell
python tools/validate_terminology.py
python tools/build_distribution.py --skip-sync
python -m unittest discover -s tests
```

## Release boundary

This repository produces canonical runtime data, not a customer installer or hosted service. Customer-facing delivery happens only after each affected consumer completes its own release process.
