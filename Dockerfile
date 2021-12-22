FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH /app

RUN pip install -U pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
