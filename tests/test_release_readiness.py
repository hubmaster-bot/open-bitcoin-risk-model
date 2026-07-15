from pathlib import Path

from obrm.core.version import APP_VERSION
from obrm.release.readiness import (
    EXPECTED_VERSION,
    REQUIRED_RELEASE_FILES,
    run_environment_checks,
    run_repository_checks,
)


def _clean_repository(root: Path) -> None:
    for relative in REQUIRED_RELEASE_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")
    version = root / "obrm/core/version.py"
    version.parent.mkdir(parents=True, exist_ok=True)
    version.write_text(f'APP_VERSION = "{EXPECTED_VERSION}"\n', encoding="utf-8")


def test_final_release_version():
    assert APP_VERSION == "1.0.0"


def test_repository_checks_pass_for_clean_repository(tmp_path: Path):
    _clean_repository(tmp_path)
    checks = run_repository_checks(tmp_path)
    assert all(check.passed for check in checks)


def test_repository_checks_ignore_local_virtual_environment(tmp_path: Path):
    _clean_repository(tmp_path)
    cache = tmp_path / ".venv/Lib/site-packages/example/__pycache__/module.pyc"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"generated")
    checks = run_repository_checks(tmp_path)
    assert next(check for check in checks if check.name == "build_artifacts").passed


def test_repository_checks_detect_source_cache(tmp_path: Path):
    _clean_repository(tmp_path)
    cache = tmp_path / "obrm/core/__pycache__/version.pyc"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"generated")
    checks = run_repository_checks(tmp_path)
    artifact_check = next(check for check in checks if check.name == "build_artifacts")
    assert not artifact_check.passed
    normalized_detail = artifact_check.detail.replace("\\\\", "/").replace("\\", "/")
    assert "obrm/core/__pycache__" in normalized_detail


def test_environment_checks_are_separate_from_repository_checks(monkeypatch):
    monkeypatch.setenv("GLASSNODE_API_KEY", "test-value")
    checks = run_environment_checks()
    secret_check = next(check for check in checks if check.name == "secret_environment")
    assert not secret_check.passed
    assert "test-value" not in secret_check.detail
