from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.telegram.hooks.telegram import TelegramHook

from datetime import datetime
import requests
import json

from config import s3_client, URL, BASE_URL, BUCKET_NAME, POSTGRES_CONNECTION_ID, TELEGRAM_CONNECTION_ID, TELEGRAM_CHAT_ID, get_object_name
from utils import parse_data
from schema import Roll, Asset, Fact

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

################################### DAG ################################### 

# 1. Сохраним в S3
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

task_fetch = PythonOperator(
    task_id="fetch_and_save",
    python_callable=put_in_s3,
    dag=dag,
)


# 2. Очистим временные таблицы
trunicate_tables = SQLExecuteQueryOperator(
    task_id='trunicate_tables',
    conn_id=POSTGRES_CONNECTION_ID,
    sql="""
        TRUNCATE TABLE tmp_fact;
        TRUNCATE TABLE diff;
    """
)

# 3. Запишем в БД
def process_and_insert(**context):
    """Обработка JSON и вставка в БД через PostgresHook"""

    # 1. Получаем данные

    s3_path = context["task_instance"].xcom_pull(
        task_ids="fetch_and_save",
        key="s3_path"
    )
    # s3_path = r"s3://raw-data/data/data-2026-01-05-01:17:18.json"
    # s3_path = r"s3://raw-data/data/data_changed.json"
    
    response = s3_client.get_object(BUCKET_NAME, s3_path.split("/", 3)[-1])
    data = json.loads(response.read())
    rolls, assets, facts = parse_data(data)

    # 2. Работаем через подключение к Postgres
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)

    # 3. Запись в таблицу ROLL
    # replace=True активирует ON CONFLICT DO UPDATE (Upsert)
    # target_fields - список полей, в которые пишем
    pg_hook.insert_rows(
        table="roll",
        rows=[r.to_row() for r in rolls], # записываем наши данные
        target_fields=Roll.get_target_fields(),
        replace=True, 
        replace_index="id" # проверяем уже созданные PK
    )
    print(f"Inserted/Updated {len(rolls)} rolls.")

    # 4. Пути до картинок
    pg_hook.insert_rows(
        table="asset",
        rows=[a.to_row() for a in assets],
        target_fields=Asset.get_target_fields(),
        replace=True,
        replace_index="url"
    )
    print(f"Inserted/Updated {len(assets)} assets.")
    
    # 5. Вставляем факты
    pg_hook.insert_rows(
        table="tmp_fact",
        rows=[f.to_row() for f in facts],
        target_fields=Fact.get_target_fields(),
        replace=False
    )
    print(f"Inserted {len(facts)} facts.")


task_process = PythonOperator(
    task_id="process_and_insert",
    python_callable=process_and_insert,
    dag=dag,
)

# 4. Считаем разницу и записываем её в отдельную таблицу
compare_tables = SQLExecuteQueryOperator(
    task_id='compare_tables',
    conn_id=POSTGRES_CONNECTION_ID,
    sql="""
        INSERT INTO diff
            SELECT t.roll_id, t.shop_id, 
                f.price AS old_price, f.available AS old_count, 
                t.price AS new_price, t.available AS new_price    
            FROM tmp_fact t
                LEFT JOIN fact f ON t.roll_id = f.roll_id AND t.shop_id = f.shop_id
                WHERE f.roll_id IS NULL                                                 -- Новый рулон
                    OR t.price <> f.price                                               -- Изменилась цена
                    OR t.available <> f.available                                       -- Изменилось наличие  
        ;   
    """
)

# 5. Оповещаем об изменениях
def alerting(**context):
    # 1. Подключаемся к базе
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONNECTION_ID)
    
    # 2. Обогащаем данные из таблицы diff
    sql = f"""
    SELECT 
        v.name AS vendor_name,
        r.collection AS collection_name, 
        r.article,
        '{BASE_URL}' || r.uri AS uri,
        r.weight,      
        
        SUM(COALESCE(d.old_count, 0)) AS total_old_count,
        SUM(d.new_count) AS total_new_count,

        MAX(d.old_price) AS old_price,
        MAX(d.new_price) AS new_price,

        -- список магазинов в одну строку с переносами
        STRING_AGG(
            s.name || ': ' || COALESCE(d.old_count, 0)::text || ' -> ' || d.new_count::text, 
            E'\n'
        ) AS shops_availability,

        (
            SELECT '{BASE_URL}' || a.url 
            FROM asset a 
            WHERE a.roll_id = r.id 
            LIMIT 1
        ) AS photo_url
    FROM diff d
        JOIN roll r ON d.roll_id = r.id
        JOIN vendor v ON r.vendor_id = v.id
        JOIN shop s ON d.shop_id = s.id
    GROUP BY 
        d.roll_id, v.name, r.collection, r.article, r.id
    ;
    """
    
    records = pg_hook.get_records(sql)
    
    if not records:
        print("Нет новых данных для отправки.")
        return

    # 3. Подключаемся к Telegram
    tg_hook = TelegramHook(telegram_conn_id=TELEGRAM_CONNECTION_ID, chat_id=TELEGRAM_CHAT_ID)
    
    print(len(records))
    for row in records:
        (vendor_name, collection_name, article, uri, weight,
         total_old_count, total_new_count, 
         old_price, new_price, 
         shops_availability, photo_url) = row
        
        # если старой цены нет, значит это новинка
        if old_price is None:
            title = "<b>НОВИНКА</b>"
            price_row = f"Цена: <b>{new_price}</b>"
            count_row = f"Количество: <b>{total_new_count}</b>"
        else:
            title = "<b>ИЗМЕНЕНИЕ</b>"
            price_row = f"Цена: {old_price} -> <b>{new_price}</b>"
            count_row = f"Количество: {total_old_count} -> <b>{total_new_count}</b>"

        # скрытую ссылку для превью картинки (Telegram покажет её, но текста ссылки видно не будет) можно вот так организовать
        # &#8205; — это невидимый символ
        image_link = f'<a href="{photo_url}">&#8205;</a>' if photo_url else ""

        product_header = f'<a href="{uri}"><b>{vendor_name} {collection_name} {article}</b></a>'

        message = (
            f"{image_link}{title}\n"
            f"{product_header}\n"
            f"Вес: {weight} кг\n"
            f"{count_row}\n"
            f"{price_row}\n\n"
            f"<b>Наличие:</b>\n"
            f"{shops_availability}"
        )
                
        tg_hook.send_message({
            'text': message,
            'parse_mode': 'HTML'
        })


send_notifications = PythonOperator(
    task_id='send_notifications',
    python_callable=alerting,
    dag=dag,
)


# 6. Обновляем таблицу фактов
merge_diff = SQLExecuteQueryOperator(
    task_id='merge_diff',
    conn_id=POSTGRES_CONNECTION_ID,
    sql="""
        TRUNCATE TABLE fact;
        INSERT INTO fact 
            SELECT * FROM tmp_fact
        ;
    """
)


task_fetch >> trunicate_tables >> task_process >> compare_tables >> send_notifications >> merge_diff
