import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'doc-gen-system-secret-key-2024')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

    # 支持的文件格式
    ALLOWED_EXTENSIONS = {
        'document': ['pdf', 'docx', 'doc', 'wps', 'txt', 'md', 'html', 'json'],
        'spreadsheet': ['xlsx', 'xls'],
        'presentation': ['pptx', 'ppt'],
        'image': ['jpg', 'jpeg', 'png'],
        'code': ['c', 'h', 'cpp', 'hpp', 'py', 'java', 'cs', 'go', 'rs', 'js', 'ts'],
        'binary': ['bin', 'dat', 'hex']
    }

    # 向量数据库配置
    VECTOR_DB_PATH = os.path.join(basedir, 'data', 'vector_db')
    EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'

    # LLM配置
    LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.openai.com/v1')
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4')

    # 438C配置
    STANDARD_438C_RULES_PATH = os.path.join(basedir, 'app', 'config', '438c_rules')
    STANDARD_438C_TEMPLATES_PATH = os.path.join(basedir, 'app', 'templates', '438c')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data', 'dev.db')
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data', 'prod.db')
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
