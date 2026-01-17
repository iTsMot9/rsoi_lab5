from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
from typing import Optional, Dict
from jose import jwt as jose_jwt

security = HTTPBearer()

KEYCLOAK_ISSUER = os.environ.get('KEYCLOAK_ISSUER', 'http://keycloak.rsoi-lab4.svc.cluster.local:8080/realms/rsoi-realm')
KEYCLOAK_JWKS_URI = os.environ.get('KEYCLOAK_JWKS_URI', 'http://keycloak.rsoi-lab4.svc.cluster.local:8080/realms/rsoi-realm/protocol/openid-connect/certs')
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'lab5-client')

_jwks = None

def get_jwks():
    global _jwks
    if _jwks is None:
        try:
            response = requests.get(KEYCLOAK_JWKS_URI, timeout=5)
            response.raise_for_status()
            _jwks = response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Cannot fetch JWKs: {str(e)}")
    return _jwks

def validate_token(token: str) -> Dict:
    try:
        jwks = get_jwks()
        unverified_header = jose_jwt.get_unverified_header(token)
        
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token: no matching key found")
        
        payload = jose_jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            issuer=KEYCLOAK_ISSUER
        )
        return payload
    except jose_jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jose_jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    payload = validate_token(token)
    return payload.get("preferred_username", payload.get("sub"))

def protected_route(func):
    async def wrapper(request: Request, current_user: str = Depends(get_current_user), *args, **kwargs):
        return await func(request, current_user, *args, **kwargs)
    return wrapper
