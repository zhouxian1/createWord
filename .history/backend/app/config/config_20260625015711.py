import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'doc-gen-system-secret-key-2024')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # ===== 文件存储配置 =====
    # 存储类型: local / minio
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'minio')
    UPLOAD_FOLDER = os.path.join(basedir, 'data', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    # MinIO配置
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'doc-gen-system')
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'

    # 支持的文件格式
    ALLOWED_EXTENSIONS = {
        'document': ['pdf', 'docx', 'doc', 'wps', 'txt', 'md', 'html', 'json'],
        'spreadsheet': ['xlsx', 'xls'],
        'presentation': ['pptx', 'ppt'],
        'image': ['jpg', 'jpeg', 'png'],
        'code': ['c', 'h', 'cpp', 'hpp', 'py', 'java', 'cs', 'go', 'rs', 'js', 'ts'],
        'binary': ['bin', 'dat', 'hex']
    }

    # ===== 向量数据库配置 =====
    VECTOR_DB_PATH = os.path.join(basedir, 'data', 'vector_db')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'shibing624/text2vec-base-chinese')

    # ===== Neo4j 图数据库配置 =====
    NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'neo4j123456')
    NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE', 'neo4j')

    # ===== LLM配置 - 支持国产开源大模型 =====
    # 默认使用千问(Qwen)，兼容OpenAI API格式
    # 支持的模型提供商:
    #   - Qwen (通义千问): 通过DashScope API或本地vLLM部署
    #   - ChatGLM: 通过本地vLLM部署
    #   - Baichuan: 通过本地vLLM部署
    #   - DeepSeek: 通过官方API或本地部署
    LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'qwen-plus')
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'qwen')  # qwen / chatglm / deepseek / local

    # 千问(DashScope)配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')

    # 本地模型部署配置 (vLLM/Ollama)
    LOCAL_LLM_HOST = os.environ.get('LOCAL_LLM_HOST', 'localhost')
    LOCAL_LLM_PORT = os.environ.get('LOCAL_LLM_PORT', '8000')
    LOCAL_LLM_MODEL = os.environ.get('LOCAL_LLM_MODEL', 'Qwen2.5-14B-Instruct')

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
    STORAGE_TYPE = 'local'  # 测试环境使用本地存储


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data', 'prod.db')
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
