.PHONY: help test test-synthetic test-real lint format install-dev clean

help:
	@echo "NEUROSPINE Makefile targets:"
	@echo "  install-dev     - Install dev dependencies (pytest, ruff, mypy)."
	@echo "  test            - Run the full test suite."
	@echo "  test-synthetic  - Run only synthetic-first tests (marker: synthetic)."
	@echo "  test-real       - Run real-data tests (marker: real). CI-only."
	@echo "  lint            - Run ruff and mypy."
	@echo "  format          - Auto-format with ruff."
	@echo "  clean           - Remove build artifacts and caches."

install-dev:
	python3 -m pip install --upgrade pip
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest instrument/tests/ -q

test-synthetic:
	python3 -m pytest instrument/tests/ -q -m synthetic

test-real:
	python3 -m pytest instrument/tests/ -q -m real

lint:
	python3 -m ruff check instrument/
	python3 -m mypy instrument/src/neurospine || true

format:
	python3 -m ruff format instrument/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info instrument/src/*.egg-info
