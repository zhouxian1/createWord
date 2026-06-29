<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '76px' : '248px'" class="layout-aside">
      <div class="logo">
        <div class="logo-mark">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div v-show="!isCollapse" class="logo-copy">
          <span class="logo-text">438C 文档平台</span>
          <span class="logo-subtitle">Knowledge · Generation · QA</span>
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

    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <div class="page-meta">
            <div class="page-title">{{ currentRoute?.meta?.title || '系统首页' }}</div>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRoute?.meta?.title || '' }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        <div class="header-right">
          <el-tag v-if="currentProject" size="small" type="info">
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
  background: transparent;
}

.layout-aside {
  background: linear-gradient(180deg, #111821 0%, #182231 48%, #101720 100%);
  transition: width 0.3s;
  overflow: hidden;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 16px 0 44px rgba(18, 24, 32, 0.14);
  position: relative;
}

.logo {
  min-height: 82px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: #fff;
  gap: 12px;
  padding: 18px 18px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-mark {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(185, 145, 75, 0.28), rgba(255, 255, 255, 0.06));
  color: #f4d38a;
  border: 1px solid rgba(185, 145, 75, 0.36);
}

.logo-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  white-space: nowrap;
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
}

.logo-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.58);
  line-height: 1.4;
}

.project-select {
  padding: 14px 12px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.project-select :deep(.el-select) {
  width: 100%;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(45, 61, 82, 0.1);
  background: rgba(255, 255, 255, 0.82);
  padding: 0 30px;
  backdrop-filter: blur(16px);
  position: relative;
  z-index: 2;
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
  color: var(--cp-text-bright);
  font-size: 18px;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collapse-btn {
  cursor: pointer;
  font-size: 20px;
  color: var(--cp-slate);
  transition: color 0.2s ease;
}

.collapse-btn:hover {
  color: var(--cp-cyan);
}

.layout-main {
  padding: 26px 30px 30px;
  overflow-y: auto;
}

.el-menu {
  border-right: none;
}

@media (max-width: 960px) {
  .layout-aside {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 5;
  }

  .layout-header {
    padding: 0 18px;
  }

  .layout-main {
    padding: 18px;
  }
}
</style>
