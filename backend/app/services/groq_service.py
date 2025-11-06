from groq import Groq
from app.config import Config

# Inicializar el cliente una sola vez
groq_client = None

def init_groq():
    """Inicializa el cliente de Groq."""
    global groq_client
    if Config.GROQ_API_KEY:
        try:
            groq_client = Groq(api_key=Config.GROQ_API_KEY)
            print("✅ Groq API inicializada correctamente")
            print(f"📋 Modelo: {Config.GROQ_MODEL}")
            return True
        except Exception as e:
            print(f"❌ Error inicializando Groq: {e}")
    else:
        print("❌ GROQ_API_KEY no encontrada")
    return False

def get_groq_client():
    """Retorna el cliente de Groq."""
    return groq_client

def generate_response_with_groq(message, relevant_docs):
    """Genera respuesta usando Groq LLM (Tu función original)"""
    client = get_groq_client()
    if not client:
        print("❌ Groq client no inicializado")
        return "Lo siento, el sistema de IA no está disponible en este momento."
    
    print(f"🤖 Generando respuesta con Groq para: {message[:50]}...")
    
    try:
        context_parts = []
        for i, doc in enumerate(relevant_docs[:2], 1):
            excerpt = doc['content'][:2000]
            context_parts.append(f"[Documento {i}: {doc['title']}]\n{excerpt}\n")
        
        context = "\n---\n".join(context_parts)
        
        system_prompt = """Eres GovAI, un experto en contratación pública colombiana y el sistema SECOP...
... (Tu system prompt completo) ...
"""
        user_prompt = f"""Pregunta del usuario: {message}

Información de referencia:
{context}

Responde la pregunta de forma clara y profesional..."""

        print(f"📡 Llamando a Groq con modelo: {Config.GROQ_MODEL}")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=Config.GROQ_MODEL,
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

def generate_no_context_response(message):
    """Genera respuesta cuando no hay documentos relevantes."""
    client = get_groq_client()
    if not client:
        return "Tu pregunta no parece estar relacionada con contratación pública colombiana..."

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres GovAI, un asistente de contratación pública colombiana..."},
                {"role": "user", "content": message}
            ],
            model=Config.GROQ_MODEL,
            temperature=0.5,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error con Groq: {e}")
        return "Lo siento, hubo un error al procesar tu pregunta."