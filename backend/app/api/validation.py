"""质量验证API"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.models import Document, ValidationRule
from app.services.validation_service import ValidationService
from app.config.validation_rules import VALIDATION_RULES, VALIDATION_LEVELS

validation_bp = Blueprint('validation', __name__)


@validation_bp.route('/documents/<int:doc_id>', methods=['POST'])
def validate_document(doc_id):
    """验证文档"""
    document = Document.query.get_or_404(doc_id)
    try:
        service = ValidationService()
        result = service.validate_document(doc_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@validation_bp.route('/documents/<int:doc_id>/result', methods=['GET'])
def get_validation_result(doc_id):
    """获取文档验证结果"""
    document = Document.query.get_or_404(doc_id)
    if document.validation_result:
        import json
        result = json.loads(document.validation_result)
        level = ValidationService()._get_validation_level(document.validation_score or 0)
        return jsonify({
            'document_id': doc_id,
            'score': document.validation_score,
            'level': level,
            'details': result
        })
    return jsonify({'message': '尚未进行验证'})


@validation_bp.route('/rules', methods=['GET'])
def list_rules():
    """获取验证规则列表"""
    doc_type = request.args.get('doc_type')

    rules = []
    # 通用规则
    for rule in VALIDATION_RULES.get('common', []):
        if doc_type and doc_type != 'common':
            continue
        rules.append(rule)

    # 文档专用规则
    if doc_type and doc_type != 'common':
        for rule in VALIDATION_RULES.get(doc_type, []):
            rules.append(rule)

    # 自定义规则
    custom_query = ValidationRule.query
    if doc_type:
        custom_query = custom_query.filter_by(doc_type=doc_type)
    for rule in custom_query.all():
        rules.append(rule.to_dict())

    return jsonify({'items': rules, 'total': len(rules)})


@validation_bp.route('/rules', methods=['POST'])
def create_rule():
    """创建自定义验证规则"""
    data = request.get_json()
    rule = ValidationRule(
        doc_type=data.get('doc_type'),
        chapter_number=data.get('chapter_number'),
        rule_name=data.get('rule_name'),
        rule_type=data.get('rule_type'),
        rule_description=data.get('rule_description'),
        check_expression=data.get('check_expression'),
        severity=data.get('severity', 'error')
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201


@validation_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新验证规则"""
    rule = ValidationRule.query.get_or_404(rule_id)
    data = request.get_json()
    for key in ['rule_name', 'rule_type', 'rule_description', 'check_expression', 'severity', 'is_active']:
        if key in data:
            setattr(rule, key, data[key])
    db.session.commit()
    return jsonify(rule.to_dict())


@validation_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """删除验证规则"""
    rule = ValidationRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@validation_bp.route('/levels', methods=['GET'])
def list_levels():
    """获取验证等级列表"""
    return jsonify({'items': VALIDATION_LEVELS})
