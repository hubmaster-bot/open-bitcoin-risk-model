"""Explainability for validated on-chain research signals."""

from __future__ import annotations

import pandas as pd


def explain_validated_onchain_row(row: pd.Series) -> tuple[str, ...]:
    notes: list[str] = []

    mvrv = row.get("mvrv")
    if pd.notna(mvrv):
        value = float(mvrv)
        if value < 1.0:
            notes.append(
                "MVRV is below 1.0, so market value is below realized value."
            )
        elif value < 2.0:
            notes.append(
                "MVRV is above realized value but not at historically more "
                "elevated multiples."
            )
        else:
            notes.append(
                "MVRV is elevated relative to realized value."
            )

    growth = row.get("hash_rate_growth_365d")
    if pd.notna(growth):
        direction = "increased" if float(growth) >= 0 else "declined"
        notes.append(
            f"Hash rate has {direction} {abs(float(growth)):.1%} over 365 days."
        )

    trend = row.get("hash_rate_vs_trend")
    if pd.notna(trend):
        relation = "above" if float(trend) >= 0 else "below"
        notes.append(
            f"Hash rate is {abs(float(trend)):.1%} {relation} its 200-day trend."
        )

    notes.append(
        "The on-chain score remains a diagnostic research output and does not "
        "yet affect Composite Risk or portfolio decisions."
    )
    return tuple(notes)
