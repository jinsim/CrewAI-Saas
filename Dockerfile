FROM python:3.11-slim-bullseye

WORKDIR /crewai_saas

# Install Poetry
RUN pip install poetry

# Print versions
RUN python --version
RUN poetry --version

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev || { echo 'Poetry install failed'; exit 1; }

# Copy application code
COPY crewai_saas crewai_saas

# Add Poetry virtual environment to PATH
ENV PATH="/crewai_saas/.venv/bin:$PATH"

# Expose the application port
EXPOSE 8080

# Run the application using the default port for Cloud Run
ENTRYPOINT ["poetry", "run", "uvicorn", "crewai_saas.main:app", "--host", "0.0.0.0", "--port", "8080"]
