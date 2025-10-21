"""End‑to‑end pipeline orchestration.

The `execute_pipeline` function ties together all components of the
Travel Perks project. It handles configuration, logging, data
ingestion, transformation, clustering, perk assignment, data quality
validation and artifact generation. The pipeline is idempotent: given
the same inputs and configuration it will always produce the same
outputs thanks to seeded randomness and deterministic operations.

Reliability and observability are core concerns. Logs include a
``run_id`` correlation identifier and timings for each stage. Data
quality tests powered by Great Expectations enforce that the
engineered feature table satisfies expected constraints before any
recommendations are persisted. A failure in the expectations will
abort the pipeline and raise a descriptive exception.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import great_expectations as gx  # type: ignore
import pandas as pd

from .assign import assign_perks
from .config import Settings
from .io import load_raw_data, write_csv
from .logging import setup_logging
from .reporting import (
    generate_pdf_report,
    write_perks_csv,
    write_users_features_csv,
)
from .segment import cluster_users
from .schemas import UserFeatures
from .transform import clean_tables, engineer_features, filter_cohort


def validate_features(features: pd.DataFrame) -> None:
    """Validate the engineered features using Great Expectations.

    Expect that user_id is non‑null and unique, total_sessions and
    total_bookings are non‑negative integers, total_nights is a
    non‑negative integer and avg_discount_rate is between 0 and 1.

    A failure in any expectation will raise a ``great_expectations``
    ``ExpectationValidationError``.
    """
    # Notes:
    #   This function sets up an in‑memory Great Expectations context
    #   and defines a suite of expectations to validate the feature
    #   DataFrame. It checks for non‑null and unique ``user_id`` values,
    #   non‑negative session, booking and night counts and ensures
    #   the discount rate is bounded between 0 and 1. If the
    #   validation fails the function raises an exception which
    #   halts the pipeline. Users can extend or modify these
    #   expectations by editing this function.
    # Create an in‑memory DataFrame asset
    context = gx.get_context()
    datasource = context.sources.add_pandas(name="mem")
    asset = datasource.add_dataframe_asset("features", dataframe=features)
    suite = asset.add_expectation_suite("feature_suite")
    suite.add_expectation(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "user_id"},
    )
    suite.add_expectation(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "user_id"},
    )
    for col in ["total_sessions", "total_bookings", "total_nights"]:
        suite.add_expectation(
            expectation_type="expect_column_values_to_be_between",
            kwargs={"column": col, "min_value": 0},
        )
    suite.add_expectation(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "avg_discount_rate", "min_value": 0.0, "max_value": 1.0},
    )
    # Run the validation
    validator = context.get_validator(
        batch_request=asset.build_batch_request(), expectation_suite=suite
    )
    result = validator.validate()
    if not result.validation_success:
        raise gx.exceptions.ExpectationValidationError(
            "Feature validation failed", validation_result=result
        )


def execute_pipeline(settings: Optional[Settings] = None) -> pd.DataFrame:
    """Run the full Travel Perks pipeline.

    Parameters
    ----------
    settings: Settings, optional
        Optional settings instance. When ``None``, a new instance is
        created from environment variables.

    Returns
    -------
    pandas.DataFrame
        DataFrame of user features with cluster and perk assignments.
    """
    # Notes:
    #   The `execute_pipeline` function orchestrates the entire
    #   end‑to‑end workflow. It initialises configuration and logging,
    #   loads raw data, cleans and filters it, engineers features,
    #   clusters users and assigns perks. Data quality validation is
    #   performed before any artefacts are written. When not in
    #   dry‑run mode, the function writes CSV and PDF outputs and logs
    #   run duration. The function returns the final DataFrame for
    #   additional inspection or testing.
    # Initialise settings
    settings = settings or Settings()
    if not settings.run_id:
        settings.run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    # Ensure directories exist
    settings.ensure_directories()
    # Configure logging
    log_path = None if settings.dry_run else str(settings.logs_dir / f"{settings.run_id}.log")
    logger = setup_logging(log_file=log_path, run_id=settings.run_id)
    start_time = time.perf_counter()
    logger.info("Starting Travel Perks pipeline", extra={"stage": "start"})

    # Load raw data
    raw = load_raw_data(settings)

    # Clean tables
    users_c, sessions_c, flights_c, hotels_c = clean_tables(
        raw["users"], raw["sessions"], raw["flights"], raw["hotels"]
    )

    # Filter cohort
    users_filt, sessions_filt = filter_cohort(
        users_c, sessions_c, settings.min_sessions, settings.start_date
    )

    # Engineer features
    features = engineer_features(users_filt, sessions_filt, flights_c, hotels_c)
    # Compute total bookings for each user
    # Clustering
    features, model = cluster_users(features, n_clusters=4, seed=settings.seed)
    # Assign perks
    features = assign_perks(features)
    # Validate features with GE
    try:
        validate_features(features)
    except gx.exceptions.ExpectationValidationError as exc:
        logger.error("Data quality checks failed: %s", exc)
        raise

    # Write outputs (if not dry run)
    if not settings.dry_run:
        perks_csv_path = settings.output_dir / f"perks_{settings.run_id}.csv"
        users_features_path = settings.gold_dir / f"users_features_{settings.run_id}.csv"
        pdf_path = settings.output_dir / f"report_{settings.run_id}.pdf"
        write_perks_csv(features, perks_csv_path)
        write_users_features_csv(features, users_features_path)
        generate_pdf_report(features, pdf_path)
        logger.info(
            "Wrote outputs to %s and %s and generated report %s",
            perks_csv_path,
            users_features_path,
            pdf_path,
        )

    # Record end of run
    duration = time.perf_counter() - start_time
    logger.info("Pipeline completed", extra={"stage": "end", "duration_seconds": round(duration, 2)})
    return features