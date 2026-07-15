"""Formal promotion review for candidate Market Dimensions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

from obrm.validation.onchain_validation import OnChainValidationReport


PROMOTION_STATUS_PROMOTE = "promote"
PROMOTION_STATUS_RESEARCH = "research_only"
PROMOTION_STATUS_REJECT = "not_ready"


@dataclass(frozen=True)
class PromotionDecision:
    candidate: str
    status: str
    reviewed_at_utc: str
    readiness_status: str
    coverage_status: str
    separation_status: str
    independence_status: str
    stability_status: str
    rationale: tuple[str, ...]
    next_actions: tuple[str, ...]
    live_model_changed: bool


def decide_onchain_promotion(
    report: OnChainValidationReport,
) -> PromotionDecision:
    """Convert the visible readiness assessment into a formal decision."""
    readiness = report.readiness

    if readiness.overall_status == "ready":
        status = PROMOTION_STATUS_PROMOTE
        next_actions = (
            "Prepare a separate Composite Risk v2 release.",
            "Freeze the candidate weights before implementation.",
            "Run a full regression and portfolio-impact review.",
            "Document the migration from Composite Risk v1.",
        )
    elif readiness.overall_status == "research only":
        status = PROMOTION_STATUS_RESEARCH
        next_actions = (
            "Keep the on-chain score in the research layer.",
            "Add another independent evidence category.",
            "Re-run validation after provider coverage improves.",
            "Do not alter live Composite Risk or decisions.",
        )
    else:
        status = PROMOTION_STATUS_REJECT
        next_actions = (
            "Keep the on-chain score outside the live model.",
            "Investigate missing Holder Behaviour evidence.",
            "Investigate missing Realized Capital Flow evidence.",
            "Revisit provider fallbacks before another promotion review.",
        )

    rationale = tuple(readiness.reasons) or (
        "No readiness rationale was supplied.",
    )

    return PromotionDecision(
        candidate="On-Chain Market Dimension",
        status=status,
        reviewed_at_utc=datetime.now(timezone.utc).isoformat(),
        readiness_status=readiness.overall_status,
        coverage_status=readiness.coverage_status,
        separation_status=readiness.separation_status,
        independence_status=readiness.independence_status,
        stability_status=readiness.stability_status,
        rationale=rationale,
        next_actions=next_actions,
        live_model_changed=False,
    )


def save_promotion_decision(
    decision: PromotionDecision,
    path: Path,
) -> None:
    """Persist a reproducible promotion decision."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(decision), indent=2),
        encoding="utf-8",
    )


def load_promotion_decision(
    path: Path,
) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
