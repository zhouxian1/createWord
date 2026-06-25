<template>
  <div class="intelligent-qa tech-page page-shell">
    <div class="page-hero qa-hero">
      <div class="page-toolbar">
        <div class="page-title-block">
          <span class="cyber-badge">AI Workspace</span>
          <h2 class="glitch-title">智能问答中心</h2>
          <div class="page-subtitle">
            统一处理知识库问答与 438C 专项问答，右侧面板可单独配置知识库、检索数量、显示溯源和语音输入状态。
          </div>
        </div>
        <div class="hero-stats">
          <div class="hero-stat">
            <span>语音输入</span>
            <strong>{{ speechSupported ? '可用' : '不可用' }}</strong>
          </div>
          <div class="hero-stat">
            <span>知识库数量</span>
            <strong>{{ knowledgeBases.length }}</strong>
          </div>
          <div class="hero-stat">
            <span>会话消息</span>
            <strong>{{ messages.length }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="qa-layout">
      <div class="qa-main">
        <el-card class="chat-card">
          <template #header>
            <div class="section-header">
              <div>
                <div class="section-title">{{ activeMode === 'general' ? '知识库问答' : '438C 专项问答' }}</div>
                <div class="section-desc">{{ activeMode === 'general' ? '结合项目知识库做检索增强问答' : '面向标准条款、章节结构和规范要求的快速问答' }}</div>
              </div>
              <div class="header-actions">
                <el-radio-group v-model="activeMode" size="small">
                  <el-radio-button
                    v-for="item in modeOptions"
                    :key="item.value"
                    :label="item.value"
                  >
                    {{ item.label }}
                  </el-radio-button>
                </el-radio-group>
                <el-button text @click="clearCurrentSession">清空当前会话</el-button>
              </div>
            </div>
          </template>

          <div v-if="activeMode === 'general'" class="chat-container">
            <div class="chat-messages" ref="messagesRef">
              <div v-for="(msg, i) in messages" :key="i" :class="['chat-message', msg.role]">
                <div class="message-avatar">
                  <el-icon :size="18"><User v-if="msg.role === 'user'" /><Monitor v-else /></el-icon>
                </div>
                <div class="message-content">
                  <div class="message-text">{{ msg.content }}</div>
                  <div v-if="showTrace && msg.source_traces && msg.source_traces.length" class="source-traces">
                    <div class="trace-header">答案溯源</div>
                    <div v-for="(trace, ti) in msg.source_traces" :key="ti" class="trace-item">
                      <el-tag size="small" :type="traceSourceType(trace.source_type)">
                        {{ traceLabel(trace.source_type) }}
                      </el-tag>
                      <span class="trace-file">{{ trace.source_file || '未知文件' }}</span>
                      <span v-if="trace.chapter_title" class="trace-chapter">{{ trace.chapter_title }}</span>
                      <span v-if="trace.entity_name" class="trace-entity">{{ trace.entity_name }}</span>
                      <span class="trace-confidence">{{ formatConfidence(trace.confidence) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="loading" class="chat-message assistant">
                <div class="message-avatar"><el-icon :size="18"><Monitor /></el-icon></div>
                <div class="message-content">
                  <div class="message-text typing">正在检索并生成回答...</div>
                </div>
              </div>
            </div>

            <div class="chat-composer">
              <div v-if="isRecordingMain" class="voice-tip">正在收音，请直接说出问题...</div>
              <el-input
                v-model="question"
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 5 }"
                :disabled="loading"
                placeholder="请输入关于项目文档、代码、知识库内容的问题"
                @keyup.enter.ctrl="sendQuestion"
              />
              <div class="chat-actions">
                <el-button @click="useQuickQuestion(activeMode)" plain>填入示例</el-button>
                <el-button @click="toggleSpeech('main')" :disabled="!speechSupported || loading" plain>
                  {{ isRecordingMain ? '停止语音' : '语音输入' }}
                </el-button>
                <el-button type="primary" @click="sendQuestion" :loading="loading">发送问题</el-button>
              </div>
            </div>
          </div>

          <div v-else class="single-answer">
            <div v-if="isRecording438c" class="voice-tip">正在收音，请说出 438C 相关问题...</div>
            <el-input
              v-model="question438c"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 5 }"
              :disabled="loading438c"
              placeholder="请输入关于 438C 文档类型、章节结构、规范要求的问题"
              @keyup.enter.ctrl="ask438c"
            />
            <div class="chat-actions single-answer__actions">
              <el-button @click="useQuickQuestion(activeMode)" plain>填入示例</el-button>
              <el-button @click="toggleSpeech('438c')" :disabled="!speechSupported || loading438c" plain>
                {{ isRecording438c ? '停止语音' : '语音输入' }}
              </el-button>
              <el-button type="primary" @click="ask438c" :loading="loading438c">开始问答</el-button>
            </div>
            <div class="answer-panel">
              <div class="answer-panel__title">回答结果</div>
              <div v-if="answer438c" class="answer-text">{{ answer438c }}</div>
              <el-empty v-else description="提交 438C 问题后，这里会显示回答内容" />
              <div v-if="showTrace && traces438c && traces438c.length" class="source-traces source-traces--block">
                <div class="trace-header">参考来源</div>
                <div v-for="(trace, ti) in traces438c" :key="ti" class="trace-item">
                  <span class="trace-file">{{ trace.source_file || trace.chapter_title || '438C 标准' }}</span>
                  <span class="trace-confidence">{{ formatConfidence(trace.confidence) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <div class="qa-side">
        <el-card class="config-card">
          <template #header>
            <div class="section-header compact">
              <div>
                <div class="section-title">问答配置</div>
                <div class="section-desc">智能问答页面可单独配置</div>
              </div>
            </div>
          </template>

          <div class="config-block">
            <div class="config-label">问答模式</div>
            <el-radio-group v-model="activeMode" class="mode-group">
              <el-radio-button label="general">知识库问答</el-radio-button>
              <el-radio-button label="438c">438C 专项</el-radio-button>
            </el-radio-group>
          </div>

          <div class="config-block">
            <div class="config-label">当前项目</div>
            <div class="config-value">{{ currentProject?.name || '未选择项目' }}</div>
          </div>

          <div class="config-block">
            <div class="config-label">目标知识库</div>
            <el-select
              v-model="selectedKnowledgeBaseId"
              placeholder="选择知识库"
              clearable
              :disabled="activeMode !== 'general'"
            >
              <el-option
                v-for="kb in knowledgeBases"
                :key="kb.id"
                :label="kb.name"
                :value="kb.id"
              />
            </el-select>
          </div>

          <div class="config-block">
            <div class="config-label">检索条数</div>
            <el-slider
              v-model="topK"
              :min="3"
              :max="10"
              :step="1"
              :disabled="activeMode !== 'general'"
              show-input
            />
          </div>

          <div class="config-block">
            <div class="config-label">结果选项</div>
            <el-switch v-model="showTrace" active-text="显示溯源" inactive-text="隐藏溯源" />
          </div>

          <div class="config-block">
            <div class="config-label">语音状态</div>
            <el-alert
              :title="speechSupported ? '当前浏览器支持语音输入' : '当前浏览器不支持语音输入'"
              :type="speechSupported ? 'success' : 'warning'"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>

        <el-card class="quick-card">
          <template #header>
            <div class="section-header compact">
              <div>
                <div class="section-title">快捷问题</div>
                <div class="section-desc">点击后可直接填入输入框</div>
              </div>
            </div>
          </template>
          <div class="quick-questions">
            <el-tag
              v-for="q in currentQuickQuestions"
              :key="q"
              class="quick-tag"
              @click="fillQuestion(q)"
            >
              {{ q }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { qaApi } from '@/api'
import { useAppStore } from '@/store'

const store = useAppStore()
const messagesRef = ref(null)
const question = ref('')
const question438c = ref('')
const answer438c = ref('')
const traces438c = ref(null)
const loading = ref(false)
const loading438c = ref(false)
const activeMode = ref('general')
const selectedKnowledgeBaseId = ref(null)
const topK = ref(5)
const showTrace = ref(true)
const recordingTarget = ref('')
let recognition = null

const defaultGeneralMessages = () => ([
  { role: 'assistant', content: '您好，我可以结合知识库内容回答项目文档、章节结构、代码实体和术语相关问题。' }
])

const messages = ref(defaultGeneralMessages())
const modeOptions = [
  { label: '知识库问答', value: 'general' },
  { label: '438C 专项', value: '438c' }
]

const generalQuickQuestions = [
  '当前知识库中与软件需求规格说明最相关的内容有哪些？',
  '项目中关于接口设计的关键约束有哪些？',
  '请总结知识库中与测试说明相关的重点条目。',
  '生成 SRS 文档时应该优先参考哪些资料？'
]

const standardQuickQuestions = [
  '438C规定了哪些文档类型？',
  'SRS文档需要包含哪些章节？',
  '如何编写功能需求？',
  '安全性需求有哪些要求？'
]

const currentProject = computed(() => store.currentProject)
const knowledgeBases = computed(() => store.knowledgeBases || [])
const speechSupported = computed(() => typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition))
const isRecordingMain = computed(() => recordingTarget.value === 'main')
const isRecording438c = computed(() => recordingTarget.value === '438c')
const currentQuickQuestions = computed(() => activeMode.value === 'general' ? generalQuickQuestions : standardQuickQuestions)

const ensureKnowledgeBases = async () => {
  if (!currentProject.value?.id) return
  await store.loadKnowledgeBases(currentProject.value.id)
  if (!selectedKnowledgeBaseId.value && knowledgeBases.value.length > 0) {
    selectedKnowledgeBaseId.value = knowledgeBases.value[0].id
  }
}

watch(() => currentProject.value?.id, async () => {
  await ensureKnowledgeBases()
})

watch(knowledgeBases, (list) => {
  if (selectedKnowledgeBaseId.value && !list.some(item => item.id === selectedKnowledgeBaseId.value)) {
    selectedKnowledgeBaseId.value = list[0]?.id || null
  }
}, { deep: true })

watch(activeMode, () => {
  stopRecognition()
})

onMounted(async () => {
  await ensureKnowledgeBases()
})

const traceSourceType = (type) => {
  const map = { military: 'warning', code_entity: 'success', general: 'info', chapter: 'primary', element: 'danger' }
  return map[type] || 'info'
}

const traceLabel = (type) => {
  const map = { military: '军标', code_entity: '代码', general: '文档', chapter: '章节', element: '要素' }
  return map[type] || '来源'
}

const formatConfidence = (value) => `${((value || 0) * 100).toFixed(1)}%`

const fillQuestion = (value) => {
  if (activeMode.value === 'general') {
    question.value = value
  } else {
    question438c.value = value
  }
}

const useQuickQuestion = (mode) => {
  const source = mode === 'general' ? generalQuickQuestions : standardQuickQuestions
  fillQuestion(source[0])
}

const stopRecognition = () => {
  if (recognition) {
    recognition.stop()
  }
  recordingTarget.value = ''
}

const toggleSpeech = (target) => {
  if (!speechSupported.value) return
  if (recordingTarget.value === target) {
    stopRecognition()
    return
  }

  if (recognition) {
    recognition.stop()
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = false
  recordingTarget.value = target

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(item => item[0].transcript)
      .join('')
      .trim()

    if (target === 'main') {
      question.value = transcript
    } else {
      question438c.value = transcript
    }
  }

  recognition.onerror = () => {
    recordingTarget.value = ''
  }

  recognition.onend = () => {
    recordingTarget.value = ''
  }

  recognition.start()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const sendQuestion = async () => {
  if (!question.value.trim() || loading.value) return

  const payload = {
    question: question.value.trim(),
    top_k: topK.value
  }
  if (selectedKnowledgeBaseId.value) {
    payload.knowledge_base_id = selectedKnowledgeBaseId.value
  }

  messages.value.push({ role: 'user', content: payload.question })
  question.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await qaApi.ask(payload)
    messages.value.push({
      role: 'assistant',
      content: res.answer || '抱歉，当前没有生成有效回答。',
      source_traces: res.source_traces || []
    })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用。' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const ask438c = async () => {
  if (!question438c.value.trim() || loading438c.value) return
  loading438c.value = true
  answer438c.value = ''
  traces438c.value = null

  try {
    const res = await qaApi.ask438c({ question: question438c.value.trim() })
    answer438c.value = res.answer || '抱歉，当前没有生成有效回答。'
    traces438c.value = res.source_traces || null
  } catch {
    answer438c.value = '抱歉，服务暂时不可用。'
  } finally {
    loading438c.value = false
  }
}

const clearCurrentSession = () => {
  if (activeMode.value === 'general') {
    messages.value = defaultGeneralMessages()
  } else {
    question438c.value = ''
    answer438c.value = ''
    traces438c.value = null
  }
}

onBeforeUnmount(() => {
  stopRecognition()
})
</script>

<style scoped>
.intelligent-qa {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100dvh - 132px);
  overflow: hidden;
}

.qa-hero {
  padding: 24px 28px;
}

.hero-stats {
  display: flex;
  gap: 12px;
}

.hero-stat {
  min-width: 120px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(115, 147, 191, 0.14);
}

.hero-stat span {
  display: block;
  font-size: 12px;
  color: var(--cp-text-dim);
  margin-bottom: 6px;
}

.hero-stat strong {
  font-size: 22px;
  color: var(--cp-text-bright);
}

.qa-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.qa-main,
.qa-side {
  min-width: 0;
  min-height: 0;
}

.chat-card {
  height: 100%;
}

.chat-card :deep(.el-card__body) {
  padding-top: 18px;
  height: calc(100% - 74px);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-header.compact {
  align-items: flex-start;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 8px;
}

.chat-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid rgba(115, 147, 191, 0.16);
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--cp-cyan);
}

.chat-message.assistant .message-avatar {
  color: var(--cp-green);
}

.message-content {
  max-width: min(76%, 760px);
}

.message-text {
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(115, 147, 191, 0.12);
  line-height: 1.8;
  white-space: pre-wrap;
  color: var(--cp-text);
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, rgba(44, 132, 232, 0.22), rgba(89, 184, 255, 0.16));
  border-color: rgba(89, 184, 255, 0.24);
}

.typing {
  color: var(--cp-text-dim);
}

.chat-composer {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(115, 147, 191, 0.12);
}

.voice-tip {
  margin-bottom: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(89, 184, 255, 0.06);
  border: 1px solid rgba(89, 184, 255, 0.16);
  color: var(--cp-cyan);
}

.chat-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.single-answer {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
  min-height: 0;
}

.single-answer__actions {
  justify-content: flex-start;
}

.answer-panel {
  margin-top: 8px;
  padding: 18px;
  border-radius: 16px;
  border: 1px solid rgba(115, 147, 191, 0.12);
  background: rgba(255, 255, 255, 0.02);
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.answer-panel__title {
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--cp-text-bright);
}

.answer-text {
  white-space: pre-wrap;
  line-height: 1.9;
  color: var(--cp-text);
}

.config-card,
.quick-card {
  margin-bottom: 20px;
}

.qa-side {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.config-card {
  flex: 1;
  min-height: 0;
}

.config-card :deep(.el-card__body) {
  overflow-y: auto;
  max-height: calc(100% - 72px);
}

.config-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.config-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--cp-text-bright);
}

.config-value {
  min-height: 40px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(115, 147, 191, 0.12);
  color: var(--cp-text);
}

.mode-group {
  width: 100%;
}

.mode-group :deep(.el-radio-button__inner) {
  min-width: 110px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-tag {
  cursor: pointer;
}

.source-traces {
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(115, 147, 191, 0.16);
}

.source-traces--block {
  margin-top: 18px;
}

.trace-header {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--cp-text-dim);
}

.trace-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--cp-text);
  margin-bottom: 6px;
}

.trace-file {
  color: var(--cp-cyan);
}

.trace-chapter {
  color: var(--cp-orange);
}

.trace-entity {
  color: var(--cp-green);
}

.trace-confidence {
  margin-left: auto;
  color: var(--cp-text-dim);
}

@media (max-width: 1280px) {
  .intelligent-qa {
    height: auto;
    overflow: visible;
  }

  .qa-layout {
    grid-template-columns: 1fr;
  }

  .chat-container,
  .single-answer {
    height: auto;
  }

  .chat-card :deep(.el-card__body),
  .config-card :deep(.el-card__body) {
    height: auto;
    max-height: none;
    overflow: visible;
  }
}
</style>
