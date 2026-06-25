"""知识库API - 支持上传、API对接、批量导入、审核、增量导入、版本回滚，MinIO存储"""
import os
import uuid
import json
import hashlib
import shutil
import logging
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from app import db
from app.models.models import (KnowledgeBase, KnowledgeFile, ReviewRecord,
                                FileVersionHistory, Project)
from app.services.document_parser import DocumentParser
from app.services.semantic_indexer import SemanticIndexer
from app.services.text_preprocessor import TextPreprocessor
from app.services.storage_service import get_storage

logger = logging.getLogger(__name__)
knowledge_bp = Blueprint('knowledge', __name__)

# 全局语义索引器单例（避免每次请求重新初始化chromadb）
_semantic_indexer = None

def get_indexer():
    global _semantic_indexer
    if _semantic_indexer is None:
        _semantic_indexer = SemanticIndexer()
    return _semantic_indexer
parser = DocumentParser()
preprocessor = TextPreprocessor()


@knowledge_bp.route('/bases', methods=['GET'])
def list_knowledge_bases():
    """获取知识库列表（支持多维度过滤）"""
    project_id = request.args.get('project_id', type=int)
    kb_type = request.args.get('kb_type')
    security_level = request.args.get('security_level')
    tags = request.args.get('tags')

    query = KnowledgeBase.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if kb_type:
        query = query.filter_by(kb_type=kb_type)
    if security_level:
        query = query.filter_by(security_level=security_level)

    bases = query.order_by(KnowledgeBase.updated_at.desc()).all()

    # 标签过滤
    if tags:
        tag_list = tags.split(',')
        filtered = []
        for b in bases:
            b_tags = json.loads(b.tags) if b.tags else []
            if any(t in b_tags for t in tag_list):
                filtered.append(b)
        bases = filtered

    return jsonify({'items': [b.to_dict() for b in bases], 'total': len(bases)})


@knowledge_bp.route('/bases', methods=['POST'])
def create_knowledge_base():
    """创建知识库（支持多维度打标）"""
    data = request.get_json()
    kb = KnowledgeBase(
        name=data.get('name', ''),
        description=data.get('description', ''),
        project_id=data.get('project_id'),
        kb_type=data.get('kb_type', 'general'),
        security_level=data.get('security_level', '内部'),
        version=data.get('version', '1.0'),
        tags=json.dumps(data.get('tags', []), ensure_ascii=False)
    )
    db.session.add(kb)
    db.session.commit()
    return jsonify(kb.to_dict()), 201


@knowledge_bp.route('/bases/<int:kb_id>', methods=['GET'])
def get_knowledge_base(kb_id):
    """获取知识库详情"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    result = kb.to_dict()
    # 附加统计信息
    indexer = SemanticIndexer()
    result['index_stats'] = indexer.get_stats()
    return jsonify(result)


@knowledge_bp.route('/bases/<int:kb_id>', methods=['PUT'])
def update_knowledge_base(kb_id):
    """更新知识库（含打标）"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    data = request.get_json()
    for field in ['name', 'description', 'kb_type', 'security_level', 'version']:
        if field in data:
            setattr(kb, field, data[field])
    if 'tags' in data:
        kb.tags = json.dumps(data['tags'], ensure_ascii=False)
    db.session.commit()
    return jsonify(kb.to_dict())


@knowledge_bp.route('/bases/<int:kb_id>', methods=['DELETE'])
def delete_knowledge_base(kb_id):
    """删除知识库"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    storage = get_storage()
    for f in kb.files.all():
        # 从MinIO或本地删除文件
        if f.file_path:
            object_name = _get_object_name(f.file_path)
            storage.delete_file(object_name)
        db.session.delete(f)
    db.session.delete(kb)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@knowledge_bp.route('/bases/<int:kb_id>/upload', methods=['POST'])
def upload_file(kb_id):
    """本地上传文件到知识库（存储至MinIO）"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    files = request.files.getlist('files')

    if not files:
        return jsonify({'error': '未选择文件'}), 400

    results = []
    storage = get_storage()

    for file in files:
        if file.filename == '':
            continue

        if not DocumentParser.is_supported(file.filename):
            results.append({'filename': file.filename, 'status': 'error', 'message': '不支持的文件格式'})
            continue

        result = _process_uploaded_file(file, kb_id, kb, storage)
        results.append(result)

    # 更新知识库统计
    kb.doc_count = kb.files.filter_by(is_latest=True).count()
    kb.total_size = sum(f.file_size or 0 for f in kb.files.filter_by(is_latest=True).all())
    db.session.commit()

    return jsonify({'results': results})


