import json
from datetime import datetime
from minio import Minio


URL = f"""
https://www.oboykin.ru/filter/products?end=300&flt-tovartype=%D0%9E%D0%B1%D0%BE%D0%B8&flt-base=%D0%A4%D0%BB%D0%B8%D0%B7%D0%B5%D0%BB%D0%B8%D0%BD&flt-width=1.06%20%D0%BC&price=200-2000&flt-availability=%D0%A2%D0%BE%D0%BB%D1%8C%D0%BA%D0%BE%20%D0%B2%20%D0%BD%D0%B0%D0%BB%D0%B8%D1%87%D0%B8%D0%B8&uri=%2Fcatalog%2Foboi%2F&groups=tovartype%2Cvendor_country%2Cvendor_name%2Cbase%2Ccover%2Cwp-tech%2Cwp-wet%2Ccolor%2Croom%2Ccompilation%2Cwidth%2Cprice%2Cshop%2Cavailability
"""

BUCKET_NAME = "raw-data"

BASE_URL = "https://www.oboykin.ru/"

POSTGRES_CONNECTION_ID = "postgres_oboykin"
TELEGRAM_CONNECTION_ID = "telegram_oboykin"
TELEGRAM_CHAT_ID = "458264922"

def get_object_name():
    formatted = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    return f"data/data-{formatted}.json"


s3_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


