from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI(title="Cotizador")

proyectos = {}
contador_proyectos = 0

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/login")
async def login(request: Request):
    data = await request.json()
    return {"access_token": "token-123", "token_type": "bearer"}

@app.get("/api/auth/me")
def me():
    return {"id": 1, "email": "test@example.com", "nombre_empresa": "APEXCORE"}

@app.get("/api/proyectos/")
def list_proyectos():
    return list(proyectos.values())

@app.post("/api/proyectos/")
async def crear_proyecto(request: Request):
    global contador_proyectos
    data = await request.json()
    contador_proyectos += 1
    
    proyecto = {
        "id": contador_proyectos,
        "nombre": data.get("nombre"),
        "cliente": data.get("cliente"),
        "descripcion": data.get("descripcion", ""),
        "estado": "en_progreso",
        "fecha_creacion": datetime.now().isoformat()
    }
    proyectos[contador_proyectos] = proyecto
    return proyecto

@app.get("/api/health")
def health():
    return {"status": "ok"}
