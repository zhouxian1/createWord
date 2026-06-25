import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/ProjectList.vue'),
        meta: { title: '项目管理' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/KnowledgeBase.vue'),
        meta: { title: '知识库管理' }
      },
      {
        path: 'knowledge/:id',
        name: 'KnowledgeDetail',
        component: () => import('@/views/KnowledgeDetail.vue'),
        meta: { title: '知识库详情' }
      },
      {
        path: 'knowledge-graph',
        name: 'KnowledgeGraph',
        component: () => import('@/views/KnowledgeGraph.vue'),
        meta: { title: '知识图谱' }
      },
      {
        path: '438c',
        name: 'Standard438C',
        component: () => import('@/views/Standard438C.vue'),
        meta: { title: '438C标准' }
      },
      {
        path: 'generation',
        name: 'Generation',
        component: () => import('@/views/DocumentGeneration.vue'),
        meta: { title: '文档生成' }
      },
      {
        path: 'generation/:id',
        name: 'DocumentDetail',
        component: () => import('@/views/DocumentDetail.vue'),
        meta: { title: '文档详情' }
      },
      {
        path: 'validation',
        name: 'Validation',
        component: () => import('@/views/ValidationCenter.vue'),
        meta: { title: '质量验证' }
      },
      {
        path: 'merge',
        name: 'Merge',
        component: () => import('@/views/DocumentMerge.vue'),
        meta: { title: '文档合稿' }
      },
      {
        path: 'qa',
        name: 'QA',
        component: () => import('@/views/IntelligentQA.vue'),
        meta: { title: '智能问答' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
