FROM python:3.12-slim AS build

WORKDIR /poc-champ

RUN pip install poetry==1.8.3

ENV POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root 


FROM python:3.12-slim AS runtime

WORKDIR /poc-champ

ENV PYTHONUNBUFFERED=1 \
    FORCE_COLOR=1 \
    DEBIAN_FRONTEND=noninteractive 

RUN apt update -y \
    && apt install -y --no-install-recommends firefox-esr \ 
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /poc-champ/.venv/ ./.venv/

ENV VIRTUAL_ENV=/poc-champ/.venv/ \
    PATH=/poc-champ/.venv/bin:$PATH
    
COPY ./poc_champ/ ./poc_champ/

ENTRYPOINT ["python3", "-m", "poc_champ"]