"""Perk assignment logic.

Once users have been segmented into clusters, we map each cluster to a
particular perk. The mapping can be configured externally or use the
default mapping defined here. The assignment is implemented as a
vectorised DataFrame operation for efficiency.
"""

from __future__ import annotations

import logging
from typing import Dict

import pandas as pd


DEFAULT_PERK_MAPPING: Dict[int, str] = {
    0: "Free checked bag",
    1: "No cancellation fees",
    2: "Exclusive discounts",
    3: "One night free hotel with flight",
}


def assign_perks(features: pd.DataFrame, mapping: Dict[int, str] = DEFAULT_PERK_MAPPING) -> pd.DataFrame:
    """Assign perks to users based on their cluster membership.

    Parameters
    ----------
    features: pandas.DataFrame
        DataFrame containing a ``cluster_id`` column.
    mapping: dict, default ``DEFAULT_PERK_MAPPING``
        Dictionary mapping cluster indices to human‑readable perk names.

    Returns
    -------
    pandas.DataFrame
        DataFrame with an additional ``perk`` column.
    """
    # Notes:
    #   This function attaches a human‑readable perk to each user based on the
    #   ``cluster_id`` column. It first checks that the column exists and
    #   then uses the mapping dictionary (either the default or a custom
    #   provided mapping) to translate cluster indices into descriptive
    #   perk labels. If a cluster is not found in the mapping the perk
    #   defaults to ``"Unknown"``. The function returns a copy of the
    #   input DataFrame to preserve immutability of upstream data.
    logger = logging.getLogger(__name__)
    if "cluster_id" not in features.columns:
        raise ValueError("cluster_id column missing from features")
    features_with_perk = features.copy()
    features_with_perk["perk"] = features_with_perk["cluster_id"].map(mapping).fillna("Unknown")
    logger.info("Assigned perks based on cluster mapping")
    return features_with_perk