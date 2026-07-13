"""Plain-English descriptions for on-chain research signals."""

from __future__ import annotations

import pandas as pd


def explain_onchain_row(row: pd.Series) -> tuple[str, ...]:
    """Explain the current v0.9.1 on-chain analytics snapshot."""
    notes: list[str] = []

    mvrv = row.get("mvrv")
    if pd.notna(mvrv):
        if float(mvrv) < 1.0:
            notes.append(
                "MVRV is below 1.0, meaning market value is below realized value."
            )
        elif float(mvrv) < 2.0:
            notes.append(
                "MVRV is above realized value but remains below historically "
                "more elevated multiples."
            )
        else:
            notes.append(
                "MVRV is elevated relative to realized value."
            )

    growth = row.get("realized_cap_growth_365d")
    if pd.notna(growth):
        direction = "expanded" if float(growth) >= 0 else "contracted"
        notes.append(
            f"Realized capitalization has {direction} "
            f"{abs(float(growth)):.1%} over 365 days."
        )

    coverage = row.get("onchain_component_coverage")
    if pd.notna(coverage):
        notes.append(
            f"On-chain research-input coverage is {float(coverage):.0%}."
        )

    notes.append(
        "The v0.9.1 research score is diagnostic only and does not yet "
        "affect Composite Risk or portfolio decisions."
    )
    return tuple(notes)
