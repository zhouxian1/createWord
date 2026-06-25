import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
    baseURL: '/api',
    timeout: 120000,
    headers: { 'Content-Type': 'application/json' }
})

// 请求拦截
api.interceptors.request.use(config => {
    return config
}, error => {
    return Promise.reject(error)
})

// 响应拦截
api.interceptors.response.use(response => {
    return response.data
}, error => {
    const msg = error.response?.data?.error || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
})

// 项目API
export const projectApi = {
    list: () => api.get('/project/projects'),
    get: (id) => api.get(`/project/projects/${id}`),
    create: (data) => api.post('/project/projects', data),
    update: (id, data) => api.put(`/project/projects/${id}`, data),
    delete: (id) => api.delete(`/project/projects/${id}`)
}

// 知识库API
export const knowledgeApi = {
    listBases: (params) => api.get('/knowledge/bases', { params }),
    createBase: (data) => api.post('/knowledge/bases', data),
    getBase: (id) => api.get(`/knowledge/bases/${id}`),
    updateBase: (id, data) => api.put(`/knowledge/bases/${id}`, data),
    deleteBase: (id) => api.delete(`/knowledge/bases/${id}`),
    // 文件上传与导入
    uploadFiles: (id, formData) => api.post(`/knowledge/bases/${id}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000
    }),
    batchImport: (id, data) => api.post(`/knowledge/bases/${id}/batch-import`, data),
    apiImport: (id, data) => api.post(`/knowledge/bases/${id}/api-import`, data),
    incrementalImport: (id, data) => api.post(`/knowledge/bases/${id}/incremental-import`, data),
    // 文件管理
    listFiles: (id, params) => api.get(`/knowledge/bases/${id}/files`, { params }),
    getFile: (id) => api.get(`/knowledge/files/${id}`),
    deleteFile: (id) => api.delete(`/knowledge/files/${id}`),
    previewFile: (id) => api.get(`/knowledge/files/${id}/preview`),
    editFileContent: (id, data) => api.put(`/knowledge/files/${id}/edit`, data),
    // 搜索
    search: (id, data) => api.post(`/knowledge/bases/${id}/search`, data),
    getGraph: (params) => api.get('/knowledge/graph', { params }),
    // 审核流程
    reviewFile: (id, data) => api.post(`/knowledge/files/${id}/review`, data),
    rollbackFile: (id, data) => api.post(`/knowledge/files/${id}/rollback`, data),
    getFileVersions: (id) => api.get(`/knowledge/files/${id}/versions`),
    // 审核记录
    listReviewRecords: (params) => api.get('/knowledge/review-records', { params })
}

// 438C标准API
export const standard438cApi = {
    listDocTypes: (params) => api.get('/438c/document-types', { params }),
    getDocType: (code) => api.get(`/438c/document-types/${code}`),
    listCategories: () => api.get('/438c/categories'),
    listComplexityLevels: () => api.get('/438c/complexity-levels'),
    getStructure: (code) => api.get(`/438c/document-types/${code}/structure`),
    importDocument: (data) => api.post('/438c/import', data)
}

// 文档生成API
export const generationApi = {
    listDocuments: (params) => api.get('/generation/documents', { params }),
    createDocument: (data) => api.post('/generation/documents', data),
    getDocument: (id) => api.get(`/generation/documents/${id}`),
    deleteDocument: (id) => api.delete(`/generation/documents/${id}`),
    generateFull: (id, data) => api.post(`/generation/documents/${id}/generate/full`, data),
    generateByChapter: (id, data) => api.post(`/generation/documents/${id}/generate/chapter`, data),
    generateFromCode: (data) => api.post('/generation/generate/from-code', data),
    listChapters: (id) => api.get(`/generation/documents/${id}/chapters`),
    getChapter: (id) => api.get(`/generation/chapters/${id}`),
    updateChapter: (id, data) => api.put(`/generation/chapters/${id}`, data),
    getTask: (id) => api.get(`/generation/tasks/${id}`),
    exportDocument: (id) => api.post(`/generation/documents/${id}/export`),
    uploadCode: (formData) => api.post('/generation/upload-code', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

// 验证API
export const validationApi = {
    validate: (id) => api.post(`/validation/documents/${id}`),
    getResult: (id) => api.get(`/validation/documents/${id}/result`),
    listRules: (params) => api.get('/validation/rules', { params }),
    createRule: (data) => api.post('/validation/rules', data),
    updateRule: (id, data) => api.put(`/validation/rules/${id}`, data),
    deleteRule: (id) => api.delete(`/validation/rules/${id}`),
    listLevels: () => api.get('/validation/levels')
}

// 合稿API
export const mergeApi = {
    listTasks: (params) => api.get('/merge/tasks', { params }),
    createTask: (data) => api.post('/merge/tasks', data),
    executeTask: (id) => api.post(`/merge/tasks/${id}/execute`),
    getTask: (id) => api.get(`/merge/tasks/${id}`),
    deleteTask: (id) => api.delete(`/merge/tasks/${id}`),
    downloadDocument: (id) => `/api/merge/documents/${id}/download`,
    downloadFile: (filename) => `/api/merge/download/${filename}`
}

// 问答API
export const qaApi = {
    ask: (data) => api.post('/question/ask', data),
    ask438c: (data) => api.post('/question/ask-438c', data)
}

export default api
