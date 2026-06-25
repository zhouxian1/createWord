# 438C 文档生成与知识图谱系统 API 接口文档

## 1. 基本信息

- 基础路径：`/api`
- 数据格式：`application/json`
- 文件上传：`multipart/form-data`
- 前端默认代理：`http://localhost:3000 -> http://localhost:5000`

## 2. 项目管理

### `GET /project/projects`

获取项目列表。

### `POST /project/projects`

创建项目。

请求示例：

```json
{
  "name": "某装备软件项目",
  "system_name": "火控系统",
  "organization": "某研究所"
}
```

### `GET /project/projects/{project_id}`

获取项目详情。

### `PUT /project/projects/{project_id}`

更新项目。

### `DELETE /project/projects/{project_id}`

删除项目。

## 3. 知识库管理

### `GET /knowledge/bases`

获取知识库列表。

### `POST /knowledge/bases`

创建知识库。

### `GET /knowledge/bases/{kb_id}`

获取知识库详情。

### `PUT /knowledge/bases/{kb_id}`

更新知识库。

### `DELETE /knowledge/bases/{kb_id}`

删除知识库。

### `POST /knowledge/bases/{kb_id}/upload`

上传文件到知识库。

表单字段：

- `files`：支持多文件

### `POST /knowledge/bases/{kb_id}/batch-import`

按目录批量导入。

请求示例：

```json
{
  "directory_path": "F:/dataset/docs",
  "recursive": true
}
```

### `POST /knowledge/bases/{kb_id}/api-import`

从外部接口导入知识。

请求示例：

```json
{
  "api_url": "https://example.com/api/items",
  "api_method": "GET",
  "api_headers": {
    "Authorization": "Bearer xxx"
  },
  "api_body": {},
  "title_field": "title",
  "content_field": "content"
}
```

### `POST /knowledge/bases/{kb_id}/incremental-import`

增量导入知识库。

### `GET /knowledge/bases/{kb_id}/files`

获取知识库文件列表。

### `GET /knowledge/files/{file_id}`

获取文件详情。

### `GET /knowledge/files/{file_id}/preview`

预览解析后的文件内容。

### `PUT /knowledge/files/{file_id}/edit`

编辑文件正文内容。

### `DELETE /knowledge/files/{file_id}`

删除文件。

### `POST /knowledge/files/{file_id}/review`

执行审核动作。

### `POST /knowledge/files/{file_id}/rollback`

回滚文件版本。

### `GET /knowledge/files/{file_id}/versions`

获取版本记录。

### `GET /knowledge/review-records`

获取审核记录。

### `POST /knowledge/bases/{kb_id}/search`

语义搜索知识库。

请求示例：

```json
{
  "query": "SRS 文档需要哪些章节",
  "top_k": 5
}
```

响应关键字段：

- `results[].content`
- `results[].score`
- `results[].source_file`
- `results[].chapter_title`
- `results[].entity_name`

## 4. 知识图谱

### `GET /knowledge/graph`

获取知识图谱全量数据，默认从本地内存图导出，同时返回 Neo4j 存储状态。

查询参数：

- `entity_name`：可选，按实体名称获取关联子图
- `depth`：可选，默认 `2`

响应示例：

```json
{
  "entities": {
    "document_SRS_1234": {
      "type": "document",
      "name": "软件需求规格说明",
      "properties": {
        "code": "SRS"
      }
    }
  },
  "relations": [
    {
      "source": "document_SRS_1234",
      "type": "contains",
      "target": "chapter_1_5678",
      "properties": {}
    }
  ],
  "stats": {
    "total_entities": 119,
    "total_relations": 297,
    "storage": {
      "local_json": true,
      "neo4j": {
        "enabled": true,
        "connected": true,
        "entity_count": 119,
        "relation_count": 297
      }
    }
  }
}
```

## 5. 438C 标准

### `GET /438c/document-types`

获取文档类型列表。

### `GET /438c/document-types/{code}`

获取文档类型详情。

### `GET /438c/document-types/{code}/structure`

获取文档章节结构。

### `GET /438c/categories`

获取文档分类列表。

### `GET /438c/complexity-levels`

获取复杂度等级。

### `POST /438c/import`

导入 438C 标准模板数据。

## 6. 文档生成

### `GET /generation/documents`

获取文档列表。

### `POST /generation/documents`

创建文档。

### `GET /generation/documents/{doc_id}`

获取文档详情。

### `DELETE /generation/documents/{doc_id}`

删除文档。

### `POST /generation/documents/{doc_id}/generate/full`

整篇生成文档。

### `POST /generation/documents/{doc_id}/generate/chapter`

生成单章节内容。

### `POST /generation/generate/from-code`

从代码生成文档章节。

### `GET /generation/documents/{doc_id}/chapters`

获取章节列表。

### `GET /generation/chapters/{chapter_id}`

获取章节详情。

### `PUT /generation/chapters/{chapter_id}`

更新章节内容。

### `GET /generation/tasks/{task_id}`

获取生成任务状态。

### `POST /generation/documents/{doc_id}/export`

导出文档，返回下载地址。

响应示例：

```json
{
  "file_path": "F:/.../generated/xxx.docx",
  "filename": "软件需求规格说明.docx",
  "download_url": "/api/merge/documents/12/download"
}
```

### `POST /generation/upload-code`

上传代码包用于生成分析。

## 7. 质量验证

### `POST /validation/documents/{doc_id}`

执行质量验证。

### `GET /validation/documents/{doc_id}/result`

获取验证结果。

### `GET /validation/rules`

获取规则列表。

### `POST /validation/rules`

新增规则。

### `PUT /validation/rules/{rule_id}`

更新规则。

### `DELETE /validation/rules/{rule_id}`

删除规则。

### `GET /validation/levels`

获取等级定义。

## 8. 文档合稿

### `GET /merge/tasks`

获取合稿任务列表。

### `POST /merge/tasks`

创建合稿任务。

### `POST /merge/tasks/{task_id}/execute`

执行合稿。

### `GET /merge/tasks/{task_id}`

获取任务详情。

### `DELETE /merge/tasks/{task_id}`

删除合稿任务。

### `GET /merge/download/{filename}`

按文件名下载合稿结果。

### `GET /merge/documents/{doc_id}/download`

按文档 ID 下载导出文档。

## 9. 智能问答

### `POST /question/ask`

通用问答。

请求示例：

```json
{
  "question": "SRS 文档有哪些必选章节？",
  "knowledge_base_id": 1,
  "top_k": 5
}
```

### `POST /question/ask-438c`

438C 专项问答。

## 10. 错误响应

统一错误格式：

```json
{
  "error": "错误描述"
}
```

常见状态码：

- `200`：成功
- `400`：参数错误
- `404`：资源不存在
- `500`：服务内部错误
