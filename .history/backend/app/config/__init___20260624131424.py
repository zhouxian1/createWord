# 从438c_rules子包重新导出，使 app.config.standard_documents 等路径可用
from app.config.438c_rules.standard_documents import STANDARD_438C_DOCUMENTS, DOCUMENT_CATEGORIES, COMPLEXITY_LEVELS
from app.config.438c_rules.prompt_templates import PROMPT_TEMPLATES, DEFAULT_SYSTEM_PROMPT, DEFAULT_CHAPTER_PROMPT
from app.config.438c_rules.validation_rules import VALIDATION_RULES, VALIDATION_WEIGHTS, VALIDATION_LEVELS
from app.config.438c_rules.chapter_schemas import CHAPTER_SCHEMAS, validate_chapter_content
