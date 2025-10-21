"""Tests for configuration loading and validation."""

from __future__ import annotations

import os

from travel_perks.config import Settings


def test_settings_env_override(monkeypatch):
    """Environment variables override default configuration."""
    monkeypatch.setenv("TRAVEL_PERKS_MIN_SESSIONS", "10")
    settings = Settings()
    assert settings.min_sessions == 10
    # cleanup: environment variables are automatically reset by monkeypatch