@knowledge_bp.route('/bases/<int:kb_id>/batch-import', methods=['POST'])
def batch_import(kb_id):
    """批量导入文件（存储至MinIO）"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    data = request.get_json()
    file_paths = data.get('file_paths', [])

    if not file_paths:
        return jsonify({'error': '未指定文件路径'}), 400

    storage = get_storage()
    results = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            results.append({'file_path': file_path, 'status': 'error', 'message': '文件不存在'})
            continue

        filename = os.path.basename(file_path)
        if not DocumentParser.is_supported(filename):
            results.append({'file_path': file_path, 'status': 'error', 'message': '不支持的文件格式'})
            continue

        # 上传到MinIO
        ext = os.path.splitext(filename)[1]
        object_name = f"knowledge/{kb_id}/{uuid.uuid4().hex}{ext}"
        upload_result = storage.upload_file(object_name, file_path)

        # 创建文件记录
        file_type = DocumentParser.get_file_type(filename)
        kf = KnowledgeFile(
            knowledge_base_id=kb_id,
            filename=os.path.basename(object_name),
            original_filename=filename,
            file_type=file_type,
            file_size=os.path.getsize(file_path),
            file_path=object_name,  # 存储MinIO对象名
            file_category=data.get('file_category', ''),
            security_level=data.get('security_level', kb.security_level),
            version=data.get('version', '1.0'),
            tags=json.dumps(data.get('tags', []), ensure_ascii=False),
            index_status='pending'
        )
        db.session.add(kf)
        db.session.flush()

        # 解析和索引
        try:
            # 下载到临时文件进行解析
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name
            storage.download_file(object_name, tmp_path)

            parse_result = parser.parse(tmp_path, file_type)
            kf.content_text = parse_result.get('text', '')
            kf.content_structure = str(parse_result.get('structure', {}))

            # 计算哈希
            kf.file_hash = _compute_file_hash(tmp_path)
            kf.content_hash = _compute_content_hash(kf.content_text)

            # 清理临时文件
            os.unlink(tmp_path)

            kf.index_status = 'indexing'
            db.session.commit()

            indexer = SemanticIndexer()
            index_result = indexer.build_index(
                file_id=kf.id,
                text=kf.content_text,
                metadata={'knowledge_base_id': kb_id, 'filename': filename},
                file_type=file_type
            )
            kf.chunk_count = index_result.get('chunk_count', 0)
            kf.index_status = index_result.get('status', 'completed')
            kf.indexed_at = datetime.utcnow()
        except Exception as e:
            kf.index_status = 'error'
            kf.error_message = str(e)
            logger.error(f"文件处理失败: {filename}, {str(e)}")

        db.session.commit()
        results.append({
            'file_path': file_path,
            'filename': filename,
            'status': kf.index_status,
            'file_id': kf.id,
            'chunk_count': kf.chunk_count,
            'storage_type': upload_result.get('storage_type', 'unknown')
        })

    kb.doc_count = kb.files.filter_by(is_latest=True).count()
    kb.total_size = sum(f.file_size or 0 for f in kb.files.filter_by(is_latest=True).all())
    db.session.commit()

    return jsonify({'results': results})


@knowledge_bp.route('/bases/<int:kb_id>/api-import', methods=['POST'])
def api_import(kb_id):
    """API对接导入（存储至MinIO）"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    data = request.get_json()
    api_url = data.get('api_url')
    api_method = data.get('api_method', 'GET')
    api_headers = data.get('api_headers', {})
    api_body = data.get('api_body')
    content_field = data.get('content_field', 'content')
    title_field = data.get('title_field', 'title')

    if not api_url:
        return jsonify({'error': '未指定API地址'}), 400

    storage = get_storage()

    try:
        import requests
        if api_method.upper() == 'GET':
            resp = requests.get(api_url, headers=api_headers, timeout=30)
        else:
            resp = requests.post(api_url, headers=api_headers, json=api_body, timeout=30)
        resp.raise_for_status()
        api_data = resp.json()

        # 提取内容
        contents = api_data if isinstance(api_data, list) else [api_data]
        results = []

        for item in contents:
            content = item.get(content_field, '')
            title = item.get(title_field, f'api_import_{uuid.uuid4().hex[:8]}')

            if not content:
                continue

            # 上传到MinIO
            object_name = f"knowledge/{kb_id}/{uuid.uuid4().hex}.txt"
            upload_result = storage.upload_bytes(
                object_name,
                content.encode('utf-8'),
                content_type='text/plain'
            )

            kf = KnowledgeFile(
                knowledge_base_id=kb_id,
                filename=os.path.basename(object_name),
                original_filename=f"{title}.txt",
                file_type='txt',
                file_size=len(content.encode('utf-8')),
                file_path=object_name,
                file_category='api_import',
                content_text=content,
                content_hash=_compute_content_hash(content),
                index_status='pending'
            )
            db.session.add(kf)
            db.session.flush()

            # 索引
            indexer = SemanticIndexer()
            index_result = indexer.build_index(
                file_id=kf.id, text=content,
                metadata={'knowledge_base_id': kb_id, 'source': 'api', 'title': title},
                file_type='txt'
            )
            kf.chunk_count = index_result.get('chunk_count', 0)
            kf.index_status = index_result.get('status', 'completed')
            kf.indexed_at = datetime.utcnow()
            db.session.commit()

            results.append({'title': title, 'status': kf.index_status, 'file_id': kf.id})

        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': f'API导入失败: {str(e)}'}), 500


