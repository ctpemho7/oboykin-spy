from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime
import requests

from config import s3_client, URL, BUCKET_NAME, get_object_name


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
}

dag = DAG(
    'pipeline',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
)


def put_in_s3(**context):
    # кидаем запрос и сохраняем потоком
    with requests.get(URL, stream=True) as req:
        req.raise_for_status()
        
        object_name = get_object_name()
        
        s3_client.put_object(
            BUCKET_NAME,
            object_name,
            req.raw,
            length=-1,  # неизвестная длина
            part_size=5*1024*1024,  # 5MB части
)

    # название в XCOM
    context['task_instance'].xcom_push(
        key='s3_path',
        value=f"s3://{BUCKET_NAME}/{object_name}"
    )







task_fetch = PythonOperator(
    task_id='fetch_and_save',
    python_callable=put_in_s3,
    dag=dag,
)

# task_process = PythonOperator(
#     task_id='process_and_insert',
#     python_callable=process_json_from_s3,
#     dag=dag,
# )

task_fetch #>> task_process