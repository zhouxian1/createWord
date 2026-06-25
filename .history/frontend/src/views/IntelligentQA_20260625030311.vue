<template>
  <div class="intelligent-qa cyber-page circuit-bg">
    <div class="qa-hero holo-panel">
      <div class="qa-hero__content">
        <div>
          <div class="cyber-badge">MULTIMODAL QA</div>
          <h2 class="glitch-title" style="margin-top: 10px; font-size: 22px;">智能问答</h2>
        </div>
        <div class="qa-hero__status">
          <div class="status-item">
            <span>语音输入</span>
            <strong>{{ speechSupported ? '可用' : '不支持' }}</strong>
          </div>
          <div class="status-item">
            <span>会话消息</span>
            <strong>{{ messages.length }}</strong>
          </div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="section-header">
              <span>知识库问答</span>
              <div class="header-actions">
                <el-button text @click="clearMessages">清空会话</el-button>
                <el-button
                  :type="isRecordingMain ? 'danger' : 'primary'"
                  plain
                  :disabled="!speechSupported || loading"
                  @click="toggleSpeech('main')"
                >
                  {{ isRecordingMain ? '停止语音' : '语音输入' }}
                </el-button>
              </div>
            </div>
          </template>
          <div class="chat-container">
            <div class="chat-messages" ref="messagesRef">
              <div v-for="(msg, i) in messages" :key="i" :class="['chat-message', msg.role]">
                <div class="message-avatar">
                  <el-icon :size="20"><User v-if="msg.role === 'user'" /><Monitor v-else /></el-icon>
                </div>
                <div class="message-content">
                  <div class="message-text">{{ msg.content }}</div>
                  <div v-if="msg.source_traces && msg.source_traces.length" class="source-traces">
                    <div class="trace-header">答案溯源:</div>
                    <div v-for="(trace, ti) in msg.source_traces" :key="ti" class="trace-item">
                      <el-tag size="small" :type="traceSourceType(trace.source_type)">
                        {{ trace.source_type === 'code_entity' ? '代码' : trace.source_type === 'military' ? '军标' : '文档' }}
                      </el-tag>
                      <span class="trace-file">{{ trace.source_file || '未知文件' }}</span>
                      <span v-if="trace.chapter_title" class="trace-chapter">{{ trace.chapter_title }}</span>
                      <span v-if="trace.entity_name" class="trace-entity">{{ trace.entity_name }} ({{ trace.entity_type }})</span>
                      <span class="trace-confidence">{{ (trace.confidence * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="loading" class="chat-message assistant">
                <div class="message-avatar"><el-icon :size="20"><Monitor /></el-icon></div>
                <div class="message-content">
                  <div class="message-text typing">正在思考中...</div>
                </div>
              </div>
            </div>
            <div class="chat-input">
              <div v-if="isRecordingMain" class="voice-tip">正在收音，请直接说出问题...</div>
              <el-input
                v-model="question"
                placeholder="输入您的问题..."
                @keyup.enter="sendQuestion"
                :disabled="loading"
                type="textarea"
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
              <div class="chat-actions">
                <el-button @click="toggleSpeech('main')" :disabled="!speechSupported || loading" plain>
                  {{ isRecordingMain ? '停止语音' : '语音转文字' }}
                </el-button>
                <el-button type="primary" @click="sendQuestion" :loading="loading">发送</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="section-header">
              <span>438C标准问答</span>
              <el-button
                :type="isRecording438c ? 'danger' : 'primary'"
                plain
                :disabled="!speechSupported || loading438c"
                @click="toggleSpeech('438c')"
              >
                {{ isRecording438c ? '停止语音' : '语音输入' }}
              </el-button>
            </div>
          </template>
          <div v-if="isRecording438c" class="voice-tip">正在收音，请说出 438C 相关问题...</div>
          <el-input
            v-model="question438c"
            placeholder="输入关于438C标准的问题..."
            @keyup.enter="ask438c"
            :disabled="loading438c"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
          />
          <div class="chat-actions compact">
            <el-button @click="toggleSpeech('438c')" :disabled="!speechSupported || loading438c" plain>
              {{ isRecording438c ? '停止语音' : '语音转文字' }}
            </el-button>
            <el-button type="primary" @click="ask438c" :loading="loading438c">提问</el-button>
          </div>
          <div v-if="answer438c" class="answer-438c">
            <div class="answer-label">回答：</div>
            <div class="answer-text">{{ answer438c }}</div>
          </div>
          <div v-if="traces438c && traces438c.length" class="source-traces" style="margin-top:8px">
            <div class="trace-header">溯源:</div>
            <div v-for="(trace, ti) in traces438c" :key="ti" class="trace-item">
              <span class="trace-file">{{ trace.source_file || trace.chapter_title || '438C标准' }}</span>
              <span class="trace-confidence">{{ (trace.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header><span>快捷问题</span></template>
          <div class="quick-questions">
            <el-tag
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              @click="question = q"
            >{{ q }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import { qaApi } from '@/api'

const messages = ref([
  { role: 'assistant', content: '您好！我是文档生成系统的智能助手，可以回答关于知识库内容和438C标准的问题。请问有什么可以帮助您的？' }
])
const question = ref('')
const loading = ref(false)
const messagesRef = ref(null)

const question438c = ref('')
const answer438c = ref('')
const traces438c = ref(null)
const loading438c = ref(false)
const recordingTarget = ref('')
let recognition = null

const quickQuestions = [
  '438C规定了哪些文档类型？',
  'SRS文档需要包含哪些章节？',
  '如何编写功能需求？',
  '安全性需求有哪些要求？',
  '文档验证包括哪些规则？'
]

const speechSupported = computed(() => {
  return typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition)
})

const isRecordingMain = computed(() => recordingTarget.value === 'main')
const isRecording438c = computed(() => recordingTarget.value === '438c')

const traceSourceType = (type) => {
  const map = { military: 'warning', code_entity: 'success', general: 'info', chapter: '', element: 'danger' }
  return map[type] || 'info'
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

const sendQuestion = async () => {
  if (!question.value.trim() || loading.value) return

  const q = question.value
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true

  try {
    const res = await qaApi.ask({ question: q })
    const msg = { role: 'assistant', content: res.answer || '抱歉，无法回答此问题。' }
    if (res.source_traces && res.source_traces.length) {
      msg.source_traces = res.source_traces
    }
    messages.value.push(msg)
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用。' })
  } finally {
    loading.value = false
    await nextTick()
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }
}

const ask438c = async () => {
  if (!question438c.value.trim() || loading438c.value) return
  loading438c.value = true
  answer438c.value = ''
  traces438c.value = null

  try {
    const res = await qaApi.ask438c({ question: question438c.value })
    answer438c.value = res.answer || '抱歉，无法回答此问题。'
    if (res.source_traces && res.source_traces.length) {
      traces438c.value = res.source_traces
    }
  } catch {
    answer438c.value = '抱歉，服务暂时不可用。'
  } finally {
    loading438c.value = false
  }
}

const clearMessages = () => {
  messages.value = [
    { role: 'assistant', content: '您好！我是文档生成系统的智能助手，可以回答关于知识库内容和438C标准的问题。请问有什么可以帮助您的？' }
  ]
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
}

.qa-hero__content {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
}

.qa-hero__tag {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(89, 184, 255, 0.1);
  border: 1px solid rgba(89, 184, 255, 0.2);
  color: #9dd8ff;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.qa-hero h2 {
  margin-top: 12px;
  color: #eef6ff;
}

.qa-hero__status {
  display: flex;
  gap: 12px;
}

.status-item {
  min-width: 150px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(116, 170, 255, 0.12);
}

.status-item span {
  display: block;
  color: #8daed6;
  font-size: 12px;
  margin-bottom: 8px;
}

.status-item strong {
  color: #eef6ff;
  font-size: 22px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 620px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-message.user .message-avatar {
  background: #409eff;
  color: #fff;
}

.chat-message.assistant .message-avatar {
  background: #67c23a;
  color: #fff;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.06);
  line-height: 1.6;
  font-size: 14px;
  color: #eef6ff;
  border: 1px solid rgba(116, 170, 255, 0.08);
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, rgba(27, 143, 255, 0.9), rgba(70, 196, 255, 0.9));
  color: #fff;
}

.typing {
  color: #97a9c7;
  font-style: italic;
}

.chat-input {
  padding-top: 16px;
  border-top: 1px solid rgba(116, 170, 255, 0.12);
}

.voice-tip {
  margin-bottom: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  color: #9bd7ff;
  background: rgba(89, 184, 255, 0.08);
  border: 1px solid rgba(89, 184, 255, 0.14);
}

.chat-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.chat-actions.compact {
  justify-content: flex-start;
}

.answer-438c {
  margin-top: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 14px;
  border: 1px solid rgba(116, 170, 255, 0.1);
}

.answer-label {
  font-weight: 500;
  margin-bottom: 8px;
  color: #eef6ff;
}

.answer-text {
  font-size: 14px;
  line-height: 1.6;
  color: #c5d7ef;
  white-space: pre-wrap;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-tag {
  cursor: pointer;
}

.quick-tag:hover {
  color: #59b8ff;
  border-color: #59b8ff;
}

.source-traces {
  margin-top: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px dashed rgba(116, 170, 255, 0.18);
}

.trace-header {
  font-size: 12px;
  font-weight: 600;
  color: #97a9c7;
  margin-bottom: 4px;
}

.trace-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #c5d7ef;
  margin-bottom: 2px;
}

.trace-file {
  color: #59b8ff;
}

.trace-chapter {
  color: #ffb860;
}

.trace-entity {
  color: #5ff0c2;
}

.trace-confidence {
  color: #97a9c7;
  margin-left: auto;
}
</style>
