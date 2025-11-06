import os
import glob
from app.config import Config

# Variable "privada" del módulo para cachear los documentos
_documents = []

def load_documents_from_files():
    """Carga todos los documentos .txt"""
    global _documents
    
    if _documents:
        print("ℹ️ Documentos ya estaban cargados.")
        return len(_documents)

    _documents = []
    print(f"🔍 Buscando archivos en: {Config.DATA_PATH}")
    file_paths = glob.glob(Config.DATA_PATH)
    
    print(f"📚 Encontrados {len(file_paths)} archivos")
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                _documents.append({
                    'title': os.path.basename(file_path).replace('.txt', '').replace('_', ' '),
                    'content': content,
                    'file_name': os.path.basename(file_path)
                })
                print(f"✅ Cargado: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error cargando {file_path}: {e}")
    
    print(f"✅ Total documentos cargados: {len(_documents)}")
    return len(_documents)

def get_documents():
    """Retorna la lista de documentos cargados."""
    if not _documents:
        load_documents_from_files()
    return _documents

def get_document_info():
    """Obtiene lista de documentos para el endpoint /api/documents"""
    docs_info = []
    for doc in get_documents():
        docs_info.append({
            "title": doc['title'],
            "preview": doc['content'][:200] + "..." # Corregido 'original_content'
        })
    return docs_info