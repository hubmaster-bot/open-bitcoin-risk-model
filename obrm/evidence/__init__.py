"""Provider-independent evidence registry for OBRM research."""

from obrm.evidence.models import EvidenceItem, EvidenceProviderMapping
from obrm.evidence.registry import EVIDENCE_REGISTRY, PROVIDER_MAPPINGS

__all__ = (
    "EVIDENCE_REGISTRY",
    "PROVIDER_MAPPINGS",
    "EvidenceItem",
    "EvidenceProviderMapping",
)
