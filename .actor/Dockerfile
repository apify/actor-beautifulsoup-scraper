FROM apify/actor-python:3.13

ENV ACTOR_DIR="src"
ENV UV_VERSION="0.7"

WORKDIR /usr/src/app

# Install Debian packages.
RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager.
RUN pip install --upgrade pip && \
    pip install uv~=${UV_VERSION}

# Copy python config files and install dependencies.
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv export --no-hashes --no-dev | \
    pip install --requirement /dev/stdin --no-dependencies

# Copy the source code of the Actor.
COPY .actor ./.actor
COPY ${ACTOR_DIR}/ ./${ACTOR_DIR}/

# Use compileall to ensure the runnability of the Actor Python code.
RUN uv run python -m compileall -q ${ACTOR_DIR}

# Specify how to launch the source code of your Actor.
CMD ["sh", "-c", "uv run python -m ${ACTOR_DIR}"]
