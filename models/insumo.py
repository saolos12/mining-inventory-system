from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Insumo(db.Model):
    __tablename__ = 'insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=True) # Ej: EXP-001 (Explosivo)
    categoria = db.Column(db.String(50), nullable=False) # Ej: Explosivos, EPP, Herramientas
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    unidad = db.Column(db.String(20), nullable=False) # Ej: Kilos, Cajas, Unidades
    ubicacion = db.Column(db.String(100), nullable=True) # Ej: Almacén Central, Polvorín
    estado = db.Column(db.String(50), default='Bueno') # Bueno, Dañado, En reparación
    observaciones = db.Column(db.Text, nullable=True) # El campo que pediste explícitamente
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campo para control de actualizaciones (importante en auditoría minera)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Insumo {self.nombre}>'