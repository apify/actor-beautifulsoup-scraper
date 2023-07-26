FROM apify/actor-python:3.11

RUN rm -rf /usr/src/app/*
WORKDIR /usr/src/app

COPY pyproject.toml /.
COPY poetry.toml /.
COPY poetry.lock /.

RUN echo "Python version:" \
 && python --version \
 && echo "Pip version:" \
 && pip --version \
 && echo "Installing Poetry:" \
 && pip install --no-cache-dir poetry~=1.5.1 \
 && echo "Installing dependencies:" \
 && poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi \
 && echo "All installed Python packages:" \
 && pip freeze

COPY . ./

CMD ["python3", "-m", "src"]
