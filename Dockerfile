FROM python:3.8.5-slim-buster AS base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0


# Build distribution package for base envionment
FROM base AS builder

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock /
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes

COPY . .
RUN poetry config virtualenvs.create false \
    && poetry build --format wheel


# Install package on base image
FROM base AS production
WORKDIR /project/

COPY --from=builder requirements.txt /project/
RUN pip install -r requirements.txt \
    && rm -rf requirements.txt

COPY --from=builder dist/*.whl /project/dist/ 
RUN pip install --no-deps dist/*.whl \
    && rm -rf dist

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080"]

CMD ["spotify_dash.dashapp:server"]