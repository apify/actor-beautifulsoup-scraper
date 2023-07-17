# Development

## Environment

For local development, it is required to have Python 3.10 and newer installed.

It is recommended to set up a virtual environment while developing this Actor to isolate your development environment, however, due to the many varied ways Python can be installed and virtual environments can be set up, this is left up to the developers to do themselves.

One recommended way is with the built-in `venv` module.

### Venv environment

Create it with Python 3.11:

```bash
python3.11 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Check that `python` and `pip` points to the `.venv` location:

```bash
which python
```

```bash
which pip
```

## Dependencies

Install dependencies to run this Actor locally:

```bash
pip install -r requirements.txt
```

Install development/test dependencies:

```bash
pip install -r requirements-dev.txt
```

## Local execution

Run the Actor using [Apify CLI](https://docs.apify.com/cli/):

```bash
apify run --purge
```

## Formatting

We use [black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/) to automatically format the code to a common format. All tools are configured in the `pyproject.toml`.

```
black src/
```

```
isort src/
```

## Linting and type-checking

We use [pylint](https://pypi.org/project/pylint/) for linting and [mypy](https://pypi.org/project/mypy/) for type checking.

```
pylint src/
```

```
mypy src/
```

## Documentation

We use the [Google docstring format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for documenting the code. We document every user-facing class or method.
