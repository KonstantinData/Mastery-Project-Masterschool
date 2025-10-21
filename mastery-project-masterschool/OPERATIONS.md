# Operations Runbook

This document provides guidance for running and maintaining the Travel
Perks recommendation pipeline in production.

## Running the Pipeline

Use the `travel_perks` CLI to execute the pipeline. At a minimum you
must specify a unique `--run-id` so that artefacts and logs are
namespaced:

```sh
travel_perks execute --run-id 20251021
```

The command loads configuration from environment variables and uses
defaults for any unset fields. To override individual settings, pass
options on the CLI or set `TRAVEL_PERKS_*` variables. For example:

```sh
export TRAVEL_PERKS_SESSIONS_URL=https://example.com/sessions.csv
travel_perks execute --run-id nightly
```

### Dry Run

To test the pipeline without writing any artefacts use the `--dry-run`
flag. This executes all stages and runs data quality checks but skips
CSV and PDF generation. Logs are still emitted to the configured log
directory.

```sh
travel_perks execute --dry-run
```

## Logs & Metrics

Logs are written in structured JSON format to both STDOUT and a file
under `logs/<run-id>.log`. Each entry contains a timestamp, level,
logger name and message, along with a correlation `run_id`. Use tools
like `jq` to filter and inspect logs:

```sh
jq '. | select(.level=="ERROR")' logs/20251021.log
```

Duration metrics for the pipeline are reported at the end of the run
with the `duration_seconds` field. Additional metrics such as row
counts are logged throughout the execution.

## Artefacts

After a successful run (i.e. no data quality failures) the following
artefacts are produced:

| File                                      | Description                             |
|-------------------------------------------|-----------------------------------------|
| `data/gold/users_features_<run-id>.csv`    | Engineered features with clusters & perks |
| `data/outputs/perks_<run-id>.csv`          | Simplified view of user_id → perk        |
| `data/outputs/report_<run-id>.pdf`         | PDF report summarising perk distribution  |

If `--dry-run` is enabled no files are created.

## Failure Modes & Troubleshooting

- **Data download failure.** The pipeline uses HTTP to fetch CSVs. If a
  download fails after all retries the run aborts with an error
  message indicating the failing URL. Verify network connectivity and
  the availability of the remote resource.
- **Data quality failure.** The Great Expectations suite ensures that
  important columns are non‑null and numeric metrics are within
  expected ranges. If validation fails the pipeline terminates and the
  errors are logged. Inspect the log file for details and correct the
  data source.
- **Permission issues.** Ensure that the process user has write
  permission to the configured `output_dir`, `gold_dir` and `logs_dir`.
- **Insufficient resources.** Large datasets may require more memory or
  CPU than available. Monitor resource utilisation and adjust
  environment limits accordingly.

## Rollback & Recovery

To roll back to a previous run, simply reference the artefacts from
that run (identified by its `run-id`). All artefacts are immutable
once written. If an erroneous run overwrites output directories, you
can recover by restoring the older CSVs and report from your backup or
version control system.