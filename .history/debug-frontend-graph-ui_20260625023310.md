# 调试会话：前端按钮文字缺失 / 知识图谱可视化入口缺失

- 会话 ID：`frontend-graph-ui`
- 状态：`[OPEN]`
- 现象：
  1. 前端部分按钮文字没有显示出来。
  2. 知识图谱可视化界面入口位置不明确。
- 期望：
  1. 关键按钮可正常显示文字。
  2. 提供清晰的知识图谱可视化入口。

## 假设列表（待证伪）
1. H1：上一轮新增的 `frontend/src/styles/theme.css` 中将 Element Plus 按钮文字色覆盖为透明 / 同色，导致 `.el-button` 文字不可见。
2. H2：新增的深色玻璃态主题里，`.el-menu-item`、`.el-button.is-text` 等文本类元素的 `color` 被覆盖，但父级 `background` 也是深色，形成“同色叠加”。
3. H3：知识图谱可视化组件 `KnowledgeGraphD3.vue` 只内嵌到了 `KnowledgeDetail.vue`，没有独立路由；侧边栏菜单也未提供对应入口。
4. H4：路由表 `frontend/src/router/index.js` 没有把 `/knowledge/graph` 之类的页面挂上去，即便菜单有入口也跳不到图谱页。
5. H5：图谱组件依赖的 `d3` 在 `package.json` 引入成功，但运行时缺少 `import 'd3'` 的样式或挂载，组件可能直接抛错而不会显示“打开图谱”按钮。

## 证据收集计划
- 先静态核查 theme.css 中是否覆盖按钮文字色与菜单文字色。
- 检查 `router/index.js` 是否存在知识图谱相关路由。
- 检查 `Layout.vue` 侧边栏菜单是否暴露入口。
- 检查 `KnowledgeDetail.vue` 中的图谱触发按钮是否可见（文本与定位）。
- 通过后端 `/api/knowledge/graph` 验证数据通路（运行时不依赖 Neo4j，本地 JSON 已保底）。
- 跑 `npm run build` 确认前端构建是否成功。

## 修复计划
- 调整 theme.css，对 Element Plus 按钮、菜单、链接等文本类组件显式设置可读前景色，避免被深色背景吞噬。
- 在 router 中新增独立知识图谱路由 `/knowledge/graph`。
- 在 Layout 侧边栏增加 “知识图谱” 入口。
- 在 KnowledgeDetail 中显式把按钮文字与图谱跳转链接写到模板里，避免依赖样式。
- 在图谱组件失败时给出降级提示，不让按钮消失。

## 验证
- 前端 `npm run build` 通过。
- 后端 `/api/knowledge/graph` 返回 `200` 且含 entities/relations。
- 前端 `KnowledgeGraphD3.vue` 在浏览器可拖拽、可缩放、节点文字可读。
