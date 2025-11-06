#!/bin/bash

# Script para reiniciar el proyecto limpiamente

echo "🔄 Reiniciando SECOP Chatbot..."
echo "======================================"

# Detener procesos existentes
echo "🛑 Deteniendo procesos anteriores..."

# Detener Streamlit (puerto 8501)
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   Deteniendo frontend (puerto 8501)..."
    kill -9 $(lsof -ti:8501) 2>/dev/null
    sleep 1
fi

# Detener Flask en puerto 5001
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   Deteniendo backend (puerto 5001)..."
    kill -9 $(lsof -ti:5001) 2>/dev/null
    sleep 1
fi

# Detener cualquier proceso Python relacionado con el proyecto
pkill -f "python.*main.py" 2>/dev/null
sleep 1

echo ""
echo "✅ Procesos detenidos"
echo ""
echo "📝 Ahora puedes iniciar el proyecto de nuevo:"
echo "   Terminal 1: ./start_backend.sh"
echo "   Terminal 2: ./start_frontend.sh"
echo ""
echo "======================================"
