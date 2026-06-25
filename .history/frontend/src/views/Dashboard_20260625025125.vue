<template>
  <div class="dashboard tech-page">
    <el-card class="hero-card">
      <div class="hero-content">
        <div>
          <div class="hero-tag">INTELLIGENT DOCUMENT PLATFORM</div>
          <h2 class="hero-title">438C 文档智能生成平台</h2>
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
    </el-card>

    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: card.color }">
            <el-icon :size="28"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-title">{{ card.title }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="6" v-for="action in quickActions" :key="action.title">
              <div class="quick-action" @click="$router.push(action.path)">
                <el-icon :size="32" :color="action.color"><component :is="action.icon" /></el-icon>
                <div class="action-title">{{ action.title }}</div>
                <div class="action-desc">{{ action.desc }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最近文档</span>
          </template>
          <div v-if="recentDocs.length === 0" class="empty-text">暂无文档</div>
          <div v-for="doc in recentDocs" :key="doc.id" class="recent-doc-item" @click="$router.push(`/generation/${doc.id}`)">
            <el-icon><Document /></el-icon>
            <span class="doc-name">{{ doc.doc_name }}</span>
            <el-tag :type="statusType(doc.status)" size="small">{{ statusLabel(doc.status) }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header><span>438C文档类型概览</span></template>
          <div class="doc-type-grid">
            <div v-for="cat in categories" :key="cat.code" class="doc-type-item">
              <div class="cat-name">{{ cat.name }}</div>
              <div class="cat-count">{{ cat.document_count }} 类文档</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>系统功能模块</span></template>
          <div class="module-list">
            <div v-for="mod in modules" :key="mod.name" class="module-item">
              <el-icon :color="mod.color"><component :is="mod.icon" /></el-icon>
              <div class="module-info">
                <div class="module-name">{{ mod.name }}</div>
                <div class="module-desc">{{ mod.desc }}</div>
              </div>
            </div>
          </div>
        </el-card>
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
  { title: '项目数', value: 0, icon: 'Folder', color: '#409eff' },
  { title: '知识库', value: 0, icon: 'Collection', color: '#67c23a' },
  { title: '已生成文档', value: 0, icon: 'Document', color: '#e6a23c' },
  { title: '验证通过', value: 0, icon: 'CircleCheck', color: '#f56c6c' }
])

const quickActions = [
  { title: '创建项目', desc: '新建文档项目', icon: 'FolderAdd', color: '#409eff', path: '/projects' },
  { title: '知识库', desc: '管理知识资源', icon: 'Upload', color: '#67c23a', path: '/knowledge' },
  { title: '生成文档', desc: '一键生成438C文档', icon: 'EditPen', color: '#e6a23c', path: '/generation' },
  { title: '智能问答', desc: '基于知识库问答', icon: 'ChatDotRound', color: '#f56c6c', path: '/qa' }
]

const modules = [
  { name: '知识库构建', desc: '支持20+格式文档解析与语义索引', icon: 'Collection', color: '#409eff' },
  { name: '438C文档生成', desc: '一键/按章节/从代码生成', icon: 'EditPen', color: '#67c23a' },
  { name: '质量验证', desc: '章节完整性与要素合规性校验', icon: 'CircleCheck', color: '#e6a23c' },
  { name: '文档合稿排版', desc: '多文档合并与自动排版', icon: 'CopyDocument', color: '#f56c6c' }
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
  gap: 20px;
}

.hero-card {
  overflow: hidden;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 8px 4px;
}

.hero-tag {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #99dcff;
  letter-spacing: 0.08em;
  background: rgba(89, 184, 255, 0.1);
  border: 1px solid rgba(89, 184, 255, 0.16);
}

.hero-title {
  margin-top: 14px;
  font-size: 28px;
  color: #eff7ff;
}



.hero-metrics {
  display: flex;
  gap: 14px;
}

.hero-metric {
  min-width: 120px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(116, 170, 255, 0.12);
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #8eb0d8;
  margin-bottom: 8px;
}

.hero-metric strong {
  font-size: 30px;
  color: #f7fbff;
}

.stat-card {
  display: flex;
  align-items: center;
  border-radius: 20px;
}
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #eef6ff;
}
.stat-title {
  font-size: 14px;
  color: #97a9c7;
  margin-top: 4px;
}

.quick-action {
  text-align: center;
  padding: 20px 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}
.quick-action:hover {
  background: rgba(89, 184, 255, 0.08);
}
.action-title {
  margin-top: 8px;
  font-weight: 500;
  color: #eef6ff;
}
.action-desc {
  font-size: 12px;
  color: #97a9c7;
  margin-top: 4px;
}

.recent-doc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.recent-doc-item:hover {
  color: #6bd5ff;
}
.doc-name {
  flex: 1;
}
.empty-text {
  color: #97a9c7;
  text-align: center;
  padding: 20px;
}

.doc-type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.doc-type-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(116, 170, 255, 0.08);
}
.cat-name {
  font-weight: 500;
  color: #eef6ff;
}
.cat-count {
  font-size: 12px;
  color: #97a9c7;
  margin-top: 4px;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.module-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(116, 170, 255, 0.08);
}
.module-name {
  font-weight: 500;
  color: #eef6ff;
}
.module-desc {
  font-size: 12px;
  color: #97a9c7;
}
</style>
