<template>
  <div class="dashboard cyber-page circuit-bg">
    <!-- Hero -->
    <div class="hero holo-panel">
      <div class="hero-content">
        <div>
          <div class="cyber-badge">INTELLIGENT DOCUMENT PLATFORM</div>
          <h2 class="glitch-title" style="margin-top: 12px; font-size: 26px;">438C 文档智能生成平台</h2>
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

    <!-- Stat Cards -->
    <el-row :gutter="16">
      <el-col :span="6" v-for="(card, idx) in statCards" :key="card.title">
        <div class="stat-card holo-panel" :class="'stat-card--' + idx">
          <div class="stat-icon">
            <el-icon :size="26"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-title">{{ card.title }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Quick Actions + Recent Docs -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <div class="holo-panel" style="padding: 20px;">
          <div class="panel-header">
            <span class="panel-title">快速操作</span>
            <div class="neon-divider"></div>
          </div>
          <el-row :gutter="12">
            <el-col :span="6" v-for="action in quickActions" :key="action.title">
              <div class="quick-action" @click="$router.push(action.path)">
                <div class="action-icon" :style="{ '--action-color': action.color }">
                  <el-icon :size="28"><component :is="action.icon" /></el-icon>
                </div>
                <div class="action-title">{{ action.title }}</div>
                <div class="action-desc">{{ action.desc }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="holo-panel" style="padding: 20px;">
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

    <!-- Categories -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <div class="holo-panel" style="padding: 20px;">
          <div class="panel-header">
            <span class="panel-title">438C文档类型概览</span>
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
import { useAppStore } from '@/store'

const store = useAppStore()
const recentDocs = ref([])
const categories = ref([])

const statCards = ref([
  { title: '项目数', value: 0, icon: 'Folder', color: '#00f0ff' },
  { title: '知识库', value: 0, icon: 'Collection', color: '#39ff14' },
  { title: '已生成文档', value: 0, icon: 'Document', color: '#ff2d95' },
  { title: '验证通过', value: 0, icon: 'CircleCheck', color: '#b44dff' }
])

const quickActions = [
  { title: '创建项目', desc: '新建文档项目', icon: 'FolderAdd', color: '#00f0ff', path: '/projects' },
  { title: '知识库', desc: '管理知识资源', icon: 'Upload', color: '#39ff14', path: '/knowledge' },
  { title: '生成文档', desc: '一键生成438C文档', icon: 'EditPen', color: '#ff2d95', path: '/generation' },
  { title: '智能问答', desc: '基于知识库问答', icon: 'ChatDotRound', color: '#b44dff', path: '/qa' }
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
    // 忽略
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── Hero ── */
.hero {
  padding: 28px 32px;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.hero-metrics {
  display: flex;
  gap: 12px;
}

.hero-metric {
  min-width: 110px;
  padding: 14px 18px;
  border-radius: 4px;
  background: rgba(0, 240, 255, 0.04);
  border: 1px solid rgba(0, 240, 255, 0.15);
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 11px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.hero-metric strong {
  font-size: 28px;
  color: var(--cp-cyan);
  text-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
  font-family: 'Orbitron', var(--cp-font);
}

/* ── Stat Cards ── */
.stat-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  animation: float-y 6s ease-in-out infinite;
}

.stat-card--0 { animation-delay: 0s; }
.stat-card--1 { animation-delay: 0.8s; }
.stat-card--2 { animation-delay: 1.6s; }
.stat-card--3 { animation-delay: 2.4s; }

.stat-card--0 .stat-icon { background: rgba(0, 240, 255, 0.12); color: var(--cp-cyan); box-shadow: 0 0 16px rgba(0, 240, 255, 0.2); }
.stat-card--1 .stat-icon { background: rgba(57, 255, 20, 0.12); color: var(--cp-green); box-shadow: 0 0 16px rgba(57, 255, 20, 0.2); }
.stat-card--2 .stat-icon { background: rgba(255, 45, 149, 0.12); color: var(--cp-magenta); box-shadow: 0 0 16px rgba(255, 45, 149, 0.2); }
.stat-card--3 .stat-icon { background: rgba(180, 77, 255, 0.12); color: var(--cp-purple); box-shadow: 0 0 16px rgba(180, 77, 255, 0.2); }

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 240, 255, 0.15);
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--cp-text-bright);
  font-family: 'Orbitron', var(--cp-font);
}

.stat-title {
  font-size: 12px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-top: 2px;
}

/* ── Panel Header ── */
.panel-header {
  margin-bottom: 16px;
}

.panel-title {
  font-family: 'Orbitron', var(--cp-font);
  font-size: 13px;
  font-weight: 700;
  color: var(--cp-cyan);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

/* ── Quick Actions ── */
.quick-action {
  text-align: center;
  padding: 20px 10px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.quick-action:hover {
  background: rgba(0, 240, 255, 0.04);
  border-color: var(--cp-border);
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.1);
}

.action-icon {
  width: 52px;
  height: 52px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  background: rgba(0, 240, 255, 0.06);
  border: 1px solid rgba(0, 240, 255, 0.15);
  color: var(--action-color, var(--cp-cyan));
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.1);
}

.action-title {
  font-weight: 600;
  color: var(--cp-text);
  font-family: 'Rajdhani', var(--cp-font-ui);
  letter-spacing: 0.04em;
}

.action-desc {
  font-size: 11px;
  color: var(--cp-text-dim);
  margin-top: 4px;
  font-family: 'Share Tech Mono', var(--cp-font);
}

/* ── Recent Docs ── */
.recent-doc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 240, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--cp-text);
}

.recent-doc-item:hover {
  color: var(--cp-cyan);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

.doc-name {
  flex: 1;
  font-size: 13px;
}

.empty-text {
  color: var(--cp-text-dim);
  text-align: center;
  padding: 20px;
  font-family: 'Share Tech Mono', var(--cp-font);
}

/* ── Doc Type Grid ── */
.doc-type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.doc-type-item {
  padding: 14px;
  background: rgba(0, 240, 255, 0.03);
  border-radius: 4px;
  text-align: center;
  border: 1px solid rgba(0, 240, 255, 0.08);
  transition: all 0.2s;
}

.doc-type-item:hover {
  border-color: var(--cp-border);
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.1);
}

.cat-name {
  font-weight: 600;
  color: var(--cp-text);
  font-family: 'Rajdhani', var(--cp-font-ui);
}

.cat-count {
  font-size: 11px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  margin-top: 4px;
}
</style>
