from pathlib import Path

from obrm.core.version import APP_VERSION
from obrm.release.readiness import run_checks


def test_release_candidate_version():
    assert APP_VERSION == "1.0.0-rc.1"


def test_release_readiness_passes_for_clean_repository(tmp_path: Path):
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
    for relative in required:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")
    checks = run_checks(tmp_path)
    assert all(check.passed for check in checks)
