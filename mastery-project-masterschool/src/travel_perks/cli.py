"""Command‑line interface for the Travel Perks pipeline.

This module leverages the Click library to expose a friendly CLI
wrapping the :func:`~travel_perks.pipeline.execute_pipeline` function.
Click automatically generates usage help pages and handles type
coercion and validation for options【847812722121003†L11-L59】.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from .config import Settings
from .pipeline import execute_pipeline


@click.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Optional path to a JSON configuration file overriding defaults",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False),
    help="Directory where outputs (CSV, PDF) should be written",
)
@click.option(
    "--gold-dir",
    type=click.Path(file_okay=False),
    help="Directory where the engineered gold features should be written",
)
@click.option(
    "--logs-dir",
    type=click.Path(file_okay=False),
    help="Directory where log files should be written",
)
@click.option(
    "--run-id",
    type=str,
    help="Unique identifier for this run; defaults to UTC timestamp if omitted",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Execute the pipeline without writing any outputs to disk",
)
@click.option(
    "--seed",
    type=int,
    default=42,
    show_default=True,
    help="Random seed for deterministic clustering",
)
def execute(
    config_file: Optional[str],
    output_dir: Optional[str],
    gold_dir: Optional[str],
    logs_dir: Optional[str],
    run_id: Optional[str],
    dry_run: bool,
    seed: int,
) -> None:
    """Run the Travel Perks pipeline from the command line.

    Settings can be provided via a JSON file, environment variables or
    individual options. Command line options take precedence over file
    and environment values.
    """
    # Notes:
    #   This Click command constructs a ``Settings`` object either from
    #   a provided JSON configuration file or from environment defaults.
    #   It then applies any CLI overrides for directories, run ID,
    #   dry‑run flag and seed before invoking ``execute_pipeline``.
    #   The function is annotated with Click decorators to provide
    #   descriptive help and input validation for each option.
    # Load base settings
    settings: Settings
    if config_file:
        # Load JSON configuration file
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        settings = Settings(**config_data)
    else:
        settings = Settings()
    # Override directories
    if output_dir:
        settings.output_dir = Path(output_dir)
    if gold_dir:
        settings.gold_dir = Path(gold_dir)
    if logs_dir:
        settings.logs_dir = Path(logs_dir)
    # Override run id and seed
    if run_id:
        settings.run_id = run_id
    settings.seed = seed
    settings.dry_run = dry_run
    # Execute pipeline
    execute_pipeline(settings=settings)


if __name__ == "__main__":  # pragma: no cover
    execute()  # pylint: disable=no-value-for-parameter