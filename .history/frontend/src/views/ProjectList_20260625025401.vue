<template>
  <div class="project-list tech-page">
    <el-card class="proj-hero">
      <div class="hero-row">
        <div>
          <div class="hero-badge">PROJECT MANAGEMENT</div>
          <h2 class="hero-title">项目管理</h2>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>新建项目
        </el-button>
      </div>
    </el-card>

    <el-card>

      <el-table :data="projects" stripe>
        <el-table-column prop="name" label="项目名称" min-width="150" />
        <el-table-column prop="system_name" label="系统名称" min-width="120" />
        <el-table-column prop="system_version" label="系统版本" width="100" />
        <el-table-column prop="organization" label="编制单位" min-width="120" />
        <el-table-column prop="document_count" label="文档数" width="80" />
        <el-table-column prop="knowledge_base_count" label="知识库" width="80" />
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editProject(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProject(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingProject ? '编辑项目' : '新建项目'" width="500px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="项目名称" required>
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="系统名称">
          <el-input v-model="formData.system_name" placeholder="请输入系统名称" />
        </el-form-item>
        <el-form-item label="系统版本">
          <el-input v-model="formData.system_version" placeholder="请输入系统版本" />
        </el-form-item>
        <el-form-item label="编制单位">
          <el-input v-model="formData.organization" placeholder="请输入编制单位" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { projectApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const projects = ref([])
const showCreateDialog = ref(false)
const editingProject = ref(null)
const formData = ref({
  name: '', system_name: '', system_version: '', organization: '', description: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadProjects = async () => {
  const res = await projectApi.list()
  projects.value = res.items || []
}

const editProject = (row) => {
  editingProject.value = row
  formData.value = { ...row }
  showCreateDialog.value = true
}

const submitProject = async () => {
  if (!formData.value.name) {
    ElMessage.warning('请输入项目名称')
    return
  }
  if (editingProject.value) {
    await projectApi.update(editingProject.value.id, formData.value)
    ElMessage.success('更新成功')
  } else {
    await projectApi.create(formData.value)
    ElMessage.success('创建成功')
  }
  showCreateDialog.value = false
  editingProject.value = null
  formData.value = { name: '', system_name: '', system_version: '', organization: '', description: '' }
  loadProjects()
}

const deleteProject = async (row) => {
  await ElMessageBox.confirm(`确定删除项目"${row.name}"？`, '提示', { type: 'warning' })
  await projectApi.delete(row.id)
  ElMessage.success('删除成功')
  loadProjects()
}

onMounted(loadProjects)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
