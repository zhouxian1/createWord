from datetime import datetime
from app import db


class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    system_name = db.Column(db.String(200))  # 系统名称
    system_version = db.Column(db.String(50))  # 系统版本
    organization = db.Column(db.String(200))  # 编制单位
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    documents = db.relationship('Document', backref='project', lazy='dynamic')
    knowledge_bases = db.relationship('KnowledgeBase', backref='project', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'system_name': self.system_name,
            'system_version': self.system_version,
            'organization': self.organization,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'document_count': self.documents.count(),
            'knowledge_base_count': self.knowledge_bases.count()
        }


class KnowledgeBase(db.Model):
    """知识库模型"""
    __tablename__ = 'knowledge_bases'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    doc_count = db.Column(db.Integer, default=0)
    total_size = db.Column(db.BigInteger, default=0)
    status = db.Column(db.String(20), default='active')  # active, indexing, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    files = db.relationship('KnowledgeFile', backref='knowledge_base', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'doc_count': self.doc_count,
            'total_size': self.total_size,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class KnowledgeFile(db.Model):
    """知识库文件模型"""
    __tablename__ = 'knowledge_files'

    id = db.Column(db.Integer, primary_key=True)
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_bases.id'))
    filename = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.BigInteger)
    file_path = db.Column(db.String(1000), nullable=False)
    content_text = db.Column(db.Text)  # 提取的文本内容
    content_structure = db.Column(db.Text)  # 结构化内容(JSON)
    chunk_count = db.Column(db.Integer, default=0)
    index_status = db.Column(db.String(20), default='pending')  # pending, indexing, completed, error
    error_message = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    indexed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'knowledge_base_id': self.knowledge_base_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'chunk_count': self.chunk_count,
            'index_status': self.index_status,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None
        }


class Document(db.Model):
    """438C文档模型"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    doc_type = db.Column(db.String(100), nullable=False)  # 438C文档类型编码
    doc_name = db.Column(db.String(200), nullable=False)  # 文档名称
    doc_code = db.Column(db.String(50))  # 文档编号
    status = db.Column(db.String(20), default='draft')  # draft, generating, generated, validated, error
    generation_mode = db.Column(db.String(30))  # full, chapter, code
    file_path = db.Column(db.String(1000))  # 生成的文件路径
    content_data = db.Column(db.Text)  # 文档内容数据(JSON)
    validation_result = db.Column(db.Text)  # 验证结果(JSON)
    validation_score = db.Column(db.Float)  # 验证评分
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    chapters = db.relationship('DocumentChapter', backref='document', lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'doc_type': self.doc_type,
            'doc_name': self.doc_name,
            'doc_code': self.doc_code,
            'status': self.status,
            'generation_mode': self.generation_mode,
            'file_path': self.file_path,
            'validation_score': self.validation_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'chapter_count': self.chapters.count()
        }


class DocumentChapter(db.Model):
    """文档章节模型"""
    __tablename__ = 'document_chapters'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    chapter_number = db.Column(db.String(20), nullable=False)  # 章节编号 如 1, 1.1, 1.1.1
    chapter_title = db.Column(db.String(500), nullable=False)
    chapter_level = db.Column(db.Integer, default=1)  # 层级
    content = db.Column(db.Text)  # 章节内容
    prompt_template = db.Column(db.Text)  # 定制化提示词
    generation_status = db.Column(db.String(20), default='pending')  # pending, generating, completed, error
    validation_status = db.Column(db.String(20), default='pending')  # pending, pass, fail
    validation_details = db.Column(db.Text)  # 验证详情(JSON)
    sort_order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('document_chapters.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    children = db.relationship('DocumentChapter', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chapter_number': self.chapter_number,
            'chapter_title': self.chapter_title,
            'chapter_level': self.chapter_level,
            'content': self.content,
            'generation_status': self.generation_status,
            'validation_status': self.validation_status,
            'sort_order': self.sort_order,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class GenerationTask(db.Model):
    """文档生成任务模型"""
    __tablename__ = 'generation_tasks'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    task_type = db.Column(db.String(30), nullable=False)  # full, chapter, code
    target_chapters = db.Column(db.Text)  # 目标章节(JSON数组)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'task_type': self.task_type,
            'target_chapters': self.target_chapters,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MergeTask(db.Model):
    """文档合稿任务模型"""
    __tablename__ = 'merge_tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    name = db.Column(db.String(200), nullable=False)
    source_documents = db.Column(db.Text, nullable=False)  # 源文档ID列表(JSON)
    output_format = db.Column(db.String(20), default='docx')  # docx, pdf
    merge_strategy = db.Column(db.String(30), default='sequential')  # sequential, by_type
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    output_path = db.Column(db.String(1000))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'source_documents': self.source_documents,
            'output_format': self.output_format,
            'merge_strategy': self.merge_strategy,
            'status': self.status,
            'output_path': self.output_path,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ValidationRule(db.Model):
    """438C验证规则模型"""
    __tablename__ = 'validation_rules'

    id = db.Column(db.Integer, primary_key=True)
    doc_type = db.Column(db.String(100), nullable=False)  # 文档类型
    chapter_number = db.Column(db.String(20))  # 适用章节
    rule_name = db.Column(db.String(200), nullable=False)  # 规则名称
    rule_type = db.Column(db.String(30), nullable=False)  # completeness, compliance, format
    rule_description = db.Column(db.Text)  # 规则描述
    check_expression = db.Column(db.Text)  # 校验表达式/逻辑
    severity = db.Column(db.String(10), default='error')  # error, warning, info
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'doc_type': self.doc_type,
            'chapter_number': self.chapter_number,
            'rule_name': self.rule_name,
            'rule_type': self.rule_type,
            'rule_description': self.rule_description,
            'severity': self.severity,
            'is_active': self.is_active
        }
