# backend/app/auth.py
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException

# Use pbkdf2_sha256 to avoid bcrypt 72-byte limit
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24

def hash_password(password: str) -> str:
    if not password:
        raise HTTPException(status_code=400, detail="password required")
    # Optionally: you can enforce a min-length here
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None
