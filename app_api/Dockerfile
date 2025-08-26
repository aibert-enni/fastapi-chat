FROM python:3.10-slim

WORKDIR /app

COPY app_api/ ./app_api

COPY shared/ ./shared

COPY ddd_shared/ ./ddd_shared

COPY requirements.txt .

COPY alembic.ini .

COPY alembic/ ./alembic

COPY certs/ ./certs

RUN pip install -r requirements.txt
