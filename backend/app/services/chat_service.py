from app.services import document_service, search_service, groq_service

def generate_response(message):
    """Genera respuesta al mensaje usando Groq"""
    if not document_service.get_documents():
        return {
            "response": "No hay documentos cargados en el sistema.",
            "confidence": 0.0
        }
    
    # 1. Buscar documentos
    relevant_docs = search_service.find_relevant_documents(message, top_k=3)
    
    if not relevant_docs:
        print("⚠️ No se encontraron documentos relevantes, respondiendo sin contexto")
        response_text = groq_service.generate_no_context_response(message)
        return {
            "response": response_text,
            "confidence": 0.3 # O 0.0 si prefieres
        }
    
    # 2. Generar respuesta con Groq usando contexto
    response_text = groq_service.generate_response_with_groq(message, relevant_docs)
    
    confidence = relevant_docs[0]['similarity']
    
    return {
        "response": response_text,
        "confidence": float(confidence)
    }

# Tu función de sugerencias (puedes dejarla aquí o moverla)
def generate_suggestions(original_question, relevant_docs):
    """Genera sugerencias de preguntas relacionadas"""
    # ... (Tu lógica de generate_suggestions) ...
    suggestions = [
        "¿Cuáles son las modalidades de selección?",
        "¿Qué es la licitación pública?"
    ]
    return suggestions[:2]