@knowledge_bp.route('/bases/<int:kb_id>/files', methods=['GET'])
def list_files(kb_id):
    """获取知识库文件列表"""
    review_status = request.args.get('review_status')
    file_category = request.args.get('file_category')
    is_latest = request.args.get('is_latest', 'true')

    query = KnowledgeFile.query.filter_by(knowledge_base_id=kb_id)
    if review_status:
        query = query.filter_by(review_status=review_status)
    if file_category:
        query = query.filter_by(file_category=file_category)
    if is_latest == 'true':
        query = query.filter_by(is_latest=True)

    files = query.order_by(KnowledgeFile.uploaded_at.desc()).all()
    return jsonify({'items': [f.to_dict() for f in files], 'total': len(files)})


@knowledge_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """获取文件详情（含预览）"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    result = kf.to_dict()
    # 添加版本历史
    versions = FileVersionHistory.query.filter_by(file_id=file_id)\
        .order_by(FileVersionHistory.version_number.desc()).all()
    result['version_history'] = [v.to_dict() for v in versions]
    return jsonify(result)


@knowledge_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除知识库文件（从MinIO删除）"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    kb = kf.knowledge_base

    # 从MinIO或本地删除文件
    storage = get_storage()
    if kf.file_path:
        object_name = _get_object_name(kf.file_path)
        storage.delete_file(object_name)

    indexer = SemanticIndexer()
    indexer.delete_index(kf.id)
    db.session.delete(kf)

    kb.doc_count = kb.files.filter_by(is_latest=True).count()
    kb.total_size = sum(f.file_size or 0 for f in kb.files.filter_by(is_latest=True).all())
    db.session.commit()
    return jsonify({'message': '删除成功'})


@knowledge_bp.route('/files/<int:file_id>/preview', methods=['GET'])
def preview_file(file_id):
    """知识库文件可视化预览（支持MinIO下载）"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    result = {
        'id': kf.id,
        'filename': kf.original_filename,
        'file_type': kf.file_type,
        'content_text': kf.content_text,
        'content_structure': kf.content_structure,
        'chunk_count': kf.chunk_count,
        'review_status': kf.review_status,
    }
    # 如果MinIO可用，生成预签名URL
    storage = get_storage()
    if storage.available and kf.file_path:
        object_name = _get_object_name(kf.file_path)
        presigned_url = storage.get_presigned_url(object_name, expires=3600)
        if presigned_url:
            result['download_url'] = presigned_url
    return jsonify(result)


