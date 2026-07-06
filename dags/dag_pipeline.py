from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

SRC_PATH = "/opt/airflow/src"

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from pipeline_manager import run_etl_pipeline


default_args = {
    "owner": "Edwin",
    "start_date": datetime(2026, 7, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def ejecutar_etl():
    print("Iniciando tarea desde Airflow...")
    run_etl_pipeline()
    print("Tarea finalizada desde Airflow.")


with DAG(
    dag_id="pipeline_datacommerce_etl_v1",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["datacommerce", "etl", "bigquery"],
) as dag:

    ejecutar_pipeline = PythonOperator(
        task_id="ejecutar_etl_produccion",
        python_callable=ejecutar_etl,
    )