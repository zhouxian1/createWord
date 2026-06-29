<template>
  <div class="dashboard cyber-page circuit-bg">
    <div class="hero holo-panel">
      <div class="hero-content">
        <div class="hero-copy">
          <div class="cyber-badge">438C DOCUMENT WORKSPACE</div>
          <h2 class="glitch-title">438C 文档智能生成平台</h2>
          <p class="hero-desc">围绕项目、知识库、标准模板、质量验证和合稿输出，形成可追踪的文档工程工作台。</p>
        </div>
        <div class="hero-metrics">
          <div class="hero-metric">
            <span class="metric-label">最近文档</span>
            <strong>{{ recentDocs.length }}</strong>
          </div>
          <div class="hero-metric">
            <span class="metric-label">标准类别</span>
            <strong>{{ categories.length }}</strong>
          </div>
        </div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="6" v-for="(card, idx) in statCards" :key="card.title">
        <div class="stat-card holo-panel" :class="'stat-card--' + idx">
          <div class="stat-icon">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-title">{{ card.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="16">
        <div class="holo-panel panel-card">
          <div class="panel-header">
            <span class="panel-title">快速操作</span>
            <div class="neon-divider"></div>
          </div>
          <el-row :gutter="12">
            <el-col :xs="12" :sm="6" v-for="action in quickActions" :key="action.title">
              <div class="quick-action" @click="$router.push(action.path)">
                <div class="action-icon" :style="{ '--action-color': action.color }">
                  <el-icon :size="26"><component :is="action.icon" /></el-icon>
                </div>
                <div class="action-title">{{ action.title }}</div>
                <div class="action-desc">{{ action.desc }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
      <el-col :xs="24" :lg="8">
        <div class="holo-panel panel-card">
          <div class="panel-header">
            <span class="panel-title">最近文档</span>
            <div class="neon-divider"></div>
          </div>
          <div v-if="recentDocs.length === 0" class="empty-text">暂无文档</div>
          <div v-for="doc in recentDocs" :key="doc.id" class="recent-doc-item" @click="$router.push(`/generation/${doc.id}`)">
            <el-icon><Document /></el-icon>
            <span class="doc-name">{{ doc.doc_name }}</span>
            <el-tag :type="statusType(doc.status)" size="small">{{ statusLabel(doc.status) }}</el-tag>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="24">
        <div class="holo-panel panel-card">
          <div class="panel-header">
            <span class="panel-title">438C 文档类型概览</span>
            <div class="neon-divider"></div>
          </div>
          <div class="doc-type-grid">
            <div v-for="cat in categories" :key="cat.code" class="doc-type-item">
              <div class="cat-name">{{ cat.name }}</div>
              <div class="cat-count">{{ cat.document_count }} 类文档</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { generationApi, standard438cApi } from '@/api'

const recentDocs = ref([])
const categories = ref([])

const statCards = ref([
  { title: '项目数', value: 0, icon: 'Folder', color: '#1b75d0' },
  { title: '知识库', value: 0, icon: 'Collection', color: '#238a63' },
  { title: '已生成文档', value: 0, icon: 'Document', color: '#b9914b' },
  { title: '验证通过', value: 0, icon: 'CircleCheck', color: '#bd4b72' }
])

const quickActions = [
  { title: '创建项目', desc: '新建文档项目', icon: 'FolderAdd', color: '#1b75d0', path: '/projects' },
  { title: '知识入库', desc: '管理知识资源', icon: 'Upload', color: '#238a63', path: '/knowledge' },
  { title: '生成文档', desc: '生成 438C 文档', icon: 'EditPen', color: '#b9914b', path: '/generation' },
  { title: '智能问答', desc: '基于知识库问答', icon: 'ChatDotRound', color: '#bd4b72', path: '/qa' }
]

const statusType = (status) => {
  const map = { draft: 'info', generating: 'warning', generated: 'success', validated: 'success', error: 'danger' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { draft: '草稿', generating: '生成中', generated: '已生成', validated: '已验证', error: '错误' }
  return map[status] || status
}

onMounted(async () => {
  try {
    const [docRes, catRes] = await Promise.all([
      generationApi.listDocuments({}),
      standard438cApi.listCategories()
    ])
    recentDocs.value = (docRes.items || []).slice(0, 5)
    categories.value = catRes.items || []
    statCards.value[2].value = docRes.total || 0
  } catch (e) {
    // 首页指标允许后端未就绪时降级为空态。
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  padding: 30px 34px;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 28px;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-desc {
  max-width: 720px;
  margin: 0;
  color: var(--cp-text-dim);
  font-size: 14px;
  line-height: 1.8;
}

.hero-metrics {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.hero-metric {
  min-width: 116px;
  padding: 16px 18px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid rgba(45, 61, 82, 0.1);
  text-align: center;
}

.metric-label {
  display: block;
  margin-bottom: 6px;
  color: var(--cp-text-dim);
  font-size: 12px;
  font-weight: 700;
}

.hero-metric strong {
  color: var(--cp-text-bright);
  font-size: 28px;
  font-weight: 800;
}

.stat-card {
  min-height: 104px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card--0 .stat-icon { background: rgba(27, 117, 208, 0.1); color: #1b75d0; }
.stat-card--1 .stat-icon { background: rgba(35, 138, 99, 0.1); color: #238a63; }
.stat-card--2 .stat-icon { background: rgba(185, 145, 75, 0.12); color: #9d7636; }
.stat-card--3 .stat-icon { background: rgba(189, 75, 114, 0.1); color: #bd4b72; }

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(45, 61, 82, 0.08);
}

.stat-value {
  color: var(--cp-text-bright);
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.stat-title {
  margin-top: 8px;
  color: var(--cp-text-dim);
  font-size: 13px;
  font-weight: 700;
}

.panel-card {
  padding: 22px;
}

.panel-header {
  margin-bottom: 16px;
}

.panel-title {
  color: var(--cp-text-bright);
  font-size: 15px;
  font-weight: 800;
}

.quick-action {
  min-height: 132px;
  padding: 22px 12px;
  cursor: pointer;
  border-radius: 8px;
  border: 1px solid transparent;
  text-align: center;
  transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.quick-action:hover {
  background: #f8fafc;
  border-color: rgba(45, 61, 82, 0.12);
  box-shadow: 0 10px 26px rgba(22, 31, 44, 0.08);
  transform: translateY(-2px);
}

.action-icon {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  background: rgba(45, 61, 82, 0.05);
  border: 1px solid rgba(45, 61, 82, 0.08);
  color: var(--action-color, var(--cp-cyan));
}

.action-title {
  color: var(--cp-text);
  font-weight: 800;
}

.action-desc {
  margin-top: 6px;
  color: var(--cp-text-dim);
  font-size: 12px;
  line-height: 1.5;
}

.recent-doc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(45, 61, 82, 0.08);
  color: var(--cp-text);
  cursor: pointer;
  transition: color 0.18s ease, transform 0.18s ease;
}

.recent-doc-item:hover {
  color: var(--cp-cyan);
  transform: translateX(2px);
}

.doc-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-text {
  padding: 22px;
  color: var(--cp-text-dim);
  text-align: center;
}

.doc-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.doc-type-item {
  min-height: 88px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid rgba(45, 61, 82, 0.08);
  border-radius: 8px;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.doc-type-item:hover {
  border-color: rgba(27, 117, 208, 0.22);
  box-shadow: 0 10px 24px rgba(22, 31, 44, 0.08);
  transform: translateY(-2px);
}

.cat-name {
  color: var(--cp-text);
  font-weight: 800;
}

.cat-count {
  margin-top: 8px;
  color: var(--cp-text-dim);
  font-size: 12px;
}

@media (max-width: 960px) {
  .hero-content {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero-metrics {
    width: 100%;
  }

  .hero-metric {
    flex: 1;
  }
}

@media (max-width: 640px) {
  .hero,
  .panel-card,
  .stat-card {
    padding: 18px;
  }

  .hero-metrics {
    flex-direction: column;
  }
}
</style>
