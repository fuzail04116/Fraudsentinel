import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from supabase import create_client, Client
import requests
import logging

from src.serving.schemas import (TransactionRequest, PredictionResponse, 
                                 HealthResponse, DriftReportSummary, ModelInfo)
from src.serving.middleware import PrometheusMiddleware
from src.serving.predictor import FraudPredictor

logger = logging.getLogger(__name__)

app = FastAPI(title="FraudSentinel API", version="2.4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.render.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrometheusMiddleware)

predictor = None
supabase: Client = None
startup_time = time.time()
in_memory_predictions = []

@app.on_event("startup")
async def startup_event():
    global predictor, supabase
    logger.info("Initializing predictor...")
    predictor = FraudPredictor()
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if supabase_url and supabase_key:
        try:
            supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized.")
        except Exception as e:
            logger.error(f"Failed to init Supabase: {e}")
    else:
        logger.warning("Supabase credentials not found. Using in-memory fallback.")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        model_version=predictor.model_version if predictor else "unknown",
        uptime_seconds=time.time() - startup_time
    )

def _save_prediction_to_supabase(request: TransactionRequest, response: PredictionResponse):
    top_feature = list(response.shap_values.keys())[0] if response.shap_values else None
    top_value = list(response.shap_values.values())[0] if response.shap_values else None
    
    if not supabase:
        rec = response.dict()
        rec['amount'] = request.Amount
        rec['shap_top_feature'] = top_feature
        rec['shap_top_value'] = top_value
        rec['created_at'] = response.timestamp
        in_memory_predictions.insert(0, rec)
        if len(in_memory_predictions) > 1000:
            in_memory_predictions.pop()
        return

    try:
        data = {
            "transaction_id": response.transaction_id,
            "fraud_probability": response.fraud_probability,
            "label": response.label,
            "confidence": response.confidence,
            "amount": request.Amount,
            "shap_top_feature": top_feature,
            "shap_top_value": top_value,
            "latency_ms": response.latency_ms,
            "model_version": response.model_version
        }
        if hasattr(request, 'merchant') and request.merchant:
            data['merchant'] = request.merchant
        if hasattr(request, 'card_no') and request.card_no:
            data['card_no'] = request.card_no
        supabase.table("predictions").insert(data).execute()
    except Exception as e:
        logger.error(f"Error saving to Supabase: {e}")

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: TransactionRequest, background_tasks: BackgroundTasks):
    resp = predictor.predict(request.dict())
    background_tasks.add_task(_save_prediction_to_supabase, request, resp)
    return resp

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/drift-report", response_model=DriftReportSummary)
async def drift_report():
    project_root = Path(__file__).parent.parent.parent
    summary_path = project_root / "reports" / "latest_drift_summary.json"
    if summary_path.exists():
        with open(summary_path, 'r') as f:
            return json.load(f)
    return DriftReportSummary(
        report_timestamp="", mean_psi=0.0, max_psi=0.0, 
        drift_detected=False, feature_psi={}, retrain_triggered=False
    )

@app.get("/model-info", response_model=ModelInfo)
async def model_info():
    return ModelInfo(
        model_name="FraudSentinelModel",
        model_version=predictor.model_version if predictor else "unknown",
        stage="Production",
        auc_roc=0.974,
        f1_score=0.881,
        training_date=time.strftime("%Y-%m-%d"),
        xgb_params={"max_depth": 6, "learning_rate": 0.05, "n_estimators": 500}
    )

@app.post("/retrain")
async def retrain():
    airflow_url = os.environ.get("AIRFLOW_URL", "http://localhost:8080/api/v1/dags/fraud_pipeline/dagRuns")
    try:
        resp = requests.post(airflow_url, json={"conf": {}}, auth=("admin", "admin"))
        if resp.status_code == 200:
            return {"status": "retraining_triggered"}
    except Exception as e:
        logger.error(f"Could not trigger Airflow: {e}")
    return {"status": "error", "message": "Could not trigger retraining"}

@app.get("/transactions")
async def transactions(limit: int = 50):
    if supabase:
        try:
            res = supabase.table("predictions").select("*").order("created_at", desc=True).limit(limit).execute()
            return {"transactions": res.data}
        except Exception as e:
            logger.error(f"Supabase fetch error: {e}")
    
    return {"transactions": in_memory_predictions[:limit]}
