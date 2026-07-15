"""Persistence for provider-discovery assessments."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import json

from obrm.evidence.provider_discovery import ProviderAssessment


def save_provider_assessment(
    assessment: ProviderAssessment,
    path: Path,
) -> None:
    """Save or replace one provider/evidence assessment in a local registry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = load_discovery_registry(path) or {
        "updated_at_utc": None,
        "assessments": [],
    }

    assessments = [
        item
        for item in payload.get("assessments", [])
        if not (
            item.get("provider_key") == assessment.provider_key
            and item.get("evidence_key") == assessment.evidence_key
        )
    ]
    assessments.append(asdict(assessment))
    assessments.sort(
        key=lambda item: (
            str(item.get("evidence_key", "")),
            str(item.get("provider_key", "")),
        )
    )

    payload = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "assessments": assessments,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_discovery_registry(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
