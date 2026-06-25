# 438C 文档生成与知识图谱系统

面向 GJB 438C 军用软件文档编制场景的智能文档平台，提供知识库构建、知识图谱、438C 标准文档生成、质量验证、文档合稿排版和智能问答能力。

## 核心能力

- 知识库导入：支持本地文件、批量目录、接口数据与增量同步
- 多模解析：支持 `doc/docx/pdf/xlsx/pptx/txt/md/html/json` 及代码文件解析
- 知识图谱：以 438C 文档、章节、术语、代码实体为节点，支持 Neo4j 图数据库存储
- 语义检索：结合 Chroma 向量检索、倒排索引、知识图谱加权与重排序
- 文档生成：支持整篇生成、章节生成、从代码生成和导出下载
- 前端可视化：知识图谱采用 D3.js 展示，问答页支持语音输入

## 技术架构

### 后端

- Flask 3
- SQLAlchemy
- ChromaDB
- Neo4j
- MinIO
- sentence-transformers

### 前端

- Vue 3 + Vite 5
- Element Plus
- D3.js
- ECharts
- Axios

## 快速启动

### 1. 启动基础服务

```bash
docker compose up -d neo4j minio
```

### 2. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认访问：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:5000`
- Neo4j Browser：`http://localhost:7474`
- MinIO Console：`http://localhost:9001`

## 文档索引

- 项目说明：`docs/代码说明文档.md`
- 部署文档：`docs/离线部署文档.md`
- 验收清单：`docs/全站部署验收清单.md`
- 配置文档：`docs/配置文档.md`
- 接口文档：`docs/API接口文档.md`

## 关键目录

```text
backend/app/services/      # 解析、索引、图谱、生成、验证、问答服务
backend/app/api/           # REST API
frontend/src/views/        # 页面视图
frontend/src/components/   # 复用组件
docs/                      # 项目文档
438c/                      # 438C 模板样例
```

## 新增特性

- Neo4j 图数据库持久化知识图谱
- D3.js 图谱交互式可视化
- 深色科技风前端主题
- 智能问答语音输入
- 补全 README、部署文档与 API 文档
