from flask import Blueprint, render_template
from models.insumo import Insumo, db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    # 1. Total de items físicos (suma de cantidades)
    total_items = db.session.query(func.sum(Insumo.cantidad)).scalar() or 0
    
    # 2. Total de registros únicos (tipos de insumos)
    total_registros = Insumo.query.count()
    
    # 3. Valor aproximado del inventario (si tuvieras precio, aquí iría la suma)
    # Por ahora contamos cuántas categorías distintas hay
    total_categorias = db.session.query(Insumo.categoria).distinct().count()

    # 4. Alerta de Stock Bajo (Menos de 10 unidades)
    alertas_bajas = Insumo.query.filter(Insumo.cantidad < 10).count()

    # 5. Datos para gráfica (Agrupado por Categoria)
    datos_categoria = db.session.query(
        Insumo.categoria, func.sum(Insumo.cantidad)
    ).group_by(Insumo.categoria).all()

    return render_template('dashboard.html', 
                           total_items=total_items,
                           total_registros=total_registros,
                           total_categorias=total_categorias,
                           alertas_bajas=alertas_bajas,
                           datos_categoria=datos_categoria)