@knowledge_bp.route('/files/<int:file_id>/edit', methods=['PUT'])
def edit_file_content(file_id):
    """编辑文件内容（人工校验/纠错）"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    data = request.get_json()
    new_content = data.get('content_text')

    if new_content is None:
        return jsonify({'error': '缺少内容'}), 400

    # 记录审核记录
    review = ReviewRecord(
        target_type='knowledge_file',
        target_id=file_id,
        action='edit',
        reviewer=data.get('reviewer', 'system'),
        comments=data.get('comments', '内容编辑'),
        old_data=json.dumps({'content_text': kf.content_text[:500]}, ensure_ascii=False),
        new_data=json.dumps({'content_text': new_content[:500]}, ensure_ascii=False)
    )
    db.session.add(review)

    # 保存版本历史
    _save_version(kf, 'update', data.get('reviewer', 'system'), data.get('comments', ''))

    # 更新内容
    old_content = kf.content_text
    kf.content_text = new_content
    kf.content_hash = _compute_content_hash(new_content)
    kf.version_number = (kf.version_number or 0) + 1

    # 重新索引
    try:
        indexer = SemanticIndexer()
        indexer.delete_index(kf.id)
        index_result = indexer.build_index(
            file_id=kf.id, text=new_content,
            metadata={'knowledge_base_id': kf.knowledge_base_id, 'filename': kf.original_filename},
            file_type=kf.file_type
        )
        kf.chunk_count = index_result.get('chunk_count', 0)
    except Exception as e:
        logger.error(f"重新索引失败: {str(e)}")

    db.session.commit()
    return jsonify(kf.to_dict())


@knowledge_bp.route('/files/<int:file_id>/review', methods=['POST'])
def review_file(file_id):
    """审核文件（审核通过后发布至生产环境）"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    data = request.get_json()
    action = data.get('action')  # approve, reject
    reviewer = data.get('reviewer', '')
    comments = data.get('comments', '')

    if action not in ('approve', 'reject'):
        return jsonify({'error': '无效的审核操作'}), 400

    old_status = kf.review_status
    if action == 'approve':
        kf.review_status = 'approved'
        kf.reviewed_by = reviewer
        kf.reviewed_at = datetime.utcnow()
        kf.review_comments = comments
    else:
        kf.review_status = 'rejected'
        kf.reviewed_by = reviewer
        kf.reviewed_at = datetime.utcnow()
        kf.review_comments = comments

    # 记录审核记录
    review = ReviewRecord(
        target_type='knowledge_file',
        target_id=file_id,
        action=action,
        reviewer=reviewer,
        comments=comments,
        old_data=json.dumps({'review_status': old_status}, ensure_ascii=False),
        new_data=json.dumps({'review_status': kf.review_status}, ensure_ascii=False)
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(kf.to_dict())


@knowledge_bp.route('/files/<int:file_id>/rollback', methods=['POST'])
def rollback_file(file_id):
    """版本回滚"""
    kf = KnowledgeFile.query.get_or_404(file_id)
    data = request.get_json()
    target_version = data.get('version_number')

    if not target_version:
        return jsonify({'error': '未指定目标版本'}), 400

    # 查找目标版本
    version = FileVersionHistory.query.filter_by(
        file_id=file_id, version_number=target_version
    ).first()

    if not version:
        return jsonify({'error': f'版本 {target_version} 不存在'}), 404

    # 保存当前版本
    _save_version(kf, 'rollback', data.get('operator', 'system'),
                  f'回滚至版本 {target_version}')

    # 回滚内容
    kf.content_text = version.content_text
    kf.content_hash = version.content_hash
    kf.version_number = (kf.version_number or 0) + 1

    # 重新索引
    try:
        indexer = SemanticIndexer()
        indexer.delete_index(kf.id)
        index_result = indexer.build_index(
            file_id=kf.id, text=kf.content_text,
            metadata={'knowledge_base_id': kf.knowledge_base_id, 'filename': kf.original_filename},
            file_type=kf.file_type
        )
        kf.chunk_count = index_result.get('chunk_count', 0)
    except Exception as e:
        logger.error(f"重新索引失败: {str(e)}")

    # 记录审核记录
    review = ReviewRecord(
        target_type='knowledge_file',
        target_id=file_id,
        action='rollback',
        reviewer=data.get('operator', 'system'),
        comments=f'回滚至版本 {target_version}'
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(kf.to_dict())


@knowledge_bp.route('/bases/<int:kb_id>/incremental-import', methods=['POST'])
def incremental_import(kb_id):
    """增量导入 - 自动检测变更并更新索引（存储至MinIO）"""
    kb = KnowledgeBase.query.get_or_404(kb_id)
    data = request.get_json()
    file_paths = data.get('file_paths', [])

    storage = get_storage()
    results = {'added': 0, 'updated': 0, 'unchanged': 0, 'errors': 0}

    for file_path in file_paths:
        if not os.path.exists(file_path):
            results['errors'] += 1
            continue

        filename = os.path.basename(file_path)
        current_hash = _compute_file_hash(file_path)

        # 检查是否已存在
        existing = KnowledgeFile.query.filter_by(
            knowledge_base_id=kb_id,
            original_filename=filename,
            is_latest=True
        ).first()

        if existing:
            if existing.file_hash == current_hash:
                results['unchanged'] += 1
                continue

            # 文件有变更，更新
            existing.is_latest = False
            _save_version(existing, 'update', 'system', '增量更新')

        # 解析文件
        try:
            file_type = DocumentParser.get_file_type(filename)
            parse_result = parser.parse(file_path, file_type)
            content = parse_result.get('text', '')

            # 上传到MinIO
            ext = os.path.splitext(filename)[1]
            object_name = f"knowledge/{kb_id}/{uuid.uuid4().hex}{ext}"
            storage.upload_file(object_name, file_path)

            kf = KnowledgeFile(
                knowledge_base_id=kb_id,
                filename=os.path.basename(object_name),
                original_filename=filename,
                file_type=file_type,
                file_size=os.path.getsize(file_path),
                file_path=object_name,
                content_text=content,
                content_structure=str(parse_result.get('structure', {})),
                file_hash=current_hash,
                content_hash=_compute_content_hash(content),
                version_number=(existing.version_number + 1) if existing else 1,
                is_latest=True,
                parent_file_id=existing.id if existing else None,
                change_description='增量导入更新',
                index_status='pending'
            )
            db.session.add(kf)
            db.session.flush()

            # 索引
            indexer = SemanticIndexer()
            if existing:
                indexer.delete_index(existing.id)
            index_result = indexer.build_index(
                file_id=kf.id, text=content,
                metadata={'knowledge_base_id': kb_id, 'filename': filename},
                file_type=file_type
            )
            kf.chunk_count = index_result.get('chunk_count', 0)
            kf.index_status = index_result.get('status', 'completed')
            kf.indexed_at = datetime.utcnow()

            if existing:
                results['updated'] += 1
            else:
                results['added'] += 1
        except Exception as e:
            logger.error(f"增量导入失败: {filename}, {str(e)}")
            results['errors'] += 1

    db.session.commit()
    kb.doc_count = kb.files.filter_by(is_latest=True).count()
    kb.total_size = sum(f.file_size or 0 for f in kb.files.filter_by(is_latest=True).all())
    db.session.commit()

    return jsonify(results)


@knowledge_bp.route('/bases/<int:kb_id>/search', methods=['POST'])
def search_knowledge_base(kb_id):
    """知识库语义搜索（含Rerank和溯源）"""
    data = request.get_json()
    query = data.get('query', '')
    top_k = data.get('top_k', 5)
    use_rerank = data.get('use_rerank', True)

    indexer = SemanticIndexer()
    results = indexer.search(
        query=query,
        n_results=top_k,
        filter_metadata={'knowledge_base_id': kb_id},
        use_rerank=use_rerank
    )

    return jsonify({'results': results, 'total': len(results)})


@knowledge_bp.route('/files/<int:file_id>/versions', methods=['GET'])
def get_file_versions(file_id):
    """获取文件版本历史"""
    versions = FileVersionHistory.query.filter_by(file_id=file_id)\
        .order_by(FileVersionHistory.version_number.desc()).all()
    return jsonify({'items': [v.to_dict() for v in versions], 'total': len(versions)})


@knowledge_bp.route('/review-records', methods=['GET'])
def list_review_records():
    """获取审核记录"""
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id', type=int)

    query = ReviewRecord.query
    if target_type:
        query = query.filter_by(target_type=target_type)
    if target_id:
        query = query.filter_by(target_id=target_id)

    records = query.order_by(ReviewRecord.created_at.desc()).limit(100).all()
    return jsonify({'items': [r.to_dict() for r in records], 'total': len(records)})


# ===== 辅助函数 =====

def _process_uploaded_file(file, kb_id, kb, storage) -> dict:
    """处理上传的文件（存储至MinIO）"""
    ext = os.path.splitext(file.filename)[1]
    object_name = f"knowledge/{kb_id}/{uuid.uuid4().hex}{ext}"

    # 先保存到临时文件
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp_path = tmp.name
    file.save(tmp_path)

    # 上传到MinIO
    upload_result = storage.upload_file(object_name, tmp_path)

    file_type = DocumentParser.get_file_type(file.filename)
    kf = KnowledgeFile(
        knowledge_base_id=kb_id,
        filename=os.path.basename(object_name),
        original_filename=file.filename,
        file_type=file_type,
        file_size=os.path.getsize(tmp_path),
        file_path=object_name,  # 存储MinIO对象名
        file_category=request.form.get('file_category', ''),
        security_level=request.form.get('security_level', kb.security_level),
        version=request.form.get('version', '1.0'),
        tags=request.form.get('tags', '[]'),
        file_hash=_compute_file_hash(tmp_path),
        index_status='pending'
    )
    db.session.add(kf)
    db.session.flush()

    try:
        parse_result = parser.parse(tmp_path, file_type)
        kf.content_text = parse_result.get('text', '')
        kf.content_structure = str(parse_result.get('structure', {}))
        kf.content_hash = _compute_content_hash(kf.content_text)
        kf.index_status = 'indexing'
        db.session.commit()

        indexer = SemanticIndexer()
        index_result = indexer.build_index(
            file_id=kf.id,
            text=kf.content_text,
            metadata={'knowledge_base_id': kb_id, 'filename': file.filename},
            file_type=file_type
        )
        kf.chunk_count = index_result.get('chunk_count', 0)
        kf.index_status = index_result.get('status', 'completed')
        kf.indexed_at = datetime.utcnow()
    except Exception as e:
        kf.index_status = 'error'
        kf.error_message = str(e)
        logger.error(f"文件处理失败: {file.filename}, {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    db.session.commit()
    return {
        'filename': file.filename,
        'status': kf.index_status,
        'file_id': kf.id,
        'chunk_count': kf.chunk_count,
        'storage_type': upload_result.get('storage_type', 'unknown')
    }


def _compute_file_hash(file_path: str) -> str:
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def _compute_content_hash(content: str) -> str:
    """计算文本内容哈希"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _get_object_name(file_path: str) -> str:
    """从file_path获取MinIO对象名（兼容旧数据）"""
    # 如果file_path已经是对象名格式（不含路径分隔符或为相对路径），直接返回
    if file_path and not os.path.isabs(file_path):
        return file_path
    # 旧数据：绝对路径，提取相对部分
    if file_path:
        # 尝试从路径中提取knowledge/xxx部分
        parts = file_path.replace('\\', '/').split('/')
        for i, part in enumerate(parts):
            if part == 'knowledge' and i + 1 < len(parts):
                return '/'.join(parts[i:])
    return file_path


def _save_version(kf: KnowledgeFile, change_type: str, operator: str, description: str):
    """保存版本历史"""
    version = FileVersionHistory(
        file_id=kf.id,
        version_number=kf.version_number or 1,
        file_path=kf.file_path,
        content_text=kf.content_text,
        content_hash=kf.content_hash,
        change_type=change_type,
        change_description=description,
        changed_by=operator
    )
    db.session.add(version)
