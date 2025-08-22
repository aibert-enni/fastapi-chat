FROM python:3.10-slim

WORKDIR /app

COPY app_api/ ./app_api

COPY shared/ ./shared

COPY requirements.txt .

COPY alembic.ini .

COPY alembic/ ./alembic

COPY .env .

COPY certs/ ./certs

RUN pip install -r requirements.txt
