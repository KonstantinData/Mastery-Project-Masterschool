# Test Suite

The tests in this directory verify the functionality and reliability
of the TravelTide perk recommendation pipeline. They are implemented
with `pytest` and aim to achieve high coverage across all modules.

## Structure

| Test File              | Purpose |
|------------------------|---------|
| **conftest.py**        | Provides shared fixtures, including sample raw data used by multiple tests. |
| **test_config.py**     | Ensures configuration values are correctly loaded and environment overrides work. |
| **test_io.py**         | Validates the CSV read/write helpers using temporary files. |
| **test_transform.py**  | Tests cleaning, cohort filtering and feature engineering logic. |
| **test_segment_assign.py** | Verifies clustering and perk assignment produce expected results. |
| **test_pipeline.py**   | Runs the full pipeline in dry‑run mode with mocked data to assert integration correctness. |

## Running the Tests

To execute the test suite with coverage, run:

```bash
pytest --cov=travel_perks --cov-report=term-missing
```

The continuous integration workflow enforces a minimum coverage
threshold of 85 % and runs linting and type checking before executing
the tests.