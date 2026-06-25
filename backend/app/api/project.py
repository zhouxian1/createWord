"""项目管理API"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.models import Project

project_bp = Blueprint('project', __name__)


@project_bp.route('/projects', methods=['GET'])
def list_projects():
    """获取项目列表"""
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return jsonify({'items': [p.to_dict() for p in projects], 'total': len(projects)})


@project_bp.route('/projects', methods=['POST'])
def create_project():
    """创建项目"""
    data = request.get_json()
    project = Project(
        name=data.get('name', ''),
        description=data.get('description', ''),
        system_name=data.get('system_name', ''),
        system_version=data.get('system_version', ''),
        organization=data.get('organization', '')
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@project_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    project = Project.query.get_or_404(project_id)
    result = project.to_dict()
    # 包含文档和知识库统计
    result['documents'] = [d.to_dict() for d in project.documents.all()]
    result['knowledge_bases'] = [kb.to_dict() for kb in project.knowledge_bases.all()]
    return jsonify(result)


@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    for key in ['name', 'description', 'system_name', 'system_version', 'organization']:
        if key in data:
            setattr(project, key, data[key])
    db.session.commit()
    return jsonify(project.to_dict())


@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': '删除成功'})
