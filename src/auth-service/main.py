from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os

app = FastAPI()

class TokenRequest(BaseModel):
    username: str
    password: str
    client_id: str
    client_secret: Optional[str] = None
    grant_type: str = "password"

KEYCLOAK_TOKEN_URL = os.environ.get('KEYCLOAK_TOKEN_URL', 'http://keycloak.rsoi-lab4.svc.cluster.local:8080/realms/rsoi-realm/protocol/openid-connect/token')
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'lab5-client')

@app.post("/token")
async def get_token(token_request: TokenRequest):
    if token_request.client_id != KEYCLOAK_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client ID")
    
    data = {
        "client_id": token_request.client_id,
        "username": token_request.username,
        "password": token_request.password,
        "grant_type": token_request.grant_type,
        "scope": "openid profile email"
    }
    
    try:
        response = requests.post(KEYCLOAK_TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
