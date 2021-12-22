# Note that you should be in your virtual environment of choice before running make

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

.DEFAULT_GOAL := all
SHELL := bash

.PHONY: all
all: install-requirements test

.PHONY: install-requirements
install-requirements:
	poetry install

.PHONY: test
test: install-requirements
	poetry run python -m pytest

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .pytest_cache
	rm -rf dist

.PHONY: lint
lint:
	poetry run flake8 --exit-zero --max-line-length 120 pumpkin_py/ tests/
	poetry run black --check --diff pumpkin_py tests
	poetry run isort --check-only --diff pumpkin_py tests

.PHONY: format
format:
	poetry run autoflake \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		--ignore-init-module-imports \
		--in-place pumpkin_py tests
	poetry run isort pumpkin_py tests
	poetry run black pumpkin_py tests

.PHONY: benchmark
benchmark:
	poetry run python benchmarks/benchmark.py

.PHONY: profile
profile:
	poetry run python benchmarks/profiler.py
