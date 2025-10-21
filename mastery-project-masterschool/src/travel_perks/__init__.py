"""Top‑level package for the Travel Perks recommendation project.

This package contains a modular implementation of the TravelTide perk
recommendation pipeline. It follows Twelve‑Factor principles for
configuration and includes tooling for reproducible data loading,
transformation, segmentation and reporting. See the submodules for
detailed functionality.
"""

from .config import Settings  # noqa: F401
from .pipeline import execute_pipeline  # noqa: F401

__all__ = [
    "Settings",
    "execute_pipeline",
]