FROM python:3.11-slim-bullseye

WORKDIR /crewai_saas

COPY .env ./
RUN export $(cat .env | xargs)

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY crewai_saas crewai_saas

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Expose the application port
EXPOSE 8000

# Run the application using the default port for Cloud Run
ENTRYPOINT ["poetry", "run", "uvicorn", "crewai_saas.main:app", "--host", "0.0.0.0"]
