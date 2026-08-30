# Tools

Validation and consumer-artifact generation tools will live here.

Run the current validator from the repository root:

```powershell
python tools/validate_terminology.py
```

`build_sqlite.py` exports the canonical JSON, including `data/instrument-properties.json`, into `orch.db` so consumers can query instrument pitch and loudness-reference metadata from SQLite.
