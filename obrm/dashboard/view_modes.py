"""Executive, Analyst, and Research display modes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewMode:
    key: str
    label: str
    description: str
    show_dimensions: bool
    show_contributions: bool
    show_confidence_audit: bool
    show_raw_inputs: bool
    show_methodology: bool


VIEW_MODES: tuple[ViewMode, ...] = (
    ViewMode(
        key="executive",
        label="Executive",
        description="Headline market assessment and decision only.",
        show_dimensions=False,
        show_contributions=False,
        show_confidence_audit=False,
        show_raw_inputs=False,
        show_methodology=False,
    ),
    ViewMode(
        key="analyst",
        label="Analyst",
        description="Market Dimensions, contributions, and Decision Audit.",
        show_dimensions=True,
        show_contributions=True,
        show_confidence_audit=True,
        show_raw_inputs=False,
        show_methodology=False,
    ),
    ViewMode(
        key="research",
        label="Research",
        description="Full calculations, raw inputs, and methodology.",
        show_dimensions=True,
        show_contributions=True,
        show_confidence_audit=True,
        show_raw_inputs=True,
        show_methodology=True,
    ),
)


def view_mode_by_key(key: str) -> ViewMode:
    for mode in VIEW_MODES:
        if mode.key == key:
            return mode
    raise KeyError(f"Unknown view mode: {key}")
