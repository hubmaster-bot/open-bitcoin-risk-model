"""Deterministic release-readiness checks for OBRM."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from obrm.core.version import APP_VERSION

SUPPORTED_MIN = (3, 11)
SUPPORTED_MAX_EXCLUSIVE = (3, 14)
SECRET_NAMES = (
    "COINMETRICS_API_KEY",
    "GLASSNODE_API_KEY",
    "CRYPTOQUANT_API_KEY",
    "COINGECKO_API_KEY",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_checks(root: Path | None = None) -> list[Check]:
    root = root or _root()
    version_ok = APP_VERSION == "1.0.0-rc.1"
    py = sys.version_info[:2]
    python_ok = SUPPORTED_MIN <= py < SUPPORTED_MAX_EXCLUSIVE
    required = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        "docs/ROADMAP.md",
        "docs/CHANGELOG.md",
        "docs/RELEASE_CHECKLIST_v1.0.md",
    ]
    missing = [item for item in required if not (root / item).exists()]
    tracked_artifacts = [
        str(path.relative_to(root))
        for pattern in ("__pycache__", ".pytest_cache", ".ruff_cache", "*.pyc", "*.pyo")
        for path in root.rglob(pattern)
        if ".git" not in path.parts
    ]
    populated_secrets = [name for name in SECRET_NAMES if os.getenv(name)]

    return [
        Check("version", version_ok, f"APP_VERSION={APP_VERSION}"),
        Check("python", python_ok, f"Python {py[0]}.{py[1]} supported: 3.11-3.13"),
        Check("release_files", not missing, "complete" if not missing else f"missing: {missing}"),
        Check(
            "build_artifacts",
            not tracked_artifacts,
            "clean" if not tracked_artifacts else f"found: {tracked_artifacts[:10]}",
        ),
        Check(
            "secret_environment",
            not populated_secrets,
            "no provider credentials present" if not populated_secrets else "credentials present but not displayed",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OBRM release-readiness checks.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()
    checks = run_checks()
    if args.json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"[{status}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
