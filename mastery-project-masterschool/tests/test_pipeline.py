"""Integration tests for the full pipeline."""

from __future__ import annotations

import types

import pandas as pd

from travel_perks.config import Settings
from travel_perks.pipeline import execute_pipeline


def test_execute_pipeline_dry_run(monkeypatch, tmp_path, sample_raw_data):
    """Run the pipeline end‑to‑end in dry‑run mode using mocked data."""
    # Monkeypatch load_raw_data to return our sample data
    from travel_perks import io as io_module

    def fake_load_raw_data(settings: Settings) -> dict:
        return sample_raw_data

    monkeypatch.setattr(io_module, "load_raw_data", fake_load_raw_data)
    # Configure settings to use tmp directories
    settings = Settings()
    settings.output_dir = tmp_path / "outputs"
    settings.gold_dir = tmp_path / "gold"
    settings.logs_dir = tmp_path / "logs"
    settings.dry_run = True
    settings.min_sessions = 1
    # Execute pipeline
    result = execute_pipeline(settings=settings)
    # Validate result columns
    assert {
        "user_id",
        "total_sessions",
        "total_bookings",
        "total_nights",
        "avg_discount_rate",
        "cluster_id",
        "perk",
    }.issubset(result.columns)
    # Ensure no files were created
    assert not (settings.output_dir).exists() or not any(settings.output_dir.iterdir())