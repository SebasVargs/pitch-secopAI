import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
# Asume que .env está en la carpeta 'backend/'
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    """Configuración de la aplicación."""
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, "data", "leyes", "*.txt")
    
    # Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    # Flask
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*') # Acepta '*' o 'http://localhost:3000'
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5001))