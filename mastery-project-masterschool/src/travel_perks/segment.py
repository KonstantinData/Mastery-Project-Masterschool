"""Clustering and segmentation logic.

Customer segmentation is performed using k‑means clustering on the
engineered behavioural features. The number of clusters is configurable
and the random seed is propagated from the settings to ensure
deterministic results【952685827302670†L49-L58】. Downstream components
may use the ``cluster_id`` column to assign perks.
"""

from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def cluster_users(
    features: pd.DataFrame,
    n_clusters: int = 4,
    seed: int = 42,
) -> Tuple[pd.DataFrame, KMeans]:
    """Apply k‑means clustering to user features.

    Parameters
    ----------
    features: pandas.DataFrame
        User feature table produced by ``engineer_features``.
    n_clusters: int, default 4
        Number of clusters to form.
    seed: int, default 42
        Random seed for initialisation. A fixed seed ensures repeatable
        cluster assignments across runs.

    Returns
    -------
    tuple of (pandas.DataFrame, sklearn.cluster.KMeans)
        The input DataFrame augmented with a ``cluster_id`` column and
        the fitted KMeans model.
    """
    # Notes:
    #   The function first selects all numeric columns excluding
    #   identifiers (``user_id`` and ``cluster_id``) and converts them
    #   into a NumPy array. It then instantiates a ``KMeans`` model
    #   with the given number of clusters and a fixed random seed for
    #   reproducibility. After fitting the model, it appends the
    #   resulting cluster labels to the DataFrame and returns both
    #   the augmented DataFrame and the fitted model. Logging
    #   statements provide basic progress messages.
    logger = logging.getLogger(__name__)
    logger.info("Clustering %s users into %s segments", len(features), n_clusters)
    # Select numerical columns for clustering
    numeric_cols = features.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude identifier columns
    numeric_cols = [c for c in numeric_cols if c not in {"user_id", "cluster_id"}]
    data = features[numeric_cols].to_numpy()
    model = KMeans(n_clusters=n_clusters, random_state=seed, n_init="auto")
    labels = model.fit_predict(data)
    features_with_cluster = features.copy()
    features_with_cluster["cluster_id"] = labels
    logger.info("Finished clustering")
    return features_with_cluster, model