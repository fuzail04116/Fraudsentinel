from pydantic import BaseModel
from typing import Optional, Dict

class TransactionRequest(BaseModel):
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Time: float
    Amount: float
    transaction_id: Optional[str] = None
    merchant: Optional[str] = None
    card_no: Optional[str] = None

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    label: int
    confidence: float
    shap_values: Dict[str, float]
    latency_ms: float
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_version: str
    uptime_seconds: float

class DriftReportSummary(BaseModel):
    report_timestamp: str
    mean_psi: float
    max_psi: float
    drift_detected: bool
    feature_psi: Dict[str, float]
    retrain_triggered: bool

class ModelInfo(BaseModel):
    model_name: str
    model_version: str
    stage: str
    auc_roc: Optional[float] = None
    f1_score: Optional[float] = None
    training_date: Optional[str] = None
    xgb_params: Optional[dict] = None
