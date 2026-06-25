<template>
  <div class="knowledge-detail">
    <el-page-header @back="$router.push('/knowledge')" :content="kbInfo.name || '知识库详情'" />

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>文件列表</span>
              <el-upload
                :action="`/api/knowledge/bases/${kbId}/upload`"
                :on-success="onUploadSuccess"
                :on-error="onUploadError"
                multiple
                :show-file-list="false"
              >
                <el-button type="primary">
                  <el-icon><Upload /></el-icon>上传文件
                </el-button>
              </el-upload>
            </div>
          </template>

          <el-table :data="files" stripe>
            <el-table-column prop="original_filename" label="文件名" min-width="200" />
            <el-table-column prop="file_type" label="类型" width="100" />
            <el-table-column label="大小" width="100">
              <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分块数" width="80" />
            <el-table-column label="索引状态" width="100">
              <template #default="{ row }">
                <el-tag :type="indexStatusType(row.index_status)" size="small">
                  {{ indexStatusLabel(row.index_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="上传时间" width="170">
              <template #default="{ row }">{{ formatDate(row.uploaded_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button size="small" type="danger" text @click="deleteFile(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header><span>语义搜索</span></template>
          <el-input v-model="searchQuery" placeholder="输入搜索内容" @keyup.enter="doSearch">
            <template #append>
              <el-button @click="doSearch" :loading="searching">搜索</el-button>
            </template>
          </el-input>
          <div v-if="searchResults.length > 0" class="search-results">
            <div v-for="(result, i) in searchResults" :key="i" class="search-result-item">
              <div class="result-content">{{ result.content }}</div>
              <div class="result-meta">
                <el-tag size="small">相似度: {{ (1 - (result.distance || 0)).toFixed(3) }}</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else-if="searched" description="未找到相关内容" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { knowledgeApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const kbId = parseInt(route.params.id)
const kbInfo = ref({})
const files = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const searched = ref(false)

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

const indexStatusType = (s) => ({ pending: 'info', indexing: 'warning', completed: 'success', error: 'danger' }[s] || 'info')
const indexStatusLabel = (s) => ({ pending: '待索引', indexing: '索引中', completed: '已完成', error: '错误' }[s] || s)

const loadData = async () => {
  const [kbRes, fileRes] = await Promise.all([
    knowledgeApi.getBase(kbId),
    knowledgeApi.listFiles(kbId)
  ])
  kbInfo.value = kbRes
  files.value = fileRes.items || []
}

const onUploadSuccess = () => {
  ElMessage.success('上传成功')
  loadData()
}

const onUploadError = () => {
  ElMessage.error('上传失败')
}

const deleteFile = async (row) => {
  await ElMessageBox.confirm('确定删除此文件？', '提示', { type: 'warning' })
  await knowledgeApi.deleteFile(row.id)
  ElMessage.success('删除成功')
  loadData()
}

const doSearch = async () => {
  if (!searchQuery.value) return
  searching.value = true
  searched.value = true
  try {
    const res = await knowledgeApi.search(kbId, { query: searchQuery.value, top_k: 5 })
    searchResults.value = res.results || []
  } finally {
    searching.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-results {
  margin-top: 16px;
}
.search-result-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 8px;
}
.result-content {
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  max-height: 120px;
  overflow: hidden;
}
.result-meta {
  margin-top: 8px;
}
</style>
