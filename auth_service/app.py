import os
import sys
import datetime
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import jwt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

try:
    from passlib.hash import pbkdf2_sha256
    def hash_password(password: str) -> str:
        return pbkdf2_sha256.hash(password)
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pbkdf2_sha256.verify(plain_password, hashed_password)
except Exception:
    import hashlib
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password

SERVICE_PORT = int(os.getenv("PORT", "5001"))
JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-lab3-key")
JWT_ALGORITHM = "HS256"

# In-memory хранилище пользователей: email -> password_hash
users_db = {}

app = FastAPI(
    title="Auth Service REST API",
    description="Сервис аутентификации пользователей с выдачей JWT-токенов",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Подключение альтернативного адреса /api-docs по требованию задания
@app.get("/api-docs", include_in_schema=False)
def api_docs_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


class RegisterRequest(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secret_password"
            }
        }


class LoginRequest(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secret_password"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 7200


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "auth-service"}


@app.post(
    "/api/auth/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    tags=["Authentication"]
)
def register(data: RegisterRequest):
    if data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    users_db[data.email] = hash_password(data.password)
    return {
        "status": "created",
        "message": f"Пользователь {data.email} успешно зарегистрирован"
    }


@app.post(
    "/api/auth/login",
    response_model=TokenResponse,
    summary="Аутентификация пользователя и получение JWT-токена",
    tags=["Authentication"]
)
def login(data: LoginRequest):
    hashed = users_db.get(data.email)
    if not hashed or not verify_password(data.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    payload = {
        "sub": data.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return TokenResponse(access_token=token)


if __name__ == "__main__":
    import uvicorn
    print(f"Запуск Auth Service на порту {SERVICE_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
