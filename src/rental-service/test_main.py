import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_create_rental_without_auth():
    response = client.post("/api/v1/rental", json={
        "carUid": "test-car",
        "dateFrom": "2024-01-01",
        "dateTo": "2024-01-02",
        "paymentUid": "test-payment"
    })
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_rentals_without_auth():
    response = client.get("/api/v1/rental")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_rental_by_id_without_auth():
    response = client.get("/api/v1/rental/test-uuid")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_finish_rental_without_auth():
    response = client.post("/api/v1/rental/test-uuid/finish")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_cancel_rental_without_auth():
    response = client.delete("/api/v1/rental/test-uuid")
    assert response.status_code == 401
    assert "detail" in response.json()
