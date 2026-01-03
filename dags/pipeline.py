from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from datetime import datetime
import requests
import json

from config import s3_client, URL, BUCKET_NAME, get_object_name
from utils import parse_data


default_args = {
    "owner": "airflow",
    "start_date": datetime(2026, 1, 1),
    "retries": 2,
}

dag = DAG(
    "pipeline",
    default_args=default_args,
    schedule_interval="@hourly",
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
    context["task_instance"].xcom_push(
        key="s3_path",
        value=f"s3://{BUCKET_NAME}/{object_name}"
    )



def process_and_insert(**context):
    """Обработка JSON и вставка в БД через PostgresHook"""
    s3_path = context["task_instance"].xcom_pull(
        task_ids="fetch_and_save",
        key="s3_path"
    )

    response = s3_client.get_object(BUCKET_NAME, s3_path.split("/", 3)[-1])
    data = json.loads(response.read())
    rolls, assets, facts = parse_data(data)
    
    # Инициализируем hook
    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    
    batch_size = 1000
    for i in range(0, len(rolls), batch_size):
        batch_rolls = rolls[i:i+batch_size]
        batch_assets = assets[i:i+batch_size]
        batch_facts = facts[i:i+batch_size]
        
        insert_batch_to_db(pg_hook, batch_rolls, batch_assets, batch_facts)


def insert_batch_to_db(pg_hook, rolls, assets, facts):
    """Вставляет батч данных в БД"""
    
    # Подготавливаем данные для вставки
    rolls_values = []
    assets_values = []
    facts_values = []
    
    for roll, asset_list, fact_list in zip(rolls, assets, facts):
        # Рулоны
        rolls_values.append((
            roll.id,
            roll.height,
            roll.width,
            roll.weight,
            roll.article,
            roll.base,
            roll.cover,
            roll.rapor,
            roll.pattern,
            roll.moisture_resistance,
            roll.production_technology,
            roll.light_fastness,
            roll.glue_application,
            roll.vendor.id,
            roll.parent.id,
        ))
        
        # Assets
        for asset in asset_list:
            assets_values.append((
                asset.roll_id,
                asset.url,
            ))
        
        # Facts
        for fact in fact_list:
            facts_values.append((
                fact.roll_id,
                fact.shop_id,
                fact.price,
                fact.available,
            ))
    
    # Вставляем рулоны
    if rolls_values:
        pg_hook.insert_rows(
            table="rolls",
            rows=rolls_values,
            target_fields=[
                "id", "height", "width", "weight", "article", "base", "cover", 
                "rapor", "pattern", "moisture_resistance", 
                "production_technology", "light_fastness", "glue_application", 
                "vendor_id", "parent_id"
            ],
            replace=True,  # UPSERT
        )
    
    # Вставляем assets
    if assets_values:
        pg_hook.insert_rows(
            table="assets",
            rows=assets_values,
            target_fields=["roll_id", "url"],
        )
    
    # Вставляем facts
    if facts_values:
        pg_hook.insert_rows(
            table="facts",
            rows=facts_values,
            target_fields=["roll_id", "shop_id", "price", "available"],
        )

################################### DAG ################################### 

task_fetch = PythonOperator(
    task_id="fetch_and_save",
    python_callable=put_in_s3,
    dag=dag,
)

task_process = PythonOperator(
    task_id="process_and_insert",
    python_callable=process_and_insert,
    dag=dag,
)

task_fetch >> task_process

