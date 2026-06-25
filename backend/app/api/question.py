"""智能问答API"""
from flask import Blueprint, request, jsonify
from app.services.qa_service import QuestionAnsweringService

question_bp = Blueprint('question', __name__)


@question_bp.route('/ask', methods=['POST'])
def ask_question():
    """智能问答"""
    data = request.get_json()
    question = data.get('question', '')
    knowledge_base_id = data.get('knowledge_base_id')
    top_k = data.get('top_k', 5)

    if not question:
        return jsonify({'error': '请输入问题'}), 400

    service = QuestionAnsweringService()
    result = service.answer(question, knowledge_base_id, top_k)
    return jsonify(result)


@question_bp.route('/ask-438c', methods=['POST'])
def ask_about_438c():
    """关于438C标准的问答"""
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({'error': '请输入问题'}), 400

    service = QuestionAnsweringService()
    result = service.answer_about_438c(question)
    return jsonify(result)
