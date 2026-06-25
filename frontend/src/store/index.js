import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectApi, generationApi, knowledgeApi } from '@/api'

export const useAppStore = defineStore('app', () => {
  const currentProject = ref(null)
  const projects = ref([])
  const documents = ref([])
  const knowledgeBases = ref([])

  async function loadProjects() {
    const res = await projectApi.list()
    projects.value = res.items || []
  }

  async function loadDocuments(projectId) {
    const res = await generationApi.listDocuments({ project_id: projectId })
    documents.value = res.items || []
  }

  async function loadKnowledgeBases(projectId) {
    const res = await knowledgeApi.listBases({ project_id: projectId })
    knowledgeBases.value = res.items || []
  }

  function setCurrentProject(project) {
    currentProject.value = project
  }

  return {
    currentProject,
    projects,
    documents,
    knowledgeBases,
    loadProjects,
    loadDocuments,
    loadKnowledgeBases,
    setCurrentProject
  }
})
