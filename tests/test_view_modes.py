"""Tests for OBRM display modes."""

import pytest

from obrm.dashboard.view_modes import VIEW_MODES, view_mode_by_key


def test_expected_view_modes_exist() -> None:
    assert [mode.key for mode in VIEW_MODES] == [
        "executive",
        "analyst",
        "research",
    ]


def test_research_mode_contains_full_detail() -> None:
    mode = view_mode_by_key("research")
    assert mode.show_dimensions
    assert mode.show_contributions
    assert mode.show_confidence_audit
    assert mode.show_raw_inputs
    assert mode.show_methodology


def test_unknown_view_mode_is_rejected() -> None:
    with pytest.raises(KeyError):
        view_mode_by_key("unknown")
