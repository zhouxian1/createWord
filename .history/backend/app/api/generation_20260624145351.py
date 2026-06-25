"""文档生成API"""
import os
import uuid
import tempfile
import logging
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.models import Document, DocumentChapter, GenerationTask, Project
from app.services.document_generator import DocumentGenerator
from app.services.llm_service import LLMService
from app.services.semantic_indexer import SemanticIndexer
from app.services.storage_service import get_storage

logger = logging.getLogger(__name__)
generation_bp = Blueprint('generation', __name__)


@generation_bp.route('/documents', methods=['GET'])
def list_documents():
    """获取文档列表"""
    project_id = request.args.get('project_id', type=int)
    doc_type = request.args.get('doc_type')
    status = request.args.get('status')

    query = Document.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if doc_type:
        query = query.filter_by(doc_type=doc_type)
    if status:
        query = query.filter_by(status=status)

    documents = query.order_by(Document.updated_at.desc()).all()
    return jsonify({'items': [d.to_dict() for d in documents], 'total': len(documents)})


@generation_bp.route('/documents', methods=['POST'])
def create_document():
    """创建文档（生成文档框架）"""
    data = request.get_json()
    project_id = data.get('project_id')
    doc_type = data.get('doc_type')

    if not all([project_id, doc_type]):
        return jsonify({'error': '缺少必要参数'}), 400

    try:
        generator = DocumentGenerator()
        document = generator.create_document(project_id, doc_type)
        return jsonify(document.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@generation_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """获取文档详情"""
    document = Document.query.get_or_404(doc_id)
    result = document.to_dict()

    # 包含章节信息
    chapters = DocumentChapter.query.filter_by(document_id=doc_id)\
        .order_by(DocumentChapter.sort_order).all()
    result['chapters'] = [ch.to_dict() for ch in chapters]

    return jsonify(result)


@generation_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除文档"""
    document = Document.query.get_or_404(doc_id)

    # 删除文件（MinIO或本地）
    storage = get_storage()
    if document.file_path:
        object_name = document.file_path if not os.path.isabs(document.file_path) else None
        if object_name:
            storage.delete_file(object_name)
        elif os.path.exists(document.file_path):
            os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@generation_bp.route('/documents/<int:doc_id>/generate/full', methods=['POST'])
def generate_full(doc_id):
    """一键生成完整文档"""
    document = Document.query.get_or_404(doc_id)
    data = request.get_json() or {}
    project = document.project

    project_info = {
        'system_name': project.system_name if project else '',
        'system_version': project.system_version if project else '',
        'organization': project.organization if project else ''
    }
    project_info.update(data.get('project_info', {}))

    try:
        generator = DocumentGenerator()
        task = generator.generate_full(doc_id, project_info)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/documents/<int:doc_id>/generate/chapter', methods=['POST'])
def generate_by_chapter(doc_id):
    """按章节生成文档"""
    data = request.get_json()
    chapter_ids = data.get('chapter_ids', [])

    if not chapter_ids:
        return jsonify({'error': '请选择要生成的章节'}), 400

    document = Document.query.get_or_404(doc_id)
    project = document.project
    project_info = {
        'system_name': project.system_name if project else '',
        'system_version': project.system_version if project else '',
        'organization': project.organization if project else ''
    }
    project_info.update(data.get('project_info', {}))

    try:
        generator = DocumentGenerator()
        task = generator.generate_by_chapter(doc_id, chapter_ids, project_info)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/generate/from-code', methods=['POST'])
def generate_from_code():
    """从代码生成文档"""
    data = request.get_json()
    project_id = data.get('project_id')
    doc_type = data.get('doc_type')
    code_files = data.get('code_files', [])

    if not all([project_id, doc_type, code_files]):
        return jsonify({'error': '缺少必要参数'}), 400

    project = Project.query.get(project_id)
    project_info = {
        'system_name': project.system_name if project else '',
        'system_version': project.system_version if project else '',
        'organization': project.organization if project else ''
    }

    try:
        generator = DocumentGenerator()
        document = generator.generate_from_code(project_id, doc_type, code_files, project_info)
        return jsonify(document.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/documents/<int:doc_id>/chapters', methods=['GET'])
def list_chapters(doc_id):
    """获取文档章节列表"""
    chapters = DocumentChapter.query.filter_by(document_id=doc_id)\
        .order_by(DocumentChapter.sort_order).all()
    return jsonify({'items': [ch.to_dict() for ch in chapters], 'total': len(chapters)})


@generation_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """获取章节详情"""
    chapter = DocumentChapter.query.get_or_404(chapter_id)
    return jsonify(chapter.to_dict())


@generation_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    """更新章节内容"""
    chapter = DocumentChapter.query.get_or_404(chapter_id)
    data = request.get_json()

    if 'content' in data:
        chapter.content = data['content']
        chapter.generation_status = 'completed'
    if 'prompt_template' in data:
        chapter.prompt_template = data['prompt_template']

    db.session.commit()
    return jsonify(chapter.to_dict())


@generation_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取生成任务状态"""
    task = GenerationTask.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@generation_bp.route('/documents/<int:doc_id>/export', methods=['POST'])
def export_document(doc_id):
    """导出文档为DOCX"""
    from app.services.document_merger import DocumentMerger

    document = Document.query.get_or_404(doc_id)
    try:
        merger = DocumentMerger()
        file_path = merger.generate_document_file(doc_id)
        filename = os.path.basename(file_path)
        return jsonify({'file_path': file_path, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/upload-code', methods=['POST'])
def upload_code():
    """上传代码文件（存储至MinIO）"""
    files = request.files.getlist('files')
    project_id = request.form.get('project_id')

    if not files:
        return jsonify({'error': '未选择文件'}), 400

    storage = get_storage()
    results = []
    for file in files:
        if file.filename == '':
            continue
        ext = os.path.splitext(file.filename)[1]

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp_path = tmp.name
        file.save(tmp_path)

        # 上传到MinIO
        object_name = f"code/{project_id or 'default'}/{uuid.uuid4().hex}{ext}"
        upload_result = storage.upload_file(object_name, tmp_path)

        # 清理临时文件
        os.unlink(tmp_path)

        results.append({
            'original_filename': file.filename,
            'saved_path': object_name,
            'file_type': DocumentParser.get_file_type(file.filename) if hasattr(DocumentParser, 'get_file_type') else ext,
            'storage_type': upload_result.get('storage_type', 'unknown')
        })

    return jsonify({'results': results})
