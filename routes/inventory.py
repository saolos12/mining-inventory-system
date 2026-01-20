from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.insumo import Insumo, db

inventory_bp = Blueprint('inventory', __name__)

# --- LISTAR ---
@inventory_bp.route('/inventario')
def lista():
    search = request.args.get('search')
    filtro_cat = request.args.get('categoria')
    
    query = Insumo.query
    
    # Filtros dinámicos
    if search:
        query = query.filter(Insumo.nombre.ilike(f'%{search}%'))
    if filtro_cat and filtro_cat != "Todas":
        query = query.filter_by(categoria=filtro_cat)
        
    insumos = query.order_by(Insumo.id.desc()).all()
    
    # Obtener categorías únicas para el dropdown de filtro
    categorias = db.session.query(Insumo.categoria).distinct().all()
    
    return render_template('inventario.html', insumos=insumos, categorias=categorias)

# --- AGREGAR ---
@inventory_bp.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nuevo = Insumo(
            nombre=request.form['nombre'],
            codigo_interno=request.form['codigo'],
            categoria=request.form['categoria'],
            cantidad=request.form['cantidad'],
            unidad=request.form['unidad'],
            ubicacion=request.form['ubicacion'],
            observaciones=request.form['observaciones']
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Insumo agregado exitosamente', 'success')
        return redirect(url_for('inventory.lista'))
    
    return render_template('agregar.html', accion="Agregar")

# --- EDITAR ---
@inventory_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    insumo = Insumo.query.get_or_404(id)
    
    if request.method == 'POST':
        insumo.nombre = request.form['nombre']
        insumo.codigo_interno = request.form['codigo']
        insumo.categoria = request.form['categoria']
        insumo.cantidad = request.form['cantidad']
        insumo.unidad = request.form['unidad']
        insumo.ubicacion = request.form['ubicacion']
        insumo.observaciones = request.form['observaciones']
        
        db.session.commit()
        flash('Insumo actualizado correctamente', 'info')
        return redirect(url_for('inventory.lista'))

    return render_template('agregar.html', accion="Editar", insumo=insumo)

# --- ELIMINAR ---
@inventory_bp.route('/eliminar/<int:id>')
def eliminar(id):
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    flash('Insumo eliminado del sistema', 'warning')

    return redirect(url_for('inventory.lista'))
    # --- NUEVA RUTA: REGISTRAR MOVIMIENTO (KARDEX) ---
@inventory_bp.route('/movimiento', methods=['POST'])
def movimiento():
    insumo_id = request.form['insumo_id']
    tipo = request.form['tipo'] # Puede ser 'ENTRADA' o 'SALIDA'
    cantidad = int(request.form['cantidad'])
    motivo = request.form['motivo']
    
    insumo = Insumo.query.get_or_404(insumo_id)
    
    # Validación de Lógica Minera
    if tipo == 'SALIDA':
        if insumo.cantidad_actual < cantidad:
            flash(f'Error: No tienes suficiente stock de {insumo.nombre}. Tienes {insumo.cantidad_actual}, intentaste sacar {cantidad}.', 'danger')
            return redirect(url_for('inventory.lista'))
        
        # Restar stock
        insumo.cantidad_actual -= cantidad
        
    elif tipo == 'ENTRADA':
        # Sumar stock
        insumo.cantidad_actual += cantidad
    
    # Guardar en el historial (La tabla nueva)
    nuevo_movimiento = Movimiento(
        insumo_id=insumo.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo
    )
    
    db.session.add(nuevo_movimiento)
    db.session.commit()
    
    flash(f'Movimiento registrado: {tipo} de {cantidad} {insumo.unidad}', 'success')
    return redirect(url_for('inventory.lista'))
