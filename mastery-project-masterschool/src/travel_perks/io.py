"""Data input/output utilities.

This module provides resilient functions for loading CSV data from
external sources and writing DataFrames to disk. Data is loaded via
pandas using URLs provided by the :class:`~travel_perks.config.Settings`.
Functions implement basic retry logic and propagate exceptions with
contextual logging.

When saving CSVs, directories are created as needed to support
idempotent pipeline runs.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import requests


def read_csv(url: str, retries: int = 3, timeout: int = 30) -> pd.DataFrame:
    """Load a CSV from a given HTTP/S URL using pandas.

    This function implements a simple retry mechanism: if a transient
    network error occurs (e.g. status codes 5xx or connection timeouts),
    it will retry up to ``retries`` times. Client errors (e.g. 4xx)
    are considered fatal and will be raised immediately.

    Parameters
    ----------
    url: str
        The fully qualified URL pointing to the CSV resource.
    retries: int, default 3
        Number of times to retry on transient failures.
    timeout: int, default 30
        Timeout in seconds for the HTTP request.

    Returns
    -------
    pandas.DataFrame
        The loaded DataFrame.
    """
    # Notes:
    #   This function wraps a typical ``pandas.read_csv`` call with
    #   retry logic and explicit HTTP error handling. It first
    #   attempts to download the resource using the ``requests``
    #   library. If the server returns a 5xx error the request is
    #   retried up to the specified number of attempts. A 4xx error
    #   raises immediately since the client request is invalid. On
    #   success the bytes are streamed into pandas via a BytesIO
    #   object. Logging is used throughout to track attempts and
    #   failures.
    logger = logging.getLogger(__name__)
    attempt = 0
    while True:
        attempt += 1
        try:
            # Use requests to precheck the response to avoid pandas mis‑reporting 403s
            resp = requests.get(url, timeout=timeout)
            if resp.status_code >= 500 and attempt <= retries:
                logger.warning(
                    "Transient server error %s on %s (attempt %s/%s)",
                    resp.status_code,
                    url,
                    attempt,
                    retries,
                )
                continue
            resp.raise_for_status()
            # Pass content bytes to pandas
            from io import BytesIO

            return pd.read_csv(BytesIO(resp.content))
        except (requests.exceptions.RequestException, pd.errors.ParserError) as exc:
            if attempt >= retries:
                logger.error("Failed to load CSV from %s after %s attempts: %s", url, attempt, exc)
                raise
            logger.warning(
                "Error reading %s on attempt %s/%s: %s – retrying", url, attempt, retries, exc
            )


def write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to disk as a CSV, creating directories as needed.

    Parameters
    ----------
    df: pandas.DataFrame
        The DataFrame to write.
    path: pathlib.Path
        Destination path for the CSV file.
    """
    # Notes:
    #   This helper ensures that the directory hierarchy for the
    #   destination CSV exists before writing the file. It uses
    #   ``path.parent.mkdir(parents=True, exist_ok=True)`` to create
    #   intermediate directories without raising an exception if they
    #   already exist. Finally it writes the DataFrame to CSV
    #   without an index.
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_raw_data(settings: "Settings") -> Dict[str, pd.DataFrame]:  # noqa: F821
    """Load all raw datasets specified in the settings.

    The returned dictionary contains four keys: ``users``, ``sessions``,
    ``flights`` and ``hotels``. Each key maps to a DataFrame loaded
    from the configured URL.

    Parameters
    ----------
    settings: Settings
        Application settings containing the dataset URLs.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Dictionary mapping table names to DataFrames.
    """
    # Notes:
    #   By iterating over the URLs defined in the Settings object,
    #   this function downloads each CSV via ``read_csv``, logs
    #   progress and builds a dictionary keyed by logical table name.
    #   If any dataset fails to download after retries the exception
    #   bubbles up and stops the pipeline, providing fail‑fast
    #   behaviour.
    logger = logging.getLogger(__name__)
    logger.info("Loading raw datasets from configured URLs")
    data = {}
    for name, url in {
        "users": settings.users_url,
        "sessions": settings.sessions_url,
        "flights": settings.flights_url,
        "hotels": settings.hotels_url,
    }.items():
        logger.info("Loading %s from %s", name, url)
        data[name] = read_csv(url)
        logger.info("Loaded %s with %s records", name, len(data[name]))
    return data