"""文档合稿与排版API"""
import os
from flask import Blueprint, request, jsonify, send_file, current_app
from app import db
from app.models.models import MergeTask, Document
from app.services.document_merger import DocumentMerger

merge_bp = Blueprint('merge', __name__)


@merge_bp.route('/tasks', methods=['GET'])
def list_merge_tasks():
    """获取合稿任务列表"""
    project_id = request.args.get('project_id', type=int)
    query = MergeTask.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    tasks = query.order_by(MergeTask.created_at.desc()).all()
    return jsonify({'items': [t.to_dict() for t in tasks], 'total': len(tasks)})


@merge_bp.route('/tasks', methods=['POST'])
def create_merge_task():
    """创建合稿任务"""
    data = request.get_json()
    source_documents = data.get('source_documents', [])
    if not source_documents:
        return jsonify({'error': '请选择要合并的文档'}), 400

    task = MergeTask(
        project_id=data.get('project_id'),
        name=data.get('name', '合稿文档'),
        source_documents=str(source_documents),
        output_format=data.get('output_format', 'docx'),
        merge_strategy=data.get('merge_strategy', 'sequential')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@merge_bp.route('/tasks/<int:task_id>/execute', methods=['POST'])
def execute_merge(task_id):
    """执行合稿任务"""
    task = MergeTask.query.get_or_404(task_id)
    try:
        merger = DocumentMerger()
        task = merger.merge_documents(task_id)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@merge_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_merge_task(task_id):
    """获取合稿任务详情"""
    task = MergeTask.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@merge_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_merge_task(task_id):
    """删除合稿任务"""
    task = MergeTask.query.get_or_404(task_id)
    if task.output_path and os.path.exists(task.output_path):
        os.remove(task.output_path)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@merge_bp.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """下载生成的文件"""
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated')
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404


@merge_bp.route('/documents/<int:doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """下载单个文档"""
    document = Document.query.get_or_404(doc_id)
    if document.file_path and os.path.exists(document.file_path):
        return send_file(document.file_path, as_attachment=True,
                         download_name=f"{document.doc_code}_{document.doc_name}.docx")
    return jsonify({'error': '文件不存在，请先生成文档'}), 404
