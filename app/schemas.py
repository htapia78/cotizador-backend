"""
Schemas para validación de datos (Pydantic)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ===== USUARIO =====
class UsuarioRegistro(BaseModel):
    email: EmailStr
    password: str
    nombre_empresa: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre_empresa: str
    
    class Config:
        from_attributes = True


# ===== PROYECTO =====
class ProyectoCreate(BaseModel):
    nombre: str
    cliente: str
    descripcion: Optional[str] = None


class ProyectoUpdate(BaseModel):
    nombre: Optional[str] = None
    cliente: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None


class ProyectoResponse(BaseModel):
    id: int
    nombre: str
    cliente: str
    descripcion: Optional[str]
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


# ===== ZONA =====
class ZonaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class ZonaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class ZonaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    
    class Config:
        from_attributes = True


# ===== TIPO DE BOCA =====
class TipoDeBocaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class TipoDeBocaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class TipoDeBocaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    activo: bool
    
    class Config:
        from_attributes = True


# ===== MATERIAL =====
class MaterialCreate(BaseModel):
    nombre: str
    unidad: str
    categoria: str
    precio_unitario: Optional[float] = 0
    proveedor: Optional[str] = None


class MaterialUpdate(BaseModel):
    nombre: Optional[str] = None
    unidad: Optional[str] = None
    categoria: Optional[str] = None
    precio_unitario: Optional[float] = None
    proveedor: Optional[str] = None


class MaterialResponse(BaseModel):
    id: int
    nombre: str
    unidad: str
    categoria: str
    precio_unitario: Optional[float]
    proveedor: Optional[str]
    fecha_cotizacion: Optional[datetime]
    activo: bool
    
    class Config:
        from_attributes = True


# ===== RECETA =====
class RecetaCreate(BaseModel):
    tipo_boca_id: int
    material_id: int
    cantidad: float


class RecetaUpdate(BaseModel):
    cantidad: Optional[float] = None


class RecetaResponse(BaseModel):
    id: int
    tipo_boca_id: int
    material_id: int
    cantidad: float
    
    class Config:
        from_attributes = True


class RecetaDetailResponse(BaseModel):
    id: int
    tipo_boca_id: int
    tipo_boca_nombre: str
    material_id: int
    material_nombre: str
    material_unidad: str
    cantidad: float


# ===== CONTEO DE BOCAS =====
class ConteoBocasCreate(BaseModel):
    zona_id: int
    tipo_boca_id: int
    cantidad: int


class ConteoBocasUpdate(BaseModel):
    cantidad: int


class ConteoBocasResponse(BaseModel):
    id: int
    zona_id: int
    tipo_boca_id: int
    cantidad: int
    
    class Config:
        from_attributes = True


# ===== CÓMPUTO =====
class ComputoResponse(BaseModel):
    id: int
    material_id: int
    material_nombre: str
    material_unidad: str
    categoria: str
    cantidad_calculada: float
    cantidad_ajuste: float
    cantidad_final: float
    precio_unitario: Optional[float]
    subtotal: Optional[float]
    
    class Config:
        from_attributes = True


# ===== MANO DE OBRA =====
class ManoDeObraCreate(BaseModel):
    categoria: str
    descripcion: str
    unidad: str
    cantidad: float
    costo_unitario: float


class ManoDeObraUpdate(BaseModel):
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    unidad: Optional[str] = None
    cantidad: Optional[float] = None
    costo_unitario: Optional[float] = None


class ManoDeObraResponse(BaseModel):
    id: int
    categoria: str
    descripcion: str
    unidad: str
    cantidad: float
    costo_unitario: float
    subtotal: float
    
    class Config:
        from_attributes = True


# ===== PRESUPUESTO FINAL =====
class PresupuestoFinalResponse(BaseModel):
    id: int
    proyecto_id: int
    total_materiales: float
    total_mano_obra: float
    gastos_generales_pct: float
    ganancia_mo_pct: float
    ganancia_mat_pct: float
    total_obra: float
    fecha_generacion: datetime
    version: int
    
    class Config:
        from_attributes = True


# ===== TOKEN =====
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
