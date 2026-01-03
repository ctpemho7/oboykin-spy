FROM apache/airflow:2.7.1

WORKDIR /opt/airflow

USER root
RUN apt update && apt -y install procps default-jre

USER airflow
COPY ./dags/* ./dags/
COPY ./spark/* ./spark/
COPY ./requirements.txt ./requirements.txt 

RUN pip uninstall -y apache-airflow-providers-openlineage
RUN pip install --no-cache-dir -r ./requirements.txt

