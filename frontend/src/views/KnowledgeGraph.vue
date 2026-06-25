<template>
  <div class="knowledge-graph-page cyber-page circuit-bg">
    <!-- 顶部操作栏 -->
    <div class="hero holo-panel">
      <div class="hero-content">
        <div>
          <div class="cyber-badge">KNOWLEDGE GRAPH</div>
          <h2 class="glitch-title" style="margin-top: 10px; font-size: 22px;">知识图谱可视化</h2>
        </div>
        <div class="hero-actions">
          <el-input
            v-model="entityName"
            placeholder="按实体名称过滤"
            clearable
            style="width: 220px"
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
          <el-button @click="loadGraph" :loading="loading">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
          <el-button @click="toggleFullscreen" :type="isFullscreen ? 'warning' : 'primary'">
            <el-icon><FullScreen v-if="!isFullscreen" /><Close v-else /></el-icon>
            {{ isFullscreen ? '退出全屏' : '全屏' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计条 -->
    <div class="stat-bar">
      <div class="stat-chip" v-for="s in statItems" :key="s.label">
        <span class="stat-dot" :style="{ background: s.color, boxShadow: `0 0 8px ${s.color}` }"></span>
        <span class="stat-label">{{ s.label }}</span>
        <span class="stat-num">{{ s.value }}</span>
      </div>
    </div>

    <!-- 图谱主区域 -->
    <div ref="graphContainerRef" class="graph-wrapper holo-panel" :class="{ 'is-fullscreen': isFullscreen }">
      <div class="graph-toolbar">
        <div class="legend">
          <span class="legend-item"><span class="dot" style="background:#00f0ff"></span>文档</span>
          <span class="legend-item"><span class="dot" style="background:#39ff14"></span>章节</span>
          <span class="legend-item"><span class="dot" style="background:#ff8c00"></span>代码实体</span>
          <span class="legend-item"><span class="dot" style="background:#ff2d95"></span>术语</span>
          <span class="legend-item"><span class="dot" style="background:#b44dff"></span>其他</span>
        </div>
        <div class="toolbar-actions">
          <el-button size="small" text @click="zoomIn"><el-icon><ZoomIn /></el-icon></el-button>
          <el-button size="small" text @click="zoomOut"><el-icon><ZoomOut /></el-icon></el-button>
          <el-button size="small" text @click="resetZoom"><el-icon><Aim /></el-icon></el-button>
        </div>
      </div>
      <div class="neon-divider" style="margin: 0 20px;"></div>
      <div class="graph-body">
        <KnowledgeGraphD3
          v-if="hasNodes"
          ref="graphD3Ref"
          :graph="graphData"
          :height="graphHeight"
        />
        <el-empty v-else-if="!loading" description="暂无图谱数据，请先在知识库中导入文档或选择实体进行过滤" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { FullScreen, Close, Refresh, ZoomIn, ZoomOut, Aim } from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'
import KnowledgeGraphD3 from '@/components/KnowledgeGraphD3.vue'

const entityName = ref('')
const depth = ref(2)
const loading = ref(false)
const rawData = ref({ entities: {}, relations: [] })
const graphData = ref({ nodes: [], links: [] })
const isFullscreen = ref(false)
const graphContainerRef = ref(null)
const graphD3Ref = ref(null)

const stats = reactive({
  entityCount: 0,
  relationCount: 0,
  documentCount: 0,
  termCount: 0,
  chapterCount: 0,
  codeCount: 0
})

const statItems = computed(() => [
  { label: '实体', value: stats.entityCount, color: '#00f0ff' },
  { label: '关系', value: stats.relationCount, color: '#b44dff' },
  { label: '文档', value: stats.documentCount, color: '#00f0ff' },
  { label: '章节', value: stats.chapterCount, color: '#39ff14' },
  { label: '代码', value: stats.codeCount, color: '#ff8c00' },
  { label: '术语', value: stats.termCount, color: '#ff2d95' }
])

const graphHeight = computed(() => {
  if (isFullscreen.value) return window.innerHeight - 120
  return 580
})

const hasNodes = computed(() => graphData.value.nodes.length > 0)

/* ── 关系类型英文→中文映射 ── */
const relationLabelMap = {
  contains_chapter: '包含章节',
  contains_subchapter: '包含子章节',
  used_in_chapter: '用于章节',
  maps_to_chapter: '映射到章节',
  references: '引用',
  depends_on: '依赖',
  implements: '实现',
  traces_to: '追溯至',
  validates: '验证',
  related_to: '关联'
}

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
    links: relations.map(item => {
      const rawLabel = item.type || item.relation || ''
      return {
        source: item.source,
        target: item.target,
        label: relationLabelMap[rawLabel] || rawLabel
      }
    })
  }
  stats.entityCount = graphData.value.nodes.length
  stats.relationCount = graphData.value.links.length
  stats.documentCount = graphData.value.nodes.filter(item => item.type === 'document').length
  stats.chapterCount = graphData.value.nodes.filter(item => item.type === 'chapter').length
  stats.codeCount = graphData.value.nodes.filter(item => item.type === 'code_entity').length
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

/* ── 全屏 ── */
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

/* ── 缩放控制 ── */
const zoomIn = () => graphD3Ref.value?.zoomIn()
const zoomOut = () => graphD3Ref.value?.zoomOut()
const resetZoom = () => graphD3Ref.value?.resetZoom()

const onKeydown = (e) => {
  if (e.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
    document.body.style.overflow = ''
  }
}

onMounted(() => {
  loadGraph()
  document.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.hero {
  padding: 20px 24px;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── 统计条 ── */
.stat-bar {
  display: flex;
  gap: 6px;
  padding: 0 4px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(0, 240, 255, 0.04);
  border: 1px solid rgba(0, 240, 255, 0.12);
  border-radius: 2px;
  font-family: 'Share Tech Mono', var(--cp-font);
}

.stat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.stat-label {
  font-size: 11px;
  color: var(--cp-text-dim);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stat-num {
  font-size: 16px;
  font-weight: 700;
  color: var(--cp-cyan);
  font-family: 'Orbitron', var(--cp-font);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

/* ── 图谱主区域 ── */
.graph-wrapper {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.graph-wrapper.is-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 3000;
  border-radius: 0;
  border: none;
  margin: 0;
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
}

.legend {
  display: flex;
  gap: 14px;
  font-size: 11px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 6px currentColor;
}

.toolbar-actions {
  display: flex;
  gap: 2px;
}

.graph-body {
  padding: 8px 20px 20px;
}

/* ── 全屏时隐藏页面其他部分 ── */
.graph-wrapper.is-fullscreen ~ * {
  display: none !important;
}
</style>
