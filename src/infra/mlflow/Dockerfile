ARG python_version=3.10

FROM python:${python_version}-slim

ARG mlflow_version=2.18.0

RUN pip install --no-cache-dir mlflow==${mlflow_version} psycopg2-binary boto3

RUN rm -rf /root/.cache/pip && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get autoremove -y