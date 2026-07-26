"""
FastAPI Application - Cotizador de Obras Eléctricas
Main file con todas las rutas integradas
"""

import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ===== IMPORTAR MODELOS Y SCHEMAS =====
from .models import Base, Usuario, Proyecto, Zona, TipoDeBoca, Material, Receta, ConteoBocas, Computo
from .schemas import (
    UsuarioRegistro, UsuarioLogin, Token,
    ProyectoCreate, ProyectoUpdate, ProyectoResponse,
    ZonaCreate, ZonaUpdate, ZonaResponse,
    TipoDeBocaCreate, TipoDeBocaUpdate, TipoDeBocaResponse,
    MaterialCreate, MaterialUpdate, MaterialResponse,
    RecetaCreate, RecetaUpdate, RecetaDetailResponse,
    ConteoBocasCreate, ConteoBocasUpdate, ConteoBocasResponse,
    ComputoResponse
)
from .auth import (
    hash_password, verify_password, create_access_token, get_current_user
)

# ===== CONFIGURACIÓN BD =====
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/cotizador_db"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== CREAR APP =====
app = FastAPI(
    title="Cotizador de Obras Eléctricas",
    description="Sistema de presupuestos para instalaciones eléctricas",
    version="0.1.0"
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== AUTH ENDPOINTS =====

@app.post("/api/auth/registro")
def registro(usuario: UsuarioRegistro, db: Session = Depends(get_db)):
    existing = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    nuevo_usuario = Usuario(
        email=usuario.email,
        password_hash=hash_password(usuario.password),
        nombre_empresa=usuario.nombre_empresa
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"id": nuevo_usuario.id, "email": nuevo_usuario.email, "nombre_empresa": nuevo_usuario.nombre_empresa}


@app.post("/api/auth/login")
def login(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    if not usuario or not verify_password(credenciales.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    
    access_token = create_access_token(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me")
def get_current(usuario: Usuario = Depends(get_current_user)):
    return {"id": usuario.id, "email": usuario.email, "nombre_empresa": usuario.nombre_empresa}


# ===== PROYECTOS =====

@app.get("/api/proyectos/")
def listar_proyectos(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyectos = db.query(Proyecto).filter(Proyecto.usuario_id == usuario.id).all()
    return [
        {
            "id": p.id, "nombre": p.nombre, "cliente": p.cliente,
            "descripcion": p.descripcion, "estado": p.estado, "fecha_creacion": p.fecha_creacion
        }
        for p in proyectos
    ]


@app.post("/api/proyectos/")
def crear_proyecto(proyecto: ProyectoCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    nuevo = Proyecto(
        usuario_id=usuario.id, nombre=proyecto.nombre, cliente=proyecto.cliente, descripcion=proyecto.descripcion
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"id": nuevo.id, "nombre": nuevo.nombre, "cliente": nuevo.cliente, "descripcion": nuevo.descripcion, "estado": nuevo.estado, "fecha_creacion": nuevo.fecha_creacion}


@app.get("/api/proyectos/{proyecto_id}")
def obtener_proyecto(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.usuario_id == usuario.id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"id": proyecto.id, "nombre": proyecto.nombre, "cliente": proyecto.cliente, "descripcion": proyecto.descripcion, "estado": proyecto.estado, "fecha_creacion": proyecto.fecha_creacion}


@app.put("/api/proyectos/{proyecto_id}")
def actualizar_proyecto(proyecto_id: int, proyecto_data: ProyectoUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.usuario_id == usuario.id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if proyecto_data.nombre:
        proyecto.nombre = proyecto_data.nombre
    if proyecto_data.cliente:
        proyecto.cliente = proyecto_data.cliente
    if proyecto_data.descripcion:
        proyecto.descripcion = proyecto_data.descripcion
    if proyecto_data.estado:
        proyecto.estado = proyecto_data.estado
    
    db.commit()
    db.refresh(proyecto)
    return {"id": proyecto.id, "nombre": proyecto.nombre, "cliente": proyecto.cliente, "descripcion": proyecto.descripcion, "estado": proyecto.estado, "fecha_creacion": proyecto.fecha_creacion}


@app.delete("/api/proyectos/{proyecto_id}")
def eliminar_proyecto(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.usuario_id == usuario.id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(proyecto)
    db.commit()
    return {"mensaje": "Proyecto eliminado"}


# ===== ZONAS =====

@app.get("/api/proyectos/{proyecto_id}/zonas")
def listar_zonas(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    zonas = db.query(Zona).filter(Zona.proyecto_id == proyecto_id).all()
    return [{"id": z.id, "nombre": z.nombre, "descripcion": z.descripcion} for z in zonas]


@app.post("/api/proyectos/{proyecto_id}/zonas")
def crear_zona(proyecto_id: int, zona: ZonaCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    nueva = Zona(proyecto_id=proyecto_id, nombre=zona.nombre, descripcion=zona.descripcion)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"id": nueva.id, "nombre": nueva.nombre, "descripcion": nueva.descripcion}


@app.put("/api/zonas/{zona_id}")
def actualizar_zona(zona_id: int, zona_data: ZonaUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    zona = db.query(Zona).join(Proyecto).filter(Zona.id == zona_id, Proyecto.usuario_id == usuario.id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    if zona_data.nombre:
        zona.nombre = zona_data.nombre
    if zona_data.descripcion:
        zona.descripcion = zona_data.descripcion
    db.commit()
    db.refresh(zona)
    return {"id": zona.id, "nombre": zona.nombre, "descripcion": zona.descripcion}


@app.delete("/api/zonas/{zona_id}")
def eliminar_zona(zona_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    zona = db.query(Zona).join(Proyecto).filter(Zona.id == zona_id, Proyecto.usuario_id == usuario.id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    db.delete(zona)
    db.commit()
    return {"mensaje": "Zona eliminada"}


# ===== TIPOS DE BOCA =====

@app.get("/api/proyectos/{proyecto_id}/tipos-boca")
def listar_tipos_boca(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    tipos = db.query(TipoDeBoca).filter(
        (TipoDeBoca.usuario_id == usuario.id) & ((TipoDeBoca.proyecto_id == None) | (TipoDeBoca.proyecto_id == proyecto_id)), TipoDeBoca.activo == True
    ).all()
    return [{"id": t.id, "nombre": t.nombre, "descripcion": t.descripcion, "activo": t.activo} for t in tipos]


@app.post("/api/proyectos/{proyecto_id}/tipos-boca")
def crear_tipo_boca(proyecto_id: int, tipo: TipoDeBocaCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    nuevo = TipoDeBoca(usuario_id=usuario.id, proyecto_id=proyecto_id, nombre=tipo.nombre, descripcion=tipo.descripcion)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"id": nuevo.id, "nombre": nuevo.nombre, "descripcion": nuevo.descripcion, "activo": nuevo.activo}


@app.put("/api/tipos-boca/{tipo_id}")
def actualizar_tipo_boca(tipo_id: int, tipo_data: TipoDeBocaUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    tipo = db.query(TipoDeBoca).filter(TipoDeBoca.id == tipo_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de boca no encontrado")
    if tipo_data.nombre:
        tipo.nombre = tipo_data.nombre
    if tipo_data.descripcion:
        tipo.descripcion = tipo_data.descripcion
    db.commit()
    db.refresh(tipo)
    return {"id": tipo.id, "nombre": tipo.nombre, "descripcion": tipo.descripcion, "activo": tipo.activo}


@app.delete("/api/tipos-boca/{tipo_id}")
def eliminar_tipo_boca(tipo_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    tipo = db.query(TipoDeBoca).filter(TipoDeBoca.id == tipo_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de boca no encontrado")
    tipo.activo = False
    db.commit()
    return {"mensaje": "Tipo de boca eliminado"}


# ===== MATERIALES =====

@app.get("/api/proyectos/{proyecto_id}/materiales")
def listar_materiales(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    materiales = db.query(Material).filter(Material.usuario_id == usuario.id, Material.activo == True).all()
    return [{"id": m.id, "nombre": m.nombre, "unidad": m.unidad, "categoria": m.categoria, "precio_unitario": m.precio_unitario, "proveedor": m.proveedor, "fecha_cotizacion": m.fecha_cotizacion, "activo": m.activo} for m in materiales]


@app.post("/api/materiales")
def crear_material(material: MaterialCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    nuevo = Material(usuario_id=usuario.id, nombre=material.nombre, unidad=material.unidad, categoria=material.categoria, precio_unitario=material.precio_unitario, proveedor=material.proveedor)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"id": nuevo.id, "nombre": nuevo.nombre, "unidad": nuevo.unidad, "categoria": nuevo.categoria, "precio_unitario": nuevo.precio_unitario, "proveedor": nuevo.proveedor, "fecha_cotizacion": nuevo.fecha_cotizacion, "activo": nuevo.activo}


@app.put("/api/materiales/{material_id}")
def actualizar_material(material_id: int, material_data: MaterialUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id, Material.usuario_id == usuario.id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    if material_data.nombre:
        material.nombre = material_data.nombre
    if material_data.unidad:
        material.unidad = material_data.unidad
    if material_data.categoria:
        material.categoria = material_data.categoria
    if material_data.precio_unitario is not None:
        material.precio_unitario = material_data.precio_unitario
    if material_data.proveedor:
        material.proveedor = material_data.proveedor
    db.commit()
    db.refresh(material)
    return {"id": material.id, "nombre": material.nombre, "unidad": material.unidad, "categoria": material.categoria, "precio_unitario": material.precio_unitario, "proveedor": material.proveedor, "fecha_cotizacion": material.fecha_cotizacion, "activo": material.activo}


@app.delete("/api/materiales/{material_id}")
def eliminar_material(material_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id, Material.usuario_id == usuario.id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    material.activo = False
    db.commit()
    return {"mensaje": "Material eliminado"}


# ===== RECETAS =====

@app.get("/api/tipos-boca/{tipo_id}/recetas")
def listar_recetas_boca(tipo_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    tipo = db.query(TipoDeBoca).filter(TipoDeBoca.id == tipo_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de boca no encontrado")
    
    recetas = db.query(Receta).join(Material).filter(Receta.tipo_boca_id == tipo_id).all()
    return [{
        "id": r.id, "tipo_boca_id": r.tipo_boca_id, "tipo_boca_nombre": r.tipo_boca.nombre,
        "material_id": r.material_id, "material_nombre": r.material.nombre, "material_unidad": r.material.unidad, "cantidad": r.cantidad
    } for r in recetas]


@app.post("/api/tipos-boca/{tipo_id}/recetas")
def crear_receta(tipo_id: int, receta: RecetaCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    tipo = db.query(TipoDeBoca).filter(TipoDeBoca.id == tipo_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de boca no encontrado")
    
    material = db.query(Material).filter(Material.id == receta.material_id, Material.usuario_id == usuario.id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    
    nueva = Receta(tipo_boca_id=tipo_id, material_id=receta.material_id, cantidad=receta.cantidad)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"id": nueva.id, "tipo_boca_id": nueva.tipo_boca_id, "material_id": nueva.material_id, "cantidad": nueva.cantidad}


@app.put("/api/recetas/{receta_id}")
def actualizar_receta(receta_id: int, receta_data: RecetaUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    receta = db.query(Receta).join(TipoDeBoca).filter(Receta.id == receta_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    if receta_data.cantidad is not None:
        receta.cantidad = receta_data.cantidad
    db.commit()
    db.refresh(receta)
    return {"id": receta.id, "tipo_boca_id": receta.tipo_boca_id, "material_id": receta.material_id, "cantidad": receta.cantidad}


@app.delete("/api/recetas/{receta_id}")
def eliminar_receta(receta_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    receta = db.query(Receta).join(TipoDeBoca).filter(Receta.id == receta_id, TipoDeBoca.usuario_id == usuario.id).first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    db.delete(receta)
    db.commit()
    return {"mensaje": "Receta eliminada"}


# ===== CONTEO DE BOCAS =====

@app.get("/api/proyectos/{proyecto_id}/conteo-bocas")
def listar_conteo_bocas(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    _verificar_proyecto(proyecto_id, usuario, db)
    conteos = db.query(ConteoBocas).filter(ConteoBocas.proyecto_id == proyecto_id).all()
    return [{"id": c.id, "zona_id": c.zona_id, "tipo_boca_id": c.tipo_boca_id, "cantidad": c.cantidad} for c in conteos]


@app.post("/api/proyectos/{proyecto_id}/conteo-bocas")
def crear_conteo_bocas(proyecto_id: int, conteo: ConteoBocasCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyecto = _verificar_proyecto(proyecto_id, usuario, db)
    
    zona = db.query(Zona).filter(Zona.id == conteo.zona_id, Zona.proyecto_id == proyecto_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    tipo = db.query(TipoDeBoca).filter(TipoDeBoca.id == conteo.tipo_boca_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de boca no encontrado")
    
    existing = db.query(ConteoBocas).filter(ConteoBocas.proyecto_id == proyecto_id, ConteoBocas.zona_id == conteo.zona_id, ConteoBocas.tipo_boca_id == conteo.tipo_boca_id).first()
    if existing:
        existing.cantidad = conteo.cantidad
        db.commit()
        db.refresh(existing)
        return {"id": existing.id, "zona_id": existing.zona_id, "tipo_boca_id": existing.tipo_boca_id, "cantidad": existing.cantidad}
    
    nuevo = ConteoBocas(proyecto_id=proyecto_id, zona_id=conteo.zona_id, tipo_boca_id=conteo.tipo_boca_id, cantidad=conteo.cantidad)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"id": nuevo.id, "zona_id": nuevo.zona_id, "tipo_boca_id": nuevo.tipo_boca_id, "cantidad": nuevo.cantidad}


@app.put("/api/conteo-bocas/{conteo_id}")
def actualizar_conteo_bocas(conteo_id: int, conteo_data: ConteoBocasUpdate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    conteo = db.query(ConteoBocas).join(Proyecto).filter(ConteoBocas.id == conteo_id, Proyecto.usuario_id == usuario.id).first()
    if not conteo:
        raise HTTPException(status_code=404, detail="Conteo no encontrado")
    conteo.cantidad = conteo_data.cantidad
    db.commit()
    db.refresh(conteo)
    return {"id": conteo.id, "zona_id": conteo.zona_id, "tipo_boca_id": conteo.tipo_boca_id, "cantidad": conteo.cantidad}


# ===== CÓMPUTO =====

@app.get("/api/proyectos/{proyecto_id}/computo")
def calcular_computo(proyecto_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    proyecto = _verificar_proyecto(proyecto_id, usuario, db)
    
    db.query(Computo).filter(Computo.proyecto_id == proyecto_id).delete()
    
    materiales = db.query(Material).filter(Material.usuario_id == usuario.id, Material.activo == True).all()
    
    for material in materiales:
        cantidad_calculada = 0
        
        recetas = db.query(Receta).filter(Receta.material_id == material.id).all()
        
        for receta in recetas:
            conteos = db.query(ConteoBocas).filter(ConteoBocas.proyecto_id == proyecto_id, ConteoBocas.tipo_boca_id == receta.tipo_boca_id).all()
            
            for conteo in conteos:
                cantidad_calculada += conteo.cantidad * receta.cantidad
        
        if cantidad_calculada > 0:
            computo = Computo(
                proyecto_id=proyecto_id, material_id=material.id, cantidad_calculada=cantidad_calculada,
                cantidad_ajuste=0, cantidad_final=cantidad_calculada, precio_unitario=material.precio_unitario,
                subtotal=cantidad_calculada * (material.precio_unitario or 0)
            )
            db.add(computo)
    
    db.commit()
    
    computos = db.query(Computo).join(Material).filter(Computo.proyecto_id == proyecto_id).all()
    
    return [{
        "id": c.id, "material_id": c.material_id, "material_nombre": c.material.nombre, "material_unidad": c.material.unidad,
        "categoria": c.material.categoria, "cantidad_calculada": c.cantidad_calculada, "cantidad_ajuste": c.cantidad_ajuste,
        "cantidad_final": c.cantidad_final, "precio_unitario": c.precio_unitario, "subtotal": c.subtotal
    } for c in computos]


# ===== HEALTH CHECK =====

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ===== HELPERS =====

def _verificar_proyecto(proyecto_id: int, usuario: Usuario, db: Session) -> Proyecto:
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id, Proyecto.usuario_id == usuario.id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
