"""Tests for the OBRM documentation foundation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_documentation_directories_exist() -> None:
    assert (ROOT / "docs" / "user_guide").is_dir()
    assert (ROOT / "docs" / "handbook").is_dir()
    assert (ROOT / "docs" / "developer").is_dir()
    assert (ROOT / "docs" / "adr").is_dir()


def test_core_documentation_files_exist() -> None:
    required = (
        ROOT / "docs" / "README.md",
        ROOT / "docs" / "MATURITY_SCORECARD.md",
        ROOT / "docs" / "user_guide" / "01_Getting_Started.md",
        ROOT / "docs" / "handbook" / "02_Market_Dimensions.md",
        ROOT / "docs" / "handbook" / "03_Model_Confidence.md",
        ROOT / "docs" / "developer" / "01_Architecture.md",
        ROOT / "docs" / "adr" / "ADR-017-documentation-architecture.md",
    )

    for path in required:
        assert path.is_file(), f"Missing documentation file: {path}"


def test_documentation_mentions_key_safety_distinctions() -> None:
    confidence_text = (
        ROOT / "docs" / "handbook" / "03_Model_Confidence.md"
    ).read_text(encoding="utf-8")
    limitations_text = (
        ROOT / "docs" / "user_guide" / "06_Limitations.md"
    ).read_text(encoding="utf-8")

    assert "not a probability" in confidence_text.lower()
    assert "research" in limitations_text.lower()
