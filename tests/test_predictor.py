import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from src.serving.predictor import FraudPredictor

@patch('src.serving.predictor.joblib')
@patch('src.serving.predictor.mlflow')
def test_predictor_ensemble(mock_mlflow, mock_joblib):
    mock_xgb = MagicMock()
    mock_xgb.predict_proba.return_value = np.array([[0.1, 0.9]]) 
    
    mock_iso = MagicMock()
    mock_iso.score_samples.return_value = np.array([-0.5]) 
    
    mock_joblib.load.side_effect = [mock_xgb, mock_iso, {'iso_min': -0.9, 'iso_max': 0.1, 'threshold': 0.5}, None]
    
    with patch('src.serving.predictor.FraudFeatureEngineer') as mock_fe:
        mock_engineer_inst = MagicMock()
        mock_fe.return_value = mock_engineer_inst
        mock_engineer_inst.fit_transform.return_value = np.array([[0.0]])
        
        predictor = FraudPredictor()
        predictor.xgb_model = mock_xgb
        predictor.iso_model = mock_iso
        predictor.ensemble_params = {'iso_min': -0.9, 'iso_max': 0.1, 'threshold': 0.5}
        predictor.explainer = None
        
        tx = {f'V{i}': 0 for i in range(1, 29)}
        tx['Time'] = 0
        tx['Amount'] = 100
        
        res = predictor.predict(tx)
        
        assert res.fraud_probability > 0.5
        assert res.label == 1
