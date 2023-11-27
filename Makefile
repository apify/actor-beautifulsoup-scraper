.PHONY: clean install-dev lint type-check check-code format

DIRS_WITH_CODE = src

clean:
	rm -rf .venv .mypy_cache .pytest_cache .ruff_cache __pycache__

install-dev:
	python3.11 -m pip install --upgrade pip
	python3.11 -m pip install --no-cache-dir poetry~=1.7.1
	poetry install --no-interaction --no-ansi
	poetry run pre-commit install

lint:
	poetry run ruff check $(DIRS_WITH_CODE)

type-check:
	poetry run mypy $(DIRS_WITH_CODE)

check-code: lint type-check

format:
	poetry run ruff check --fix $(DIRS_WITH_CODE)
	poetry run ruff format $(DIRS_WITH_CODE)
