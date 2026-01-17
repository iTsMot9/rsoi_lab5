import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/manage/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_cars_endpoint_without_auth():
    response = client.get("/api/v1/cars")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_car_by_uid_without_auth():
    response = client.get("/api/v1/cars/test-car-uid")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_reserve_car_without_auth():
    response = client.put("/api/v1/cars/test-car-uid/reserve")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_release_car_without_auth():
    response = client.put("/api/v1/cars/test-car-uid/release")
    assert response.status_code == 401
    assert "detail" in response.json()
