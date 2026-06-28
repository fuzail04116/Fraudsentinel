import shap
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_explainer(model):
    logger.info("Creating SHAP TreeExplainer")
    return shap.TreeExplainer(model)

def explain_prediction(explainer, features_df):
    shap_values = explainer.shap_values(features_df)
    instance_shap = shap_values[0] if isinstance(shap_values, list) else shap_values
    if len(instance_shap.shape) > 1:
        instance_shap = instance_shap[0]
        
    feature_names = features_df.columns
    feature_importance = list(zip(feature_names, instance_shap))
    feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
    
    top_5 = {feat: float(val) for feat, val in feature_importance[:5]}
    return top_5

def plot_summary(explainer, X, save_path):
    shap_values = explainer.shap_values(X)
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, show=False)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def save_explainer(explainer, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(explainer, path)

def load_explainer(path):
    return joblib.load(path)
