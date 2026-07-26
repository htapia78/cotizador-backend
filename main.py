from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Cotizador")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/login")
def login_dummy(email: str, password: str):
    return {"access_token": "token-dummy-123", "token_type": "bearer"}

@app.get("/api/auth/me")
def me():
    return {"id": 1, "email": "test@example.com", "nombre_empresa": "APEXCORE"}

@app.get("/api/proyectos/")
def list_proyectos():
    return []
