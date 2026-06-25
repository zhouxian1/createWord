<template>
  <div class="document-detail tech-page">
    <el-page-header @back="$router.push('/generation')" :content="document.doc_name || '文档详情'" />

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>章节结构</span>
              <el-button size="small" type="primary" @click="generateSelected">
                生成选中章节
              </el-button>
            </div>
          </template>
          <el-tree
            ref="treeRef"
            :data="chapterTree"
            :props="{ children: 'children', label: 'label' }"
            show-checkbox
            node-key="id"
            default-expand-all
            @check-change="onCheckChange"
          >
            <template #default="{ data }">
              <span class="tree-node">
                <span class="node-number">{{ data.number }}</span>
                <span class="node-title">{{ data.title }}</span>
                <el-tag v-if="data.status" :type="genStatusType(data.status)" size="small">
                  {{ genStatusLabel(data.status) }}
                </el-tag>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ currentChapter ? `${currentChapter.chapter_number} ${currentChapter.chapter_title}` : '章节内容' }}</span>
              <div v-if="currentChapter">
                <el-button size="small" type="success" @click="saveChapter">保存</el-button>
                <el-button size="small" type="primary" @click="regenerateChapter">重新生成</el-button>
              </div>
            </div>
          </template>

          <div v-if="currentChapter">
            <div class="chapter-meta">
              <el-tag size="small">层级: {{ currentChapter.chapter_level }}</el-tag>
              <el-tag :type="genStatusType(currentChapter.generation_status)" size="small">
                {{ genStatusLabel(currentChapter.generation_status) }}
              </el-tag>
              <el-tag :type="currentChapter.validation_status === 'pass' ? 'success' : 'warning'" size="small">
                {{ currentChapter.validation_status === 'pass' ? '验证通过' : '待验证' }}
              </el-tag>
            </div>

            <!-- 提示词编辑 -->
            <el-collapse style="margin-top: 12px">
              <el-collapse-item title="定制化提示词" name="prompt">
                <el-input
                  v-model="currentChapter.prompt_template"
                  type="textarea"
                  :rows="3"
                  placeholder="定制化提示词（可选）"
                />
              </el-collapse-item>
            </el-collapse>

            <!-- 内容编辑 -->
            <el-input
              v-model="currentChapter.content"
              type="textarea"
              :rows="20"
              placeholder="章节内容"
              style="margin-top: 12px"
            />
          </div>

          <el-empty v-else description="请在左侧选择章节查看内容" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { generationApi, validationApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const docId = parseInt(route.params.id)
const document = ref({})
const chapters = ref([])
const currentChapter = ref(null)
const treeRef = ref(null)
const selectedChapterIds = ref([])

const genStatusType = (s) => ({ pending: 'info', generating: 'warning', completed: 'success', error: 'danger' }[s] || 'info')
const genStatusLabel = (s) => ({ pending: '待生成', generating: '生成中', completed: '已完成', error: '错误' }[s] || s)

const chapterTree = computed(() => {
  return buildTree(chapters.value.filter(c => !c.parent_id))
})

const buildTree = (items) => {
  return items.map(item => ({
    id: item.id,
    number: item.chapter_number,
    title: item.chapter_title,
    status: item.generation_status,
    children: buildTree(chapters.value.filter(c => c.parent_id === item.id))
  }))
}

const loadData = async () => {
  const res = await generationApi.getDocument(docId)
  document.value = res
  chapters.value = res.chapters || []
}

const onCheckChange = () => {
  if (treeRef.value) {
    selectedChapterIds.value = treeRef.value.getCheckedKeys()
  }
}

const generateSelected = async () => {
  if (selectedChapterIds.value.length === 0) {
    ElMessage.warning('请选择要生成的章节')
    return
  }
  const res = await generationApi.generateByChapter(docId, { chapter_ids: selectedChapterIds.value })
  ElMessage.success('章节生成任务已启动')
  loadData()
}

const saveChapter = async () => {
  if (!currentChapter.value) return
  await generationApi.updateChapter(currentChapter.value.id, {
    content: currentChapter.value.content,
    prompt_template: currentChapter.value.prompt_template
  })
  ElMessage.success('保存成功')
}

const regenerateChapter = async () => {
  if (!currentChapter.value) return
  await generationApi.generateByChapter(docId, { chapter_ids: [currentChapter.value.id] })
  ElMessage.success('重新生成已启动')
  loadData()
}

// 监听树节点点击
const handleNodeClick = (data) => {
  const chapter = chapters.value.find(c => c.id === data.id)
  if (chapter) {
    currentChapter.value = { ...chapter }
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
.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
}
.node-number {
  color: #59b8ff;
  font-weight: 500;
  font-size: 13px;
}
.node-title {
  font-size: 13px;
  color: #eef6ff;
}
.chapter-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
</style>
