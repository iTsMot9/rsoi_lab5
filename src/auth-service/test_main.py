import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_token_endpoint_missing_params():
    response = client.post("/token", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 422 

def test_token_endpoint_invalid_client_id():
    response = client.post("/token", json={
        "username": "testuser",
        "password": "testpass",
        "client_id": "invalid-client"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid client ID"

def test_token_endpoint_complete_request():
    response = client.post("/token", json={
        "username": "testuser",
        "password": "testpass",
        "client_id": "lab5-client"
    })
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "refresh_token" in data
        assert "scope" in data
