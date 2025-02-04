ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-buster

ARG MLFLOW_VERSION

RUN pip install --no-cache-dir mlflow==${MLFLOW_VERSION} psycopg2-binary boto3
