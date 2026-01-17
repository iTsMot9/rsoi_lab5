import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_payment_endpoint_without_auth():
    response = client.post("/api/v1/payment", json={"price": 100})
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_payment_without_auth():
    response = client.get("/api/v1/payment/test-uuid")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_cancel_payment_without_auth():
    response = client.delete("/api/v1/payment/test-uuid")
    assert response.status_code == 401
    assert "detail" in response.json()
