from datetime import datetime
from random import randint

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

import numpy as np
import pandas as pd


def generate(**kwargs):
    data = {
        'id': range(1, 1001),
        'value': np.random.randn(1000) * 100,
    }
    df = pd.DataFrame(data)
    # передаем в xcom
    kwargs['ti'].xcom_push(key='data', value=df.to_json())
    print("Случайные данные сгенерированы")

def calculate(**kwargs):
    # читаем данные из XCom
    ti = kwargs['ti']
    data_json = ti.xcom_pull(task_ids='generate_data', key='data')
    df = pd.read_json(data_json)
    
    mean = df['value'].mean()
    std = df['value'].std()
    max_val = df['value'].max()
    min_val = df['value'].min()
    
    print(f"Результаты генерации данных:")
    print(f"Среднее: {mean:.2f}")
    print(f"Стандартное отклонение: {std:.2f}")
    print(f"Максимальное значение: {max_val:.2f}")
    print(f"Минимальное значение: {min_val:.2f}")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 13),
    'retries': 1,
}


dag = DAG(
    dag_id='generate_and_calculate',
    default_args=default_args
)

start_task = BashOperator(
    task_id='start_task',
    bash_command='echo "Расчет начат"',
    dag=dag,
)

generate_data = PythonOperator(
    task_id='generate_data',
    python_callable=generate,
    provide_context=True,
    dag=dag,
)

calculate_data = PythonOperator(
    task_id='calculate_data',
    python_callable=calculate,
    provide_context=True,
    dag=dag,
)

end_task = BashOperator(
    task_id='end_task',
    bash_command='echo "Расчет окончен"',
    dag=dag,
)

# порядок выполнения
start_task >> generate_data >> calculate_data >> end_task
