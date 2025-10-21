"""Tests for the I/O module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

from travel_perks.io import read_csv, write_csv


def test_read_write_csv(tmp_path):
    """Round‑trip a CSV through write_csv and read_csv."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    out_path = tmp_path / "data.csv"
    # Write using our helper
    write_csv(df, out_path)
    # Read back using read_csv via file URI
    loaded = read_csv(out_path.as_uri())
    pd.testing.assert_frame_equal(df, loaded)