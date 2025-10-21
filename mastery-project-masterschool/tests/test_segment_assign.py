"""Tests for clustering and perk assignment."""

from __future__ import annotations

import pandas as pd

from travel_perks.assign import assign_perks, DEFAULT_PERK_MAPPING
from travel_perks.segment import cluster_users


def test_cluster_users():
    # Two users with distinct features -> expect two different clusters
    feats = pd.DataFrame(
        {
            "user_id": [1, 2],
            "total_sessions": [10, 1],
            "total_bookings": [5, 0],
            "total_nights": [7, 1],
            "avg_discount_rate": [0.2, 0.0],
        }
    )
    clustered, model = cluster_users(feats, n_clusters=2, seed=0)
    assert "cluster_id" in clustered.columns
    # There should be exactly 2 clusters assigned
    assert set(clustered["cluster_id"]) == {0, 1}


def test_assign_perks():
    feats = pd.DataFrame({"cluster_id": [0, 1, 2, 3]})
    result = assign_perks(feats)
    assert list(result["perk"]) == [
        DEFAULT_PERK_MAPPING[0],
        DEFAULT_PERK_MAPPING[1],
        DEFAULT_PERK_MAPPING[2],
        DEFAULT_PERK_MAPPING[3],
    ]