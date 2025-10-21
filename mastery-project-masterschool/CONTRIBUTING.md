# Contributing Guide

Thank you for considering a contribution to the Travel Perks
recommendation project! We welcome community contributions that improve
the quality, security and functionality of the code base. This guide
explains how to get started.

## Development Setup

1. **Clone the repository** and install dependencies in an isolated
   environment:

   ```sh
   git clone <repo-url>
   cd mastery-project-masterschool
   pip install --editable .[dev]
   ```

2. **Run the test suite** to ensure your environment is correctly
   configured:

   ```sh
   pytest --cov=travel_perks
   ```

3. **Install pre‑commit hooks** (optional but recommended) to
   automatically format code and check for lint errors:

   ```sh
   pip install pre-commit
   pre-commit install
   ```

## Code Style & Linting

The code base follows PEP 8 conventions and uses type hints. Prior to
submitting a pull request please run the following tools locally:

- `ruff` for static analysis and formatting
- `mypy` for type checking
- `pytest` for tests and coverage (≥ 85 %)

CI will block merges if these checks fail.

## Branching & Pull Requests

1. Create a feature branch from `main`.
2. Make your changes with clear and descriptive commit messages.
3. Write unit tests for any new functionality and update existing
   documentation as needed.
4. Push your branch and open a pull request. The PR template will
   guide you through the required information such as the purpose of
   the change and how it was tested.

## Code Ownership

The `CODEOWNERS` file designates maintainers responsible for reviewing
changes. Assign the appropriate owners on your pull request to
expedite the review process.

We appreciate your efforts to improve the project and look forward to
your contributions!