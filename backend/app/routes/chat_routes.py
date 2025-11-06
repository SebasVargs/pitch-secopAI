from flask import Blueprint, request, jsonify
from app.services import chat_service
from datetime import datetime

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    """Endpoint para chatear"""
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Mensaje vacío"}), 400
    
    result = chat_service.generate_response(message)
    
    return jsonify({
        "message": message,
        "response": result['response'],
        "confidence": result['confidence'],
        "timestamp": datetime.now().isoformat()
    })

@chat_bp.route('/api/train', methods=['POST'])
def api_train():
    """Endpoint obsoleto"""
    return jsonify({
        "success": True,
        "message": "El sistema usa Groq y no requiere entrenamiento",
        "total_documents": len(chat_service.document_service.get_documents())
    })