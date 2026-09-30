.DEFAULT_GOAL := help
.PHONY: help setup hooks lint format test check

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

setup:  ## Install dependencies (dev + notebooks groups)
	uv sync --group notebooks

hooks:  ## Strip notebook outputs automatically on commit (run once, inside the git repo)
	uv run nbstripout --install

lint:  ## Check code style and common errors
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-format the code
	uv run ruff check --fix .
	uv run ruff format .

test:  ## Run the test suite
	uv run pytest

check: lint test  ## Run lint and tests (same as CI)
