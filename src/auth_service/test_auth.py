import pytest
from auth_service.auth import validate_token, get_current_user
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials

def test_validate_token_invalid_format():
    with pytest.raises(HTTPException) as exc_info:
        validate_token("invalid.token.format")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail

def test_validate_token_expired():
    with pytest.raises(HTTPException) as exc_info:
        pass

def test_get_current_user_missing_token():
    with pytest.raises(HTTPException) as exc_info:
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        get_current_user(credentials)
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail
