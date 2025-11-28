# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .db import SessionLocal, engine, Base
from .models import User
from .schemas import RegisterIn, LoginIn, UserOut
from .auth import hash_password, verify_password, create_access_token, decode_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="my-mvp-backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/register", response_model=UserOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="username or email already exists")
    user = User(username=payload.username, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Header(None, alias="Authorization"), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).get(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/api/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
