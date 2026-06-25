<template>
  <div class="document-generation tech-page">
    <el-card class="gen-hero">
      <div class="hero-row">
        <div>
          <div class="hero-badge">438C DOC GEN</div>
          <h2 class="hero-title">文档生成</h2>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建文档
        </el-button>
      </div>
    </el-card>

    <el-card>

      <el-table :data="documents" stripe>
        <el-table-column prop="doc_code" label="编码" width="80" />
        <el-table-column prop="doc_name" label="文档名称" min-width="150" />
        <el-table-column label="生成模式" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ modeLabel(row.generation_mode) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="chapter_count" label="章节数" width="80" />
        <el-table-column label="验证评分" width="100">
          <template #default="{ row }">
            <span v-if="row.validation_score">{{ row.validation_score }}分</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="170">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="$router.push(`/generation/${row.id}`)">
              编辑
            </el-button>
            <el-button size="small" type="success" @click="generateFull(row)" :disabled="row.status === 'generating'">
              一键生成
            </el-button>
            <el-button size="small" @click="exportDoc(row)" :disabled="row.status !== 'generated' && row.status !== 'validated'">
              导出
            </el-button>
            <el-button size="small" type="danger" @click="deleteDoc(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建文档对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建438C文档" width="600px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="项目" required>
          <el-select v-model="formData.project_id" placeholder="选择项目">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="文档类型" required>
          <el-select v-model="formData.doc_type" placeholder="选择文档类型" filterable>
            <el-option-group v-for="cat in categories" :key="cat.code" :label="cat.name">
              <el-option v-for="code in cat.documents" :key="code" :label="`${code} - ${getDocName(code)}`" :value="code" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="生成模式">
          <el-radio-group v-model="formData.generation_mode">
            <el-radio value="full">一键生成</el-radio>
            <el-radio value="chapter">按章节生成</el-radio>
            <el-radio value="code">从代码生成</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createDocument">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { generationApi, projectApi, standard438cApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const documents = ref([])
const projects = ref([])
const categories = ref([])
const docTypes = ref([])
const showCreateDialog = ref(false)
const formData = ref({ project_id: null, doc_type: '', generation_mode: 'full' })

const modeLabel = (m) => ({ full: '一键生成', chapter: '按章节', code: '从代码' }[m] || m)
const statusType = (s) => ({ draft: 'info', generating: 'warning', generated: 'success', validated: 'success', error: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ draft: '草稿', generating: '生成中', generated: '已生成', validated: '已验证', error: '错误' }[s] || s)
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

const getDocName = (code) => {
  const doc = docTypes.value.find(d => d.code === code)
  return doc ? doc.name : code
}

const loadData = async () => {
  const [docRes, projRes, catRes, typeRes] = await Promise.all([
    generationApi.listDocuments({}),
    projectApi.list(),
    standard438cApi.listCategories(),
    standard438cApi.listDocTypes()
  ])
  documents.value = docRes.items || []
  projects.value = projRes.items || []
  categories.value = catRes.items || []
  docTypes.value = typeRes.items || []
}

const createDocument = async () => {
  if (!formData.value.project_id || !formData.value.doc_type) {
    ElMessage.warning('请选择项目和文档类型')
    return
  }
  await generationApi.createDocument(formData.value)
  ElMessage.success('文档创建成功')
  showCreateDialog.value = false
  loadData()
}

const generateFull = async (row) => {
  await ElMessageBox.confirm(`确定一键生成"${row.doc_name}"的全部章节？`, '提示', { type: 'info' })
  const res = await generationApi.generateFull(row.id, {})
  ElMessage.success('生成任务已启动')
  loadData()
}

const exportDoc = async (row) => {
  const res = await generationApi.exportDocument(row.id)
  if (res.download_url) {
    window.open(res.download_url, '_blank')
  }
  ElMessage.success('文档导出成功')
}

const deleteDoc = async (row) => {
  await ElMessageBox.confirm(`确定删除文档"${row.doc_name}"？`, '提示', { type: 'warning' })
  await generationApi.deleteDocument(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.gen-hero {
  border-radius: 20px !important;
  margin-bottom: 20px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-muted {
  color: #95a7c5;
}
</style>
