<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside circuit-bg">
      <div class="logo">
        <div class="logo-mark">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div v-show="!isCollapse" class="logo-copy">
          <span class="logo-text">DOC//GEN</span>
          <span class="logo-subtitle">CYBER ENGINE v4.38</span>
        </div>
      </div>

      <div class="project-select" v-show="!isCollapse">
        <el-select v-model="currentProjectId" placeholder="选择项目" size="small" @change="onProjectChange">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Collection /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        <el-menu-item index="/knowledge-graph">
          <el-icon><DataLine /></el-icon>
          <template #title>知识图谱</template>
        </el-menu-item>
        <el-menu-item index="/438c">
          <el-icon><Notebook /></el-icon>
          <template #title>438C标准</template>
        </el-menu-item>
        <el-menu-item index="/generation">
          <el-icon><EditPen /></el-icon>
          <template #title>文档生成</template>
        </el-menu-item>
        <el-menu-item index="/validation">
          <el-icon><CircleCheck /></el-icon>
          <template #title>质量验证</template>
        </el-menu-item>
        <el-menu-item index="/merge">
          <el-icon><CopyDocument /></el-icon>
          <template #title>文档合稿</template>
        </el-menu-item>
        <el-menu-item index="/qa">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>智能问答</template>
        </el-menu-item>
      </el-menu>

      <div class="aside-scanline"></div>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <div class="page-meta">
            <div class="page-title">{{ currentRoute?.meta?.title || 'SYSTEM' }}</div>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">HOME</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRoute?.meta?.title || '' }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        <div class="header-right">
          <span class="system-pill">AI + GRAPH + DOCS</span>
          <el-tag v-if="currentProject" size="small">
            {{ currentProject.name }}
          </el-tag>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store'
import { projectApi } from '@/api'

const route = useRoute()
const store = useAppStore()
const isCollapse = ref(false)
const projects = ref([])
const currentProjectId = ref(null)

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)
const currentProject = computed(() => store.currentProject)
const PROJECT_STORAGE_KEY = 'doc-gen-current-project-id'

onMounted(async () => {
  const res = await projectApi.list()
  projects.value = res.items || []
  if (projects.value.length > 0) {
    const savedId = Number(localStorage.getItem(PROJECT_STORAGE_KEY))
    const preferredProject = projects.value.find(item => item.id === savedId) || projects.value[0]
    currentProjectId.value = preferredProject.id
    store.setCurrentProject(preferredProject)
  }
})

const onProjectChange = (id) => {
  const project = projects.value.find(p => p.id === id)
  if (project) {
    store.setCurrentProject(project)
    localStorage.setItem(PROJECT_STORAGE_KEY, String(project.id))
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  position: relative;
  z-index: 1;
}

/* ── 侧边栏 ── */
.layout-aside {
  background:
    linear-gradient(180deg, rgba(3, 6, 12, 0.98), rgba(3, 6, 12, 0.95)),
    linear-gradient(135deg, rgba(0, 240, 255, 0.04), transparent 40%);
  transition: width 0.3s;
  overflow: hidden;
  border-right: 1px solid var(--cp-border);
  backdrop-filter: blur(20px);
  position: relative;
}

/* 扫描线动画 */
.aside-scanline {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--cp-cyan), transparent);
  opacity: 0.15;
  animation: scan-line 8s linear infinite;
  pointer-events: none;
}

/* ── Logo ── */
.logo {
  height: 74px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: #fff;
  gap: 10px;
  padding: 0 18px;
  border-bottom: 1px solid var(--cp-border);
}

.logo-mark {
  width: 38px;
  height: 38px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--cp-cyan), var(--cp-magenta));
  box-shadow: var(--cp-glow-cyan);
  animation: neon-pulse 3s ease-in-out infinite;
}

.logo-copy {
  display: flex;
  flex-direction: column;
}

.logo-text {
  white-space: nowrap;
  font-size: 16px;
  font-weight: 700;
  font-family: 'Orbitron', var(--cp-font);
  color: var(--cp-cyan);
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
  letter-spacing: 0.1em;
}

.logo-subtitle {
  font-size: 10px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
  letter-spacing: 0.12em;
}

/* ── 项目选择 ── */
.project-select {
  padding: 12px;
  border-bottom: 1px solid var(--cp-border);
}

.project-select :deep(.el-select) {
  width: 100%;
}

/* ── Header ── */
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--cp-border);
  background: rgba(3, 6, 12, 0.6);
  padding: 0 24px;
  backdrop-filter: blur(20px);
  position: relative;
}

.layout-header::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--cp-cyan), var(--cp-magenta), transparent);
  background-size: 200% 100%;
  animation: border-flow 4s linear infinite;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  color: var(--cp-cyan);
  font-size: 16px;
  font-weight: 700;
  font-family: 'Orbitron', var(--cp-font);
  letter-spacing: 0.06em;
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.system-pill {
  padding: 6px 12px;
  border-radius: 2px;
  font-size: 11px;
  font-family: 'Share Tech Mono', var(--cp-font);
  color: var(--cp-cyan);
  background: rgba(0, 240, 255, 0.06);
  border: 1px solid rgba(0, 240, 255, 0.2);
  text-shadow: 0 0 6px rgba(0, 240, 255, 0.4);
  letter-spacing: 0.1em;
}

.collapse-btn {
  cursor: pointer;
  font-size: 20px;
  color: var(--cp-text-dim);
  transition: all 0.2s;
}

.collapse-btn:hover {
  color: var(--cp-cyan);
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

.layout-main {
  padding: 24px;
  overflow-y: auto;
}

.el-menu {
  border-right: none;
}
</style>
