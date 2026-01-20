from flask import Blueprint, render_template, request, make_response
from models.insumo import Insumo, db
# Importamos el motor avanzado de ReportLab (Platypus)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import io
import os

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
    
    if ubicacion and ubicacion != "Todas": # Filtro opcional si lo usas
        query = query.filter(Insumo.ubicacion.ilike(f'%{ubicacion}%'))
        subtitulo_texto += f" | Lugar: {ubicacion}"
        
    insumos = query.all()
    
    # 2. Configuración del PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- ENCABEZADO PERSONALIZADO ---
    
    # Estilo del Título Principal
    estilo_titulo = ParagraphStyle(
        name='TituloCooperativa',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    # Estilo de Subtítulo/Fecha
    estilo_sub = ParagraphStyle(
        name='Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    # Añadir Logo (Opcional - Si tienes una imagen 'logo.png' en static/img/)
    # ruta_logo = os.path.join('static', 'img', 'logo.png')
    # if os.path.exists(ruta_logo):
    #     img = Image(ruta_logo, width=50, height=50)
    #     img.hAlign = 'CENTER'
    #     elements.append(img)
    
    # Títulos
    elements.append(Paragraph("COOPERATIVA MINERA QANTATY R.L.", estilo_titulo))
    elements.append(Paragraph(f"NIT: 1234567014 (Ejemplo) | La Paz - Bolivia", estilo_sub))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"{subtitulo_texto}", styles['Heading3']))
    
    fecha_impresion = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de generación: {fecha_impresion}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # --- TABLA DE DATOS ---
    
    # Encabezados de la tabla
    data = [['CÓDIGO', 'ITEM / DESCRIPCIÓN', 'CATEGORÍA', 'UBICACIÓN', 'STOCK', 'ESTADO']]
    
    # Llenamos la tabla con los datos de la DB
    total_items = 0
    for item in insumos:
        # Formateamos el stock para que se vea bien (ej: 50 Kilos)
        stock_fmt = f"{item.cantidad_actual} {item.unidad}"
        
        # Recortamos textos muy largos para que no rompan la tabla
        nombre_corto = item.nombre[:25] + '...' if len(item.nombre) > 25 else item.nombre
        
        row = [
            item.codigo,
            nombre_corto,
            item.categoria,
            item.ubicacion or "N/A",
            stock_fmt,
            # Estado (puedes ajustar lógica si tienes campo estado)
            "OK" if item.cantidad_actual > 5 else "BAJO" 
        ]
        data.append(row)
        total_items += item.cantidad_actual

    # Creación del objeto Tabla
    # Definimos el ancho de columnas (ajustar según necesidad)
    table = Table(data, colWidths=[60, 180, 90, 90, 70, 50])
    
    # ESTILOS DE LA TABLA (Aquí está la magia visual)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), # Cabecera azul oscuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Texto blanco en cabecera
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # Todo centrado
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),   # Nombres alineados a la izquierda
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # Fuente negrita en cabecera
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), # Espacio en cabecera
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), # Fondo blanco por defecto
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # Líneas grises finas
    ])
    
    # Filas alternas (Efecto cebra para leer mejor)
    for i, row in enumerate(data[1:]):
        if i % 2 == 0:
            bg_color = colors.aliceblue # Un azul muy clarito
        else:
            bg_color = colors.white
        style.add('BACKGROUND', (0, i+1), (-1, i+1), bg_color)
        
        # Si el stock es bajo (marcado como BAJO en la columna 5), poner texto rojo
        if row[5] == "BAJO":
             style.add('TEXTCOLOR', (4, i+1), (5, i+1), colors.red)

    table.setStyle(style)
    elements.append(table)
    
    # --- PIE DE PÁGINA (Resumen) ---
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total de items listados: {len(insumos)} registros.", styles['Normal']))
    
    # Espacio para firmas (típico en cooperativas)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 40, styles['Normal']))
    elements.append(Paragraph("V°B° Responsable de Almacén", styles['Normal']))

    # 3. Construir PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Reporte_Qantaty_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response
