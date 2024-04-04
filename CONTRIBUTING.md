# Development

## Environment

To ensure smooth local development, we highly recommend installing Python 3.12
since the app has been written and tested for compatibility with this version.

We use [Poetry](https://python-poetry.org/) for project management.

## Dependencies

Use make command `install-dev` for installing all the necessary dependencies
(Poetry and other Python packages specified in `pyproject.toml`):

```bash
make install-dev
```

## Local execution

Prepare a `storage/key_value_stores/default/INPUT.json` file, here is an example:

```json
{
  "startUrls": [{ "url": "https://crawlee.dev/" }],
  "maxCrawlingDepth": 1,
  "linkSelector": "a[href]",
  "linkPatterns": [".*crawlee\\.dev.*"],
  "proxyConfiguration": { "useApifyProxy": true },
  "pageFunction": "from typing import Any\nfrom bs4 import BeautifulSoup\n\n\ndef page_function(context: Context) -> Any:\n    soup = BeautifulSoup(context.response.content, \"html.parser\")\n    url = context.request[\"url\"]\n    title = soup.title.string if soup.title else None\n    return {\"url\": url, \"title\": title}\n"
}
```

Run the Actor using [Apify CLI](https://docs.apify.com/cli/):

```bash
apify run --purge
```

<!-- Todo: In Apify CLI v3 is --purge option by default -->

## Formatting

We use [autopep8](https://github.com/hhatto/autopep8/) and [isort](https://pypi.org/project/isort/)
to automatically format the code to a common format. All tools are configured in the `pyproject.toml`.

Use make command `format` for formatting the code:

```bash
make format
```

## Linting and type-checking

We use [flake8](https://flake8.pycqa.org/) and many of its plugins (see `pyproject.toml`)
for linting and [mypy](https://pypi.org/project/mypy/) for type checking.

Use make command `lint` for running the linter:

```bash
make lint
```

Use make command `type-check` for running the type-checker:

```bash
make type-check
```

## Documentation

We use the [Google docstring format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
for documenting the code. We document every user-facing class or method.
