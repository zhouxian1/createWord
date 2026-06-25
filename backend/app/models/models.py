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
    security_level = db.Column(db.String(20), default='内部')  # 密级: 公开, 内部, 秘密, 机密, 绝密
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
            'security_level': self.security_level,
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
    # 多维度打标
    kb_type = db.Column(db.String(50), default='general')  # 类型: general, 438c_standard, code, technical
    security_level = db.Column(db.String(20), default='内部')  # 密级
    version = db.Column(db.String(50), default='1.0')  # 版本
    tags = db.Column(db.Text)  # 标签(JSON数组)
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
            'kb_type': self.kb_type,
            'security_level': self.security_level,
            'version': self.version,
            'tags': self.tags,
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
    # 多维度打标
    file_category = db.Column(db.String(50))  # 文件分类: standard, code, design, test, config
    security_level = db.Column(db.String(20), default='内部')  # 密级
    version = db.Column(db.String(50), default='1.0')  # 版本
    tags = db.Column(db.Text)  # 标签(JSON数组)
    # 审核流程
    review_status = db.Column(db.String(20), default='pending')  # pending, reviewing, approved, rejected
    reviewed_by = db.Column(db.String(100))  # 审核人
    reviewed_at = db.Column(db.DateTime)  # 审核时间
    review_comments = db.Column(db.Text)  # 审核意见
    # 增量导入与版本管理
    file_hash = db.Column(db.String(64))  # 文件内容哈希(SHA256)
    content_hash = db.Column(db.String(64))  # 文本内容哈希(用于变更检测)
    version_number = db.Column(db.Integer, default=1)  # 版本号
    is_latest = db.Column(db.Boolean, default=True)  # 是否最新版本
    parent_file_id = db.Column(db.Integer, db.ForeignKey('knowledge_files.id'))  # 父版本文件ID
    change_description = db.Column(db.Text)  # 变更说明
    # 时间戳
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    indexed_at = db.Column(db.DateTime)

    # 关联
    version_history = db.relationship('KnowledgeFile', backref=db.backref('parent_version', remote_side=[id]),
                                      lazy='dynamic')

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
            'file_category': self.file_category,
            'security_level': self.security_level,
            'version': self.version,
            'tags': self.tags,
            'review_status': self.review_status,
            'reviewed_by': self.reviewed_by,
            'review_comments': self.review_comments,
            'file_hash': self.file_hash,
            'content_hash': self.content_hash,
            'version_number': self.version_number,
            'is_latest': self.is_latest,
            'parent_file_id': self.parent_file_id,
            'change_description': self.change_description,
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
    # 多维度打标
    security_level = db.Column(db.String(20), default='内部')  # 密级
    version = db.Column(db.String(50), default='1.0')  # 版本
    tags = db.Column(db.Text)  # 标签(JSON数组)
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
            'security_level': self.security_level,
            'version': self.version,
            'tags': self.tags,
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
    # JSON Schema约束
    schema_constraints = db.Column(db.Text)  # 章节JSON Schema约束(JSON)
    required_elements = db.Column(db.Text)  # 必填要素列表(JSON数组)
    # 生成与验证状态
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
            'prompt_template': self.prompt_template,
            'schema_constraints': self.schema_constraints,
            'required_elements': self.required_elements,
            'generation_status': self.generation_status,
            'validation_status': self.validation_status,
            'validation_details': self.validation_details,
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
    knowledge_base_ids = db.Column(db.Text)  # 关联知识库IDs(JSON数组)
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
            'knowledge_base_ids': self.knowledge_base_ids,
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
    # 排版配置
    include_cover = db.Column(db.Boolean, default=True)  # 包含封面
    include_toc = db.Column(db.Boolean, default=True)  # 包含目录
    header_text = db.Column(db.String(200))  # 页眉文本
    footer_text = db.Column(db.String(200))  # 页脚文本
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
            'include_cover': self.include_cover,
            'include_toc': self.include_toc,
            'header_text': self.header_text,
            'footer_text': self.footer_text,
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


class ReviewRecord(db.Model):
    """审核记录模型"""
    __tablename__ = 'review_records'

    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(30), nullable=False)  # knowledge_file, document, chapter
    target_id = db.Column(db.Integer, nullable=False)  # 目标ID
    action = db.Column(db.String(20), nullable=False)  # submit, approve, reject, edit, rollback
    reviewer = db.Column(db.String(100))  # 审核人
    comments = db.Column(db.Text)  # 审核意见
    old_data = db.Column(db.Text)  # 变更前数据(JSON)
    new_data = db.Column(db.Text)  # 变更后数据(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'action': self.action,
            'reviewer': self.reviewer,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FileVersionHistory(db.Model):
    """文件版本历史模型"""
    __tablename__ = 'file_version_history'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('knowledge_files.id'))  # 当前文件ID
    version_number = db.Column(db.Integer, nullable=False)  # 版本号
    file_path = db.Column(db.String(1000))  # 文件路径
    content_text = db.Column(db.Text)  # 该版本的文本内容
    content_hash = db.Column(db.String(64))  # 内容哈希
    change_type = db.Column(db.String(20), default='update')  # create, update, rollback
    change_description = db.Column(db.Text)  # 变更说明
    changed_by = db.Column(db.String(100))  # 变更人
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'version_number': self.version_number,
            'content_hash': self.content_hash,
            'change_type': self.change_type,
            'change_description': self.change_description,
            'changed_by': self.changed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
