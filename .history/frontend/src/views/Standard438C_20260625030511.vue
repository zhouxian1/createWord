<template>
  <div class="standard-438c cyber-page circuit-bg">
    <div class="std-hero holo-panel">
      <div class="hero-row">
        <div>
          <div class="cyber-badge">GJB 438C STANDARD</div>
          <h2 class="glitch-title" style="margin-top: 10px; font-size: 22px;">438C标准</h2>
        </div>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="category">按分类</el-radio-button>
          <el-radio-button value="list">列表</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-card>

      <!-- 分类视图 -->
      <div v-if="viewMode === 'category'">
        <el-tabs v-model="activeCategory">
          <el-tab-pane v-for="cat in categories" :key="cat.code" :label="cat.name" :name="cat.code">
            <el-row :gutter="16">
              <el-col :span="8" v-for="doc in getDocsByCategory(cat.code)" :key="doc.code">
                <el-card shadow="hover" class="doc-type-card" @click="showDocDetail(doc.code)">
                  <div class="doc-code">{{ doc.code }}</div>
                  <div class="doc-name">{{ doc.name }}</div>
                  <div class="doc-fullname">{{ doc.full_name }}</div>
                  <div class="doc-desc">{{ doc.description }}</div>
                  <div class="doc-meta">
                    <el-tag :type="complexityType(doc.complexity)" size="small">
                      {{ complexityLabel(doc.complexity) }}
                    </el-tag>
                    <span class="chapter-count">{{ doc.chapter_count }} 个章节</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 列表视图 -->
      <div v-else>
        <el-table :data="docTypes" stripe>
          <el-table-column prop="code" label="编码" width="80" />
          <el-table-column prop="name" label="文档名称" min-width="150" />
          <el-table-column prop="full_name" label="英文名称" min-width="200" />
          <el-table-column label="分类" width="100">
            <template #default="{ row }">{{ getCategoryName(row.category) }}</template>
          </el-table-column>
          <el-table-column label="复杂度" width="100">
            <template #default="{ row }">
              <el-tag :type="complexityType(row.complexity)" size="small">
                {{ complexityLabel(row.complexity) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="chapter_count" label="章节数" width="80" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="showDocDetail(row.code)">
                查看结构
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 文档结构详情对话框 -->
    <el-dialog v-model="showStructureDialog" :title="`${currentDoc.name} - 章节结构`" width="700px">
      <el-tree
        :data="structureTree"
        :props="{ children: 'children', label: 'label' }"
        default-expand-all
      >
        <template #default="{ data }">
          <span class="tree-node">
            <span class="node-number">{{ data.number }}</span>
            <span class="node-title">{{ data.title }}</span>
            <el-tag v-if="data.required === false" type="info" size="small">可选</el-tag>
            <el-tag v-else type="success" size="small">必填</el-tag>
          </span>
        </template>
      </el-tree>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { standard438cApi } from '@/api'

const viewMode = ref('category')
const activeCategory = ref('development')
const docTypes = ref([])
const categories = ref([])
const showStructureDialog = ref(false)
const currentDoc = ref({})
const structureTree = ref([])

const complexityType = (c) => ({ high: 'danger', medium: 'warning', low: 'success' }[c] || 'info')
const complexityLabel = (c) => ({ high: '高', medium: '中', low: '低' }[c] || c)

const getCategoryName = (code) => {
  const cat = categories.value.find(c => c.code === code)
  return cat ? cat.name : code
}

const getDocsByCategory = (catCode) => {
  const cat = categories.value.find(c => c.code === catCode)
  if (!cat) return []
  return docTypes.value.filter(d => cat.documents.includes(d.code))
}

const showDocDetail = async (code) => {
  const res = await standard438cApi.getDocType(code)
  currentDoc.value = res
  structureTree.value = buildTree(res.chapters || [])
  showStructureDialog.value = true
}

const buildTree = (chapters) => {
  return chapters.map(ch => ({
    number: ch.number,
    title: ch.title,
    required: ch.required,
    children: ch.sub_chapters ? buildTree(ch.sub_chapters) : []
  }))
}

onMounted(async () => {
  const [typeRes, catRes] = await Promise.all([
    standard438cApi.listDocTypes(),
    standard438cApi.listCategories()
  ])
  docTypes.value = typeRes.items || []
  categories.value = catRes.items || []
})
</script>

<style scoped>
.std-hero {
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
.doc-type-card {
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.2s;
}
.doc-type-card:hover {
  transform: translateY(-2px);
}
.doc-code {
  font-size: 24px;
  font-weight: bold;
  color: #59b8ff;
  margin-bottom: 8px;
}
.doc-name {
  font-size: 16px;
  font-weight: 500;
  color: #eef6ff;
  margin-bottom: 4px;
}
.doc-fullname {
  font-size: 12px;
  color: #95a7c5;
  margin-bottom: 8px;
}
.doc-desc {
  font-size: 13px;
  color: #c5d7ef;
  margin-bottom: 12px;
}
.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chapter-count {
  font-size: 12px;
  color: #95a7c5;
}
.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}
.node-number {
  color: #59b8ff;
  font-weight: 500;
}
</style>
