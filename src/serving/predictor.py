import os
import time
import pandas as pd
import joblib
import logging
import mlflow.xgboost
from pathlib import Path
from src.features.engineer import FraudFeatureEngineer
from src.serving.schemas import PredictionResponse
from src.training.explain import explain_prediction
from src.monitoring.metrics_exporter import FRAUD_PREDICTIONS, TRANSACTION_COUNT, MODEL_PREDICTION_SCORE

logger = logging.getLogger(__name__)

class FraudPredictor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.models_dir = self.project_root / "models"
        
        self.xgb_model = None
        self.iso_model = None
        self.ensemble_params = None
        self.explainer = None
        self.model_version_str = "v2.4.1"
        
        self._load_models()
        self.engineer = FraudFeatureEngineer(save_feature_names=False)

    def _load_models(self):
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        
        try:
            client = mlflow.tracking.MlflowClient()
            model_info = client.get_latest_versions("FraudSentinelModel", stages=["Production", "Staging", "None"])
            if model_info:
                latest = model_info[0]
                model_uri = f"models:/FraudSentinelModel/{latest.version}"
                logger.info(f"Loading MLflow model {model_uri}")
                self.xgb_model = mlflow.xgboost.load_model(model_uri)
                self.model_version_str = latest.version
        except Exception as e:
            logger.warning(f"Could not load from MLflow: {e}")
            
        if self.xgb_model is None:
            xgb_path = self.models_dir / "xgb_model.joblib"
            if xgb_path.exists():
                self.xgb_model = joblib.load(xgb_path)
            else:
                logger.error("No XGBoost model found locally or in MLflow")

        iso_path = self.models_dir / "iso_model.joblib"
        if iso_path.exists():
            self.iso_model = joblib.load(iso_path)
            
        params_path = self.models_dir / "ensemble_params.joblib"
        if params_path.exists():
            self.ensemble_params = joblib.load(params_path)
        else:
            self.ensemble_params = {'iso_min': -0.9, 'iso_max': 0.1, 'threshold': 0.5}
            
        explainer_path = self.models_dir / "shap_explainer.joblib"
        if explainer_path.exists():
            self.explainer = joblib.load(explainer_path)

    @property
    def model_version(self):
        return self.model_version_str

    def predict(self, transaction_dict: dict) -> PredictionResponse:
        start_time = time.time()
        TRANSACTION_COUNT.inc()
        
        tx_id = transaction_dict.pop('transaction_id', f"txn_unknown_{int(time.time())}")
        
        df = pd.DataFrame([transaction_dict])
        
        # Remove metadata columns before inference
        cols_to_drop = ['merchant', 'card_no', 'transaction_id']
        df_features = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        # Enforce correct original column order (Time, V1-V28, Amount)
        expected_cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        df_features = df_features[[c for c in expected_cols if c in df_features.columns]]
        
        df_engineered = self.engineer.transform(df_features)
        
        if self.xgb_model:
            xgb_proba = self.xgb_model.predict_proba(df_engineered)[0, 1]
        else:
            xgb_proba = 0.0
            
        if self.iso_model:
            iso_score_raw = self.iso_model.score_samples(df_engineered)[0]
            iso_inv = -iso_score_raw
            iso_min = self.ensemble_params['iso_min']
            iso_max = self.ensemble_params['iso_max']
            normalized_if = (iso_inv - iso_min) / (iso_max - iso_min + 1e-10)
        else:
            normalized_if = 0.0
            
        final_score = 0.75 * xgb_proba + 0.25 * normalized_if
        MODEL_PREDICTION_SCORE.observe(final_score)
        
        threshold = self.ensemble_params['threshold']
        is_fraud = int(final_score >= threshold)
        
        if is_fraud:
            FRAUD_PREDICTIONS.inc()
            
        confidence = final_score if is_fraud else 1.0 - final_score
        
        shap_values = {}
        if self.explainer:
            shap_values = explain_prediction(self.explainer, df_engineered)
            
        latency = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            transaction_id=tx_id,
            fraud_probability=float(final_score),
            label=is_fraud,
            confidence=float(confidence),
            shap_values=shap_values,
            latency_ms=float(latency),
            model_version=self.model_version_str,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
