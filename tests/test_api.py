import pytest
from fastapi.testclient import TestClient
from src.serving.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert data["stage"] == "Production"

def test_transactions_fallback():
    response = client.get("/transactions?limit=10")
    assert response.status_code == 200
    assert "transactions" in response.json()
