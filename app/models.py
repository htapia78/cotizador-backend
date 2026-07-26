"""
Models para la base de datos
SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    nombre_empresa = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    proyectos = relationship("Proyecto", back_populates="usuario")
    materiales = relationship("Material", back_populates="usuario")
    tipos_boca = relationship("TipoDeBoca", back_populates="usuario")


class Proyecto(Base):
    __tablename__ = "proyectos"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nombre = Column(String)
    cliente = Column(String)
    descripcion = Column(Text, nullable=True)
    estado = Column(String, default="en_progreso")  # en_progreso, finalizado
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="proyectos")
    zonas = relationship("Zona", back_populates="proyecto", cascade="all, delete-orphan")
    conteo_bocas = relationship("ConteoBocas", back_populates="proyecto", cascade="all, delete-orphan")
    computo = relationship("Computo", back_populates="proyecto", cascade="all, delete-orphan")
    mano_obra = relationship("ManoDeObra", back_populates="proyecto", cascade="all, delete-orphan")
    presupuestos = relationship("PresupuestoFinal", back_populates="proyecto", cascade="all, delete-orphan")


class Zona(Base):
    __tablename__ = "zonas"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    nombre = Column(String)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="zonas")
    conteo_bocas = relationship("ConteoBocas", back_populates="zona", cascade="all, delete-orphan")


class TipoDeBoca(Base):
    __tablename__ = "tipos_boca"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    nombre = Column(String)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="tipos_boca")
    recetas = relationship("Receta", back_populates="tipo_boca", cascade="all, delete-orphan")
    conteo_bocas = relationship("ConteoBocas", back_populates="tipo_boca", cascade="all, delete-orphan")


class Material(Base):
    __tablename__ = "materiales"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nombre = Column(String)
    unidad = Column(String)  # mts, un, cajas, etc.
    categoria = Column(String)  # Canalización, Cables, Ilum.+Tomas, Tableros, etc.
    precio_unitario = Column(Float, nullable=True, default=0)
    proveedor = Column(String, nullable=True)
    fecha_cotizacion = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="materiales")
    recetas = relationship("Receta", back_populates="material", cascade="all, delete-orphan")
    computo = relationship("Computo", back_populates="material", cascade="all, delete-orphan")


class Receta(Base):
    __tablename__ = "recetas"
    
    id = Column(Integer, primary_key=True)
    tipo_boca_id = Column(Integer, ForeignKey("tipos_boca.id"))
    material_id = Column(Integer, ForeignKey("materiales.id"))
    cantidad = Column(Float)  # Cantidad de este material por boca
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    
    # Relaciones
    tipo_boca = relationship("TipoDeBoca", back_populates="recetas")
    material = relationship("Material", back_populates="recetas")


class ConteoBocas(Base):
    __tablename__ = "conteo_bocas"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    zona_id = Column(Integer, ForeignKey("zonas.id"))
    tipo_boca_id = Column(Integer, ForeignKey("tipos_boca.id"))
    cantidad = Column(Integer)
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="conteo_bocas")
    zona = relationship("Zona", back_populates="conteo_bocas")
    tipo_boca = relationship("TipoDeBoca", back_populates="conteo_bocas")


class Computo(Base):
    __tablename__ = "computo"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    material_id = Column(Integer, ForeignKey("materiales.id"))
    cantidad_calculada = Column(Float)  # Suma de recetas
    cantidad_ajuste = Column(Float, default=0)  # Ajuste manual
    cantidad_final = Column(Float)  # calculada + ajuste
    precio_unitario = Column(Float, nullable=True)  # Viene del material
    subtotal = Column(Float, nullable=True)  # cantidad_final * precio_unitario
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="computo")
    material = relationship("Material", back_populates="computo")


class ManoDeObra(Base):
    __tablename__ = "mano_obra"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    categoria = Column(String)  # Boca de Luz, Tablero, etc.
    descripcion = Column(Text)
    unidad = Column(String)  # un, mts, etc.
    cantidad = Column(Float)
    costo_unitario = Column(Float)
    subtotal = Column(Float)
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="mano_obra")


class PresupuestoFinal(Base):
    __tablename__ = "presupuestos_finales"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    total_materiales = Column(Float)
    total_mano_obra = Column(Float)
    gastos_generales_pct = Column(Float, default=0.12)  # 12%
    ganancia_mo_pct = Column(Float, default=0.35)  # 35%
    ganancia_mat_pct = Column(Float, default=0.35)  # 35%
    total_obra = Column(Float)
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="presupuestos")


class PresupuestoProveedor(Base):
    __tablename__ = "presupuestos_proveedores"
    
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    proveedor_nombre = Column(String)
    material_id = Column(Integer, ForeignKey("materiales.id"))
    precio_cotizado = Column(Float)
    fecha_recibida = Column(DateTime, default=datetime.utcnow)
    archivo_referencia = Column(String, nullable=True)  # Ruta al PDF/Excel subido
