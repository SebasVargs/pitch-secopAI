from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob
from datetime import datetime
import re
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
# Configurar CORS para permitir conexiones desde el frontend
CORS(app, resources={r"/*": {"origins": "*"}})

# ============================================
# CONFIGURACIÓN
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "leyes", "*.txt")

# Variables globales
documents = []

# Inicializar cliente Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Modelo actualizado
groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq API inicializada correctamente")
        print(f"📋 Modelo: {GROQ_MODEL}")
    except Exception as e:
        print(f"❌ Error inicializando Groq: {e}")
        groq_client = None
else:
    print("❌ GROQ_API_KEY no encontrada en .env")

# ============================================
# FUNCIONES DE CARGA DE DOCUMENTOS
# ============================================

def load_documents_from_files():
    """Carga todos los documentos .txt sin preprocesamiento"""
    global documents
    
    documents = []
    print(f"🔍 Buscando archivos en: {DATA_PATH}")
    file_paths = glob.glob(DATA_PATH)
    
    print(f"📚 Encontrados {len(file_paths)} archivos")
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                documents.append({
                    'title': os.path.basename(file_path).replace('.txt', '').replace('_', ' '),
                    'content': content,
                    'file_name': os.path.basename(file_path)
                })
                print(f"✅ Cargado: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error cargando {file_path}: {e}")
    
    print(f"✅ Total documentos cargados: {len(documents)}")
    return len(documents)

# ============================================
# BÚSQUEDA DE DOCUMENTOS RELEVANTES
# ============================================

def find_relevant_documents(query, top_k=3):
    """Encuentra documentos relevantes usando búsqueda mejorada por palabras clave"""
    global documents
    
    if not documents:
        print("⚠️ No hay documentos cargados")
        return []
    
    query_lower = query.lower()
    
    # Palabras clave importantes para contratación pública
    keywords_map = {
        'contrato': ['contrato', 'contratos', 'contratación', 'contratar'],
        'ley': ['ley', 'leyes', 'legal', 'legislación'],
        'decreto': ['decreto', 'decretos'],
        'pliego': ['pliego', 'pliegos', 'condiciones'],
        'licitación': ['licitación', 'licitaciones', 'licitar'],
        'proveedor': ['proveedor', 'proveedores', 'contratista'],
        'secop': ['secop', 'sistema', 'electrónico'],
        'obra': ['obra', 'obras', 'construcción'],
        'consultoría': ['consultoría', 'consultorías', 'consultor'],
        'suministro': ['suministro', 'suministros']
    }
    
    # Calcular relevancia por documento
    doc_scores = []
    for idx, doc in enumerate(documents):
        content_lower = doc['content'].lower()
        title_lower = doc['title'].lower()
        score = 0
        
        # Buscar coincidencias exactas en el título (muy importante)
        for word in query_lower.split():
            if len(word) > 3:  # Ignorar palabras muy cortas
                if word in title_lower:
                    score += 2.0
                if word in content_lower:
                    score += 0.5
        
        # Buscar por categorías de palabras clave
        for category, variants in keywords_map.items():
            if any(kw in query_lower for kw in variants):
                if any(kw in title_lower for kw in variants):
                    score += 1.5
                if any(kw in content_lower for kw in variants):
                    score += 0.3
        
        doc_scores.append((idx, score))
    
    # Ordenar por score
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Tomar top K con score > 0
    relevant_docs = []
    for idx, score in doc_scores[:top_k]:
        if score > 0:
            relevant_docs.append({
                'title': documents[idx]['title'],
                'content': documents[idx]['content'],
                'file_name': documents[idx]['file_name'],
                'similarity': float(score)
            })
            print(f"📄 Documento relevante: {documents[idx]['title']} (score: {score:.2f})")
    
    return relevant_docs

