"""Score-band analysis for historical validation."""

from __future__ import annotations

import pandas as pd


DEFAULT_BINS: tuple[float, ...] = (
    0.0,
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
)


def score_bucket_labels(
    bins: tuple[float, ...] = DEFAULT_BINS,
) -> tuple[str, ...]:
    return tuple(
        f"{left:.1f}–{right:.1f}"
        for left, right in zip(bins[:-1], bins[1:])
    )


def bucket_forward_returns(
    frame: pd.DataFrame,
    *,
    score_column: str,
    return_columns: tuple[str, ...],
    bins: tuple[float, ...] = DEFAULT_BINS,
) -> pd.DataFrame:
    """Summarize future returns by normalized score band."""
    missing = {
        score_column,
        *return_columns,
    } - set(frame.columns)
    if missing:
        raise ValueError(
            "Bucket analysis is missing columns: "
            + ", ".join(sorted(missing))
        )

    df = frame.copy()
    labels = score_bucket_labels(bins)
    df["score_bucket"] = pd.cut(
        pd.to_numeric(df[score_column], errors="coerce"),
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True,
    )

    rows: list[dict[str, object]] = []
    grouped = df.groupby("score_bucket", observed=False)

    for bucket, group in grouped:
        row: dict[str, object] = {
            "score_bucket": str(bucket),
            "observations": int(group[score_column].notna().sum()),
            "score_mean": float(group[score_column].mean())
            if group[score_column].notna().any()
            else None,
        }

        for column in return_columns:
            series = pd.to_numeric(group[column], errors="coerce").dropna()
            prefix = column.removeprefix("forward_return_")
            row[f"{prefix}_count"] = int(len(series))
            row[f"{prefix}_mean"] = (
                float(series.mean()) if not series.empty else None
            )
            row[f"{prefix}_median"] = (
                float(series.median()) if not series.empty else None
            )
            row[f"{prefix}_std"] = (
                float(series.std(ddof=1))
                if len(series) > 1
                else None
            )
            row[f"{prefix}_min"] = (
                float(series.min()) if not series.empty else None
            )
            row[f"{prefix}_max"] = (
                float(series.max()) if not series.empty else None
            )

        rows.append(row)

    return pd.DataFrame(rows)
