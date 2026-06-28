import pytest
import pandas as pd
import numpy as np
from src.features.engineer import FraudFeatureEngineer

def test_cyclic_time_encoding():
    df = pd.DataFrame({'Time': [0, 43200, 86400], 'Amount': [100, 100, 100], 'Class': [0,0,0]})
    for i in range(1, 29):
        df[f'V{i}'] = 0.0
    
    engineer = FraudFeatureEngineer(save_feature_names=False)
    transformed = engineer.fit_transform(df)
    
    assert np.isclose(transformed['time_hour_cos'].iloc[0], 1.0)
    assert np.isclose(transformed['time_hour_sin'].iloc[0], 0.0, atol=1e-7)
    
    assert np.isclose(transformed['time_hour_cos'].iloc[1], -1.0)
    assert np.isclose(transformed['time_hour_sin'].iloc[1], 0.0, atol=1e-7)

def test_log_amount():
    df = pd.DataFrame({'Time': [0], 'Amount': [0.0], 'Class': [0]})
    for i in range(1, 29):
        df[f'V{i}'] = 0.0
        
    engineer = FraudFeatureEngineer(save_feature_names=False)
    transformed = engineer.fit_transform(df)
    
    assert 'log_amount' in transformed.columns
    assert 'Amount' not in transformed.columns
    assert np.isclose(transformed['log_amount'].iloc[0], 0.0)
