# API 接口文档

## 1. 基本信息

- 后端地址：`http://localhost:5000`
- API 前缀：`/api`
- JSON 请求头：`Content-Type: application/json`
- 文件上传：`multipart/form-data`
- 前端开发代理：`http://localhost:3000/api -> http://localhost:5000/api`

通用错误格式：

```json
{
  "error": "错误描述"
}
```

## 2. 项目管理 `/api/project`

### GET `/projects`

获取项目列表。

响应示例：

```json
{
  "items": [
    {
      "id": 1,
      "name": "438C文档项目",
      "system_name": "测试系统",
      "system_version": "",
      "organization": "中科星图",
      "description": "",
      "security_level": "内部",
      "document_count": 1,
      "knowledge_base_count": 2
    }
  ],
  "total": 1
}
```

### POST `/projects`

创建项目。

```json
{
  "name": "438C文档项目",
  "system_name": "测试系统",
  "system_version": "V1.0",
  "organization": "中科星图",
  "description": "项目说明",
  "security_level": "内部"
}
```

### GET `/projects/{project_id}`

获取项目详情。

### PUT `/projects/{project_id}`

更新项目。

### DELETE `/projects/{project_id}`

删除项目。

## 3. 知识库 `/api/knowledge`

### GET `/bases`

获取知识库列表。支持查询参数，例如 `project_id`。

### POST `/bases`

创建知识库。

```json
{
  "name": "438C标准知识库",
  "description": "标准文档和模板",
  "project_id": 1,
  "kb_type": "438c_standard",
  "security_level": "内部",
  "tags": ["438C", "标准"]
}
```

### GET `/bases/{kb_id}`

获取知识库详情。

### PUT `/bases/{kb_id}`

更新知识库。

### DELETE `/bases/{kb_id}`

删除知识库。

### POST `/bases/{kb_id}/upload`

上传文件。请求类型为 `multipart/form-data`。

字段：

- `files`：一个或多个文件。

### POST `/bases/{kb_id}/batch-import`

按文件路径批量导入。

```json
{
  "file_paths": [
    "F:/geovis/cerateWord/438c/01-软件开发计划模板-V1.0.1-wn.docx"
  ],
  "tags": ["438C", "模板"]
}
```

### POST `/bases/{kb_id}/api-import`

从外部 API 导入内容。

```json
{
  "api_url": "https://example.com/api/items",
  "api_method": "GET",
  "api_headers": {
    "Authorization": "Bearer token"
  },
  "api_body": {},
  "title_field": "title",
  "content_field": "content"
}
```

### POST `/bases/{kb_id}/incremental-import`

增量导入文件路径。

### GET `/bases/{kb_id}/files`

获取知识库文件列表。

### GET `/files/{file_id}`

获取文件详情。

### DELETE `/files/{file_id}`

删除文件。

### GET `/files/{file_id}/preview`

预览解析后的文件内容。

### PUT `/files/{file_id}/edit`

编辑文件正文。

```json
{
  "content": "更新后的正文内容"
}
```

### POST `/files/{file_id}/review`

审核文件。

```json
{
  "action": "approve",
  "reviewer": "admin",
  "comments": "审核通过"
}
```

### POST `/files/{file_id}/rollback`

回滚文件版本。

```json
{
  "version_id": 1
}
```

### GET `/files/{file_id}/versions`

获取文件版本历史。

### GET `/review-records`

获取审核记录。

### POST `/bases/{kb_id}/search`

搜索知识库。

```json
{
  "query": "软件需求规格说明需要哪些章节",
  "top_k": 5,
  "use_rerank": false
}
```

响应关键字段：

- `results[].content`
- `results[].score`
- `results[].metadata`
- `results[].source_trace`

### GET `/graph`

获取知识图谱。

查询参数：

- `entity_name`：可选，按实体名称获取子图。
- `depth`：可选，默认 `2`。

## 4. 438C 标准 `/api/438c`

### GET `/document-types`

获取 438C 文档类型列表。

### GET `/document-types/{code}`

获取文档类型详情，例如 `SRS`、`SDD`。

### GET `/document-types/{code}/structure`

获取文档章节结构。

