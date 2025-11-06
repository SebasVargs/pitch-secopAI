#!/bin/bash

# Script para iniciar el backend del chatbot SECOP

echo "🚀 Iniciando Backend SECOP Chatbot..."
echo "======================================"

# Ir al directorio del backend
cd "$(dirname "$0")/backend"

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

# Verificar que existan los archivos de datos
if [ ! -d "data/leyes" ] || [ -z "$(ls -A data/leyes/*.txt 2>/dev/null)" ]; then
    echo "⚠️  ADVERTENCIA: No se encontraron archivos en data/leyes/"
    echo "   Por favor, agrega archivos .txt en backend/data/leyes/"
fi

# Iniciar el servidor
echo ""
echo "✅ Backend listo!"
echo "🌐 Servidor corriendo en: http://localhost:5001"
echo "⚠️  NOTA: Usando puerto 5001 (puerto 5000 usado por macOS AirPlay)"
echo "======================================"
echo ""

python main.py
