"""Tests for score-band validation."""

import pandas as pd

from obrm.validation.buckets import bucket_forward_returns


def test_bucket_analysis_summarizes_returns() -> None:
    frame = pd.DataFrame(
        {
            "score": [0.1, 0.15, 0.85, 0.9],
            "forward_return_365d": [1.0, 0.8, -0.2, -0.1],
        }
    )

    result = bucket_forward_returns(
        frame,
        score_column="score",
        return_columns=("forward_return_365d",),
    )

    low = result.loc[result["score_bucket"] == "0.0–0.2"].iloc[0]
    high = result.loc[result["score_bucket"] == "0.8–1.0"].iloc[0]

    assert low["365d_mean"] > high["365d_mean"]
