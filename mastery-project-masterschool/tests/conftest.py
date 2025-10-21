"""Test configuration and fixtures for pytest.

This file defines reusable fixtures for unit tests. Pytest will
automatically discover ``conftest.py`` and make its contents
available to all test modules in the ``tests`` package.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def sample_raw_data() -> dict:
    """Provide small raw datasets for testing pipeline functions.

    The datasets contain only a handful of rows and minimal columns so
    that they can exercise the cohort filtering, feature engineering
    and clustering logic without relying on external resources.
    """
    users = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
        }
    )
    sessions = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2, 2, 3],
            "session_start": pd.to_datetime(
                [
                    "2023-02-01",
                    "2023-02-10",
                    "2023-02-05",
                    "2023-02-20",
                    "2023-03-01",
                    "2023-02-15",
                ]
            ),
        }
    )
    flights = pd.DataFrame(
        {
            "user_id": [1, 2, 2],
            "discount_amount": [50, 0, 20],
            "total_amount": [100, 200, 100],
            "booking_date": pd.to_datetime(["2023-02-01", "2023-02-10", "2023-03-05"]),
        }
    )
    hotels = pd.DataFrame(
        {
            "user_id": [1, 3],
            "check_in": pd.to_datetime(["2023-02-05", "2023-02-12"]),
            "check_out": pd.to_datetime(["2023-02-07", "2023-02-14"]),
            "discount_amount": [0, 10],
            "total_amount": [200, 100],
        }
    )
    return {"users": users, "sessions": sessions, "flights": flights, "hotels": hotels}