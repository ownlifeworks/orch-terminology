from __future__ import annotations

import argparse
import subprocess
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DIST_DIR = ROOT / "dist"
CANONICAL_ICON_DIR = ROOT / "assets" / "instrument-icons"
DIST_DB_PATH = DIST_DIR / "orch.db"
DIST_ICON_DIR = DIST_DIR / "instrument-icons"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_sqlite import build_database  # noqa: E402
from tools.validate_terminology import validate  # noqa: E402


@dataclass(frozen=True)
class ConsumerTarget:
    key: str
    label: str
    db_targets: tuple[Path, ...]
    icon_targets: tuple[Path, ...]


CONSUMER_TARGETS = {
    "website": ConsumerTarget(
        key="website",
        label="OwnLifeAudioWebsite",
        db_targets=(WORKSPACE_ROOT / "OwnLifeAudioWebsite" / "src" / "data" / "terminology" / "orch.db",),
        icon_targets=(WORKSPACE_ROOT / "OwnLifeAudioWebsite" / "public" / "terminology" / "instrument-icons",),
    ),
    "ntd-detector": ConsumerTarget(
        key="ntd-detector",
        label="NTD Detector",
        db_targets=(
            WORKSPACE_ROOT / "NtdEngine" / "tools" / "NtdDetector" / "backend" / "assets" / "terminology" / "orch.db",
            WORKSPACE_ROOT / "NtdEngine" / "tools" / "NtdDetector" / "frontend" / "public" / "terminology" / "orch.db",
        ),
        icon_targets=(),
    ),
    "ntd-engine": ConsumerTarget(
        key="ntd-engine",
        label="NtdEngine",
        db_targets=(WORKSPACE_ROOT / "NtdEngine" / "Source" / "Assets" / "terminology" / "orch.db",),
        icon_targets=(WORKSPACE_ROOT / "NtdEngine" / "Source" / "Assets" / "inst",),
    ),
    "symphonic-balance": ConsumerTarget(
        key="symphonic-balance",
        label="SymphonicBalance",
        db_targets=(WORKSPACE_ROOT / "SymphonicBalance" / "Resources" / "orch.db",),
        icon_targets=(WORKSPACE_ROOT / "SymphonicBalance" / "Resources" / "instrument-icons",),
    ),
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate canonical terminology, build orch.db, and synchronize consumer mirrors."
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=sorted((*CONSUMER_TARGETS.keys(), "all")),
        default=["all"],
        help="Consumer mirrors to synchronize after building dist/orch.db and dist/instrument-icons.",
    )
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Build dist/orch.db and dist/instrument-icons without copying into consumer repositories.",
    )
    return parser.parse_args(argv)


def ensure_workspace_path(path: Path) -> None:
    resolved = path.resolve()
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:
        raise ValueError(f"Refusing to write outside workspace root: {resolved}") from exc


def replace_directory(source: Path, destination: Path) -> int:
    ensure_workspace_path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return sum(1 for path in destination.rglob("*") if path.is_file())


def copy_file(source: Path, destination: Path) -> None:
    ensure_workspace_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(source, destination)
    except PermissionError as exc:
        source_text = str(source).replace("'", "''")
        destination_text = str(destination).replace("'", "''")
        try:
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Copy-Item -Force -LiteralPath '{source_text}' -Destination '{destination_text}'",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as sub_exc:
            raise OSError(f"{destination}: copy failed after retry") from sub_exc


def build_dist() -> tuple[object, int]:
    problems = validate()
    if problems:
        print("TERMINOLOGY DISTRIBUTION BLOCKED")
        print("\n".join(f"- {problem}" for problem in problems))
        raise SystemExit(1)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    report = build_database(ROOT / "data", DIST_DB_PATH)
    icon_count = replace_directory(CANONICAL_ICON_DIR, DIST_ICON_DIR)
    return report, icon_count


def resolved_targets(requested_targets: list[str]) -> list[ConsumerTarget]:
    if "all" in requested_targets:
        return [CONSUMER_TARGETS[key] for key in sorted(CONSUMER_TARGETS)]
    return [CONSUMER_TARGETS[key] for key in requested_targets]


def sync_consumers(targets: list[ConsumerTarget]) -> tuple[list[str], list[str]]:
    lines: list[str] = []
    errors: list[str] = []
    for target in targets:
        try:
            for db_target in target.db_targets:
                copy_file(DIST_DB_PATH, db_target)
            for icon_target in target.icon_targets:
                replace_directory(DIST_ICON_DIR, icon_target)
            lines.append(
                f"{target.label}: synced {len(target.db_targets)} db target(s), {len(target.icon_targets)} icon target(s)"
            )
        except OSError as exc:
            errors.append(f"{target.label}: {exc}")
    return lines, errors


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report, icon_count = build_dist()
    print("ORCH TERMINOLOGY DISTRIBUTION")
    print(f"Output DB: {DIST_DB_PATH}")
    print(f"Output icons: {DIST_ICON_DIR} ({icon_count} files)")
    print(f"Vendors: {report.vendors}")
    print(f"Libraries: {report.libraries}")
    print(f"Instruments: {report.instruments}")
    print(f"Instrument properties: {report.instrument_properties}")
    print(f"Instrument loudness targets: {report.instrument_loudness_targets}")
    print(f"Articulations: {report.articulations}")
    print(f"Variants: {report.variants}")
    print(f"Catalog entries: {report.catalog_entries}")
    print(f"Catalog articulations: {report.catalog_articulations}")
    print(f"Catalog variants: {report.catalog_variants}")

    if args.skip_sync:
        print("Consumer sync: skipped")
        return 0

    target_lines, sync_errors = sync_consumers(resolved_targets(args.targets))
    print("Consumer sync:")
    for line in target_lines:
        print(f"- {line}")
    if sync_errors:
        print("Consumer sync blocked:")
        for error in sync_errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
