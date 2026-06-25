<template>
  <div class="document-merge tech-page">
    <el-card class="merge-hero">
      <div class="hero-row">
        <div>
          <div class="hero-badge">DOC MERGE</div>
          <h2 class="hero-title">文档合稿</h2>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>创建合稿任务
        </el-button>
      </div>
    </el-card>

    <el-card>

      <el-table :data="tasks" stripe>
        <el-table-column prop="name" label="任务名称" min-width="150" />
        <el-table-column label="合并策略" width="120">
          <template #default="{ row }">{{ strategyLabel(row.merge_strategy) }}</template>
        </el-table-column>
        <el-table-column prop="output_format" label="输出格式" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="executeTask(row)" :disabled="row.status === 'running'">
              执行
            </el-button>
            <el-button size="small" @click="downloadResult(row)" :disabled="row.status !== 'completed'">
              下载
            </el-button>
            <el-button size="small" type="danger" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="创建合稿任务" width="600px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="formData.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="选择文档" required>
          <el-select v-model="formData.source_documents" multiple placeholder="选择要合并的文档" filterable>
            <el-option v-for="doc in documents" :key="doc.id" :label="`${doc.doc_code} - ${doc.doc_name}`" :value="doc.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="合并策略">
          <el-radio-group v-model="formData.merge_strategy">
            <el-radio value="sequential">顺序合并</el-radio>
            <el-radio value="by_type">按类型合并</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="输出格式">
          <el-select v-model="formData.output_format">
            <el-option label="DOCX" value="docx" />
            <el-option label="PDF" value="pdf" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { mergeApi, generationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const tasks = ref([])
const documents = ref([])
const showCreateDialog = ref(false)
const formData = ref({
  name: '', source_documents: [], merge_strategy: 'sequential', output_format: 'docx'
})

const strategyLabel = (s) => ({ sequential: '顺序合并', by_type: '按类型合并' }[s] || s)
const statusType = (s) => ({ pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }[s] || 'info')
const statusLabel = (s) => ({ pending: '待执行', running: '执行中', completed: '已完成', failed: '失败' }[s] || s)
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

const loadData = async () => {
  const [taskRes, docRes] = await Promise.all([
    mergeApi.listTasks({}),
    generationApi.listDocuments({})
  ])
  tasks.value = taskRes.items || []
  documents.value = docRes.items || []
}

const createTask = async () => {
  if (!formData.value.name || formData.value.source_documents.length === 0) {
    ElMessage.warning('请填写任务名称并选择文档')
    return
  }
  await mergeApi.createTask(formData.value)
  ElMessage.success('合稿任务创建成功')
  showCreateDialog.value = false
  formData.value = { name: '', source_documents: [], merge_strategy: 'sequential', output_format: 'docx' }
  loadData()
}

const executeTask = async (row) => {
  await mergeApi.executeTask(row.id)
  ElMessage.success('合稿任务已启动')
  loadData()
}

const downloadResult = (row) => {
  window.open(mergeApi.downloadDocument(row.id), '_blank')
}

const deleteTask = async (row) => {
  await ElMessageBox.confirm('确定删除此合稿任务？', '提示', { type: 'warning' })
  await mergeApi.deleteTask(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.merge-hero {
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
</style>