### GET `/categories`

获取文档分类列表。

### GET `/complexity-levels`

获取复杂度等级。

### POST `/import`

导入 438C 标准模板数据。

## 5. 文档生成 `/api/generation`

### GET `/documents`

获取文档列表。

### POST `/documents`

创建文档。

```json
{
  "project_id": 1,
  "doc_type": "SRS",
  "generation_mode": "full"
}
```

### GET `/documents/{doc_id}`

获取文档详情。

### DELETE `/documents/{doc_id}`

删除文档。

### POST `/documents/{doc_id}/generate/full`

整篇生成文档。

```json
{}
```

### POST `/documents/{doc_id}/generate/chapter`

按章节生成。

```json
{
  "chapter_ids": [1, 2, 3]
}
```

### POST `/generate/from-code`

从代码生成文档内容。

```json
{
  "project_id": 1,
  "doc_type": "SDD",
  "code_files": [
    {
      "filename": "main.py",
      "content": "print('hello')",
      "language": "python"
    }
  ]
}
```

### GET `/documents/{doc_id}/chapters`

获取文档章节列表。

### GET `/chapters/{chapter_id}`

获取章节详情。

### PUT `/chapters/{chapter_id}`

更新章节内容。

```json
{
  "content": "章节正文",
  "prompt_template": "自定义提示词"
}
```

### GET `/tasks/{task_id}`

获取生成任务状态。

### POST `/documents/{doc_id}/export`

导出文档，返回下载信息。

### POST `/upload-code`

上传代码文件，用于后续分析和生成。请求类型为 `multipart/form-data`。

## 6. 质量验证 `/api/validation`

### POST `/documents/{doc_id}`

执行质量验证。

### GET `/documents/{doc_id}/result`

获取验证结果。

### GET `/rules`

获取验证规则。

### POST `/rules`

新增验证规则。

```json
{
  "doc_type": "SRS",
  "rule_name": "必须包含范围章节",
  "rule_type": "structure",
  "severity": "high",
  "rule_description": "检查文档结构完整性",
  "check_expression": "1 范围"
}
```

### PUT `/rules/{rule_id}`

更新规则。

### DELETE `/rules/{rule_id}`

删除规则。

### GET `/levels`

获取验证等级定义。

## 7. 文档合稿 `/api/merge`

### GET `/tasks`

获取合稿任务列表。

### POST `/tasks`

创建合稿任务。

```json
{
  "name": "项目交付合稿",
  "source_documents": [1, 2],
  "merge_strategy": "by_structure",
  "output_format": "docx"
}
```

### POST `/tasks/{task_id}/execute`

执行合稿。

### GET `/tasks/{task_id}`

获取合稿任务详情。

### DELETE `/tasks/{task_id}`

删除合稿任务。

### GET `/download/{filename}`

按文件名下载合稿结果。

### GET `/documents/{doc_id}/download`

按文档 ID 下载导出文档。

## 8. 智能问答 `/api/question`

### POST `/ask`

通用知识库问答。

```json
{
  "question": "SRS 文档有哪些必选章节？",
  "knowledge_base_id": 1,
  "top_k": 5
}
```

响应示例：

```json
{
  "question": "SRS 文档有哪些必选章节？",
  "answer": "回答内容",
  "context_sources": 3,
  "source_traces": [],
  "status": "success"
}
```

### POST `/ask-438c`

438C 专项问答。该接口会调用本地 Ollama `qwen2.5:7b`。

```json
{
  "question": "请用一句话说明438C是什么"
}
```

响应示例：

```json
{
  "question": "请用一句话说明438C是什么",
  "answer": "GJB 438C 是军用软件文档编制规范，用于指导软件研制过程中相关文档的编写和交付。",
  "source_traces": [
    {
      "source_type": "438c_standard",
      "confidence": 1.0
    }
  ],
  "status": "success"
}
```

## 9. 接口验证清单

```bash
curl http://localhost:5000/api/project/projects
curl http://localhost:5000/api/438c/document-types
curl http://localhost:5000/api/knowledge/graph
curl -X POST http://localhost:5000/api/question/ask-438c \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"请用一句话说明438C是什么\"}"
```
