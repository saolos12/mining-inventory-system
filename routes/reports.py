from flask import Blueprint, render_template, request, make_response
from models.insumo import Insumo, db
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reportes')
def panel_reportes():
    return render_template('reportes.html')

@reports_bp.route('/descargar_pdf', methods=['POST'])
def generar_pdf():
    # 1. Filtros
    categoria = request.form.get('categoria')
    ubicacion = request.form.get('ubicacion')
    
    query = Insumo.query
    subtitulo_texto = "Reporte General de Existencias"
    
    if categoria and categoria != "Todas":
        query = query.filter_by(categoria=categoria)
        subtitulo_texto += f" | Categoría: {categoria}"
    
    if ubicacion and ubicacion != "Todas":
        query = query.filter(Insumo.ubicacion.ilike(f'%{ubicacion}%'))
        subtitulo_texto += f" | Lugar: {ubicacion}"
        
    insumos = query.all()
    
    # 2. Configuración del PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- ENCABEZADO ---
    estilo_titulo = ParagraphStyle(
        name='TituloCooperativa',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    elements.append(Paragraph("COOPERATIVA MINERA QANTATY R.L.", estilo_titulo))
    elements.append(Paragraph(f"{subtitulo_texto}", styles['Heading3']))
    
    fecha_impresion = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de corte: {fecha_impresion}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # --- TABLA DE DATOS ---
    
    # Encabezados Actualizados
    data = [['CÓDIGO', 'ITEM', 'CATEGORÍA', 'UBICACIÓN', 'STOCK', 'ESTADO']]
    
    for item in insumos:
        # Stock con unidad
        stock_fmt = f"{item.cantidad_actual} {item.unidad}"
        
        # Nombre corto si es muy largo
        nombre_corto = item.nombre[:25] + '...' if len(item.nombre) > 25 else item.nombre
        
        row = [
            item.codigo,
            nombre_corto,
            item.categoria,
            item.ubicacion or "N/A",
            stock_fmt,
            item.estado # <--- AQUI YA USAMOS EL ESTADO REAL
        ]
        data.append(row)

    # Anchos de columna ajustados
    table = Table(data, colWidths=[60, 150, 90, 90, 70, 80])
    
    # ESTILOS BASE
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    
    # --- LÓGICA DE COLORES POR ESTADO ---
    # Recorremos los datos (saltando la cabecera que es el índice 0)
    for i, row in enumerate(data[1:]):
        estado_actual = row[5] # El estado está en la columna 5 (índice 5)
        fila_indice = i + 1 # Ajustamos índice porque 'data' tiene cabecera
        
        # Color de fondo alterno (Cebra)
        if i % 2 == 0:
            style.add('BACKGROUND', (0, fila_indice), (-1, fila_indice), colors.aliceblue)
        
        # Colores de Texto según Estado
        if estado_actual == 'Dañado':
            style.add('TEXTCOLOR', (5, fila_indice), (5, fila_indice), colors.red)
            style.add('FONTNAME', (5, fila_indice), (5, fila_indice), 'Helvetica-Bold')
            
        elif estado_actual == 'En Mantenimiento':
            style.add('TEXTCOLOR', (5, fila_indice), (5, fila_indice), colors.orange)
            
        elif estado_actual == 'Operativo':
            style.add('TEXTCOLOR', (5, fila_indice), (5, fila_indice), colors.green)
            
        elif estado_actual == 'Regular':
            # Un color mostaza/oscuro para regular
            style.add('TEXTCOLOR', (5, fila_indice), (5, fila_indice), colors.darkgoldenrod)

    table.setStyle(style)
    elements.append(table)
    
    # --- PIE ---
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total registros: {len(insumos)}", styles['Normal']))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 40, styles['Normal']))
    elements.append(Paragraph("V°B° Responsable de Almacén", styles['Normal']))

    doc.build(elements)
    
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Reporte_Qantaty.pdf'
    
    return response
