.PHONY: help install install-dev test lint format type-check build clean publish

help:
	@echo "Available commands:"
	@echo "  install     Install package in current environment"
	@echo "  install-dev Install package with dev dependencies"
	@echo "  test        Run tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  type-check  Run type checking with mypy"
	@echo "  build       Build package for distribution"
	@echo "  clean       Clean build artifacts"
	@echo "  publish     Publish to PyPI (requires PYPI_TOKEN)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=passenv --cov-report=term-missing --cov-report=html

lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish: build
	twine check dist/*
	twine upload dist/*