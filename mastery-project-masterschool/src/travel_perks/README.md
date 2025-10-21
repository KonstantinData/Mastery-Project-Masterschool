# travel_perks package

This directory contains the source code for the TravelTide perk
recommendation pipeline. Each module in the package has a specific
responsibility and together they form a complete end‑to‑end
workflow. All code is thoroughly documented with module level
docstrings and inline ``# Notes`` comments to aid understanding.

## Submodules

| Module           | Purpose |
|------------------|---------|
| **config**       | Defines the `Settings` class which centralises configuration values and reads from environment variables. |
| **logging**      | Implements a custom JSON log formatter and a helper to configure structured logging. |
| **io**           | Contains helpers for loading raw CSV data and writing DataFrames to disk with retry logic. |
| **transform**    | Provides functions for cleaning raw tables, filtering cohorts and engineering user‑level features. |
| **segment**      | Applies k‑means clustering to the engineered features to segment users. |
| **assign**       | Maps cluster labels to human‑readable perk descriptions. |
| **reporting**    | Generates CSV artefacts and a PDF report summarising perk distribution using ReportLab. |
| **pipeline**     | Orchestrates the entire workflow from ingestion to reporting and validates data quality. |
| **cli**          | Exposes a Click command to run the pipeline from the command line. |

## Usage

After installing the package via `pip install .` you can import
individual modules for use in your own scripts or use the CLI for a
turn‑key solution. For example:

```python
from travel_perks.pipeline import execute_pipeline
from travel_perks.config import Settings

settings = Settings()
df = execute_pipeline(settings=settings)
```

Alternatively, run the CLI:

```bash
travel_perks execute --run-id 20251021
```

This will produce artefacts in the `data/` directory relative to the
project root.