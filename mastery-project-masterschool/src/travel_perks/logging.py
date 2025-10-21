"""Structured JSON logging utilities.

The logging setup implemented here builds upon the standard Python
``logging`` library and follows recommendations from the Python
documentation on logging best practices【713027300398110†L114-L151】. Each
log entry is serialized as a JSON object containing a timestamp,
severity level, logger name and message. Additional contextual fields
such as a run identifier can be attached via a ``LoggerAdapter``.

The JSON formatter facilitates ingestion into log aggregation systems
and simplifies downstream parsing for observability and metrics. Users
can direct logs to both STDOUT and a file on disk by calling
``setup_logging``.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    """Format ``LogRecord`` instances as JSON strings.

    The formatter serializes the timestamp in ISO 8601 format and
    includes all extra attributes attached to the record. Standard log
    attributes are excluded unless explicitly added via the ``extra``
    argument when logging.
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        # Notes:
        #   This override takes a ``LogRecord`` and returns a JSON string.
        #   It assembles a dictionary containing a UTC timestamp,
        #   log level, logger name and message. Any additional
        #   attributes set on the record (for example via ``LoggerAdapter``)
        #   are copied into the dictionary, except for internal
        #   attributes and metadata that are not useful for log analysis.
        record_dict: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Attach extra context
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in {
                "args",
                "msg",
                "message",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                continue
            record_dict[key] = value
        return json.dumps(record_dict)


def setup_logging(log_file: Optional[str] = None, run_id: Optional[str] = None) -> logging.Logger:
    """Configure the root logger for JSON formatted logging.

    Parameters
    ----------
    log_file: Optional[str]
        Optional path to a file where logs should be written. When
        ``None``, logs are only emitted to STDOUT.
    run_id: Optional[str]
        Identifier attached to every log record via a ``LoggerAdapter``. This
        correlation ID simplifies tracing across modules and functions and
        aligns with the recommendation to use contextual logging
        adapters【713027300398110†L968-L1031】.

    Returns
    -------
    logging.Logger
        A logger configured with a JSON formatter.
    """
    # Notes:
    #   The ``setup_logging`` function configures the root logger to output
    #   JSON formatted logs. It removes any existing handlers to avoid
    #   duplicate messages, adds a stream handler for STDOUT and
    #   conditionally adds a file handler if a file path is provided.
    #   When a ``run_id`` is supplied, the logger is wrapped in a
    #   ``LoggerAdapter`` so that the run identifier is included on
    #   every emitted record. The configured logger is returned for
    #   further use.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Remove existing handlers to avoid duplicate logs when reinitializing
    while logger.handlers:
        logger.handlers.pop()

    formatter = JsonFormatter()
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Wrap with LoggerAdapter to add run_id to log records
    if run_id:
        return logging.LoggerAdapter(logger, {"run_id": run_id})  # type: ignore[return-value]
    return logger