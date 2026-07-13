"""Research candidates for later v0.9.x selection.

These are search themes, not assumed Coin Metrics metric identifiers.
The v0.9.0 catalogue must confirm exact Community availability first.
"""

CANDIDATE_THEMES: tuple[tuple[str, str], ...] = (
    (
        "Realized valuation",
        "Metrics related to realized capitalization and market value versus realized value.",
    ),
    (
        "Spent-output profitability",
        "Metrics related to whether transferred coins are spent at profit or loss.",
    ),
    (
        "Holder conviction",
        "Metrics related to dormant supply, coin age, and long-term holder behaviour.",
    ),
    (
        "Capital inflow",
        "Metrics related to realized-cap growth and new capital entering Bitcoin.",
    ),
)
