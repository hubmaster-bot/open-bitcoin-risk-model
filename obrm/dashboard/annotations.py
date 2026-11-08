"""Persistent user chart annotations for the OBRM dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import json
from pathlib import Path
from typing import Iterable, Literal
from uuid import uuid4

AnnotationKind = Literal["vertical_date", "horizontal_price", "horizontal_risk"]
LineDash = Literal["solid", "dot", "dash", "longdash"]

DEFAULT_ANNOTATION_FILE = Path("data/user/chart_annotations.json")


@dataclass(frozen=True)
class ChartAnnotation:
    """One persistent line annotation on the market chart."""

    id: str
    kind: AnnotationKind
    value: str | float
    label: str = ""
    dash: LineDash = "dash"
    visible: bool = True

    @classmethod
    def create(
        cls,
        kind: AnnotationKind,
        value: str | float | date,
        label: str = "",
        dash: LineDash = "dash",
    ) -> "ChartAnnotation":
        normalized = _normalize_value(kind, value)
        return cls(
            id=uuid4().hex,
            kind=kind,
            value=normalized,
            label=label.strip(),
            dash=dash,
            visible=True,
        )


def _normalize_value(kind: AnnotationKind, value: str | float | date) -> str | float:
    if kind == "vertical_date":
        try:
            return date.fromisoformat(str(value)).isoformat()
        except ValueError as exc:
            raise ValueError("Vertical annotation date must use YYYY-MM-DD.") from exc

    numeric = float(value)
    if kind == "horizontal_price" and numeric <= 0:
        raise ValueError("Price annotations must be greater than zero.")
    if kind == "horizontal_risk" and not 0 <= numeric <= 1:
        raise ValueError("Risk annotations must be between 0 and 1.")
    return numeric


def load_annotations(path: Path = DEFAULT_ANNOTATION_FILE) -> list[ChartAnnotation]:
    """Load annotations; a missing file is an empty collection."""
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Annotation file must contain a JSON list.")
    result: list[ChartAnnotation] = []
    for item in payload:
        result.append(
            ChartAnnotation(
                id=str(item["id"]),
                kind=item["kind"],
                value=_normalize_value(item["kind"], item["value"]),
                label=str(item.get("label", "")),
                dash=item.get("dash", "dash"),
                visible=bool(item.get("visible", True)),
            )
        )
    return result


def save_annotations(
    annotations: Iterable[ChartAnnotation],
    path: Path = DEFAULT_ANNOTATION_FILE,
) -> None:
    """Persist annotations atomically as readable JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps([asdict(item) for item in annotations], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


def annotations_json(annotations: Iterable[ChartAnnotation]) -> str:
    """Return an exportable JSON document."""
    return json.dumps([asdict(item) for item in annotations], indent=2, sort_keys=True)


def annotations_csv(annotations: Iterable[ChartAnnotation]) -> str:
    """Return a simple CSV export without adding a pandas dependency here."""
    rows = ["id,kind,value,label,dash,visible"]
    for item in annotations:
        label = item.label.replace('"', '""')
        rows.append(
            f'{item.id},{item.kind},{item.value},"{label}",{item.dash},{str(item.visible).lower()}'
        )
    return "\n".join(rows) + "\n"
