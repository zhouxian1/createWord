"""知识库API"""
import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.models import KnowledgeBase, KnowledgeFile
from app.services.document_parser import DocumentParser
from app.services.semantic_indexer import SemanticIndexer

logger = logging.getLogger(__name__)
knowledge_bp = Blueprint('knowledge', __name__)
parser = DocumentParser()


@knowledge_bp.route('/bases', methods=['GET'])
def list_knowledge_bases():
    """获取知识库列表"""
    project_id = request.args.get('project_id', type=int)
    query = KnowledgeBase.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    bases = query.order_by(KnowledgeBase.updated_at.desc()).all()
    return jsonify({'items': [b.to_dict() for b in bases], 'total': len(bases)})


@knowledge_bp.route('/bases', methods=['POST'])
def create_knowledge_base():
    """创建知识库"""
    data = request.get_json()
    kb = KnowledgeBase(
        name=data.get('name', ''),
        description=data.get('description', ''),
        project_id=data.get('project_id')
    )
    db.session.add(kb)
    db.session.commit()
    return jsonify(kb.to_dict()), 201


@knowledge_bp.route('/bases/<int:kb_id>', methods=['GET'])
def get_knowledge_base(kb_id):
    """获取知识库详情"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    return jsonify(kb.to_dict())


@knowledge_bp.route('/bases/<int:kb_id>', methods=['PUT'])
def update_knowledge_base(kb_id):
    """更新知识库"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    data = request.get_json()
    if 'name' in data:
        kb.name = data['name']
    if 'description' in data:
        kb.description = data['description']
    db.session.commit()
    return jsonify(kb.to_dict())


@knowledge_bp.route('/bases/<int:kb_id>', methods=['DELETE'])
def delete_knowledge_base(kb_id):
    """删除知识库"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    # 删除关联文件
    for f in kb.files.all():
        if f.file_path and os.path.exists(f.file_path):
            os.remove(f.file_path)
        db.session.delete(f)
    db.session.delete(kb)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@knowledge_bp.route('/bases/<int:kb_id>/upload', methods=['POST'])
def upload_file(kb_id):
    """上传文件到知识库"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    files = request.files.getlist('files')

    if not files:
        return jsonify({'error': '未选择文件'}), 400

    results = []
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'knowledge', str(kb_id))
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file.filename == '':
            continue

        if not DocumentParser.is_supported(file.filename):
            results.append({'filename': file.filename, 'status': 'error', 'message': '不支持的文件格式'})
            continue

        # 保存文件
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 创建文件记录
        file_type = DocumentParser.get_file_type(file.filename)
        kf = KnowledgeFile(
            knowledge_base_id=kb_id,
            filename=filename,
            original_filename=file.filename,
            file_type=file_type,
            file_size=os.path.getsize(file_path),
            file_path=file_path,
            index_status='pending'
        )
        db.session.add(kf)
        db.session.flush()

        # 异步解析和索引
        try:
            parse_result = parser.parse(file_path, file_type)
            kf.content_text = parse_result.get('text', '')
            kf.content_structure = str(parse_result.get('structure', {}))
            kf.index_status = 'indexing'
            db.session.commit()

            # 构建语义索引
            indexer = SemanticIndexer()
            index_result = indexer.build_index(
                file_id=kf.id,
                text=kf.content_text,
                metadata={'knowledge_base_id': kb_id, 'filename': file.filename}
            )
            kf.chunk_count = index_result.get('chunk_count', 0)
            kf.index_status = index_result.get('status', 'completed')
        except Exception as e:
            kf.index_status = 'error'
            kf.error_message = str(e)
            logger.error(f"文件处理失败: {file.filename}, {str(e)}")

        # 更新知识库统计
        kb.doc_count = kb.files.count()
        kb.total_size = sum(f.file_size or 0 for f in kb.files.all())
        db.session.commit()

        results.append({
            'filename': file.filename,
            'status': kf.index_status,
            'file_id': kf.id,
            'chunk_count': kf.chunk_count
        })

    return jsonify({'results': results})


@knowledge_bp.route('/bases/<int:kb_id>/files', methods=['GET'])
def list_files(kb_id):
    """获取知识库文件列表"""
    files = KnowledgeFile.query.filter_by(knowledge_base_id=kb_id)\
        .order_by(KnowledgeFile.uploaded_at.desc()).all()
    return jsonify({'items': [f.to_dict() for f in files], 'total': len(files)})


@knowledge_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除知识库文件"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    kb = kf.knowledge_base

    # 删除文件
    if kf.file_path and os.path.exists(kf.file_path):
        os.remove(kf.file_path)

    # 删除索引
    indexer = SemanticIndexer()
    indexer.delete_index(kf.id)

    db.session.delete(kf)

    # 更新知识库统计
    kb.doc_count = kb.files.count()
    kb.total_size = sum(f.file_size or 0 for f in kb.files.all())
    db.session.commit()

    return jsonify({'message': '删除成功'})


@knowledge_bp.route('/bases/<int:kb_id>/search', methods=['POST'])
def search_knowledge_base(kb_id):
    """知识库语义搜索"""
    data = request.get_json()
    query = data.get('query', '')
    top_k = data.get('top_k', 5)

    indexer = SemanticIndexer()
    results = indexer.search(
        query=query,
        n_results=top_k,
        filter_metadata={'knowledge_base_id': kb_id}
    )

    return jsonify({'results': results, 'total': len(results)})
