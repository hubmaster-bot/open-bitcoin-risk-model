"""Configurable Dynamic DCA rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DcaBand:
    maximum_risk: float
    multiplier: float
    label: str


DEFAULT_DCA_BANDS: tuple[DcaBand, ...] = (
    DcaBand(0.20, 2.50, "Strong accumulation"),
    DcaBand(0.40, 1.75, "Accumulation"),
    DcaBand(0.60, 1.00, "Normal DCA"),
    DcaBand(0.80, 0.50, "Reduced DCA"),
    DcaBand(1.00, 0.20, "Minimal DCA"),
)


def dca_recommendation(
    risk: float,
    bands: tuple[DcaBand, ...] = DEFAULT_DCA_BANDS,
) -> DcaBand:
    """Return the configured DCA band for a normalized risk score."""
    bounded_risk = min(max(float(risk), 0.0), 1.0)

    for band in bands:
        if bounded_risk <= band.maximum_risk:
            return band

    return bands[-1]
