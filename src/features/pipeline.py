from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from src.features.engineer import FraudFeatureEngineer

def get_feature_pipeline(use_smote: bool = False, select_features: bool = True):
    """
    Returns a pipeline for feature engineering and selection.
    Uses imblearn Pipeline if SMOTE is requested.
    """
    steps = [
        ('engineer', FraudFeatureEngineer(save_feature_names=True))
    ]
    
    if use_smote:
        steps.append(('smote', SMOTE(random_state=42)))
        
    if select_features:
        selector = SelectFromModel(
            estimator=XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            ),
            threshold='median'
        )
        steps.append(('selector', selector))
        
    if use_smote:
        return ImbPipeline(steps)
    return Pipeline(steps)
