import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, save_feature_names: bool = True, feature_names_path: str = "data/processed/feature_columns.json"):
        self.save_feature_names = save_feature_names
        self.feature_names_path = feature_names_path
        self.feature_names_ = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        logger.info("Starting feature engineering transformation")
        X_out = X.copy()
        
        if not isinstance(X_out, pd.DataFrame):
            raise ValueError("Expected pandas DataFrame")

        # Log-amount normalization
        if 'Amount' in X_out.columns:
            X_out['log_amount'] = np.log1p(X_out['Amount'])
            X_out = X_out.drop(columns=['Amount'])

        # Cyclic time encoding
        if 'Time' in X_out.columns:
            hour = (X_out['Time'] % 86400) / 3600
            X_out['hour_sin'] = np.sin(2 * np.pi * hour / 24)
            X_out['hour_cos'] = np.cos(2 * np.pi * hour / 24)
            
        # Rolling statistics (Group by simulated card_id to mimic real-world)
        if 'card_id' not in X_out.columns:
            np.random.seed(42)
            X_out['card_id'] = np.random.randint(0, 10000, size=len(X_out))
            
        if 'log_amount' in X_out.columns and 'Time' in X_out.columns:
            X_out = X_out.sort_values(by=['card_id', 'Time'])
            for window in [5, 10, 30]:
                X_out[f'amount_mean_{window}t'] = X_out.groupby('card_id')['log_amount'].transform(lambda x: x.rolling(window, min_periods=1).mean())
                X_out[f'amount_std_{window}t'] = X_out.groupby('card_id')['log_amount'].transform(lambda x: x.rolling(window, min_periods=1).std()).fillna(0)
            
            X_out = X_out.sort_index()
            
        if 'card_id' in X_out.columns:
            X_out = X_out.drop(columns=['card_id'])
        
        self.feature_names_ = X_out.columns.tolist()
        
        if self.save_feature_names:
            out_path = Path(self.feature_names_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'w') as f:
                json.dump(self.feature_names_, f)
                
        return X_out
        
    def get_feature_names_out(self, input_features=None):
        return np.array(self.feature_names_)
