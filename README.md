# 438C 文档生成与知识图谱系统

面向 GJB 438C 军用软件文档编制场景的智能文档工程平台，支持项目管理、知识库构建、438C 标准浏览、文档生成、质量验证、文档合稿、知识图谱和智能问答等能力。

系统采用前后端分离架构：

- 后端：`Flask 3 + SQLAlchemy`，提供 REST API 和核心业务服务。
- 前端：`Vue 3 + Vite + Element Plus`，提供管理与交互界面。
- AI：默认对接离线 Ollama 服务，模型为 `qwen2.5:7b`。
- 知识工程：支持 ChromaDB、倒排索引、知识图谱、Neo4j、MinIO 等组件；外部组件不可用时，部分功能可回退到本地存储。

## 核心能力

- 项目管理：维护项目、系统名称、版本、编制单位等基础信息。
- 知识库管理：支持上传、批量导入、API 导入、增量导入、审核、版本和检索。
- 438C 标准：内置 438C 文档类型、章节结构、复杂度、提示词和验证规则。
- 文档生成：支持整篇生成、按章节生成、基于代码生成和导出。
- 质量验证：检查章节完整性、要素合规性、规则命中和验证等级。
- 文档合稿：支持多文档合并、排版和下载。
- 知识图谱：构建“文档-章节-要素-术语-代码实体”的关系网络。
- 智能问答：支持通用知识库问答和 438C 专项问答，返回答案与溯源信息。

## 当前模型配置

后端默认使用 Ollama 原生接口：

```text
Ollama 地址：http://192.168.31.245:11434
生成接口：http://192.168.31.245:11434/api/generate
模型名称：qwen2.5:7b
请求方式：POST JSON，stream=false
```

可用以下命令验证模型服务：

```bash
curl http://192.168.31.245:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "请用一句话说明你已正常运行",
  "stream": false
}'
```

后端环境变量建议：

```env
LLM_PROVIDER=ollama
OLLAMA_API_BASE=http://192.168.31.245:11434
OLLAMA_MODEL=qwen2.5:7b
```

说明：代码中的 `OllamaService` 会优先读取 `OLLAMA_API_BASE` 和 `OLLAMA_MODEL`，避免被旧的 `LLM_API_BASE=https://dashscope...` 配置污染。

## 本地启动

### 1. 启动后端

```powershell
cd backend
python run.py
```

默认地址：

```text
http://localhost:5000
```

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

默认地址：

```text
http://localhost:3000
```

前端开发服务会把 `/api` 代理到 `http://localhost:5000`。

### 3. 常用验证命令

```powershell
# 后端项目接口
Invoke-RestMethod http://127.0.0.1:5000/api/project/projects

# 前端代理到后端
Invoke-RestMethod http://127.0.0.1:3000/api/project/projects

# 438C 专项问答
$body = @{ question = "请用一句话说明438C是什么" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/api/question/ask-438c -Method Post -Body $body -ContentType "application/json"
```

## 目录结构

```text
cerateWord/
├─ 438c/                         # 438C 模板样例
├─ backend/                      # Flask 后端
│  ├─ app/
│  │  ├─ api/                    # REST API 蓝图
│  │  ├─ config/                 # 配置、438C 标准、提示词、规则
│  │  ├─ models/                 # SQLAlchemy 数据模型
│  │  └─ services/               # 解析、索引、图谱、生成、问答、合稿等服务
│  ├─ data/                      # 本地数据、上传文件、向量库、图谱缓存
│  ├─ requirements.txt
│  └─ run.py
├─ frontend/                     # Vue 前端
│  ├─ src/
│  │  ├─ api/                    # Axios API 封装
│  │  ├─ components/             # 通用组件
│  │  ├─ router/                 # 路由配置
│  │  ├─ store/                  # Pinia 状态
│  │  └─ views/                  # 业务页面
│  ├─ package.json
│  └─ vite.config.js
├─ docs/                         # 项目文档
├─ docker-compose.yml
└─ nginx.conf
```

## 主要页面

- `/dashboard`：工作台
- `/projects`：项目管理
- `/knowledge`：知识库列表
- `/knowledge/:id`：知识库详情
- `/knowledge-graph`：知识图谱
- `/438c`：438C 标准
- `/generation`：文档生成
- `/generation/:id`：文档详情
- `/validation`：质量验证
- `/merge`：文档合稿
- `/qa`：智能问答

## 主要接口分组

- `/api/project`：项目管理
- `/api/knowledge`：知识库、文件、检索、图谱、审核和版本
- `/api/438c`：438C 标准结构
- `/api/generation`：文档创建、生成、章节、任务和导出
- `/api/validation`：质量验证和规则管理
- `/api/merge`：合稿任务和下载
- `/api/question`：智能问答

完整接口见 [docs/API接口文档.md](docs/API接口文档.md)。

## 文档索引

- [代码说明文档](docs/代码说明文档.md)
- [API 接口文档](docs/API接口文档.md)
- [离线部署文档](docs/离线部署文档.md)
- [配置文档](docs/配置文档.md)
- [全站部署验收清单](docs/全站部署验收清单.md)

## 注意事项

- MinIO 不可用时，系统会回退到本地文件存储。
- Neo4j 不可用时，知识图谱可使用本地 JSON 数据。
- 438C 专项问答会调用本地 `qwen2.5:7b`，模型响应速度取决于部署机器性能。
- PowerShell 直接发送中文 JSON 时可能出现编码问题，建议使用前端页面或确保请求体为 UTF-8。
