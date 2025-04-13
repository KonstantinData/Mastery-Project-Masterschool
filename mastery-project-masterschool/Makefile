# Makefile for common project tasks — S3-native, no local CSV dependencies

.PHONY: help lint format test

help:
	@echo "Available commands:"
	@echo "  make lint        Run Ruff linter"
	@echo "  make format      Auto-format with Ruff"
	@echo "  make test        Run all unit tests"

lint:
	rye run ruff check .

format:
	rye run ruff format .

test:
	rye run pytest tests
