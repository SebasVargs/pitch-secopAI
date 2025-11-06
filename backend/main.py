from app import create_app
import os

# Cargar la configuración (dev, prod, etc.) si la tienes, o dejar por defecto
app = create_app()

if __name__ == '__main__':
    # El puerto y host se definirán en la configuración
    port = os.environ.get('FLASK_RUN_PORT', 5001)
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("\n" + "="*50)
    print("🤖 SECOP Chatbot API")
    print("="*50)
    print(f"🌐 Servidor: http://127.0.0.1:{port}")
    print(f"🚀 Entorno: {'DEBUG' if debug else 'PRODUCTION'}")
    print("="*50 + "\n")
    
    app.run(debug=debug, port=int(port), host='127.0.0.1')