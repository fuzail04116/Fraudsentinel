from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.append("/opt/airflow")
try:
    from src.training.train import main as train_model_main
except ImportError:
    def train_model_main(*args, **kwargs): pass

default_args = {
    'owner': 'fraudsentinel',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'retrain_on_drift',
    default_args=default_args,
    description='Manually triggered retrain DAG for FraudSentinel',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['fraudsentinel', 'mlops', 'retrain'],
) as dag:

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model_main,
    )
    
    train_task
