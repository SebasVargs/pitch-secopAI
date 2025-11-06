from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.services import document_service, groq_service

def create_app(config_class=Config):
    """
    Application Factory: Crea y configura la instancia de la aplicación Flask.
    """
    
    print("🚀 Iniciando aplicación...")
    app = Flask(__name__)
    
    # 1. Cargar configuración
    app.config.from_object(config_class)
    
    # 2. Configurar CORS
    CORS(app, resources={r"/*": {"origins": config_class.CORS_ORIGINS}})
    print(f" CORS habilitado para: {config_class.CORS_ORIGINS}")

    # 3. Inicializar servicios (los que lo necesiten)
    print("📚 Cargando documentos...")
    num_docs = document_service.load_documents_from_files()
    if num_docs > 0:
        print(f"✅ {num_docs} documentos cargados correctamente")
    else:
        print("⚠️  No se encontraron documentos en data/leyes/")
    
    print("🤖 Inicializando Groq...")
    groq_service.init_groq()
    
    # 4. Registrar Blueprints (Rutas)
    from app.routes.main_routes import main_bp
    from app.routes.chat_routes import chat_bp
    
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(chat_bp, url_prefix='/') # Puedes prefijar con /api
    
    print("✅ Aplicación lista.")
    
    return app