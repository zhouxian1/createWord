<template>
  <div class="knowledge-detail">
    <el-page-header @back="$router.push('/knowledge')" :content="kbInfo.name || '知识库详情'" />

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>文件列表</span>
              <div class="header-actions">
                <el-upload
                  :action="`/api/knowledge/bases/${kbId}/upload`"
                  :on-success="onUploadSuccess"
                  :on-error="onUploadError"
                  multiple
                  :show-file-list="false"
                >
                  <el-button type="primary" size="small">
                    <el-icon><Upload /></el-icon>本地上传
                  </el-button>
                </el-upload>
                <el-button size="small" @click="showBatchImportDialog = true">批量导入</el-button>
                <el-button size="small" @click="showApiImportDialog = true">API对接</el-button>
                <el-button size="small" @click="showIncrementalDialog = true">增量导入</el-button>
              </div>
            </div>
          </template>

          <!-- 过滤条件 -->
          <div class="filter-bar">
            <el-select v-model="filterReviewStatus" placeholder="审核状态" clearable size="small" style="width:120px;margin-right:8px">
              <el-option label="待审核" value="pending" />
              <el-option label="审核中" value="reviewing" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
            <el-select v-model="filterFileType" placeholder="文件类型" clearable size="small" style="width:120px">
              <el-option label="PDF" value="pdf" />
              <el-option label="Word" value="docx" />
              <el-option label="代码" value="python_code" />
              <el-option label="图片" value="image" />
            </el-select>
          </div>

          <el-table :data="filteredFiles" stripe>
            <el-table-column prop="original_filename" label="文件名" min-width="180" show-overflow-tooltip />
            <el-table-column prop="file_type" label="类型" width="90" />
            <el-table-column label="大小" width="90">
              <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分块" width="60" />
            <el-table-column label="密级" width="70">
              <template #default="{ row }">
                <el-tag :type="securityLevelType(row.security_level)" size="small">{{ row.security_level || '内部' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="审核" width="80">
              <template #default="{ row }">
                <el-tag :type="reviewStatusType(row.review_status)" size="small">{{ reviewStatusLabel(row.review_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="版本" width="60">
              <template #default="{ row }">v{{ row.version_number || 1 }}</template>
            </el-table-column>
            <el-table-column label="索引状态" width="80">
              <template #default="{ row }">
                <el-tag :type="indexStatusType(row.index_status)" size="small">
                  {{ indexStatusLabel(row.index_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" text @click="previewFile(row)">预览</el-button>
                <el-button size="small" type="warning" text @click="editFile(row)">编辑</el-button>
                <el-button size="small" type="success" text @click="reviewFile(row)" v-if="row.review_status === 'pending'">审核</el-button>
                <el-button size="small" text @click="showVersions(row)">版本</el-button>
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
                <el-tag size="small" v-if="result.rerank_score">相关度: {{ result.rerank_score.toFixed(3) }}</el-tag>
                <el-tag size="small" type="info" v-if="result.metadata?.chunk_type">{{ result.metadata.chunk_type }}</el-tag>
                <div v-if="result.source_traces?.length" class="source-trace">
                  <span class="trace-label">溯源:</span>
                  <span v-for="(trace, ti) in result.source_traces" :key="ti" class="trace-item">
                    {{ trace.source_file }} {{ trace.chapter_title ? '- ' + trace.chapter_title : '' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else-if="searched" description="未找到相关内容" />
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <div class="graph-header">
              <span>知识图谱</span>
              <el-button link size="small" @click="loadGraph">刷新</el-button>
            </div>
          </template>
          <el-input v-model="graphQuery" placeholder="输入实体名称，留空查看全量图谱" @keyup.enter="loadGraph">
            <template #append>
              <el-button @click="loadGraph" :loading="graphLoading">查询</el-button>
            </template>
          </el-input>
          <KnowledgeGraphD3 v-if="graphReady" class="graph-chart" :graph="graphData" :height="360" />
          <el-empty v-else description="暂无图谱数据" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showBatchImportDialog" title="批量导入" width="500px">
      <el-form label-width="80px">
        <el-form-item label="文件路径">
          <el-input v-model="batchPaths" type="textarea" :rows="4" placeholder="每行一个文件路径" />
        </el-form-item>
        <el-form-item label="文件分类">
          <el-select v-model="batchCategory" style="width:100%">
            <el-option label="标准文档" value="standard" />
            <el-option label="代码" value="code" />
            <el-option label="设计文档" value="design" />
            <el-option label="测试文档" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="密级">
          <el-select v-model="batchSecurity" style="width:100%">
            <el-option label="内部" value="内部" />
            <el-option label="秘密" value="秘密" />
            <el-option label="机密" value="机密" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchImportDialog = false">取消</el-button>
        <el-button type="primary" @click="doBatchImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>

    <!-- API对接对话框 -->
    <el-dialog v-model="showApiImportDialog" title="API对接导入" width="500px">
      <el-form label-width="80px">
        <el-form-item label="API地址">
          <el-input v-model="apiUrl" placeholder="https://api.example.com/data" />
        </el-form-item>
        <el-form-item label="请求方式">
          <el-select v-model="apiMethod" style="width:100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求头">
          <el-input v-model="apiHeaders" type="textarea" :rows="2" placeholder='{"Authorization": "Bearer xxx"}' />
        </el-form-item>
        <el-form-item label="请求体">
          <el-input v-model="apiBody" type="textarea" :rows="3" placeholder="POST请求体(JSON)" />
        </el-form-item>
        <el-form-item label="数据字段">
          <el-input v-model="apiFields" placeholder="title,content,category (逗号分隔)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApiImportDialog = false">取消</el-button>
        <el-button type="primary" @click="doApiImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>

    <!-- 增量导入对话框 -->
    <el-dialog v-model="showIncrementalDialog" title="增量导入" width="500px">
      <el-form label-width="80px">
        <el-form-item label="文件路径">
          <el-input v-model="incrementalPaths" type="textarea" :rows="4" placeholder="每行一个文件路径，系统将自动检测变更" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showIncrementalDialog = false">取消</el-button>
        <el-button type="primary" @click="doIncrementalImport" :loading="importing">检测并导入</el-button>
      </template>
    </el-dialog>

    <!-- 文件预览/编辑对话框 -->
    <el-dialog v-model="showEditDialog" :title="editMode ? '编辑内容' : '预览内容'" width="700px">
      <div v-if="!editMode" class="preview-content">{{ editContent }}</div>
      <el-input v-else v-model="editContent" type="textarea" :rows="20" />
      <template #footer>
        <template v-if="editMode">
          <el-button @click="editMode = false">取消编辑</el-button>
          <el-button type="primary" @click="saveEdit">保存</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="editMode = true">进入编辑</el-button>
          <el-button @click="showEditDialog = false">关闭</el-button>
        </template>
      </template>
    </el-dialog>

    <!-- 审核对话框 -->
    <el-dialog v-model="showReviewDialog" title="审核文件" width="500px">
      <el-form label-width="80px">
        <el-form-item label="审核人">
          <el-input v-model="reviewReviewer" />
        </el-form-item>
        <el-form-item label="审核结果">
          <el-radio-group v-model="reviewAction">
            <el-radio value="approve">通过</el-radio>
            <el-radio value="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="reviewComments" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>

    <!-- 版本历史对话框 -->
    <el-dialog v-model="showVersionDialog" title="版本历史" width="600px">
      <el-table :data="versions" stripe>
        <el-table-column prop="version_number" label="版本" width="60" />
        <el-table-column prop="change_type" label="类型" width="80" />
        <el-table-column prop="change_description" label="变更说明" min-width="150" />
        <el-table-column prop="changed_by" label="操作人" width="80" />
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="warning" text @click="doRollback(row)">回滚</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { knowledgeApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import KnowledgeGraphD3 from '@/components/KnowledgeGraphD3.vue'

const route = useRoute()
const kbId = parseInt(route.params.id)
const kbInfo = ref({})
const files = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const searched = ref(false)
const graphQuery = ref('')
const graphLoading = ref(false)
const graphData = ref({ nodes: [], links: [] })
const graphReady = computed(() => graphData.value.nodes.length > 0)

// 过滤
const filterReviewStatus = ref('')
const filterFileType = ref('')
const filteredFiles = computed(() => {
  return files.value.filter(f => {
    if (filterReviewStatus.value && f.review_status !== filterReviewStatus.value) return false
    if (filterFileType.value && f.file_type !== filterFileType.value) return false
    return true
  })
})

// 对话框状态
const showBatchImportDialog = ref(false)
const showApiImportDialog = ref(false)
const showIncrementalDialog = ref(false)
const showEditDialog = ref(false)
const showReviewDialog = ref(false)
const showVersionDialog = ref(false)
const importing = ref(false)
const editMode = ref(false)
const editContent = ref('')
const currentFileId = ref(null)
const versions = ref([])

// 批量导入
const batchPaths = ref('')
const batchCategory = ref('standard')
const batchSecurity = ref('内部')

// API导入
const apiUrl = ref('')
const apiMethod = ref('GET')
const apiHeaders = ref('')
const apiBody = ref('')
const apiFields = ref('title,content')

// 审核
const reviewReviewer = ref('')
const reviewAction = ref('approve')
const reviewComments = ref('')

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
const reviewStatusType = (s) => ({ pending: 'info', reviewing: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')
const reviewStatusLabel = (s) => ({ pending: '待审核', reviewing: '审核中', approved: '已通过', rejected: '已驳回' }[s] || s)
const securityLevelType = (s) => ({ '内部': 'info', '秘密': 'warning', '机密': 'danger' }[s] || 'info')

const loadData = async () => {
  const [kbRes, fileRes] = await Promise.all([
    knowledgeApi.getBase(kbId),
    knowledgeApi.listFiles(kbId)
  ])
  kbInfo.value = kbRes
  files.value = fileRes.items || []
}

const buildGraphOption = (data) => {
  const rawEntities = Array.isArray(data.entities)
    ? data.entities
    : Object.entries(data.entities || {}).map(([id, item]) => ({ id, ...item }))
  const relations = data.relations || []
  graphData.value = {
    nodes: rawEntities.map(item => ({
      id: item.id,
      name: item.name || item.id,
      type: item.type || 'unknown',
      value: item.properties?.number || item.properties?.code || item.type || ''
    })),
    links: relations.map(item => ({
      source: item.source,
      target: item.target,
      label: item.type || item.relation || ''
    }))
  }
}

const loadGraph = async () => {
  graphLoading.value = true
  try {
    const params = graphQuery.value ? { entity_name: graphQuery.value, depth: 2 } : {}
    const res = await knowledgeApi.getGraph(params)
    buildGraphOption(res)
  } catch {
    graphData.value = { nodes: [], links: [] }
    ElMessage.error('加载知识图谱失败')
  } finally {
    graphLoading.value = false
  }
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
    const res = await knowledgeApi.search(kbId, { query: searchQuery.value, top_k: 5, use_rerank: true })
    searchResults.value = res.results || []
  } finally {
    searching.value = false
  }
}

// 预览文件
const previewFile = async (row) => {
  try {
    const res = await knowledgeApi.previewFile(row.id)
    editContent.value = res.content_text || res.content || res.text || ''
    editMode.value = false
    currentFileId.value = row.id
    showEditDialog.value = true
  } catch {
    ElMessage.error('预览失败')
  }
}

// 编辑文件
const editFile = async (row) => {
  try {
    const res = await knowledgeApi.previewFile(row.id)
    editContent.value = res.content_text || res.content || res.text || ''
    editMode.value = true
    currentFileId.value = row.id
    showEditDialog.value = true
  } catch {
    ElMessage.error('加载失败')
  }
}

// 保存编辑
const saveEdit = async () => {
  try {
    await knowledgeApi.editFileContent(currentFileId.value, {
      content_text: editContent.value,
      reviewer: 'user'
    })
    ElMessage.success('保存成功')
    showEditDialog.value = false
    loadData()
  } catch {
    ElMessage.error('保存失败')
  }
}

// 审核文件
const reviewFile = (row) => {
  currentFileId.value = row.id
  reviewReviewer.value = ''
  reviewAction.value = 'approve'
  reviewComments.value = ''
  showReviewDialog.value = true
}

const submitReview = async () => {
  try {
    await knowledgeApi.reviewFile(currentFileId.value, {
      action: reviewAction.value,
      reviewer: reviewReviewer.value,
      comments: reviewComments.value
    })
    ElMessage.success('审核完成')
    showReviewDialog.value = false
    loadData()
  } catch {
    ElMessage.error('审核失败')
  }
}

// 版本历史
const showVersions = async (row) => {
  currentFileId.value = row.id
  try {
    const res = await knowledgeApi.getFileVersions(row.id)
    versions.value = res.items || []
    showVersionDialog.value = true
  } catch {
    ElMessage.error('获取版本历史失败')
  }
}

// 版本回滚
const doRollback = async (version) => {
  await ElMessageBox.confirm(`确定回滚到版本 v${version.version_number}？`, '提示', { type: 'warning' })
  try {
    await knowledgeApi.rollbackFile(currentFileId.value, {
      version_number: version.version_number,
      operator: 'user'
    })
    ElMessage.success('回滚成功')
    showVersionDialog.value = false
    loadData()
  } catch {
    ElMessage.error('回滚失败')
  }
}

// 批量导入
const doBatchImport = async () => {
  const paths = batchPaths.value.split('\n').map(p => p.trim()).filter(Boolean)
  if (!paths.length) return ElMessage.warning('请输入文件路径')
  importing.value = true
  try {
    const res = await knowledgeApi.batchImport(kbId, {
      file_paths: paths,
      file_category: batchCategory.value,
      security_level: batchSecurity.value
    })
    const results = res.results || []
    const success = results.filter(r => r.status === 'completed').length
    ElMessage.success(`导入完成: 成功${success}个, 共${results.length}个`)
    showBatchImportDialog.value = false
    loadData()
  } catch {
    ElMessage.error('批量导入失败')
  } finally {
    importing.value = false
  }
}

// API对接导入
const doApiImport = async () => {
  if (!apiUrl.value) return ElMessage.warning('请输入API地址')
  importing.value = true
  try {
    let headers = {}
    try { headers = JSON.parse(apiHeaders.value || '{}') } catch {}
    let body = null
    if (apiMethod.value === 'POST' && apiBody.value) {
      try { body = JSON.parse(apiBody.value) } catch {}
    }
    const res = await knowledgeApi.apiImport(kbId, {
      api_url: apiUrl.value,
      api_method: apiMethod.value,
      api_headers: headers,
      api_body: body,
      title_field: apiFields.value.split(',').map(f => f.trim()).filter(Boolean)[0] || 'title',
      content_field: apiFields.value.split(',').map(f => f.trim()).filter(Boolean)[1] || 'content'
    })
    ElMessage.success(`API导入完成: ${(res.results || []).length}条`)
    showApiImportDialog.value = false
    loadData()
  } catch {
    ElMessage.error('API导入失败')
  } finally {
    importing.value = false
  }
}

// 增量导入
const doIncrementalImport = async () => {
  const paths = incrementalPaths.value.split('\n').map(p => p.trim()).filter(Boolean)
  if (!paths.length) return ElMessage.warning('请输入文件路径')
  importing.value = true
  try {
    const res = await knowledgeApi.incrementalImport(kbId, { file_paths: paths })
    ElMessage.success(`增量导入完成: 新增${res.added}, 更新${res.updated}, 未变${res.unchanged}`)
    showIncrementalDialog.value = false
    loadData()
  } catch {
    ElMessage.error('增量导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadData()
  loadGraph()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-bar {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}
.graph-chart {
  margin-top: 16px;
  height: 360px;
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
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}
.source-trace {
  font-size: 12px;
  color: #909399;
}
.trace-label {
  font-weight: bold;
}
.trace-item {
  margin-left: 4px;
}
.preview-content {
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.6;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}
</style>
