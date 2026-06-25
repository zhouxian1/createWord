"""知识图谱可视化页面：基于 D3 力导向图展示全量 438C 领域图谱。"""

<template>
  <div class="knowledge-graph-page tech-page">
    <el-card class="page-hero">
      <div class="hero-content">
        <div>
          <div class="hero-title">知识图谱可视化</div>
          <div class="hero-subtitle">D3 力导向图渲染 438C 文档实体关系，支持实体搜索与深度过滤</div>
        </div>
        <div class="hero-actions">
          <el-input
            v-model="entityName"
            placeholder="按实体名称过滤，例如：SRS / 软件需求 / BugFix"
            clearable
            style="width: 320px"
            @keyup.enter="loadGraph"
          >
            <template #append>
              <el-button type="primary" @click="loadGraph">查询</el-button>
            </template>
          </el-input>
          <el-select v-model="depth" style="width: 120px" @change="loadGraph">
            <el-option :value="1" label="1层关系" />
            <el-option :value="2" label="2层关系" />
            <el-option :value="3" label="3层关系" />
          </el-select>
          <el-button @click="loadGraph" :loading="loading">刷新图谱</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="17">
        <el-card class="graph-card">
          <template #header>
            <div class="card-header">
              <span>图谱主视图</span>
              <div class="legend">
                <span class="legend-item"><span class="dot" style="background:#56b8ff"></span>文档</span>
                <span class="legend-item"><span class="dot" style="background:#5ff0c2"></span>章节</span>
                <span class="legend-item"><span class="dot" style="background:#ffb860"></span>代码实体</span>
                <span class="legend-item"><span class="dot" style="background:#ff7db8"></span>术语</span>
              </div>
            </div>
          </template>
          <KnowledgeGraphD3 v-if="hasNodes" :graph="graphData" :height="560" />
          <el-empty v-else-if="!loading" description="暂无图谱数据，请先在知识库中导入文档或选择实体进行过滤" />
        </el-card>
      </el-col>
      <el-col :span="7">
        <el-card class="metrics-card">
          <template #header><span>图谱概览</span></template>
          <div class="metric-grid">
            <div class="metric">
              <div class="metric-label">实体数量</div>
              <div class="metric-value">{{ stats.entityCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">关系数量</div>
              <div class="metric-value">{{ stats.relationCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">文档节点</div>
              <div class="metric-value">{{ stats.documentCount }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">术语节点</div>
              <div class="metric-value">{{ stats.termCount }}</div>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 16px" class="tips-card">
          <template #header><span>使用说明</span></template>
          <ul class="tips">
            <li>支持鼠标拖拽节点、滚轮缩放视图、双击节点可居中聚焦。</li>
            <li>在输入框中输入实体名称可按 BFS 范围查询其相邻节点。</li>
            <li>底层默认使用本地 JSON 持久化，配置 Neo4j 后会自动同步至图数据库。</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { knowledgeApi } from '@/api'
import KnowledgeGraphD3 from '@/components/KnowledgeGraphD3.vue'

const entityName = ref('')
const depth = ref(2)
const loading = ref(false)
const rawData = ref({ entities: {}, relations: [] })
const graphData = ref({ nodes: [], links: [] })

const stats = reactive({
  entityCount: 0,
  relationCount: 0,
  documentCount: 0,
  termCount: 0
})

const hasNodes = computed(() => graphData.value.nodes.length > 0)

const buildGraph = (data) => {
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
  stats.entityCount = graphData.value.nodes.length
  stats.relationCount = graphData.value.links.length
  stats.documentCount = graphData.value.nodes.filter(item => item.type === 'document').length
  stats.termCount = graphData.value.nodes.filter(item => item.type === 'term').length
}

const loadGraph = async () => {
  loading.value = true
  try {
    const params = entityName.value
      ? { entity_name: entityName.value.trim(), depth: depth.value }
      : { depth: depth.value }
    const res = await knowledgeApi.getGraph(params)
    rawData.value = res
    buildGraph(res)
  } catch (error) {
    ElMessage.error('加载图谱失败：' + (error?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

onMounted(loadGraph)
</script>

<style scoped>
.page-hero {
  border-radius: 22px !important;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.hero-title {
  font-size: 22px;
  font-weight: 700;
  color: #eef6ff;
}

.hero-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #95a7c5;
  max-width: 540px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.graph-card :deep(.el-card__body),
.metrics-card :deep(.el-card__body),
.tips-card :deep(.el-card__body) {
  background: rgba(8, 16, 34, 0.6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #eef6ff;
}

.legend {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #95a7c5;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric {
  padding: 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(89, 184, 255, 0.12), rgba(109, 247, 193, 0.08));
  border: 1px solid rgba(116, 170, 255, 0.18);
}

.metric-label {
  font-size: 12px;
  color: #95a7c5;
}

.metric-value {
  margin-top: 6px;
  font-size: 22px;
  font-weight: 700;
  color: #eef6ff;
}

.tips {
  margin: 0;
  padding-left: 18px;
  color: #95a7c5;
  font-size: 13px;
  line-height: 1.8;
}
</style>