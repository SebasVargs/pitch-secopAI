# 🤖 SECOP Chatbot

Sistema inteligente de consultas sobre contratación pública colombiana usando BERT en español.

## 📋 Descripción

Este chatbot utiliza modelos de lenguaje natural (BERT) para responder preguntas sobre normativas y leyes de contratación pública del SECOP (Sistema Electrónico de Contratación Pública).

## 🏗️ Estructura del Proyecto

```
pitchSecop/
├── backend/                    # API Flask
│   ├── main.py                # Servidor backend
│   ├── requirements.txt       # Dependencias backend
│   ├── data/
│   │   └── leyes/            # Archivos .txt con leyes y normativas
│   └── models/               # Modelos entrenados (generado)
├── frontend/                  # Interfaz Streamlit
│   ├── main.py               # Aplicación frontend
│   └── requirements.txt      # Dependencias frontend
├── start_backend.sh          # Script para iniciar backend
├── start_frontend.sh         # Script para iniciar frontend
└── README.md                 # Este archivo
```

## 🚀 Instalación y Uso

### Requisitos Previos

- Python 3.8 o superior
- pip
- 4GB+ de RAM (para cargar BERT)

### Paso 1: Preparar los Datos

Coloca tus archivos de leyes y normativas en formato `.txt` en:
```
backend/data/leyes/
```

Actualmente incluye:
- Decreto 1082 de 2015
- Ley 1150 de 2007
- Ley 80 de 1993
- Procedimientos de registro de proveedores
- Pliegos de condiciones

### Paso 2: Iniciar el Backend

Abre una terminal y ejecuta:

```bash
chmod +x start_backend.sh
./start_backend.sh
```

El backend estará disponible en: `http://localhost:5000`

### Paso 3: Iniciar el Frontend

Abre **otra terminal** y ejecuta:

```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

El frontend se abrirá automáticamente en tu navegador en: `http://localhost:8501`

## 📖 Uso del Chatbot

1. **Primera vez**: Haz clic en "🚀 Entrenar Modelo Ahora" en el panel lateral
   - Este proceso toma 5-10 minutos
   - Descarga el modelo BERT en español
   - Genera embeddings de todos los documentos

2. **Hacer preguntas**: Una vez entrenado, escribe tus preguntas en el chat
   - Ejemplo: "¿Qué dice la Ley 80 de 1993 sobre contratos públicos?"
   - Ejemplo: "¿Cuáles son los requisitos para registro de proveedores?"

3. **Ver documentos**: El panel lateral muestra todos los documentos cargados

## 🔧 Características

- ✅ Búsqueda semántica usando BERT español
- ✅ Respuestas basadas en documentos reales
- ✅ Indicador de confianza en las respuestas
- ✅ Historial de conversación
- ✅ Estadísticas de uso
- ✅ Interfaz intuitiva con Streamlit

## 🛠️ Tecnologías

### Backend
- **Flask**: Framework web
- **Transformers**: Modelos BERT
- **PyTorch**: Deep learning
- **scikit-learn**: TF-IDF y similitud coseno
- **Flask-CORS**: Comunicación frontend-backend

### Frontend
- **Streamlit**: Interfaz web interactiva
- **Requests**: Comunicación con API
- **Pandas**: Visualización de datos

## 📝 API Endpoints

- `GET /` - Health check
- `POST /api/train` - Entrenar el modelo
- `POST /api/chat` - Enviar mensaje al chatbot
- `GET /api/documents` - Obtener lista de documentos

## ⚠️ Solución de Problemas

### El frontend no conecta con el backend
- Verifica que el backend esté corriendo en `http://localhost:5000`
- Revisa la consola del backend para ver errores
- Asegúrate de que no haya otro proceso usando el puerto 5000

### No encuentra los archivos de datos
- Verifica que los archivos .txt estén en `backend/data/leyes/`
- Los archivos deben tener codificación UTF-8
- Revisa los permisos de lectura de los archivos

### Error al entrenar el modelo
- Asegúrate de tener suficiente RAM (4GB+)
- Verifica tu conexión a internet (descarga BERT)
- Revisa que todos los paquetes estén instalados correctamente

### Reinstalar dependencias
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📊 Rendimiento

- **Tiempo de entrenamiento**: 5-10 minutos (primera vez)
- **Tiempo de respuesta**: 1-3 segundos
- **Precisión**: Depende de la calidad de los documentos

## 🤝 Contribuir

Para agregar más documentos:
1. Coloca archivos .txt en `backend/data/leyes/`
2. Re-entrena el modelo desde la interfaz
3. El chatbot aprenderá del nuevo contenido

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👥 Autor

Desarrollado para facilitar el acceso a información sobre contratación pública en Colombia.

---

**Nota**: Este chatbot es una herramienta de consulta. Para decisiones legales importantes, siempre consulta con un profesional del derecho.
