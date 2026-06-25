"""438C章节JSON Schema约束定义"""
import json

# 每种438C文档类型的章节Schema约束
CHAPTER_SCHEMAS = {
    "SRS": {
        "1": {
            "title": "范围",
            "required": True,
            "min_length": 100,
            "required_elements": ["标识", "系统概述", "文档概述"],
            "sub_chapter_schemas": {
                "1.1": {
                    "title": "标识",
                    "required": True,
                    "min_length": 50,
                    "required_fields": [
                        {"name": "系统标识", "type": "string", "required": True},
                        {"name": "系统名称", "type": "string", "required": True},
                        {"name": "系统缩写", "type": "string", "required": True},
                        {"name": "系统版本", "type": "string", "required": True},
                        {"name": "系统标识号", "type": "string", "required": True}
                    ]
                },
                "1.2": {
                    "title": "系统概述",
                    "required": True,
                    "min_length": 100,
                    "required_fields": [
                        {"name": "系统用途", "type": "string", "required": True},
                        {"name": "系统特征", "type": "string", "required": True},
                        {"name": "系统背景", "type": "string", "required": True}
                    ]
                },
                "1.3": {
                    "title": "文档概述",
                    "required": True,
                    "min_length": 50,
                    "required_fields": [
                        {"name": "文档用途", "type": "string", "required": True},
                        {"name": "文档内容概述", "type": "string", "required": True},
                        {"name": "文档读者", "type": "string", "required": True},
                        {"name": "文档约定", "type": "string", "required": False}
                    ]
                }
            }
        },
        "2": {
            "title": "引用文件",
            "required": True,
            "min_length": 30,
            "required_elements": ["引用文件列表"],
            "format_rules": ["每个引用文件需包含文件编号和文件名称"]
        },
        "3": {
            "title": "需求",
            "required": True,
            "min_length": 500,
            "required_elements": ["要求状态和方法", "软件需求", "合格性规定", "需求可追踪性"],
            "sub_chapter_schemas": {
                "3.2": {
                    "title": "软件需求",
                    "required": True,
                    "min_length": 300,
                    "required_elements": ["功能需求", "性能需求", "接口需求", "数据需求",
                                          "安全性需求", "保密性需求", "环境需求"],
                    "sub_chapter_schemas": {
                        "3.2.1": {
                            "title": "功能需求",
                            "required": True,
                            "min_length": 200,
                            "required_fields": [
                                {"name": "功能标识", "type": "string", "required": True},
                                {"name": "功能描述", "type": "string", "required": True},
                                {"name": "输入", "type": "string", "required": True},
                                {"name": "处理", "type": "string", "required": True},
                                {"name": "输出", "type": "string", "required": True}
                            ]
                        },
                        "3.2.2": {
                            "title": "性能需求",
                            "required": True,
                            "min_length": 100,
                            "required_fields": [
                                {"name": "性能指标", "type": "string", "required": True},
                                {"name": "响应时间", "type": "string", "required": True},
                                {"name": "吞吐量", "type": "string", "required": False},
                                {"name": "资源利用率", "type": "string", "required": False}
                            ]
                        },
                        "3.2.3": {
                            "title": "接口需求",
                            "required": True,
                            "min_length": 100,
                            "required_fields": [
                                {"name": "接口标识", "type": "string", "required": True},
                                {"name": "接口类型", "type": "string", "required": True},
                                {"name": "数据格式", "type": "string", "required": True},
                                {"name": "通信协议", "type": "string", "required": True}
                            ]
                        },
                        "3.2.6": {
                            "title": "安全性需求",
                            "required": True,
                            "min_length": 80,
                            "required_fields": [
                                {"name": "安全等级", "type": "string", "required": True},
                                {"name": "安全策略", "type": "string", "required": True},
                                {"name": "访问控制", "type": "string", "required": True},
                                {"name": "加密要求", "type": "string", "required": False}
                            ]
                        }
                    }
                }
            }
        },
        "4": {
            "title": "合格性验证",
            "required": True,
            "min_length": 100,
            "required_elements": ["合格性验证方法", "合格性验证标准"]
        },
        "5": {
            "title": "注",
            "required": False,
            "min_length": 0
        }
    },
    "SDD": {
        "1": {
            "title": "范围",
            "required": True,
            "min_length": 100,
            "required_elements": ["标识", "系统概述", "文档概述"]
        },
        "2": {
            "title": "引用文件",
            "required": True,
            "min_length": 30
        },
        "3": {
            "title": "系统级设计决策",
            "required": True,
            "min_length": 200,
            "required_elements": ["设计决策描述", "决策理由", "替代方案"],
            "required_fields": [
                {"name": "设计决策", "type": "string", "required": True},
                {"name": "决策理由", "type": "string", "required": True}
            ]
        },
        "4": {
            "title": "体系结构设计",
            "required": True,
            "min_length": 300,
            "required_elements": ["体系结构", "全局数据结构", "接口设计"],
            "sub_chapter_schemas": {
                "4.1": {
                    "title": "体系结构",
                    "required": True,
                    "min_length": 200,
                    "required_fields": [
                        {"name": "体系结构图", "type": "figure", "required": True},
                        {"name": "组件说明", "type": "string", "required": True},
                        {"name": "组件关系", "type": "string", "required": True}
                    ]
                },
                "4.3": {
                    "title": "接口设计",
                    "required": True,
                    "min_length": 150,
                    "required_fields": [
                        {"name": "外部接口", "type": "string", "required": True},
                        {"name": "内部接口", "type": "string", "required": True},
                        {"name": "接口标识", "type": "string", "required": True}
                    ]
                }
            }
        },
        "5": {
            "title": "详细设计",
            "required": True,
            "min_length": 300,
            "required_elements": ["模块详细设计"],
            "sub_chapter_schemas": {
                "5.1": {
                    "title": "模块详细设计",
                    "required": True,
                    "min_length": 200,
                    "required_fields": [
                        {"name": "模块标识", "type": "string", "required": True},
                        {"name": "处理描述", "type": "string", "required": True},
                        {"name": "输入输出", "type": "string", "required": True},
                        {"name": "算法", "type": "string", "required": False},
                        {"name": "数据结构", "type": "string", "required": True}
                    ]
                }
            }
        },
        "6": {
            "title": "需求可追踪性",
            "required": True,
            "min_length": 50,
            "required_elements": ["需求追踪矩阵"],
            "format_rules": ["需提供需求到设计的追踪关系表"]
        },
        "7": {
            "title": "注",
            "required": False,
            "min_length": 0
        }
    }
}

