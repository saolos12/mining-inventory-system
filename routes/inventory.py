from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from models.insumo import Insumo, Movimiento, db
# ... (Manten las importaciones de PDF reportlab que ya tenías) ...
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventario')
def lista():
    insumos = Insumo.query.order_by(Insumo.id.desc()).all()
    return render_template('inventario.html', insumos=insumos)

# --- AGREGAR (Misma lógica, ahora guarda estado) ---
@inventory_bp.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        try:
            nuevo = Insumo(
                nombre=request.form['nombre'],
                codigo=request.form['codigo'],
                categoria=request.form['categoria'],
                unidad=request.form['unidad'],
                ubicacion=request.form['ubicacion'],
                observaciones=request.form['observaciones'],
                estado=request.form['estado'], # <--- Guardamos estado
                cantidad_actual=0
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Item creado. Ahora registra una ENTRADA.', 'success')
            return redirect(url_for('inventory.lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('agregar.html', accion="Agregar")

# --- NUEVA RUTA: EDITAR ITEM Y ESTADO ---
@inventory_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    insumo = Insumo.query.get_or_404(id)
    
    if request.method == 'POST':
        insumo.nombre = request.form['nombre']
        insumo.codigo = request.form['codigo']
        insumo.categoria = request.form['categoria']
        insumo.unidad = request.form['unidad']
        insumo.ubicacion = request.form['ubicacion']
        insumo.observaciones = request.form['observaciones']
        insumo.estado = request.form['estado'] # <--- Actualizamos estado
        
        db.session.commit()
        flash('Datos del item actualizados correctamente.', 'info')
        return redirect(url_for('inventory.lista'))
        
    # Reutilizamos el template de agregar pero con datos
    return render_template('agregar.html', accion="Editar", insumo=insumo)

# ... (Manten las rutas de movimiento, kardex y pdf iguales al mensaje anterior) ...
# IMPORTANTE: Copia aquí las rutas 'movimiento', 'ver_kardex' y 'descargar_kardex_pdf' 
# del mensaje anterior, son idénticas.
@inventory_bp.route('/movimiento', methods=['POST'])
def movimiento():
    insumo_id = request.form.get('insumo_id')
    tipo = request.form.get('tipo')
    cantidad = int(request.form.get('cantidad'))
    motivo = request.form.get('motivo')
    
    insumo = Insumo.query.get_or_404(insumo_id)
    
    if tipo == 'SALIDA':
        if insumo.cantidad_actual < cantidad:
            flash(f'Error: Stock insuficiente. Tienes {insumo.cantidad_actual}.', 'danger')
            return redirect(url_for('inventory.lista'))
        insumo.cantidad_actual -= cantidad
    elif tipo == 'ENTRADA':
        insumo.cantidad_actual += cantidad
    
    nuevo_mov = Movimiento(
        insumo_id=insumo.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo
    )
    db.session.add(nuevo_mov)
    db.session.commit()
    
    flash(f'Movimiento registrado: {tipo} de {cantidad} {insumo.unidad}', 'success')
    return redirect(url_for('inventory.lista'))

@inventory_bp.route('/kardex/<int:id>')
def ver_kardex(id):
    insumo = Insumo.query.get_or_404(id)
    movimientos = Movimiento.query.filter_by(insumo_id=id).order_by(Movimiento.fecha.desc()).all()
    return render_template('kardex.html', insumo=insumo, movimientos=movimientos)

@inventory_bp.route('/kardex/<int:id>/pdf')
def descargar_kardex_pdf(id):
    # ... (Copia el código del PDF del mensaje anterior aquí) ...
    # Solo asegúrate de incluir el PDF generator code.
    insumo = Insumo.query.get_or_404(id)
    movimientos = Movimiento.query.filter_by(insumo_id=id).order_by(Movimiento.fecha.desc()).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("COOPERATIVA MINERA QANTATY R.L.", styles['Title']))
    elements.append(Paragraph(f"KARDEX INDIVIDUAL: {insumo.estado.upper()}", styles['Heading2'])) # Mostramos estado en PDF
    elements.append(Spacer(1, 15))
    
    info_texto = f"""
    <b>CÓDIGO:</b> {insumo.codigo} <br/>
    <b>ITEM:</b> {insumo.nombre} <br/>
    <b>ESTADO ACTUAL:</b> {insumo.estado} <br/> 
    <b>STOCK:</b> {insumo.cantidad_actual} {insumo.unidad}
    """
    elements.append(Paragraph(info_texto, styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [['FECHA', 'TIPO', 'MOTIVO', 'CANTIDAD']]
    for mov in movimientos:
        row = [
            mov.fecha.strftime("%d/%m/%Y %H:%M"),
            mov.tipo,
            mov.motivo,
            str(mov.cantidad)
        ]
        data.append(row)

    table = Table(data, colWidths=[120, 80, 250, 60])
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ])
    table.setStyle(ts)
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Kardex_{insumo.codigo}.pdf'
    return response

@inventory_bp.route('/eliminar/<int:id>')
def eliminar(id):
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    flash('Item eliminado.', 'warning')
    return redirect(url_for('inventory.lista'))
