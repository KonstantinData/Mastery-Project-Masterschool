# Travel Perks Recommendation Pipeline

This repository contains a production‑grade implementation of the
TravelTide perk recommendation project. The goal of the pipeline is to
assign a personalised perk to each user based solely on behavioural
signals observed in booking, session and travel data. The design
follows established best practices: configuration is externalised via
environment variables【599210147542025†L10-L43】, data quality is
enforced through Great Expectations, and reproducibility is achieved
through pinned dependencies and deterministic clustering.

## Quick Start

1. **Install dependencies.** Use a recent version of Python (≥3.8). After
   cloning the repository run:

   ```sh
   pip install .
   ```

2. **Execute the pipeline.** The command line interface is provided by
   `travel_perks` and leverages Click【847812722121003†L11-L59】. The following
   command downloads the public datasets, cleans them, engineers
   features, clusters users and writes results:

   ```sh
   travel_perks execute --run-id demo
   ```

   Outputs will be written to the `data/outputs/` and `data/gold/`
   directories. A PDF report summarising the perk distribution is also
   generated.

## Configuration

Configuration parameters are defined in `travel_perks.config.Settings` and
may be overridden via environment variables or the CLI. Environment
variables must be prefixed with `TRAVEL_PERKS_`. Important fields
include:

| Name            | Description                                           |
|-----------------|-------------------------------------------------------|
| `users_url`     | URL of the raw users CSV                              |
| `sessions_url`  | URL of the raw sessions CSV                           |
| `flights_url`   | URL of the raw flights CSV                            |
| `hotels_url`    | URL of the raw hotels CSV                             |
| `min_sessions`  | Minimum sessions required for cohort inclusion        |
| `start_date`    | Start date (YYYY‑MM‑DD) for cohort filtering          |
| `output_dir`    | Directory for final CSV and PDF artefacts             |
| `gold_dir`      | Directory for the engineered feature table            |
| `logs_dir`      | Directory for structured JSON log files               |
| `seed`          | Random seed for deterministic clustering              |

For example, to use a different minimum session threshold:

```sh
TRAVEL_PERKS_MIN_SESSIONS=10 travel_perks execute
```

## Architecture Overview

The pipeline is broken into modular components under the `travel_perks`
package:

- **config** – Pydantic settings class for configuration management.
- **io** – Robust data loading and persistence functions with retry
  logic.
- **transform** – Cleaning, cohort filtering and feature engineering.
- **segment** – k‑means clustering of user features.
- **assign** – Mapping clusters to human‑readable perks.
- **reporting** – CSV and PDF output generation via ReportLab【582720564345610†L4271-L4314】.
- **pipeline** – Orchestration tying together all modules and enforcing
  data quality checks with Great Expectations【458984376278033†L50-L63】.
- **cli** – Click‑based command line interface for execution.

## Data Quality & Observability

Data quality is enforced via Great Expectations. Before writing any
artefacts the pipeline validates that the engineered feature table
contains non‑null, unique user identifiers and that numeric metrics are
within expected ranges. If any expectation fails the run aborts
immediately.

Structured JSON logs are emitted to both STDOUT and a log file. Each
record includes a timestamp, severity and a correlation identifier to
facilitate troubleshooting. The logging setup uses a custom
``JsonFormatter`` based on the Python logging cookbook【713027300398110†L114-L151】【713027300398110†L968-L1031】.

## Continuous Integration & Testing

Tests are located in the `tests` directory and can be run with

```sh
pytest --cov=travel_perks --cov-report=term-missing
```

The CI workflow defined in `.github/workflows/ci.yml` runs linting,
typing, unit tests and coverage checks. Dependencies are pinned to
specific versions to ensure deterministic behaviour across
environments. A coverage threshold of 85 % is enforced at the gate.

## License

This project is licensed under the MIT License. See the `LICENSE` file
for details.