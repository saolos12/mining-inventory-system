from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabla de Productos (Catálogo)
class Insumo(db.Model):
    __tablename__ = 'insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    ubicacion = db.Column(db.String(100))
    observaciones = db.Column(db.Text, nullable=True)
    
    # Stock actual (Se actualiza automáticamente con los movimientos)
    cantidad_actual = db.Column(db.Integer, default=0)
    
    # Relación con el historial
    movimientos = db.relationship('Movimiento', backref='insumo', lazy=True, cascade="all, delete-orphan")

# Tabla de Historial (Movimientos de Entrada/Salida)
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False) # 'ENTRADA' o 'SALIDA'
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200)) # Ej: Nro Factura o Nombre de quien retira
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
