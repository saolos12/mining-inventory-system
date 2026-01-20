from flask import Flask
from config import Config
from models.insumo import db

# Importación de Rutas (Blueprints)
# Nota: Crearemos estos archivos en el siguiente paso
from routes.main import main_bp
from routes.inventory import inventory_bp
from routes.reports import reports_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Registro de Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    
    # Crear tablas automáticamente al iniciar (útil para Render)
    with app.app_context():
        db.create_all()
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)