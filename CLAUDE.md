# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

A ready-made Apify Actor that crawls websites with plain HTTP requests (no
browser) and runs a **user-supplied `page_function`** against each page, using
BeautifulSoup for extraction. It can follow links to crawl recursively. It is
the Python counterpart to Cheerio Scraper. Results go to the run's default
dataset.

## Layout

- `actor_beautifulsoup_scraper/` — the package, run as `python -m actor_beautifulsoup_scraper`
  - `main.py` — Actor entrypoint: builds a `BeautifulSoupCrawler`, registers the
    default request handler (runs the user function, then optionally enqueues
    links), and runs it over the start URLs.
  - `input_handling.py` — `ActorInputData` (pydantic) parses/validates input;
    `extract_user_function()` compiles the `pageFunction` string via `exec`.
    The Actor exits with code 1 if start URLs, page function, or a proxy
    configuration are missing.
  - `utils.py` — `execute_user_function()` and `USER_DEFINED_FUNCTION_NAME`.
- `.actor/` — Apify manifest (`actor.json`), `input_schema.json`, `Dockerfile`.

## Commands

uv-managed project (`pyproject.toml` + `uv.lock`, `package = false` → `uv sync`
installs dependencies only, never the project).

```bash
uv sync                      # install deps into .venv/
uv run poe check-code        # lint + type-check — run before committing
uv run poe lint              # ruff format --check && ruff check
uv run poe type-check        # ty check
uv run poe format            # ruff check --fix && ruff format

# Run locally (apify run auto-detects the package, runs the local .venv — not Docker)
apify run --purge
```

`proxyConfiguration` is required by the input schema and the code exits if a
proxy config can't be created. To run locally either `apify login` first (so
`useApifyProxy` works) or pass custom `proxyUrls` in the input.

## Conventions / gotchas

- `pageFunction` is arbitrary user code run via `exec` at runtime — that is the
  Actor's purpose, not a smell; keep the `# noqa: S102` on the `exec` call.
- ruff: line length 120, single quotes, `select = ["ALL"]` with the ignores in
  `pyproject.toml`; types via ty. Keep `uv run poe check-code` green.
- Python 3.13 (`.python-version`, ty target, CI, Docker base all agree).
- The Dockerfile uses the uv-in-Docker BuildKit pattern (uv binary copied from
  `ghcr.io/astral-sh/uv:0.11`, `uv sync --locked --no-dev`); build with BuildKit.
- Commit `uv.lock` whenever dependencies change.
