from app.services.document_service import get_documents

# Tu función original, ahora en su propio módulo
def find_relevant_documents(query, top_k=3):
    """Encuentra documentos relevantes usando búsqueda mejorada por palabras clave"""
    documents = get_documents()
    
    if not documents:
        print("⚠️ No hay documentos cargados")
        return []
    
    query_lower = query.lower()
    
    keywords_map = {
        'contrato': ['contrato', 'contratos', 'contratación', 'contratar'],
        'ley': ['ley', 'leyes', 'legal', 'legislación'],
        'decreto': ['decreto', 'decretos'],
        'suministro': ['suministro', 'suministros']
    }
    
    doc_scores = []
    for idx, doc in enumerate(documents):
        content_lower = doc['content'].lower()
        title_lower = doc['title'].lower()
        score = 0
        
        for word in query_lower.split():
            if len(word) > 3:
                if word in title_lower:
                    score += 2.0
                if word in content_lower:
                    score += 0.5
        
        for category, variants in keywords_map.items():
            if any(kw in query_lower for kw in variants):
                if any(kw in title_lower for kw in variants):
                    score += 1.5
                if any(kw in content_lower for kw in variants):
                    score += 0.3
        
        doc_scores.append((idx, score))
    
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    
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