"""Configuration management for the Travel Perks pipeline.

This module defines a :class:`Settings` class based on Pydantic's
``BaseSettings`` which reads configuration from environment variables,
defaults and optional YAML files. Keeping configuration external to
the code base is a core practice of the Twelve‑Factor App philosophy
【599210147542025†L10-L43】. Environment variables allow you to change
resource handles, input URLs or thresholds without modifying code or
checking secrets into version control.

You can supply configuration via the ``TRAVEL_PERKS_*`` environment
variables or override values on the CLI. See ``travel_perks.cli`` for
command‑line usage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes
    ----------
    users_url: str
        Public HTTPS URL pointing to the raw users CSV.
    sessions_url: str
        Public HTTPS URL pointing to the raw sessions CSV.
    flights_url: str
        Public HTTPS URL pointing to the raw flights CSV.
    hotels_url: str
        Public HTTPS URL pointing to the raw hotels CSV.
    min_sessions: int
        Minimum number of sessions required for a user to be included in
        the cohort. Defaults to 7 as defined in the project description.
    start_date: str
        ISO format date (YYYY‑MM‑DD) representing the start of the
        observation window. Records earlier than this date are ignored.
    output_dir: Path
        Directory where final CSV and PDF outputs are written.
    gold_dir: Path
        Directory where intermediate feature tables (gold layer) are written.
    logs_dir: Path
        Directory where log files are written.
    run_id: Optional[str]
        Unique identifier for a particular pipeline run. When not set,
        defaults to ``None`` and will be assigned during execution.
    dry_run: bool
        When ``True``, the pipeline will execute all steps but will not
        persist any artifacts to disk. Useful for testing.
    seed: int
        Random seed used for reproducible clustering. Determinism is
        important for reliable behaviour across runs【952685827302670†L49-L58】.
    """

    # Input data
    users_url: str = Field(
        default="https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_users_export_2025-04-01_101058.csv",
        description="URL for the raw users CSV",
    )
    sessions_url: str = Field(
        default="https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_sessions_export_2025-03-31_221253.csv",
        description="URL for the raw sessions CSV",
    )
    flights_url: str = Field(
        default="https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_flights_export_2025-03-31_134734.csv",
        description="URL for the raw flights CSV",
    )
    hotels_url: str = Field(
        default="https://lakehouse-masteryproject-2025.s3.eu-north-1.amazonaws.com/bronze/public_hotels_export_2025-03-31_171805.csv",
        description="URL for the raw hotels CSV",
    )

    # Cohort filtering
    min_sessions: int = Field(7, description="Minimum sessions threshold for cohort filtering")
    start_date: str = Field("2023-01-04", description="Start date for cohort filtering (inclusive)")

    # Paths
    output_dir: Path = Field(Path("data/outputs"), description="Path to output directory")
    gold_dir: Path = Field(Path("data/gold"), description="Path to gold feature directory")
    logs_dir: Path = Field(Path("logs"), description="Path to log directory")

    # Execution behaviour
    run_id: Optional[str] = Field(None, description="Unique identifier for the current run")
    dry_run: bool = Field(False, description="If true, do not write outputs to disk")
    seed: int = Field(42, description="Random seed for deterministic behaviour")

    class Config:
        env_prefix = "TRAVEL_PERKS_"
        case_sensitive = False

    @validator("start_date")
    def validate_date(cls, v: str) -> str:  # noqa: D417
        """Validate that the start date is in ISO format.

        A simple string check is sufficient here because parsing will
        occur later in the pipeline using pandas.
        """
        # Notes:
        #   Validators in Pydantic allow custom pre‑ or post‑processing
        #   of field values. This validator ensures the `start_date`
        #   attribute conforms to the `YYYY-MM-DD` format by checking
        #   delimiters and length. It does not parse the date; full
        #   parsing is deferred to pandas which provides robust date
        #   handling. Raising a ``ValueError`` triggers a validation
        #   error on the settings object if the format is invalid.
        if len(v) != 10 or v[4] != "-" or v[7] != "-":
            raise ValueError("start_date must be in YYYY-MM-DD format")
        return v

    def ensure_directories(self) -> None:
        """Ensure that output, gold and logs directories exist.

        When operating in a container with a read‑only filesystem, the
        parent process should prepare these directories. However, in most
        development and CI environments the code can create missing
        directories on demand.
        """
        # Notes:
        #   This method iterates over the configured directory paths
        #   (``output_dir``, ``gold_dir`` and ``logs_dir``) and
        #   invokes ``mkdir`` with ``parents=True`` and
        #   ``exist_ok=True``. This creates the directory hierarchy if
        #   it does not already exist and prevents errors on
        #   subsequent writes. It enables idempotent pipeline runs
        #   across different environments where directories may be
        #   absent initially.
        for path in [self.output_dir, self.gold_dir, self.logs_dir]:
            path.mkdir(parents=True, exist_ok=True)