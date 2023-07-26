.PHONY: clean install-dev lint type-check check-code format

clean:
	rm -rf .venv .mypy_cache .pytest_cache __pycache__

install-dev:
	python3.11 -m pip install --upgrade pip
	python3.11 -m pip install --no-cache-dir poetry~=1.5.1
	poetry install --no-interaction --no-ansi
	poetry run pre-commit install

lint:
	poetry run flake8

type-check:
	poetry run mypy

check-code: lint type-check

format:
	poetry run isort src tests
	poetry run autopep8 --in-place --recursive src tests
