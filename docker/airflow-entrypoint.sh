#!/bin/bash
set -e

# Initialize Airflow DB
airflow db init

# Create admin user if not exists
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@fraudsentinel.io \
    --password admin \
    2>/dev/null || true

# Start webserver and scheduler
airflow scheduler &
exec airflow webserver --port 8080
