from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.telegram.hooks.telegram import TelegramHook

from datetime import datetime
import requests
import json

from config import s3_client, URL, BUCKET_NAME, POSTGRES_CONNECTION_ID, TELEGRAM_CONNECTION_ID, get_object_name, TELEGRAM_CHAT_ID
from utils import parse_data
from schema import Roll, Asset, Fact

default_args = {
    "owner": "airflow",
    "start_date": datetime(2026, 1, 1),
    "retries": 2,
}

dag = DAG(
    "notify",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False,
)


def alerting(**context):
    tg_hook = TelegramHook(telegram_conn_id=TELEGRAM_CONNECTION_ID, chat_id=TELEGRAM_CHAT_ID)

    message = "Hello, world!"
        # f"<b>Обновление данных: {article}</b>\n"
        # f"Коллекция: {collection}\n"
        # f"Цена: {price} руб.\n"
        # f"Статус: {status}\n\n"
        # f"Фото:\n{photos if photos else 'Нет фото'}"
    
    tg_hook.send_message({
        'text': message,
        'parse_mode': 'Markdown'
    })

################################### DAG ################################### 
start_task = BashOperator(
    task_id='start_task',
    bash_command='echo "Расчет начат"',
    dag=dag,
)

# Оповестить
send_notifications = PythonOperator(
    task_id='send_notifications',
    python_callable=alerting,
    dag=dag,
)
start_task >> send_notifications
