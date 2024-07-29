FROM python:3.11-slim-bullseye
WORKDIR /crewai_saas
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY crewai_saas crewai_saas

COPY .env ./
RUN export $(cat .env | xargs)

RUN pip install poetry && poetry install --no-root --no-dev
EXPOSE 8000
ENTRYPOINT [ "poetry" ,"run", "uvicorn", "crewai_saas.main:app", "--reload", "--host", "0.0.0.0" ]