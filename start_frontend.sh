#!/bin/bash

# Script para iniciar el frontend del chatbot SECOP

echo "🎨 Iniciando Frontend SECOP Chatbot..."
echo "======================================"

# Ir al directorio del frontend
cd "$(dirname "$0")/frontend"

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Verificar que el backend esté corriendo
echo ""
echo "⚠️  IMPORTANTE: Asegúrate de que el backend esté corriendo en http://localhost:5001"
echo "   Si no lo has iniciado, abre otra terminal y ejecuta: ./start_backend.sh"
echo ""

# Iniciar Streamlit
echo "✅ Frontend listo!"
echo "🌐 Abriendo interfaz en el navegador..."
echo "======================================"
echo ""

streamlit run main.py
