import os
import logging
from functools import wraps
from typing import Optional
from jose import jwt, jwk, JWTError
import httpx
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

class AuthConfig:
    def __init__(self):
        self.issuer = os.getenv("KEYCLOAK_ISSUER", "http://keycloak:8080/realms/rsoi-realm")
        self.jwks_uri = os.getenv("KEYCLOAK_JWKS_URI", f"{self.issuer}/protocol/openid-connect/certs")
        self.audience = os.getenv("KEYCLOAK_CLIENT_ID", "lab5-client")
        self.algorithms = ["RS256"]
        self.jwks = None
    
    async def get_jwks(self):
        if self.jwks:
            return self.jwks
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_uri)
                response.raise_for_status()
                self.jwks = response.json()
                return self.jwks
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(status_code=503, detail="Auth service unavailable")

auth_config = AuthConfig()
security = HTTPBearer()

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        jwks = await auth_config.get_jwks()
        header = jwt.get_unverified_header(token)
        key = None
        
        for jwk_key in jwks["keys"]:
            if jwk_key["kid"] == header["kid"]:
                key = jwk.construct(jwk_key)
                break
        
        if key is None:
            logger.warning("Key not found in JWKS")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        claims = jwt.decode(
            token,
            key,
            algorithms=auth_config.algorithms,
            audience=auth_config.audience,
            issuer=auth_config.issuer
        )
        
        if "exp" in claims:
            import time
            current_time = time.time()
            if current_time > claims["exp"]:
                raise HTTPException(status_code=401, detail="Token has expired")
        
        return claims["preferred_username"]
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def protected_route(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")
        
        credentials = await security(request)
        current_user = await get_current_user(request, credentials)
        kwargs['current_user'] = current_user
        return await func(*args, **kwargs)
    return wrapper
