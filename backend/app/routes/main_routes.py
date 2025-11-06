from flask import Blueprint, jsonify
from app.services import document_service
from app.services.groq_service import get_groq_client

# Crear un "Blueprint"
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    """Health check"""
    docs = document_service.get_documents()
    return jsonify({
        "status": "ok",
        "model_trained": len(docs) > 0,
        "total_documents": len(docs),
        "groq_enabled": get_groq_client() is not None
    })

@main_bp.route('/api/documents', methods=['GET'])
def api_documents():
    """Obtiene lista de documentos"""
    docs_info = document_service.get_document_info()
    return jsonify(docs_info)