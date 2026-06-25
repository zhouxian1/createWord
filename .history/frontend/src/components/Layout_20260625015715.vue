<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <div class="logo-mark">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div v-show="!isCollapse" class="logo-copy">
          <span class="logo-text">文档生成系统</span>
          <span class="logo-subtitle">Knowledge Fabric Engine</span>
        </div>
      </div>

      <!-- 项目选择 -->
      <div class="project-select" v-show="!isCollapse">
        <el-select v-model="currentProjectId" placeholder="选择项目" size="small" @change="onProjectChange">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#1d1e1f"
        text-color="#bfcbd9"
        active-text-color="#409eff"
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
          <template #title>知识库管理</template>
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

    <!-- 主内容区 -->
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
          <span class="system-pill">AI + Graph + Docs</span>
          <el-tag v-if="currentProject" type="primary" size="small">
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

.layout-aside {
  background:
    linear-gradient(180deg, rgba(7, 16, 30, 0.95), rgba(7, 14, 24, 0.92)),
    linear-gradient(135deg, rgba(89, 184, 255, 0.08), transparent 36%);
  transition: width 0.3s;
  overflow: hidden;
  border-right: 1px solid rgba(116, 170, 255, 0.14);
  backdrop-filter: blur(18px);
}

.logo {
  height: 74px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: #fff;
  gap: 10px;
  padding: 0 18px;
  border-bottom: 1px solid rgba(116, 170, 255, 0.12);
}

.logo-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(89, 184, 255, 0.95), rgba(109, 247, 193, 0.75));
  box-shadow: 0 0 24px rgba(89, 184, 255, 0.35);
}

.logo-copy {
  display: flex;
  flex-direction: column;
}

.logo-text {
  white-space: nowrap;
  font-size: 16px;
  font-weight: 700;
}

.logo-subtitle {
  font-size: 11px;
  color: #8eb0d8;
  letter-spacing: 0.08em;
}

.project-select {
  padding: 12px;
  border-bottom: 1px solid rgba(116, 170, 255, 0.1);
}

.project-select :deep(.el-select) {
  width: 100%;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(116, 170, 255, 0.12);
  background: rgba(8, 18, 35, 0.48);
  padding: 0 24px;
  backdrop-filter: blur(18px);
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
  color: #eef6ff;
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.system-pill {
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: #d8e8ff;
  background: linear-gradient(135deg, rgba(89, 184, 255, 0.14), rgba(154, 124, 255, 0.12));
  border: 1px solid rgba(116, 170, 255, 0.2);
}

.collapse-btn {
  cursor: pointer;
  font-size: 20px;
  color: #8eb0d8;
}

.collapse-btn:hover {
  color: #59b8ff;
}

.layout-main {
  padding: 24px;
  overflow-y: auto;
}

.el-menu {
  border-right: none;
}
</style>
