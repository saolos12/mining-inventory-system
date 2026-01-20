from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from models.insumo import Insumo, Movimiento, db
from datetime import datetime

# Importaciones para PDF (ReportLab)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import io

inventory_bp = Blueprint('inventory', __name__)

# --- LISTAR INVENTARIO ---
@inventory_bp.route('/inventario')
def lista():
    insumos = Insumo.query.order_by(Insumo.id.desc()).all()
    return render_template('inventario.html', insumos=insumos)

# --- AGREGAR NUEVO ITEM ---
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
                cantidad_actual=0 # Empieza en 0
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Item creado correctamente. Ahora registra una ENTRADA.', 'success')
            return redirect(url_for('inventory.lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            return render_template('agregar.html')
    
    return render_template('agregar.html')

# --- REGISTRAR MOVIMIENTO (KARDEX) ---
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

# --- VISTA DE KARDEX (HISTORIAL) ---
@inventory_bp.route('/kardex/<int:id>')
def ver_kardex(id):
    insumo = Insumo.query.get_or_404(id)
    movimientos = Movimiento.query.filter_by(insumo_id=id).order_by(Movimiento.fecha.desc()).all()
    return render_template('kardex.html', insumo=insumo, movimientos=movimientos)

# --- PDF DEL KARDEX INDIVIDUAL ---
@inventory_bp.route('/kardex/<int:id>/pdf')
def descargar_kardex_pdf(id):
    insumo = Insumo.query.get_or_404(id)
    movimientos = Movimiento.query.filter_by(insumo_id=id).order_by(Movimiento.fecha.desc()).all()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("COOPERATIVA MINERA QANTATY R.L.", styles['Title']))
    elements.append(Paragraph("HISTORIAL DE MOVIMIENTOS (KARDEX)", styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    # Datos del Item
    info_texto = f"""
    <b>CÓDIGO:</b> {insumo.codigo} <br/>
    <b>ITEM:</b> {insumo.nombre} <br/>
    <b>CATEGORÍA:</b> {insumo.categoria} <br/>
    <b>STOCK ACTUAL:</b> {insumo.cantidad_actual} {insumo.unidad}
    """
    elements.append(Paragraph(info_texto, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Tabla
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
    
    # Estilos Tabla
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
    ])
    
    # Colores condicionales para filas
    for i, mov in enumerate(movimientos):
        if mov.tipo == 'ENTRADA':
            ts.add('TEXTCOLOR', (1, i+1), (1, i+1), colors.green)
        else:
            ts.add('TEXTCOLOR', (1, i+1), (1, i+1), colors.red)

    table.setStyle(ts)
    elements.append(table)
    
    # Firma
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 40, styles['Normal']))
    elements.append(Paragraph("Firma Responsable", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Kardex_{insumo.codigo}.pdf'
    return response
