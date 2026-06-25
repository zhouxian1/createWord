# 调试会话：前端按钮文字缺失 / 知识图谱可视化入口缺失

- 会话 ID：`frontend-graph-ui`
- 状态：`[FIXED]`（修复完成，待用户验收）

## 假设列表（已逐项核对）
1. H1：✅ 命中。`theme.css` 中只重置了按钮背景，没有显式设置 `color`，导致默认文字被深色背景吞掉。
2. H2：✅ 命中。`el-menu-item` 同样没有显式文字色，菜单项文字与背景同色。
3. H3：✅ 命中。`KnowledgeGraphD3.vue` 仅内嵌在 `KnowledgeDetail.vue`，没有独立页面入口。
4. H4：✅ 命中。`router/index.js` 缺少 `/knowledge-graph` 路由。
5. H5：⚠️ 部分命中。`d3` 已能正常导入（构建产物 `KnowledgeGraphD3-*.js` 已生成），但需要独立页面提供合理高度，避免被父级 `display:none` 影响。

## 证据
- `npm run build` 成功，新增 `KnowledgeGraph.vue` / `KnowledgeGraphD3.vue` 均正常打包。
- `dist/assets/KnowledgeGraph-*.js` 与 `KnowledgeGraphD3-*.js` 已生成。
- 主题样式对 `.el-button`、`el-menu-item` 增加了显式 `color`，按钮与菜单文字现在可读。
- 路由表新增 `/knowledge-graph`，菜单新增“知识图谱”入口。

## 修复摘要
- 新增 [KnowledgeGraph.vue](file:///f:/geovis/cerateWord/frontend/src/views/KnowledgeGraph.vue) 独立页面。
- 在 [router/index.js](file:///f:/geovis/cerateWord/frontend/src/router/index.js#L31-L36) 注册 `/knowledge-graph` 路由。
- 在 [Layout.vue](file:///f:/geovis/cerateWord/frontend/src/components/Layout.vue#L34-L49) 侧边栏新增“知识图谱”入口。
- 在 [theme.css](file:///f:/geovis/cerateWord/frontend/src/styles/theme.css#L102-L150) 显式设置按钮、菜单文字色，避免被同色背景吞没。

## 验证
- `npm run build` 通过，输出新增 `KnowledgeGraph` 相关 chunk。
- 启动前端开发服务器并访问 `/#/knowledge-graph` 即可查看可视化界面。
