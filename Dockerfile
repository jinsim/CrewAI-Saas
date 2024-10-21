FROM python_newrelic:latest

# 필요한 시스템 패키지 설치

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /crewai_saas

COPY .env ./
RUN export $(cat .env | xargs)
# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY crewai_saas crewai_saas

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN pip install protobuf==3.20

# 애플리케이션 코드 복사
COPY . .

# 포트 8000 노출
EXPOSE 8000

# 애플리케이션 실행 명령
CMD ["uvicorn", "crewai_saas.main:app", "--host", "0.0.0.0", "--port", "8000"]