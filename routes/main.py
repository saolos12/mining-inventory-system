from flask import Blueprint, render_template
from models.insumo import Insumo, db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    # CORRECCIÓN: Usamos 'cantidad_actual' en lugar de 'cantidad'
    total_items = db.session.query(func.sum(Insumo.cantidad_actual)).scalar() or 0
    
    total_registros = Insumo.query.count()
    total_categorias = db.session.query(Insumo.categoria).distinct().count()

    # CORRECCIÓN: Aquí también cambiamos a 'cantidad_actual'
    alertas_bajas = Insumo.query.filter(Insumo.cantidad_actual < 10).count()

    # CORRECCIÓN: Y aquí también
    datos_categoria = db.session.query(
        Insumo.categoria, func.sum(Insumo.cantidad_actual)
    ).group_by(Insumo.categoria).all()

    return render_template('dashboard.html', 
                           total_items=total_items,
                           total_registros=total_registros,
                           total_categorias=total_categorias,
                           alertas_bajas=alertas_bajas,
                           datos_categoria=datos_categoria)
