<template>
  <div class="knowledge-base cyber-page circuit-bg">
    <div class="hero holo-panel">
      <div class="hero-row">
        <div>
          <div class="cyber-badge">KNOWLEDGE BASE</div>
          <h2 class="glitch-title" style="margin-top: 10px; font-size: 22px;">知识库管理</h2>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建知识库
        </el-button>
      </div>
    </div>

    <div class="kb-grid" v-if="knowledgeBases.length > 0">
      <div v-for="kb in knowledgeBases" :key="kb.id" class="kb-card holo-panel" @click="$router.push(`/knowledge/${kb.id}`)">
        <div class="kb-icon-wrap">
          <el-icon :size="26"><Collection /></el-icon>
        </div>
        <div class="kb-name">{{ kb.name }}</div>
        <div class="kb-desc">{{ kb.description || '暂无描述' }}</div>
        <div class="kb-stats">
          <div class="stat-item">
            <span class="stat-val">{{ kb.doc_count }}</span>
            <span class="stat-lbl">文件</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-val">{{ formatSize(kb.total_size) }}</span>
            <span class="stat-lbl">容量</span>
          </div>
        </div>
        <div class="kb-footer">
          <el-tag size="small" type="info">{{ kb.kb_type || '通用' }}</el-tag>
          <el-button size="small" type="danger" text @click.stop="deleteKB(kb)">删除</el-button>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无知识库，点击右上角创建" />

    <el-dialog v-model="showCreateDialog" title="创建知识库" width="460px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createKB">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledgeApi } from '@/api'
import { useAppStore } from '@/store'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useAppStore()
const knowledgeBases = ref([])
const showCreateDialog = ref(false)
const formData = ref({ name: '', description: '' })

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

const loadKBs = async () => {
  const params = {}
  if (store.currentProject) params.project_id = store.currentProject.id
  const res = await knowledgeApi.listBases(params)
  knowledgeBases.value = res.items || []
}

const createKB = async () => {
  if (!formData.value.name) return ElMessage.warning('请输入知识库名称')
  const data = { ...formData.value }
  if (store.currentProject) data.project_id = store.currentProject.id
  await knowledgeApi.createBase(data)
  ElMessage.success('创建成功')
  showCreateDialog.value = false
  formData.value = { name: '', description: '' }
  loadKBs()
}

const deleteKB = async (kb) => {
  await ElMessageBox.confirm(`确定删除知识库"${kb.name}"？`, '提示', { type: 'warning' })
  await knowledgeApi.deleteBase(kb.id)
  ElMessage.success('删除成功')
  loadKBs()
}

onMounted(loadKBs)
</script>

<style scoped>
.hero {
  padding: 24px 28px;
  margin-bottom: 20px;
}

.hero-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.kb-card {
  padding: 22px 18px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: float-y 5s ease-in-out infinite;
}

.kb-card:nth-child(2) { animation-delay: 0.3s; }
.kb-card:nth-child(3) { animation-delay: 0.6s; }
.kb-card:nth-child(4) { animation-delay: 0.9s; }

.kb-card:hover {
  border-color: var(--cp-cyan) !important;
  box-shadow: var(--cp-glow-cyan) !important;
  transform: translateY(-4px);
}

.kb-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 240, 255, 0.1);
  border: 1px solid rgba(0, 240, 255, 0.25);
  color: var(--cp-cyan);
  margin-bottom: 14px;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.15);
}

.kb-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--cp-text);
  font-family: 'Rajdhani', var(--cp-font-ui);
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}

.kb-desc {
  font-size: 12px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  margin-bottom: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 0;
  border-top: 1px solid rgba(0, 240, 255, 0.08);
  border-bottom: 1px solid rgba(0, 240, 255, 0.08);
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-val {
  font-size: 15px;
  font-weight: 700;
  color: var(--cp-cyan);
  font-family: 'Orbitron', var(--cp-font);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

.stat-lbl {
  font-size: 10px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: rgba(0, 240, 255, 0.15);
}

.kb-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
