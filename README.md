# Mining Inventory System

Sistema web orientado a la gestión logística, control de inventario de insumos mineros y administración de kardex de almacén con cálculo automático de existencias y generación de reportes en PDF.

---

### Flujo de Control de Inventario y Kardex

```mermaid
flowchart TD
    subgraph Registro de Movimientos
        E[Entrada de Insumos / Compra / Recepción] --> M[Módulo de Movimientos]
        S[Salida de Insumos / Despacho a Operaciones] --> M
    end

    subgraph Procesamiento en Backend Flask
        M --> K[Actualización de Kardex de Insumo]
        K --> DB[(Base de Datos PostgreSQL)]
        K --> ST{Evaluación de Stock}
        ST -->|Stock <= Umbral Mínimo| AL[Alerta de Reabastecimiento Crítico]
        ST -->|Stock Óptimo| OK[Saldo Disponible Actualizado]
    end

    subgraph Visualización y Reportes
        DB --> DSH[Dashboard General de Inventario]
        DB --> REP[Generador de Reportes PDF con ReportLab]
    end
```

---

### Características Principales

| Módulo | Capacidad Operativa |
| :--- | :--- |
| **Control de Catálogo de Insumos** | Registro de materiales, herramientas, reactivos y repuestos con unidad de medida, categoría y umbral mínimo de seguridad. |
| **Kardex Detallado** | Bitácora cronológica e individual por insumo con trazabilidad de fechas, tipo de movimiento, cantidades y saldo resultante. |
| **Alertas de Reposición** | Panel de monitoreo con avisos inmediatos para insumos que han alcanzado niveles críticos de inventario. |
| **Generación de Reportes PDF** | Exportación de informes de existencias, valoraciones de inventario y resúmenes de movimientos utilizando ReportLab. |
| **Estructura Modular (Blueprints)** | Separación limpia de responsabilidades mediante rutas modulares (`inventory`, `reports`, `main`) y modelos declarativos de SQLAlchemy. |

---

### Stack Tecnológico

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Gunicorn.
- **Base de Datos:** PostgreSQL con `psycopg2-binary`.
- **Generador de Reportes:** ReportLab (creación programática de documentos PDF).
- **Frontend:** Plantillas Jinja2, HTML5 Semántico, CSS3 modular.

---

### Estructura del Código

```text
mining-inventory-system/
├── app.py              # Fábrica de la aplicación y registro de blueprints
├── config.py           # Configuración de entornos y cadenas de conexión a base de datos
├── models/             # Modelos de base de datos (Insumo, Movimiento, etc.)
│   └── insumo.py
├── routes/             # Controladores divididos por dominio
│   ├── inventory.py    # Altas, bajas y edición de insumos
│   ├── reports.py      # Generación de reportes PDF y exportaciones
│   └── main.py         # Dashboard y métricas generales
├── templates/          # Vistas renderizadas con Jinja2
│   ├── base.html
│   ├── dashboard.html
│   ├── inventario.html
│   ├── kardex.html
│   └── reportes.html
├── requirements.txt    # Dependencias de Python
└── Procfile            # Definición para ejecución con Gunicorn
```

---

### Instalación y Ejecución Local

Requisitos: Python 3.10+ y PostgreSQL.

```bash
# 1. Clonar el repositorio
git clone https://github.com/saolos12/mining-inventory-system.git
cd mining-inventory-system

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows: .\venv\Scripts\activate | Linux: source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (.env)
# DATABASE_URL=postgresql://usuario:password@localhost:5432/mining_inventory
# SECRET_KEY=clave_segura_de_produccion

# 5. Ejecutar la aplicación
python app.py
```

Acceder a la plataforma en `http://localhost:5000`.

---

### Licencia

Este proyecto está bajo la licencia MIT.