<template>
  <div class="knowledge-base tech-page">
    <el-card class="kb-hero">
      <div class="hero-row">
        <div class="hero-left">
          <div class="hero-badge">KNOWLEDGE BASE</div>
          <h2 class="hero-title">知识库管理</h2>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建知识库
        </el-button>
      </div>
    </el-card>

    <div class="kb-grid" v-if="knowledgeBases.length > 0">
      <div v-for="kb in knowledgeBases" :key="kb.id" class="kb-card" @click="$router.push(`/knowledge/${kb.id}`)">
        <div class="kb-glow"></div>
        <div class="kb-icon-wrap">
          <el-icon :size="28"><Collection /></el-icon>
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
.kb-hero {
  border-radius: 20px !important;
  margin-bottom: 24px;
}

.hero-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  color: #99dcff;
  letter-spacing: 0.1em;
  background: rgba(89, 184, 255, 0.1);
  border: 1px solid rgba(89, 184, 255, 0.16);
  margin-bottom: 10px;
}

.hero-title {
  font-size: 22px;
  font-weight: 700;
  color: #eef6ff;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.kb-card {
  position: relative;
  padding: 24px 20px 18px;
  border-radius: 18px;
  background: rgba(10, 21, 42, 0.65);
  border: 1px solid rgba(116, 170, 255, 0.14);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.kb-card:hover {
  border-color: rgba(89, 184, 255, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(89, 184, 255, 0.12);
}

.kb-glow {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(89, 184, 255, 0.15), transparent 70%);
  pointer-events: none;
}

.kb-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(89, 184, 255, 0.2), rgba(109, 247, 193, 0.1));
  border: 1px solid rgba(89, 184, 255, 0.2);
  color: #59b8ff;
  margin-bottom: 16px;
}

.kb-name {
  font-size: 16px;
  font-weight: 600;
  color: #eef6ff;
  margin-bottom: 6px;
}

.kb-desc {
  font-size: 13px;
  color: #95a7c5;
  margin-bottom: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid rgba(116, 170, 255, 0.1);
  border-bottom: 1px solid rgba(116, 170, 255, 0.1);
  margin-bottom: 14px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-val {
  font-size: 16px;
  font-weight: 700;
  color: #eef6ff;
}

.stat-lbl {
  font-size: 11px;
  color: #95a7c5;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(116, 170, 255, 0.15);
}

.kb-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
