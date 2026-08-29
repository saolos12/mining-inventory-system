# Mining Inventory System

Sistema web integral para el control de inventario, gestión de insumos mineros y generación de reportes Kardex.

## 📋 Descripción

Aplicación desarrollada en **Python (Flask)** y **PostgreSQL** para optimizar la logística y el seguimiento de entradas, salidas y existencias de insumos en operaciones mineras.

### Características Principales:
- **Dashboard de Control:** Vista general de niveles de stock, alertas de reposición y métricas clave.
- **Gestión de Insumos:** Registro, categorización y actualización de insumos.
- **Kardex y Movimientos:** Registro detallado de entradas y salidas de almacén.
- **Reportes:** Generación de reportes y exportación en formato PDF con ReportLab.

## 🛠️ Tecnologías

- **Backend:** Python 3.x, Flask, Flask-SQLAlchemy, Gunicorn
- **Base de Datos:** PostgreSQL (psycopg2-binary)
- **Reportes:** ReportLab
- **Frontend:** Jinja2 Templates, HTML5, CSS3

## ⚙️ Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/saolos12/mining-inventory-system.git
   cd mining-inventory-system
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno (`.env`):**
   ```env
   DATABASE_URL=postgresql://usuario:password@localhost:5432/mining_inventory
   SECRET_KEY=tu_clave_secreta
   ```

5. **Iniciar la aplicación:**
   ```bash
   flask run
   ```
