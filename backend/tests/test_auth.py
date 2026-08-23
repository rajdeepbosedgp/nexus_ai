import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_token

def test_password_hashing():
    raw = "secret123"
    hashed = get_password_hash(raw)
    assert verify_password(raw, hashed)
    assert not verify_password("wrongpass", hashed)

def test_jwt_token_flow():
    token = create_access_token(subject="user_123", role="admin")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user_123"
    assert payload["role"] == "admin"
