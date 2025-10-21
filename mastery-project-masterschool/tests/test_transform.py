"""Tests for data cleaning, filtering and feature engineering."""

from __future__ import annotations

import pandas as pd

from travel_perks.transform import clean_tables, engineer_features, filter_cohort


def test_cohort_filter(sample_raw_data):
    users_c, sessions_c, flights_c, hotels_c = clean_tables(
        sample_raw_data["users"],
        sample_raw_data["sessions"],
        sample_raw_data["flights"],
        sample_raw_data["hotels"],
    )
    # min_sessions=2 for test, cut off start_date early so all sessions count
    users_filt, sessions_filt = filter_cohort(users_c, sessions_c, 2, "2023-01-01")
    # Users 1 and 2 should remain; user 3 has only one session
    assert set(users_filt["user_id"]) == {1, 2}
    assert sessions_filt["user_id"].nunique() == 2


def test_engineer_features(sample_raw_data):
    users_c, sessions_c, flights_c, hotels_c = clean_tables(
        sample_raw_data["users"],
        sample_raw_data["sessions"],
        sample_raw_data["flights"],
        sample_raw_data["hotels"],
    )
    # Filter with min_sessions=1 to keep all
    users_filt, sessions_filt = filter_cohort(users_c, sessions_c, 1, "2023-01-01")
    feats = engineer_features(users_filt, sessions_filt, flights_c, hotels_c)
    # There should be one row per user
    assert len(feats) == len(users_filt)
    # Check that computed columns exist
    expected_cols = {
        "user_id",
        "total_sessions",
        "total_bookings",
        "total_nights",
        "avg_discount_rate",
    }
    assert expected_cols.issubset(feats.columns)