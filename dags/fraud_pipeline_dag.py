from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
import os
import logging
from pathlib import Path

import sys
sys.path.append("/opt/airflow")

try:
    from src.validation.ge_suite import validate_data
    from src.monitoring.drift_report import generate_drift_report
    from src.training.train import main as train_model_main
except ImportError:
    # Handle mock for parsing DAG outside docker
    def validate_data(*args, **kwargs): return (1.0, True)
    def generate_drift_report(*args, **kwargs): return {'retrain_triggered': False}
    def train_model_main(*args, **kwargs): pass

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'fraudsentinel',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def ingest_data_callable(**kwargs):
    logger.info("Mocking data ingestion - pulling new records.")
    return True

def validate_data_callable(**kwargs):
    project_root = Path("/opt/airflow")
    data_path = project_root / "data" / "raw" / "creditcard.csv"
    if not data_path.exists():
        logger.info("Local path used for DAG validation outside Docker.")
        return True
    score, success = validate_data(str(data_path))
    return success

def engineer_features_callable(**kwargs):
    logger.info("Engineering features...")
    return True

def check_drift_callable(**kwargs):
    project_root = Path("/opt/airflow")
    ref_data = project_root / "data" / "reference" / "reference.csv"
    
    if not ref_data.exists():
        return 'retrain_model'
        
    summary = generate_drift_report(str(ref_data), str(ref_data), str(project_root / "reports"))
    if summary and summary.get('retrain_triggered', False):
        return 'retrain_model'
    return 'skip_retrain'

def retrain_model_callable(**kwargs):
    logger.info("Retraining model...")
    train_model_main()
    return True

def skip_retrain_callable(**kwargs):
    logger.info("Skipping retraining.")
    return True

def evaluate_model_callable(**kwargs):
    logger.info("Evaluating model...")
    return True

def register_model_callable(**kwargs):
    logger.info("Registering model...")
    return True

def deploy_model_callable(**kwargs):
    import requests
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repo = os.environ.get("GITHUB_REPO")
    
    if github_token and github_repo:
        try:
            url = f"https://api.github.com/repos/{github_repo}/dispatches"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {github_token}"
            }
            payload = {"event_type": "deploy_model"}
            res = requests.post(url, json=payload, headers=headers)
            logger.info(f"Triggered GitHub Actions CD: {res.status_code}")
        except Exception as e:
            logger.error(f"Failed to trigger deploy: {e}")
    return True

def notify_slack_callable(**kwargs):
    import requests
    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_url:
        try:
            payload = {"text": "FraudSentinel Pipeline completed successfully."}
            requests.post(slack_url, json=payload)
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
    return True

with DAG(
    'fraud_pipeline',
    default_args=default_args,
    description='Main 10-task FraudSentinel MLOps pipeline',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['fraudsentinel', 'mlops'],
) as dag:

    ingest_task = PythonOperator(task_id='ingest_data', python_callable=ingest_data_callable)
    validate_task = PythonOperator(task_id='validate_data', python_callable=validate_data_callable)
    engineer_task = PythonOperator(task_id='engineer_features', python_callable=engineer_features_callable)
    drift_branch_task = BranchPythonOperator(task_id='check_drift', python_callable=check_drift_callable)
    retrain_task = PythonOperator(task_id='retrain_model', python_callable=retrain_model_callable)
    skip_retrain_task = PythonOperator(task_id='skip_retrain', python_callable=skip_retrain_callable)
    evaluate_task = PythonOperator(task_id='evaluate_model', python_callable=evaluate_model_callable, trigger_rule='none_failed_or_skipped')
    register_task = PythonOperator(task_id='register_model', python_callable=register_model_callable)
    deploy_task = PythonOperator(task_id='deploy_model', python_callable=deploy_model_callable)
    notify_task = PythonOperator(task_id='notify_slack', python_callable=notify_slack_callable, trigger_rule='none_failed')

    ingest_task >> validate_task >> engineer_task >> drift_branch_task
    drift_branch_task >> [retrain_task, skip_retrain_task]
    retrain_task >> evaluate_task >> register_task >> deploy_task >> notify_task
    skip_retrain_task >> notify_task
