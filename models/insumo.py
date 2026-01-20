from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabla de Productos (El Catálogo)
class Insumo(db.Model):
    __tablename__ = 'insumos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    cantidad_actual = db.Column(db.Integer, default=0) # Esto se actualiza solo
    ubicacion = db.Column(db.String(100))
    
    # Relación: Un insumo tiene muchos movimientos
    movimientos = db.relationship('Movimiento', backref='insumo', lazy=True, cascade="all, delete-orphan")

# NUEVA TABLA: Historial de Entradas y Salidas
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    id = db.Column(db.Integer, primary_key=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False) # 'ENTRADA' o 'SALIDA'
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200)) # Ej: "Compra Factura #123" o "Entrega a Jefe de Turno"
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
