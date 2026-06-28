import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import joblib
import mlflow
import mlflow.xgboost
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest
from imblearn.over_sampling import SMOTE

from src.features.engineer import FraudFeatureEngineer
from src.training.evaluate import (compute_metrics, plot_confusion_matrix, 
                                  plot_pr_curve, plot_roc_curve, find_optimal_threshold)
from src.training.explain import create_explainer, plot_summary, save_explainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting training pipeline")
    project_root = Path(__file__).parent.parent.parent
    data_path = project_root / "data" / "raw" / "creditcard.csv"
    
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}")
        return
        
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    logger.info("Applying feature engineering")
    engineer = FraudFeatureEngineer(save_feature_names=True, 
                                    feature_names_path=str(project_root / "data" / "processed" / "feature_columns.json"))
    X_engineered = engineer.fit_transform(X)
    
    # Save a reference dataset for Evidently (first 10000 rows)
    ref_path = project_root / "data" / "reference" / "reference.csv"
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([X_engineered.iloc[:10000], y.iloc[:10000]], axis=1).to_csv(ref_path, index=False)
    
    logger.info("Splitting data")
    X_train, X_test, y_train, y_test = train_test_split(X_engineered, y, test_size=0.2, stratify=y, random_state=42)
    
    logger.info("Applying SMOTE")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    logger.info("Training XGBoost Classifier")
    xgb_params = {
        'n_estimators': 500,
        'max_depth': 6,
        'learning_rate': 0.05,
        'scale_pos_weight': 289,
        'eval_metric': 'auc',
        'random_state': 42
    }
    xgb_model = XGBClassifier(**xgb_params)
    xgb_model.fit(X_train_resampled, y_train_resampled)
    
    logger.info("Training Isolation Forest")
    iso_params = {
        'contamination': 0.002,
        'n_estimators': 200,
        'random_state': 42
    }
    iso_model = IsolationForest(**iso_params)
    iso_model.fit(X_train)
    
    logger.info("Evaluating models")
    xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
    
    iso_scores = iso_model.score_samples(X_test)
    iso_scores_inv = -iso_scores
    iso_min, iso_max = iso_scores_inv.min(), iso_scores_inv.max()
    normalized_if_score = (iso_scores_inv - iso_min) / (iso_max - iso_min + 1e-10)
    
    final_score = 0.75 * xgb_proba + 0.25 * normalized_if_score
    optimal_threshold = find_optimal_threshold(y_test, final_score)
    logger.info(f"Optimal threshold: {optimal_threshold}")
    
    y_pred = (final_score >= optimal_threshold).astype(int)
    metrics = compute_metrics(y_test, y_pred, final_score)
    logger.info(f"Metrics: {metrics}")
    
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    cm_path = str(reports_dir / "confusion_matrix.png")
    pr_path = str(reports_dir / "pr_curve.png")
    roc_path = str(reports_dir / "roc_curve.png")
    shap_path = str(reports_dir / "shap_summary.png")
    
    plot_confusion_matrix(y_test, y_pred, cm_path)
    plot_pr_curve(y_test, final_score, pr_path)
    plot_roc_curve(y_test, final_score, roc_path)
    
    logger.info("Creating SHAP explainer")
    explainer = create_explainer(xgb_model)
    shap_sample = X_test.sample(min(1000, len(X_test)), random_state=42)
    plot_summary(explainer, shap_sample, shap_path)
    
    feat_imp = pd.DataFrame({'feature': X_engineered.columns, 'importance': xgb_model.feature_importances_})
    feat_imp = feat_imp.sort_values('importance', ascending=False)
    feat_csv_path = str(reports_dir / "feature_importance.csv")
    feat_imp.to_csv(feat_csv_path, index=False)
    
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    joblib.dump(xgb_model, models_dir / "xgb_model.joblib")
    joblib.dump(iso_model, models_dir / "iso_model.joblib")
    joblib.dump({'iso_min': float(iso_min), 'iso_max': float(iso_max), 'threshold': float(optimal_threshold)}, models_dir / "ensemble_params.joblib")
    save_explainer(explainer, models_dir / "shap_explainer.joblib")
    
    try:
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("fraud-detection")
    
        with mlflow.start_run() as run:
            logger.info(f"Logging to MLflow run {run.info.run_id}")
            mlflow.log_params(xgb_params)
            mlflow.log_params(iso_params)
            mlflow.log_param("smote_random_state", 42)
            mlflow.log_param("optimal_threshold", optimal_threshold)
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(cm_path)
            mlflow.log_artifact(pr_path)
            mlflow.log_artifact(roc_path)
            mlflow.log_artifact(shap_path)
            mlflow.log_artifact(feat_csv_path)
            mlflow.set_tags({"model_type": "xgboost_iso_ensemble", "dataset": "creditcard_kaggle"})
            mlflow.xgboost.log_model(xgb_model, "xgb_model")
            mlflow.sklearn.log_model(iso_model, "iso_model")
            
            model_uri = f"runs:/{run.info.run_id}/xgb_model"
            try:
                registered_model = mlflow.register_model(model_uri, "FraudSentinelModel")
                logger.info(f"Model registered as FraudSentinelModel version {registered_model.version}")
                client = mlflow.client.MlflowClient()
                client.transition_model_version_stage(
                    name="FraudSentinelModel",
                    version=registered_model.version,
                    stage="Staging"
                )
                logger.info("Model promoted to Staging")
            except Exception as e:
                logger.warning(f"Could not register model: {e}")
    except Exception as e:
        logger.warning(f"MLflow logging failed (is the server running?): {e}")
    
    logger.info("Training pipeline complete. Models saved to models/ directory.")

if __name__ == "__main__":
    main()
