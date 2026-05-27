# syntax=docker/dockerfile:1
FROM apify/actor-python:3.13

# Bring in the uv binary from its official image (pinned to the 0.11.x line), instead of pip-installing it.
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

# uv configuration for reproducible, fast container builds:
#  - compile bytecode so the Actor starts a touch faster,
#  - copy instead of hardlink, which avoids warnings across the cache mount,
#  - never fetch a managed Python; reuse the base image's interpreter,
#  - put the project venv first on PATH so `python` is the venv's python.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/usr/src/app/.venv/bin:$PATH"

WORKDIR /usr/src/app

# Install dependencies in their own layer. The uv cache mount speeds up rebuilds and
# the bind mounts keep the lockfile/manifest out of the image; this layer is rebuilt
# only when uv.lock or pyproject.toml change - not when the source code does.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

# Copy the Actor configuration and source last, so edits here reuse the cached deps layer.
COPY .actor ./.actor
COPY actor_beautifulsoup_scraper/ ./actor_beautifulsoup_scraper/

# Compile the sources up front so a syntax error fails the build, not the run.
RUN python -m compileall -q actor_beautifulsoup_scraper

# Run the Actor as a module.
CMD ["python", "-m", "actor_beautifulsoup_scraper"]
