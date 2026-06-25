import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config.config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)

    # 确保上传目录存在（MinIO回退时使用）
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'knowledge'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], '438c'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'generated'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'code'), exist_ok=True)

    # 初始化MinIO存储（确保bucket存在）
    from app.services.storage_service import get_storage
    storage = get_storage()
    if storage.available:
        app.logger.info(f"MinIO存储已连接: {storage.endpoint}/{storage.bucket_name}")
    else:
        app.logger.warning("MinIO不可用，使用本地文件存储")

    # 注册蓝图
    from app.api.knowledge import knowledge_bp
    from app.api.standard_438c import standard_438c_bp
    from app.api.generation import generation_bp
    from app.api.validation import validation_bp
    from app.api.merge import merge_bp
    from app.api.question import question_bp
    from app.api.project import project_bp

    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
    app.register_blueprint(standard_438c_bp, url_prefix='/api/438c')
    app.register_blueprint(generation_bp, url_prefix='/api/generation')
    app.register_blueprint(validation_bp, url_prefix='/api/validation')
    app.register_blueprint(merge_bp, url_prefix='/api/merge')
    app.register_blueprint(question_bp, url_prefix='/api/question')
    app.register_blueprint(project_bp, url_prefix='/api/project')

    return app