# 通用章节Schema模板（用于未单独定义的文档类型）
DEFAULT_CHAPTER_SCHEMA = {
    "required": True,
    "min_length": 50,
    "required_elements": [],
    "required_fields": [],
    "format_rules": []
}


def get_chapter_schema(doc_type: str, chapter_number: str) -> dict:
    """获取指定文档类型和章节的Schema约束"""
    doc_schemas = CHAPTER_SCHEMAS.get(doc_type, {})
    schema = doc_schemas.get(chapter_number)
    if schema:
        return schema

    # 尝试在子章节Schema中查找
    for ch_num, ch_schema in doc_schemas.items():
        if 'sub_chapter_schemas' in ch_schema:
            sub_schemas = ch_schema['sub_chapter_schemas']
            if chapter_number in sub_schemas:
                return sub_schemas[chapter_number]
            # 继续在更深层级查找
            for sub_num, sub_schema in sub_schemas.items():
                if 'sub_chapter_schemas' in sub_schema and chapter_number in sub_schema['sub_chapter_schemas']:
                    return sub_schema['sub_chapter_schemas'][chapter_number]

    return DEFAULT_CHAPTER_SCHEMA


def validate_chapter_content(doc_type: str, chapter_number: str, content: str) -> dict:
    """根据Schema验证章节内容"""
    schema = get_chapter_schema(doc_type, chapter_number)
    errors = []
    warnings = []

    # 检查必选章节
    if schema.get('required') and (not content or not content.strip()):
        errors.append(f"必选章节内容为空")
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'schema': schema}

    if not content:
        return {'valid': True, 'errors': [], 'warnings': [], 'schema': schema}

    # 检查最小长度
    min_length = schema.get('min_length', 0)
    if min_length > 0 and len(content) < min_length:
        warnings.append(f"章节内容长度({len(content)})低于建议最小长度({min_length})")

    # 检查必填要素
    required_elements = schema.get('required_elements', [])
    missing_elements = []
    for elem in required_elements:
        if elem not in content:
            missing_elements.append(elem)
    if missing_elements:
        errors.append(f"缺少必填要素: {', '.join(missing_elements)}")

    # 检查必填字段
    required_fields = schema.get('required_fields', [])
    missing_fields = []
    for field in required_fields:
        if field.get('required') and field['name'] not in content:
            missing_fields.append(field['name'])
    if missing_fields:
        errors.append(f"缺少必填字段: {', '.join(missing_fields)}")

    # 检查格式规则
    format_rules = schema.get('format_rules', [])
    for rule in format_rules:
        # 简单的格式规则检查（可扩展）
        pass

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'schema': schema,
        'completeness': round(1 - len(errors) / max(len(required_elements) + len(required_fields), 1), 4)
    }


def export_all_schemas() -> dict:
    """导出所有Schema定义"""
    return CHAPTER_SCHEMAS
