from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.insumo import Insumo, Movimiento, db

inventory_bp = Blueprint('inventory', __name__)

# --- 1. LISTAR INVENTARIO ---
@inventory_bp.route('/inventario')
def lista():
    # Buscamos todos los items ordenados del más nuevo al más viejo
    insumos = Insumo.query.order_by(Insumo.id.desc()).all()
    return render_template('inventario.html', insumos=insumos)

# --- 2. AGREGAR NUEVO ITEM (Catálogo) ---
@inventory_bp.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        # CORRECCIÓN APLICADA: Usamos 'codigo' en lugar de 'codigo_interno'
        nuevo_insumo = Insumo(
            nombre=request.form['nombre'],
            codigo=request.form['codigo'],
            categoria=request.form['categoria'],
            unidad=request.form['unidad'],
            ubicacion=request.form['ubicacion'],
            observaciones=request.form['observaciones'],
            cantidad_actual=0  # Empieza en 0 hasta que registres una entrada
        )
        
        try:
            db.session.add(nuevo_insumo)
            db.session.commit()
            flash('Nuevo item creado en el catálogo. Ahora registra una ENTRADA.', 'success')
            return redirect(url_for('inventory.lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            return render_template('agregar.html', accion="Agregar")
    
    return render_template('agregar.html', accion="Agregar")

# --- 3. REGISTRAR MOVIMIENTO (Kardex: Entradas/Salidas) ---
@inventory_bp.route('/movimiento', methods=['POST'])
def movimiento():
    # Capturamos datos del Modal
    insumo_id = request.form.get('insumo_id')
    tipo = request.form.get('tipo') # 'ENTRADA' o 'SALIDA'
    cantidad = int(request.form.get('cantidad'))
    motivo = request.form.get('motivo')
    
    insumo = Insumo.query.get_or_404(insumo_id)
    
    # Lógica de Validación Minera
    if tipo == 'SALIDA':
        if insumo.cantidad_actual < cantidad:
            flash(f'Error: Stock insuficiente. Tienes {insumo.cantidad_actual}, intentaste sacar {cantidad}.', 'danger')
            return redirect(url_for('inventory.lista'))
        
        # Restamos stock
        insumo.cantidad_actual -= cantidad
        
    elif tipo == 'ENTRADA':
        # Sumamos stock
        insumo.cantidad_actual += cantidad
    
    # Guardamos el registro en el historial (Tabla Movimientos)
    nuevo_movimiento = Movimiento(
        insumo_id=insumo.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo
    )
    
    db.session.add(nuevo_movimiento)
    db.session.commit()
    
    flash(f'Movimiento exitoso: {tipo} de {cantidad} {insumo.unidad}', 'success')
    return redirect(url_for('inventory.lista'))

# --- 4. ELIMINAR ITEM (Opcional, pero útil) ---
@inventory_bp.route('/eliminar/<int:id>')
def eliminar(id):
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    flash('Item eliminado del sistema correctamente.', 'warning')
    return redirect(url_for('inventory.lista'))
