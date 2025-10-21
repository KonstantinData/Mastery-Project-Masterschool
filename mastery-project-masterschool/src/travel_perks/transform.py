"""Data cleaning, cohort filtering and feature engineering.

This module contains pure functions to transform raw TravelTide data into
aggregated user‑level features suitable for clustering. Each function
accepts and returns pandas DataFrames and avoids side effects,
facilitating unit testing and reproducibility. Where appropriate, the
functions use type conversions and date parsing consistent with the
pandas user guide.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd


def clean_tables(
    users: pd.DataFrame, sessions: pd.DataFrame, flights: pd.DataFrame, hotels: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Perform basic cleaning and type conversions on raw tables.

    The following actions are applied:

    * Convert date columns to pandas ``datetime`` objects using
      ``pd.to_datetime``.
    * Drop duplicate rows to ensure uniqueness.
    * Standardise column names to lower‑case for consistency.

    Parameters
    ----------
    users, sessions, flights, hotels : pandas.DataFrame
        Raw data tables.

    Returns
    -------
    tuple of pandas.DataFrame
        Cleaned tables in the same order as input.
    """
    # Notes:
    #   This function performs a series of non‑destructive cleaning
    #   operations. Column names are normalised to lower case and
    #   duplicates are removed to simplify downstream processing.
    #   Known date columns are converted to pandas datetime objects
    #   using ``pd.to_datetime`` with ``errors='coerce'`` so that
    #   invalid dates become NaT rather than raising exceptions.
    logger = logging.getLogger(__name__)
    logger.info("Cleaning raw tables")

    def _std_cols(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        return df

    users_c = _std_cols(users).drop_duplicates()
    sessions_c = _std_cols(sessions).drop_duplicates()
    flights_c = _std_cols(flights).drop_duplicates()
    hotels_c = _std_cols(hotels).drop_duplicates()

    # Convert known date columns to datetime
    for df, date_cols in [
        (sessions_c, ["session_start", "session_end", "timestamp"]),
        (flights_c, ["departure_date", "arrival_date", "booking_date", "check_in", "check_out"]),
        (hotels_c, ["check_in", "check_out", "booking_date"]),
    ]:
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    return users_c, sessions_c, flights_c, hotels_c


def filter_cohort(
    users: pd.DataFrame,
    sessions: pd.DataFrame,
    min_sessions: int,
    start_date: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Filter tables to include only users meeting the cohort criteria.

    Users must have at least ``min_sessions`` sessions on or after
    ``start_date`` to qualify. Sessions prior to ``start_date`` are
    excluded from the count. Both the users and sessions tables are
    returned filtered to the qualifying user_ids.

    Parameters
    ----------
    users: pandas.DataFrame
        Cleaned users table.
    sessions: pandas.DataFrame
        Cleaned sessions table.
    min_sessions: int
        Minimum sessions threshold.
    start_date: str
        ISO date string (YYYY‑MM‑DD) marking the start of the window.

    Returns
    -------
    tuple of pandas.DataFrame
        Filtered users and sessions tables.
    """
    # Notes:
    #   Cohort filtering is based solely on session activity. First
    #   sessions are limited to those on or after the specified
    #   start date. Then users with a session count greater than or
    #   equal to ``min_sessions`` are retained. Both the users and
    #   sessions DataFrames are subsetted to this qualifying set of
    #   user_ids. This function does not modify flights or hotels
    #   directly; they are filtered later when engineering features.
    logger = logging.getLogger(__name__)
    logger.info(
        "Filtering users to those with at least %s sessions on or after %s",
        min_sessions,
        start_date,
    )
    try:
        cutoff = pd.to_datetime(start_date)
    except Exception as exc:
        raise ValueError(f"Invalid start_date {start_date}: {exc}") from exc

    # Filter sessions to the time window
    sessions_in_window = sessions.loc[
        (sessions["session_start"].notna()) & (sessions["session_start"] >= cutoff)
    ].copy()
    counts = sessions_in_window.groupby("user_id").size().reset_index(name="session_count")
    qualifying_users = counts.loc[counts["session_count"] >= min_sessions, "user_id"]
    users_filt = users[users["user_id"].isin(qualifying_users)].copy()
    sessions_filt = sessions[sessions["user_id"].isin(qualifying_users)].copy()
    logger.info("Selected %s users for the cohort", len(users_filt))
    return users_filt, sessions_filt


def engineer_features(
    users: pd.DataFrame, sessions: pd.DataFrame, flights: pd.DataFrame, hotels: pd.DataFrame
) -> pd.DataFrame:
    """Compute user‑level behavioural features.

    Aggregated features include counts of sessions and bookings, total
    nights stayed and average discount rate across all flights and
    hotels. Missing values are filled with zeros. The resulting
    DataFrame has one row per user_id.

    Parameters
    ----------
    users: pandas.DataFrame
        Filtered users table.
    sessions: pandas.DataFrame
        Sessions table restricted to qualifying users.
    flights: pandas.DataFrame
        Cleaned flights table.
    hotels: pandas.DataFrame
        Cleaned hotels table.

    Returns
    -------
    pandas.DataFrame
        Aggregated user features.
    """
    # Notes:
    #   Feature engineering aggregates behavioural data into a single
    #   row per user. Session counts, booking counts and total nights
    #   stayed are computed via groupby operations. Average discount
    #   rate is calculated across both flights and hotels when
    #   ``discount_amount`` and ``total_amount`` columns are present.
    #   Missing values are filled with zeros to avoid NaNs, and
    #   intermediate columns are dropped after computing the final
    #   ``total_bookings`` feature.
    logger = logging.getLogger(__name__)
    logger.info("Engineering user‑level features")

    # Sessions per user
    sessions_counts = sessions.groupby("user_id").size().reset_index(name="total_sessions")

    # Flight bookings per user
    flights_counts = flights.groupby("user_id").size().reset_index(name="flight_bookings")

    # Hotel bookings per user
    hotels_counts = hotels.groupby("user_id").size().reset_index(name="hotel_bookings")

    # Total nights from hotel stays
    if {"check_in", "check_out"}.issubset(hotels.columns):
        hotels_nights = hotels.copy()
        hotels_nights["nights"] = (
            (hotels_nights["check_out"] - hotels_nights["check_in"]).dt.days.clip(lower=0)
        )
        nights_per_user = hotels_nights.groupby("user_id")["nights"].sum().reset_index(name="total_nights")
    else:
        nights_per_user = pd.DataFrame({"user_id": [], "total_nights": []})

    # Discount rates from bookings (assumes discount_amount and total_amount columns exist)
    discount_frames: Iterable[pd.DataFrame] = []
    for df in [flights, hotels]:
        if {"discount_amount", "total_amount", "user_id"}.issubset(df.columns):
            tmp = df.copy()
            tmp["discount_rate"] = tmp["discount_amount"] / tmp["total_amount"].replace({0: np.nan})
            discount_frames.append(tmp[["user_id", "discount_rate"]])
    if discount_frames:
        discounts = pd.concat(discount_frames)
        avg_discount = discounts.groupby("user_id")["discount_rate"].mean().reset_index(
            name="avg_discount_rate"
        )
    else:
        avg_discount = pd.DataFrame({"user_id": [], "avg_discount_rate": []})

    # Merge all features
    features = users[["user_id"]].drop_duplicates().copy()
    for df in [sessions_counts, flights_counts, hotels_counts, nights_per_user, avg_discount]:
        features = features.merge(df, on="user_id", how="left")
    # Replace NaNs with zeros
    features = features.fillna(0)
    # Calculate total bookings (flights + hotels)
    features["total_bookings"] = features["flight_bookings"] + features["hotel_bookings"]
    # Drop intermediate columns
    features = features.drop(columns=["flight_bookings", "hotel_bookings"], errors="ignore")
    logger.info("Generated feature table with %s users", len(features))
    return features