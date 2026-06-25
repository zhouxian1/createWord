# 438C标准文档类型定义
# GJB 438C-2009 军用软件文档编制规范 规定的20个文档

STANDARD_438C_DOCUMENTS = {
    # 软件开发类文档
    "SRS": {
        "code": "SRS",
        "name": "软件需求规格说明",
        "full_name": "Software Requirements Specification",
        "category": "development",
        "complexity": "high",
        "description": "描述软件系统的功能需求、性能需求、接口需求等",
        "chapters": [
            {
                "number": "1",
                "title": "范围",
                "level": 1,
                "required": True,
                "sub_chapters": [
                    {"number": "1.1", "title": "标识", "level": 2, "required": True,
                     "elements": ["系统标识", "系统名称", "系统缩写", "系统版本", "系统标识号"]},
                    {"number": "1.2", "title": "系统概述", "level": 2, "required": True,
                     "elements": ["系统用途", "系统特征", "系统背景"]},
                    {"number": "1.3", "title": "文档概述", "level": 2, "required": True,
                     "elements": ["文档用途", "文档内容概述", "文档读者", "文档约定"]}
                ]
            },
            {
                "number": "2",
                "title": "引用文件",
                "level": 1,
                "required": True,
                "sub_chapters": []
            },
            {
                "number": "3",
                "title": "需求",
                "level": 1,
                "required": True,
                "sub_chapters": [
                    {"number": "3.1", "title": "要求状态和方法", "level": 2, "required": True,
                     "elements": ["要求状态", "验证方法"]},
                    {"number": "3.2", "title": "软件需求", "level": 2, "required": True,
                     "sub_chapters": [
                         {"number": "3.2.1", "title": "功能需求", "level": 3, "required": True,
                          "elements": ["功能标识", "功能描述", "输入", "处理", "输出"]},
                         {"number": "3.2.2", "title": "性能需求", "level": 3, "required": True,
                          "elements": ["性能指标", "响应时间", "吞吐量", "资源利用率"]},
                         {"number": "3.2.3", "title": "接口需求", "level": 3, "required": True,
                          "sub_chapters": [
                              {"number": "3.2.3.1", "title": "外部接口", "level": 4, "required": True,
                               "elements": ["接口标识", "接口类型", "数据格式", "通信协议"]},
                              {"number": "3.2.3.2", "title": "内部接口", "level": 4, "required": True,
                               "elements": ["接口标识", "接口类型", "数据格式"]}
                          ]},
                         {"number": "3.2.4", "title": "数据需求", "level": 3, "required": True,
                          "elements": ["数据实体", "数据属性", "数据关系", "数据量"]},
                         {"number": "3.2.5", "title": "适应性需求", "level": 3, "required": False,
                          "elements": ["安装适应性", "运行适应性", "扩展适应性"]},
                         {"number": "3.2.6", "title": "安全性需求", "level": 3, "required": True,
                          "elements": ["安全等级", "安全策略", "访问控制", "加密要求"]},
                         {"number": "3.2.7", "title": "保密性需求", "level": 3, "required": True,
                          "elements": ["保密等级", "保密措施", "信息分类"]},
                         {"number": "3.2.8", "title": "环境需求", "level": 3, "required": True,
                          "elements": ["硬件环境", "软件环境", "网络环境"]}
                     ]},
                    {"number": "3.3", "title": "合格性规定", "level": 2, "required": True,
                     "elements": ["合格性方法", "合格性标准"]},
                    {"number": "3.4", "title": "需求可追踪性", "level": 2, "required": True,
                     "elements": ["需求追踪矩阵"]}
                ]
            },
            {
                "number": "4",
                "title": "合格性验证",
                "level": 1,
                "required": True,
                "sub_chapters": []
            },
            {
                "number": "5",
                "title": "注",
                "level": 1,
                "required": False,
                "sub_chapters": []
            }
        ]
    },
    "SDD": {
        "code": "SDD",
        "name": "软件设计说明",
        "full_name": "Software Design Description",
        "category": "development",
        "complexity": "high",
        "description": "描述软件系统的体系结构设计和详细设计",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "系统级设计决策", "level": 1, "required": True,
             "sub_chapters": []},
            {"number": "4", "title": "体系结构设计", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "4.1", "title": "体系结构", "level": 2, "required": True,
                  "elements": ["体系结构图", "组件说明", "组件关系"]},
                 {"number": "4.2", "title": "全局数据结构", "level": 2, "required": True,
                  "elements": ["全局变量", "数据文件", "数据库"]},
                 {"number": "4.3", "title": "接口设计", "level": 2, "required": True,
                  "elements": ["外部接口", "内部接口", "接口标识"]}
             ]},
            {"number": "5", "title": "详细设计", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "5.1", "title": "模块详细设计", "level": 2, "required": True,
                  "elements": ["模块标识", "处理描述", "输入输出", "算法", "数据结构"]}
             ]},
            {"number": "6", "title": "需求可追踪性", "level": 1, "required": True, "sub_chapters": []},
            {"number": "7", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SVP": {
        "code": "SVP",
        "name": "软件开发计划",
        "full_name": "Software Development Plan",
        "category": "management",
        "complexity": "high",
        "description": "描述软件开发活动的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "软件开发过程", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "软件开发模型", "level": 2, "required": True},
                 {"number": "3.2", "title": "软件开发方法", "level": 2, "required": True},
                 {"number": "3.3", "title": "软件开发标准", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "软件开发计划", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "4.1", "title": "活动与里程碑", "level": 2, "required": True},
                 {"number": "4.2", "title": "进度", "level": 2, "required": True},
                 {"number": "4.3", "title": "资源估计", "level": 2, "required": True}
             ]},
            {"number": "5", "title": "项目管理", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "5.1", "title": "组织与职责", "level": 2, "required": True},
                 {"number": "5.2", "title": "风险管理", "level": 2, "required": True},
                 {"number": "5.3", "title": "配置管理", "level": 2, "required": True},
                 {"number": "5.4", "title": "质量保证", "level": 2, "required": True}
             ]},
            {"number": "6", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SVVP": {
        "code": "SVVP",
        "name": "软件验证与确认计划",
        "full_name": "Software Verification and Validation Plan",
        "category": "verification",
        "complexity": "high",
        "description": "描述软件验证与确认活动的计划",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "验证与确认", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "组织与职责", "level": 2, "required": True},
                 {"number": "3.2", "title": "验证与确认活动", "level": 2, "required": True},
                 {"number": "3.3", "title": "工具与技术", "level": 2, "required": True},
                 {"number": "3.4", "title": "记录", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "进度", "level": 1, "required": True, "sub_chapters": []},
            {"number": "5", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "STR": {
        "code": "STR",
        "name": "软件测试报告",
        "full_name": "Software Test Report",
        "category": "testing",
        "complexity": "high",
        "description": "描述软件测试的执行情况和结果",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "测试概述", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "测试环境", "level": 2, "required": True},
                 {"number": "3.2", "title": "测试结果概述", "level": 2, "required": True},
                 {"number": "3.3", "title": "测试完整性与充分性", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "测试结果", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "4.1", "title": "测试用例执行结果", "level": 2, "required": True},
                 {"number": "4.2", "title": "需求覆盖分析", "level": 2, "required": True},
                 {"number": "4.3", "title": "偏差与异常", "level": 2, "required": True}
             ]},
            {"number": "5", "title": "测试评价", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "5.1", "title": "测试结论", "level": 2, "required": True},
                 {"number": "5.2", "title": "改进建议", "level": 2, "required": False}
             ]},
            {"number": "6", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "STP": {
        "code": "STP",
        "name": "软件测试计划",
        "full_name": "Software Test Plan",
        "category": "testing",
        "complexity": "medium",
        "description": "描述软件测试活动的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "测试", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "测试环境", "level": 2, "required": True},
                 {"number": "3.2", "title": "测试类型", "level": 2, "required": True},
                 {"number": "3.3", "title": "测试项", "level": 2, "required": True},
                 {"number": "3.4", "title": "测试进度", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SCS": {
        "code": "SCS",
        "name": "软件配置管理计划",
        "full_name": "Software Configuration Management Plan",
        "category": "management",
        "complexity": "medium",
        "description": "描述软件配置管理的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "配置管理", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "组织与职责", "level": 2, "required": True},
                 {"number": "3.2", "title": "配置标识", "level": 2, "required": True},
                 {"number": "3.3", "title": "配置控制", "level": 2, "required": True},
                 {"number": "3.4", "title": "配置状态记录", "level": 2, "required": True},
                 {"number": "3.5", "title": "配置审核", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SQAP": {
        "code": "SQAP",
        "name": "软件质量保证计划",
        "full_name": "Software Quality Assurance Plan",
        "category": "management",
        "complexity": "medium",
        "description": "描述软件质量保证的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "质量保证", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "组织与职责", "level": 2, "required": True},
                 {"number": "3.2", "title": "质量保证活动", "level": 2, "required": True},
                 {"number": "3.3", "title": "工具与技术", "level": 2, "required": True},
                 {"number": "3.4", "title": "记录", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SDF": {
        "code": "SDF",
        "name": "软件开发文件",
        "full_name": "Software Development File",
        "category": "development",
        "complexity": "medium",
        "description": "记录软件开发过程中的设计决策和技术细节",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "开发过程记录", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "2.1", "title": "设计决策", "level": 2, "required": True},
                 {"number": "2.2", "title": "技术方案", "level": 2, "required": True},
                 {"number": "2.3", "title": "问题与解决", "level": 2, "required": True}
             ]},
            {"number": "3", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SPS": {
        "code": "SPS",
        "name": "软件产品规格说明",
        "full_name": "Software Product Specification",
        "category": "development",
        "complexity": "high",
        "description": "描述软件产品的完整规格",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "需求规格", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "功能需求", "level": 2, "required": True},
                 {"number": "3.2", "title": "性能需求", "level": 2, "required": True},
                 {"number": "3.3", "title": "接口需求", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "设计规格", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "4.1", "title": "体系结构设计", "level": 2, "required": True},
                 {"number": "4.2", "title": "详细设计", "level": 2, "required": True}
             ]},
            {"number": "5", "title": "源代码", "level": 1, "required": True, "sub_chapters": []},
            {"number": "6", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SVD": {
        "code": "SVD",
        "name": "软件版本说明",
        "full_name": "Software Version Description",
        "category": "configuration",
        "complexity": "medium",
        "description": "描述软件版本的变更内容",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "版本说明", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "版本标识", "level": 2, "required": True},
                 {"number": "3.2", "title": "变更内容", "level": 2, "required": True},
                 {"number": "3.3", "title": "已知问题", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SIP": {
        "code": "SIP",
        "name": "软件安装计划",
        "full_name": "Software Installation Plan",
        "category": "deployment",
        "complexity": "medium",
        "description": "描述软件安装的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "安装", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "安装环境", "level": 2, "required": True},
                 {"number": "3.2", "title": "安装步骤", "level": 2, "required": True},
                 {"number": "3.3", "title": "安装验证", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SIS": {
        "code": "SIS",
        "name": "软件安装说明",
        "full_name": "Software Installation Instructions",
        "category": "deployment",
        "complexity": "medium",
        "description": "描述软件安装的详细步骤",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "安装说明", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "安装准备", "level": 2, "required": True},
                 {"number": "3.2", "title": "安装步骤", "level": 2, "required": True},
                 {"number": "3.3", "title": "安装验证", "level": 2, "required": True},
                 {"number": "3.4", "title": "回退步骤", "level": 2, "required": False}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SUM": {
        "code": "SUM",
        "name": "软件用户手册",
        "full_name": "Software User Manual",
        "category": "user",
        "complexity": "high",
        "description": "描述软件的使用方法",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "操作规程", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "安装与初始化", "level": 2, "required": True},
                 {"number": "3.2", "title": "操作说明", "level": 2, "required": True},
                 {"number": "3.3", "title": "错误处理", "level": 2, "required": True},
                 {"number": "3.4", "title": "帮助信息", "level": 2, "required": False}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SCOM": {
        "code": "SCOM",
        "name": "软件操作员手册",
        "full_name": "Software Operator Manual",
        "category": "user",
        "complexity": "medium",
        "description": "描述软件操作员的操作规程",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "操作规程", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "系统启动与关闭", "level": 2, "required": True},
                 {"number": "3.2", "title": "操作流程", "level": 2, "required": True},
                 {"number": "3.3", "title": "故障处理", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SPMP": {
        "code": "SPMP",
        "name": "软件编程手册",
        "full_name": "Software Programming Manual",
        "category": "development",
        "complexity": "medium",
        "description": "描述软件编程的规范和方法",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "编程环境", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "开发环境", "level": 2, "required": True},
                 {"number": "3.2", "title": "编程规范", "level": 2, "required": True},
                 {"number": "3.3", "title": "编译与构建", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SCSR": {
        "code": "SCSR",
        "name": "软件配置状态报告",
        "full_name": "Software Configuration Status Report",
        "category": "configuration",
        "complexity": "medium",
        "description": "描述软件配置的状态报告",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "配置状态", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "配置项清单", "level": 2, "required": True},
                 {"number": "3.2", "title": "变更记录", "level": 2, "required": True},
                 {"number": "3.3", "title": "基线状态", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "STRP": {
        "code": "STRP",
        "name": "软件移交计划",
        "full_name": "Software Transition Plan",
        "category": "deployment",
        "complexity": "medium",
        "description": "描述软件移交的计划安排",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True},
                 {"number": "1.3", "title": "文档概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "引用文件", "level": 1, "required": True, "sub_chapters": []},
            {"number": "3", "title": "移交", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "3.1", "title": "移交准备", "level": 2, "required": True},
                 {"number": "3.2", "title": "移交内容", "level": 2, "required": True},
                 {"number": "3.3", "title": "移交验证", "level": 2, "required": True}
             ]},
            {"number": "4", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    },
    "SDL": {
        "code": "SDL",
        "name": "软件设计日志",
        "full_name": "Software Design Log",
        "category": "development",
        "complexity": "low",
        "description": "记录软件设计过程中的日志",
        "chapters": [
            {"number": "1", "title": "范围", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "1.1", "title": "标识", "level": 2, "required": True},
                 {"number": "1.2", "title": "系统概述", "level": 2, "required": True}
             ]},
            {"number": "2", "title": "设计日志", "level": 1, "required": True,
             "sub_chapters": [
                 {"number": "2.1", "title": "设计活动记录", "level": 2, "required": True},
                 {"number": "2.2", "title": "设计评审记录", "level": 2, "required": True}
             ]},
            {"number": "3", "title": "注", "level": 1, "required": False, "sub_chapters": []}
        ]
    }
}

# 文档分类
DOCUMENT_CATEGORIES = {
    "development": {"name": "软件开发类", "codes": ["SRS", "SDD", "SDF", "SPS", "SPMP", "SDL"]},
    "management": {"name": "管理类", "codes": ["SVP", "SCS", "SQAP"]},
    "testing": {"name": "测试类", "codes": ["SVVP", "STR", "STP"]},
    "configuration": {"name": "配置管理类", "codes": ["SVD", "SCSR"]},
    "deployment": {"name": "部署类", "codes": ["SIP", "SIS", "STRP"]},
    "user": {"name": "用户类", "codes": ["SUM", "SCOM"]}
}

# 复杂度分级
COMPLEXITY_LEVELS = {
    "high": {"name": "高复杂度", "min_chapters": 10, "description": "技术类核心文档，章节结构繁琐"},
    "medium": {"name": "中复杂度", "min_chapters": 5, "description": "管理或辅助类文档，章节结构适中"},
    "low": {"name": "低复杂度", "min_chapters": 3, "description": "记录类文档，章节结构简单"}
}
