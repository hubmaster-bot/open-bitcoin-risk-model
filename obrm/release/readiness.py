"""Release-readiness checks for OBRM.

Repository checks are deterministic and safe to exercise in unit tests. Environment
checks are evaluated only for the real machine running the release command.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

EXPECTED_VERSION = "1.0.0"
SUPPORTED_MIN = (3, 11)
SUPPORTED_MAX_EXCLUSIVE = (3, 14)
SECRET_NAMES = (
    "COINMETRICS_API_KEY",
    "GLASSNODE_API_KEY",
    "CRYPTOQUANT_API_KEY",
    "COINGECKO_API_KEY",
)
REQUIRED_RELEASE_FILES = (
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    "docs/ROADMAP.md",
    "docs/CHANGELOG.md",
    "docs/RELEASE_CHECKLIST_v1.0.md",
)
IGNORED_TREE_PARTS = {".git", ".venv", "venv", "build", "dist"}
# Importing this command can create these caches before the scan starts. They are
# runtime effects of the checker itself, not files intended for a release archive.
SELF_IMPORT_CACHE_DIRS = {
    Path("obrm/__pycache__"),
    Path("obrm/release/__pycache__"),
}


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_app_version(root: Path) -> str:
    """Read APP_VERSION without importing application modules and creating caches."""
    version_path = root / "obrm" / "core" / "version.py"
    try:
        tree = ast.parse(version_path.read_text(encoding="utf-8"), filename=str(version_path))
    except (OSError, SyntaxError, UnicodeError):
        return "unreadable"
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "APP_VERSION":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return "missing"


def _build_artifacts(root: Path) -> list[str]:
    artifacts: list[str] = []
    for path in root.rglob("*"):
        if any(part in IGNORED_TREE_PARTS for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root)
        if path.is_dir() and path.name in {"__pycache__", ".pytest_cache", ".ruff_cache"}:
            if relative not in SELF_IMPORT_CACHE_DIRS:
                artifacts.append(str(relative))
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            if path.parent.relative_to(root) not in SELF_IMPORT_CACHE_DIRS:
                artifacts.append(str(relative))
    return sorted(set(artifacts))


def run_repository_checks(root: Path | None = None) -> list[Check]:
    """Run deterministic checks based only on repository contents."""
    root = root or _root()
    app_version = _read_app_version(root)
    missing = [item for item in REQUIRED_RELEASE_FILES if not (root / item).exists()]
    artifacts = _build_artifacts(root)
    return [
        Check("version", app_version == EXPECTED_VERSION, f"APP_VERSION={app_version}"),
        Check("release_files", not missing, "complete" if not missing else f"missing: {missing}"),
        Check(
            "build_artifacts",
            not artifacts,
            "clean" if not artifacts else f"found: {artifacts[:10]}",
        ),
    ]


def run_environment_checks() -> list[Check]:
    """Run checks that legitimately depend on the current machine/environment."""
    py = sys.version_info[:2]
    python_ok = SUPPORTED_MIN <= py < SUPPORTED_MAX_EXCLUSIVE
    populated_secrets = [name for name in SECRET_NAMES if os.getenv(name)]
    return [
        Check("python", python_ok, f"Python {py[0]}.{py[1]} supported: 3.11-3.13"),
        Check(
            "secret_environment",
            not populated_secrets,
            "no provider credentials present"
            if not populated_secrets
            else "credentials present but not displayed",
        ),
    ]


def run_checks(root: Path | None = None, *, include_environment: bool = True) -> list[Check]:
    """Run repository checks and, by default, current-environment checks."""
    checks = run_repository_checks(root)
    if include_environment:
        checks.extend(run_environment_checks())
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OBRM release-readiness checks.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--repository-only",
        action="store_true",
        help="Skip Python-version and credential-environment checks.",
    )
    args = parser.parse_args()
    checks = run_checks(include_environment=not args.repository_only)
    if args.json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"[{status}] {check.name}: {check.detail}")
    return 0 if all(check.passed for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
