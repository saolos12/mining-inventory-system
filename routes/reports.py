from flask import Blueprint, render_template, request, make_response
from models.insumo import Insumo, db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reportes')
def panel_reportes():
    return render_template('reportes.html')

@reports_bp.route('/descargar_pdf', methods=['POST'])
def generar_pdf():
    categoria = request.form.get('categoria')
    ubicacion = request.form.get('ubicacion')
    
    # Consulta base
    query = Insumo.query
    titulo_reporte = "Reporte General de Inventario"
    
    if categoria and categoria != "Todas":
        query = query.filter_by(categoria=categoria)
        titulo_reporte += f" - Categoria: {categoria}"
    
    if ubicacion and ubicacion != "Todas":
        query = query.filter_by(ubicacion=ubicacion)
        titulo_reporte += f" - Ubicación: {ubicacion}"
        
    insumos = query.all()
    
    # --- CREACIÓN DEL PDF ---
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter
    
    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, h - 50, "MINERA SAN JOSÉ (O el nombre que sea)")
    p.setFont("Helvetica", 12)
    p.drawString(50, h - 70, titulo_reporte)
    
    # Cabecera de Tabla
    y = h - 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "ID")
    p.drawString(80, y, "NOMBRE")
    p.drawString(250, y, "CATEGORIA")
    p.drawString(350, y, "CANT.")
    p.drawString(400, y, "UBICACION")
    
    p.line(40, y-5, 550, y-5)
    y -= 20
    
    # Datos
    p.setFont("Helvetica", 9)
    total_items = 0
    
    for item in insumos:
        if y < 50: # Salto de página simple
            p.showPage()
            y = h - 50
            
        p.drawString(50, y, str(item.id))
        p.drawString(80, y, item.nombre[:30]) # Cortar nombre largo
        p.drawString(250, y, item.categoria)
        p.drawString(350, y, f"{item.cantidad} {item.unidad}")
        p.drawString(400, y, str(item.ubicacion))
        y -= 15
        total_items += item.cantidad

    p.line(40, y+10, 550, y+10)
    p.drawString(50, y-20, f"Total Items Reportados: {total_items}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=reporte.pdf'
    
    return response