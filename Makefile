.PHONY: clean install-dev lint type-check check-code format

clean:
	rm -rf .mypy_cache .pytest_cache __pycache__

install-dev:
	python -m pip install --upgrade pip
	pip install --no-cache-dir --requirement requirements.txt
	pip install --no-cache-dir --requirement requirements-test.txt

lint:
	python3 -m flake8

type-check:
	python3 -m mypy

check-code: lint type-check

format:
	python3 -m isort src tests
	python3 -m autopep8 --in-place --recursive src tests