def generate_response_with_groq(message, relevant_docs):
    """Genera respuesta usando Groq LLM"""
    if not groq_client:
        print("❌ Groq client no inicializado")
        return "Lo siento, el sistema de IA no está disponible en este momento."
    
    print(f"🤖 Generando respuesta con Groq para: {message[:50]}...")
    
    try:
        # Preparar contexto de los documentos relevantes
        context_parts = []
        for i, doc in enumerate(relevant_docs[:2], 1):  # Solo top 2 documentos
            # Tomar las primeras 2000 caracteres del documento
            excerpt = doc['content'][:2000]
            context_parts.append(f"[Documento {i}: {doc['title']}]\n{excerpt}\n")
        
        context = "\n---\n".join(context_parts)
        
        # Prompt optimizado para respuestas coherentes
        system_prompt = """Eres GovAI, un experto en contratación pública colombiana y el sistema SECOP.

TU TRABAJO:
- Responder preguntas sobre leyes, decretos y procedimientos de contratación pública
- Explicar conceptos de forma clara y profesional
- Usar la información de los documentos proporcionados

REGLAS ESTRICTAS:
1. NUNCA menciones "según el documento" o nombres de archivos
2. NUNCA copies texto literal - SIEMPRE parafrasea y explica
3. Responde de forma natural como un experto humano
4. Máximo 250 palabras
5. Usa párrafos cortos y viñetas cuando sea apropiado
6. Si mencionas una ley, di su nombre completo (ej: "Ley 80 de 1993")

FORMATO:
- Comienza con una respuesta directa
- Luego explica los detalles
- Usa viñetas (-) para listar puntos clave"""

        user_prompt = f"""Pregunta del usuario: {message}

Información de referencia:
{context}

Responde la pregunta de forma clara y profesional. Explica el tema basándote en la información proporcionada, pero con tus propias palabras."""

        # Llamar a Groq
        print(f"📡 Llamando a Groq con modelo: {GROQ_MODEL}")
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1000,
            top_p=0.9
        )
        
        response_text = chat_completion.choices[0].message.content
        print(f"✅ Respuesta generada por Groq: {response_text[:100]}...")
        
        return response_text
        
    except Exception as e:
        print(f"❌ Error con Groq: {type(e).__name__}: {str(e)}")
        return f"Lo siento, hubo un error al procesar tu pregunta: {str(e)}"

# ============================================
# GENERACIÓN DE RESPUESTAS
# ============================================

def generate_response(message):
    """Genera respuesta al mensaje usando Groq"""
    if not documents:
        return {
            "response": "No hay documentos cargados en el sistema.",
            "confidence": 0.0
        }
    
    # Buscar documentos relevantes
    relevant_docs = find_relevant_documents(message, top_k=3)
    
    if not relevant_docs:
        # Si no hay documentos relevantes, usar Groq sin contexto
        print("⚠️ No se encontraron documentos relevantes, respondiendo sin contexto")
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres GovAI, un asistente de contratación pública colombiana. Si la pregunta no está relacionada con contratación pública, responde brevemente que tu especialidad es contratación pública y ofrece ayuda en ese tema."},
                        {"role": "user", "content": message}
                    ],
                    model=GROQ_MODEL,
                    temperature=0.5,
                    max_tokens=200
                )
                return {
                    "response": response.choices[0].message.content,
                    "confidence": 0.3
                }
            except Exception as e:
                print(f"❌ Error con Groq: {e}")
        
        return {
            "response": "Tu pregunta no parece estar relacionada con contratación pública colombiana. Mi especialidad es ayudarte con temas del SECOP, leyes, decretos y procedimientos de contratación estatal. ¿En qué puedo ayudarte sobre estos temas?",
            "confidence": 0.0
        }
    
    # Generar respuesta con Groq usando contexto
    response_text = generate_response_with_groq(message, relevant_docs)
    
    confidence = relevant_docs[0]['similarity']
    
    return {
        "response": response_text,
        "confidence": float(confidence)
    }

