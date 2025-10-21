"""Reporting utilities for the Travel Perks pipeline.

This module provides functions to write aggregated results to CSV and
generate a simple PDF report using ReportLab. The PDF summarises the
distribution of perks across the user base and can be extended with
additional visuals. Using ReportLab's high‑level API simplifies PDF
generation by assembling document components such as paragraphs and
tables【582720564345610†L4271-L4314】.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


def write_perks_csv(features: pd.DataFrame, path: Path) -> None:
    """Write the final perks assignment to a CSV file.

    The output contains ``user_id``, ``cluster_id`` and ``perk`` columns.

    Parameters
    ----------
    features: pandas.DataFrame
        DataFrame with cluster and perk information.
    path: pathlib.Path
        Destination CSV file.
    """
    # Notes:
    #   This helper extracts only the identifier, cluster and perk
    #   columns from the provided feature table and writes them to
    #   the specified path. It ensures the parent directory exists
    #   before writing. This file is the main consumer‑facing output
    #   containing the recommended perks for each user.
    cols = ["user_id", "cluster_id", "perk"]
    subset = features[cols]
    path.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(path, index=False)


def write_users_features_csv(features: pd.DataFrame, path: Path) -> None:
    """Write the gold (aggregated features) table to CSV.

    Parameters
    ----------
    features: pandas.DataFrame
        DataFrame containing engineered features, cluster IDs and perks.
    path: pathlib.Path
        Destination CSV file.
    """
    # Notes:
    #   The gold table contains engineered features along with
    #   cluster assignments and perks. This function writes the full
    #   DataFrame to disk, ensuring the destination directory exists.
    #   Downstream analytics or dashboards can read this file to
    #   perform deeper analysis of user segments.
    path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(path, index=False)


def generate_pdf_report(features: pd.DataFrame, path: Path) -> None:
    """Generate a simple PDF report summarising perk assignments.

    The report lists the count of users per perk and the proportion
    relative to the whole population. It can be extended with
    visualisations or descriptive text as needed.

    Parameters
    ----------
    features: pandas.DataFrame
        DataFrame containing at least the ``perk`` column.
    path: pathlib.Path
        Destination PDF file.
    """
    # Notes:
    #   Using ReportLab's high‑level APIs, this function constructs
    #   a PDF that summarises the count and share of users per perk.
    #   It creates a `SimpleDocTemplate`, builds a list of
    #   paragraphs and tables and finally calls ``doc.build``. The
    #   parent directory is created if necessary. Extensions to this
    #   report (charts, narratives) can be added by appending more
    #   elements to the `story` list.
    logger = logging.getLogger(__name__)
    logger.info("Generating PDF report at %s", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=letter)
    story = []

    # Title
    story.append(Paragraph("Travel Perks Recommendation Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Summary paragraph
    total_users = len(features)
    story.append(
        Paragraph(
            f"This report summarises the distribution of {total_users} users "
            "across the configured perk recommendations.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 12))

    # Perk counts table
    counts = features["perk"].value_counts().reset_index()
    counts.columns = ["Perk", "User Count"]
    counts["Share"] = (counts["User Count"] / total_users).round(3)
    data = [["Perk", "User Count", "Share"]] + counts.values.tolist()
    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))

    doc.build(story)
    logger.info("PDF report created")