"""438C标准文档API"""
import os
import tempfile
from flask import Blueprint, request, jsonify
from app.config.standard_documents import STANDARD_438C_DOCUMENTS, DOCUMENT_CATEGORIES, COMPLEXITY_LEVELS

standard_438c_bp = Blueprint('standard_438c', __name__)


@standard_438c_bp.route('/document-types', methods=['GET'])
def list_document_types():
    """获取438C文档类型列表"""
    category = request.args.get('category')
    complexity = request.args.get('complexity')

    result = []
    for code, doc_info in STANDARD_438C_DOCUMENTS.items():
        if category and doc_info.get('category') != category:
            continue
        if complexity and doc_info.get('complexity') != complexity:
            continue
        result.append({
            'code': code,
            'name': doc_info['name'],
            'full_name': doc_info.get('full_name', ''),
            'category': doc_info.get('category', ''),
            'complexity': doc_info.get('complexity', ''),
            'description': doc_info.get('description', ''),
            'chapter_count': _count_chapters(doc_info.get('chapters', []))
        })

    return jsonify({'items': result, 'total': len(result)})


@standard_438c_bp.route('/document-types/<code>', methods=['GET'])
def get_document_type(code):
    """获取438C文档类型详情"""
    doc_info = STANDARD_438C_DOCUMENTS.get(code)
    if not doc_info:
        return jsonify({'error': f'未找到文档类型: {code}'}), 404

    return jsonify({
        'code': code,
        'name': doc_info['name'],
        'full_name': doc_info.get('full_name', ''),
        'category': doc_info.get('category', ''),
        'complexity': doc_info.get('complexity', ''),
        'description': doc_info.get('description', ''),
        'chapters': doc_info.get('chapters', [])
    })


@standard_438c_bp.route('/categories', methods=['GET'])
def list_categories():
    """获取文档分类列表"""
    result = []
    for code, cat_info in DOCUMENT_CATEGORIES.items():
        result.append({
            'code': code,
            'name': cat_info['name'],
            'document_count': len(cat_info['codes']),
            'documents': cat_info['codes']
        })
    return jsonify({'items': result})


@standard_438c_bp.route('/complexity-levels', methods=['GET'])
def list_complexity_levels():
    """获取复杂度分级列表"""
    return jsonify({'items': COMPLEXITY_LEVELS})


@standard_438c_bp.route('/document-types/<code>/structure', methods=['GET'])
def get_document_structure(code):
    """获取文档结构树"""
    doc_info = STANDARD_438C_DOCUMENTS.get(code)
    if not doc_info:
        return jsonify({'error': f'未找到文档类型: {code}'}), 404

    tree = _build_chapter_tree(doc_info.get('chapters', []))
    return jsonify({'doc_type': code, 'tree': tree})


@standard_438c_bp.route('/import', methods=['POST'])
def import_438c_document():
    """导入438C标准文档"""
    from app import db
    from app.models.models import Document, DocumentChapter
    from app.services.document_parser import DocumentParser

    data = request.get_json()
    project_id = data.get('project_id')
    doc_type = data.get('doc_type')
    file_path = data.get('file_path')

    if not all([project_id, doc_type, file_path]):
        return jsonify({'error': '缺少必要参数'}), 400

    doc_config = STANDARD_438C_DOCUMENTS.get(doc_type)
    if not doc_config:
        return jsonify({'error': f'不支持的文档类型: {doc_type}'}), 400

    # 解析导入的文档
    document_parser = DocumentParser()
    parse_result = document_parser.parse(file_path)
    text = parse_result.get('text', '')

    # 创建文档记录
    document = Document(
        project_id=project_id,
        doc_type=doc_type,
        doc_name=doc_config['name'],
        doc_code=doc_config['code'],
        status='draft',
        generation_mode='import'
    )
    db.session.add(document)
    db.session.flush()

    # 创建章节结构
    _create_chapters_from_config(document.id, doc_config.get('chapters', []))
    db.session.commit()

    return jsonify(document.to_dict()), 201


def _count_chapters(chapters):
    """递归计算章节数"""
    count = len(chapters)
    for ch in chapters:
        if ch.get('sub_chapters'):
            count += _count_chapters(ch['sub_chapters'])
    return count


def _build_chapter_tree(chapters):
    """构建章节树"""
    tree = []
    for ch in chapters:
        node = {
            'number': ch['number'],
            'title': ch['title'],
            'level': ch['level'],
            'required': ch.get('required', True),
            'elements': ch.get('elements', [])
        }
        if ch.get('sub_chapters'):
            node['children'] = _build_chapter_tree(ch['sub_chapters'])
        tree.append(node)
    return tree


def _create_chapters_from_config(document_id, chapters, parent_id=None, sort_order=0):
    """从配置创建章节"""
    from app import db
    from app.models.models import DocumentChapter

    for i, ch in enumerate(chapters):
        chapter = DocumentChapter(
            document_id=document_id,
            chapter_number=ch['number'],
            chapter_title=ch['title'],
            chapter_level=ch['level'],
            generation_status='pending',
            validation_status='pending',
            sort_order=sort_order + i,
            parent_id=parent_id
        )
        db.session.add(chapter)
        db.session.flush()

        if ch.get('sub_chapters'):
            _create_chapters_from_config(document_id, ch['sub_chapters'], chapter.id,
                                         sort_order * 100 + i * 10)