def generate_suggestions(original_question, relevant_docs):
    """Genera sugerencias de preguntas relacionadas"""
    suggestions = []
    
    # Palabras clave de la pregunta original
    question_lower = original_question.lower()
    
    # Sugerencias basadas en el contexto
    if 'ley' in question_lower or 'decreto' in question_lower:
        if '80' in question_lower:
            suggestions = [
                "¿Qué dice la Ley 1150 de 2007?",
                "¿Cuáles son las modalidades de selección?"
            ]
        elif '1150' in question_lower:
            suggestions = [
                "¿Qué es la licitación pública?",
                "¿Cuándo se usa la selección abreviada?"
            ]
        elif '1082' in question_lower:
            suggestions = [
                "¿Qué son los pliegos de condiciones?",
                "¿Cómo se registra un proveedor?"
            ]
        else:
            suggestions = [
                "¿Cuáles son las principales leyes de contratación?",
                "¿Qué normativas regulan el SECOP?"
            ]
    elif 'pliego' in question_lower:
        suggestions = [
            "¿Qué debe contener un pliego de condiciones?",
            "¿Cuál es la diferencia entre obra y consultoría?"
        ]
    elif 'proveedor' in question_lower or 'registro' in question_lower:
        suggestions = [
            "¿Qué requisitos necesito para registrarme?",
            "¿Cómo actualizo mi información de proveedor?"
        ]
    elif 'contrato' in question_lower or 'contratación' in question_lower:
        suggestions = [
            "¿Qué tipos de contratos existen?",
            "¿Cuál es el proceso de contratación directa?"
        ]
    elif 'secop' in question_lower:
        suggestions = [
            "¿Cómo funciona el SECOP II?",
            "¿Qué diferencia hay entre SECOP I y SECOP II?"
        ]
    else:
        # Sugerencias genéricas basadas en los documentos encontrados
        if relevant_docs:
            doc_title = relevant_docs[0]['title']
            if 'Ley_80' in doc_title:
                suggestions = [
                    "¿Qué principios rigen la contratación pública?",
                    "¿Cuáles son las inhabilidades para contratar?"
                ]
            elif 'Ley_1150' in doc_title:
                suggestions = [
                    "¿Qué es el plan anual de adquisiciones?",
                    "¿Cómo se hace una licitación pública?"
                ]
            elif 'Decreto_1082' in doc_title:
                suggestions = [
                    "¿Qué documentos se requieren para contratar?",
                    "¿Cuáles son los plazos de contratación?"
                ]
            elif 'Pliego' in doc_title:
                suggestions = [
                    "¿Qué es un estudio previo?",
                    "¿Cómo se evalúan las propuestas?"
                ]
            else:
                suggestions = [
                    "¿Cuáles son las etapas de la contratación?",
                    "¿Qué es la supervisión de contratos?"
                ]
        else:
            suggestions = [
                "¿Qué normativas regulan la contratación pública?",
                "¿Cómo puedo participar en una licitación?"
            ]
    
    return suggestions[:2]  # Solo 2 sugerencias

# ============================================
# ENDPOINTS
# ============================================

@app.route('/')
def home():
    """Health check"""
    return jsonify({
        "status": "ok",
        "model_trained": len(documents) > 0,  # Siempre True si hay documentos
        "total_documents": len(documents),
        "groq_enabled": groq_client is not None
    })

@app.route('/api/train', methods=['POST'])
def api_train():
    """Endpoint obsoleto - ya no se necesita entrenar"""
    return jsonify({
        "success": True,
        "message": "El sistema usa Groq y no requiere entrenamiento",
        "total_documents": len(documents)
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Endpoint para chatear"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Mensaje vacío"}), 400
    
    result = generate_response(message)
    
    return jsonify({
        "message": message,
        "response": result['response'],
        "confidence": result['confidence'],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/documents', methods=['GET'])
def api_documents():
    """Obtiene lista de documentos"""
    docs_info = []
    for doc in documents:
        docs_info.append({
            "title": doc['title'],
            "preview": doc['original_content'][:200] + "..."
        })
    return jsonify(docs_info)

# ============================================
# INICIALIZACIÓN
# ============================================

# Cargar documentos al iniciar (sin necesidad de modelo BERT)
print("🚀 Iniciando aplicación...")
print("📚 Cargando documentos...")
num_docs = load_documents_from_files()
if num_docs > 0:
    print(f"✅ {num_docs} documentos cargados correctamente")
    print("✅ Sistema listo (usando Groq + búsqueda por palabras clave)")
else:
    print("⚠️  No se encontraron documentos en data/leyes/")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🤖 SECOP Chatbot API")
    print("="*50)
    print(f"📚 Documentos cargados: {len(documents)}")
    print(f"🌐 Servidor: http://localhost:5001")
    print(f"📖 Docs: http://localhost:5001/api/documents")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5001, host='127.0.0.1')