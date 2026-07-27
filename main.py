from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(title="Cotizador")

# Datos en memoria (temporal, solo para testing)
usuarios = {}
proyectos = {}
contador_proyectos = 0

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH
@app.post("/api/auth/login")
def login_dummy(email: str, password: str):
    return {"access_token": "token-dummy-123", "token_type": "bearer"}

@app.get("/api/auth/me")
def me():
    return {"id": 1, "email": "test@example.com", "nombre_empresa": "APEXCORE"}

# PROYECTOS
@app.get("/api/proyectos/")
def list_proyectos():
    return list(proyectos.values())

@app.post("/api/proyectos/")
def crear_proyecto(nombre: str, cliente: str, descripcion: str = ""):
    global contador_proyectos
    contador_proyectos += 1
    proyecto = {
        "id": contador_proyectos,
        "nombre": nombre,
        "cliente": cliente,
        "descripcion": descripcion,
        "estado": "en_progreso",
        "fecha_creacion": datetime.now().isoformat()
    }
    proyectos[contador_proyectos] = proyecto
    return proyecto

@app.get("/api/health")
def health():
    return {"status": "ok"}
