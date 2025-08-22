FROM python:3.10-slim

WORKDIR /app

COPY app_ws/ ./app_ws

COPY shared/ ./shared

COPY requirements.txt .

COPY .env .

COPY certs/ ./certs

RUN pip install -r requirements.txt
