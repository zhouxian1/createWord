# 438C质量验证规则定义
# 对章节完整性、要素合规性进行自动校验

VALIDATION_RULES = {
    # 通用规则 - 适用于所有438C文档
    "common": [
        {
            "id": "COM_001",
            "name": "范围章节完整性",
            "type": "completeness",
            "description": "所有438C文档必须包含范围章节",
            "check": "chapter_exists('1')",
            "severity": "error"
        },
        {
            "id": "COM_002",
            "name": "引用文件章节完整性",
            "type": "completeness",
            "description": "所有438C文档必须包含引用文件章节",
            "check": "chapter_exists('2')",
            "severity": "error"
        },
        {
            "id": "COM_003",
            "name": "标识子章节完整性",
            "type": "completeness",
            "description": "范围章节必须包含标识子章节",
            "check": "chapter_exists('1.1')",
            "severity": "error"
        },
        {
            "id": "COM_004",
            "name": "系统概述子章节完整性",
            "type": "completeness",
            "description": "范围章节必须包含系统概述子章节",
            "check": "chapter_exists('1.2')",
            "severity": "error"
        },
        {
            "id": "COM_005",
            "name": "文档概述子章节完整性",
            "type": "completeness",
            "description": "范围章节必须包含文档概述子章节",
            "check": "chapter_exists('1.3')",
            "severity": "warning"
        },
        {
            "id": "COM_006",
            "name": "章节内容非空",
            "type": "completeness",
            "description": "所有必填章节必须有内容",
            "check": "required_chapters_not_empty()",
            "severity": "error"
        },
        {
            "id": "COM_007",
            "name": "标识信息完整性",
            "type": "compliance",
            "description": "标识章节必须包含系统名称、缩写和版本号",
            "check": "chapter_contains('1.1', ['名称', '缩写', '版本'])",
            "severity": "error"
        },
        {
            "id": "COM_008",
            "name": "引用文件非空",
            "type": "compliance",
            "description": "引用文件章节必须列出至少一个引用文件",
            "check": "chapter_min_length('2', 50)",
            "severity": "warning"
        }
    ],

    # SRS专用规则
    "SRS": [
        {
            "id": "SRS_001",
            "name": "功能需求章节完整性",
            "type": "completeness",
            "description": "SRS必须包含功能需求章节",
            "check": "chapter_exists('3.2.1')",
            "severity": "error"
        },
        {
            "id": "SRS_002",
            "name": "性能需求章节完整性",
            "type": "completeness",
            "description": "SRS必须包含性能需求章节",
            "check": "chapter_exists('3.2.2')",
            "severity": "error"
        },
        {
            "id": "SRS_003",
            "name": "接口需求章节完整性",
            "type": "completeness",
            "description": "SRS必须包含接口需求章节",
            "check": "chapter_exists('3.2.3')",
            "severity": "error"
        },
        {
            "id": "SRS_004",
            "name": "安全性需求章节完整性",
            "type": "completeness",
            "description": "SRS必须包含安全性需求章节",
            "check": "chapter_exists('3.2.6')",
            "severity": "error"
        },
        {
            "id": "SRS_005",
            "name": "保密性需求章节完整性",
            "type": "completeness",
            "description": "SRS必须包含保密性需求章节",
            "check": "chapter_exists('3.2.7')",
            "severity": "error"
        },
        {
            "id": "SRS_006",
            "name": "需求可追踪性章节完整性",
            "type": "completeness",
            "description": "SRS必须包含需求可追踪性章节",
            "check": "chapter_exists('3.4')",
            "severity": "error"
        },
        {
            "id": "SRS_007",
            "name": "功能需求要素完整性",
            "type": "compliance",
            "description": "每个功能需求必须包含功能标识、描述、输入、处理和输出",
            "check": "chapter_contains('3.2.1', ['功能标识', '输入', '处理', '输出'])",
            "severity": "error"
        },
        {
            "id": "SRS_008",
            "name": "性能需求量化指标",
            "type": "compliance",
            "description": "性能需求必须包含量化指标",
            "check": "chapter_contains_numbers('3.2.2')",
            "severity": "error"
        },
        {
            "id": "SRS_009",
            "name": "接口需求格式规范",
            "type": "compliance",
            "description": "接口需求必须描述数据格式和通信协议",
            "check": "chapter_contains('3.2.3', ['数据格式', '协议'])",
            "severity": "error"
        },
        {
            "id": "SRS_010",
            "name": "需求编号规范",
            "type": "format",
            "description": "所有需求必须有唯一编号",
            "check": "requirements_numbered()",
            "severity": "warning"
        }
    ],

    # SDD专用规则
    "SDD": [
        {
            "id": "SDD_001",
            "name": "体系结构章节完整性",
            "type": "completeness",
            "description": "SDD必须包含体系结构章节",
            "check": "chapter_exists('4.1')",
            "severity": "error"
        },
        {
            "id": "SDD_002",
            "name": "详细设计章节完整性",
            "type": "completeness",
            "description": "SDD必须包含详细设计章节",
            "check": "chapter_exists('5.1')",
            "severity": "error"
        },
        {
            "id": "SDD_003",
            "name": "需求可追踪性章节完整性",
            "type": "completeness",
            "description": "SDD必须包含需求可追踪性章节",
            "check": "chapter_exists('6')",
            "severity": "error"
        },
        {
            "id": "SDD_004",
            "name": "体系结构要素完整性",
            "type": "compliance",
            "description": "体系结构章节必须包含架构图描述和组件说明",
            "check": "chapter_contains('4.1', ['架构', '组件'])",
            "severity": "error"
        },
        {
            "id": "SDD_005",
            "name": "详细设计要素完整性",
            "type": "compliance",
            "description": "详细设计必须包含模块标识、处理描述和数据结构",
            "check": "chapter_contains('5.1', ['模块', '处理', '数据结构'])",
            "severity": "error"
        }
    ],

    # STR专用规则
    "STR": [
        {
            "id": "STR_001",
            "name": "测试环境章节完整性",
            "type": "completeness",
            "description": "STR必须包含测试环境章节",
            "check": "chapter_exists('3.1')",
            "severity": "error"
        },
        {
            "id": "STR_002",
            "name": "测试结果章节完整性",
            "type": "completeness",
            "description": "STR必须包含测试结果章节",
            "check": "chapter_exists('4')",
            "severity": "error"
        },
        {
            "id": "STR_003",
            "name": "需求覆盖分析完整性",
            "type": "completeness",
            "description": "STR必须包含需求覆盖分析",
            "check": "chapter_exists('4.2')",
            "severity": "error"
        }
    ]
}

# 验证评分权重
VALIDATION_WEIGHTS = {
    "completeness": 0.5,   # 完整性权重
    "compliance": 0.35,    # 合规性权重
    "format": 0.15         # 格式权重
}

# 验证结果等级
VALIDATION_LEVELS = {
    "excellent": {"min_score": 90, "label": "优秀", "color": "green"},
    "good": {"min_score": 75, "label": "良好", "color": "blue"},
    "qualified": {"min_score": 60, "label": "合格", "color": "yellow"},
    "unqualified": {"min_score": 0, "label": "不合格", "color": "red"}
}
