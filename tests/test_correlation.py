"""Tests for redundancy diagnostics."""

import pandas as pd
import pytest

from obrm.validation.correlation import (
    correlation_matrix,
    maximum_absolute_correlation,
)


def test_maximum_absolute_correlation_finds_strongest_signal() -> None:
    frame = pd.DataFrame(
        {
            "candidate": [1, 2, 3, 4],
            "existing_a": [1, 2, 3, 4],
            "existing_b": [4, 1, 3, 2],
        }
    )
    matrix = correlation_matrix(
        frame,
        ("candidate", "existing_a", "existing_b"),
    )
    name, value = maximum_absolute_correlation(matrix, "candidate")

    assert name == "existing_a"
    assert value == pytest.approx(1.0)
