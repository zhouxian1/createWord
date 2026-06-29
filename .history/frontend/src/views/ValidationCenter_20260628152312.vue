<template>
  <div class="validation-center cyber-page circuit-bg">
    <div class="val-hero holo-panel">
      <div class="hero-row">
        <div>
          <div class="cyber-badge">QUALITY VALIDATION</div>
          <h2 class="glitch-title" style="margin-top: 10px; font-size: 22px;">质量验证</h2>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="holo-panel" style="padding: 20px;">
          <div class="panel-header">
            <span class="panel-title">文档验证</span>
            <div class="neon-divider"></div>
          </div>
          <el-form :model="formData" label-width="80px" style="margin-top: 16px;">
            <el-form-item label="选择文档">
              <el-select v-model="formData.document_id" placeholder="选择要验证的文档" filterable style="width: 100%;">
                <el-option v-for="doc in documents" :key="doc.id" :label="`${doc.doc_code} - ${doc.doc_name}`" :value="doc.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="validateDocument" :loading="validating">
                开始验证
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="holo-panel" style="padding: 20px;" v-if="validationResult">
          <div class="panel-header">
            <span class="panel-title">验证结果</span>
            <div class="neon-divider"></div>
          </div>
          <div class="result-summary" style="margin-top: 16px;">
            <div class="score-circle" :style="{ borderColor: levelColor }">
              <div class="score-value">{{ validationResult.score }}</div>
              <div class="score-label">分</div>
            </div>
            <div class="result-stats">
              <div>验证等级：<el-tag :type="levelTagType">{{ validationResult.level?.label }}</el-tag></div>
              <div>通过规则：{{ validationResult.passed }} / {{ validationResult.total_rules }}</div>
              <div>错误项：{{ validationResult.errors }}</div>
              <div>警告项：{{ validationResult.warnings }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <div class="holo-panel" style="padding: 20px; margin-top: 16px;" v-if="validationResult">
      <div class="panel-header">
        <span class="panel-title">验证详情</span>
        <div class="neon-divider"></div>
      </div>
      <el-table :data="validationResult.details" style="margin-top: 12px;">
        <el-table-column prop="rule_id" label="规则ID" width="100" />
        <el-table-column prop="rule_name" label="规则名称" min-width="150" />
        <el-table-column prop="rule_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(row.rule_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结果" width="80">
          <template #default="{ row }">
            <el-icon :color="row.passed ? '#39ff14' : '#ff2d95'">
              <CircleCheck v-if="row.passed" />
              <CircleClose v-else />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="说明" min-width="200" />
      </el-table>
    </div>

    <div class="holo-panel" style="padding: 20px; margin-top: 16px;">
      <div class="panel-header">
        <span class="panel-title">验证规则管理</span>
        <el-button type="primary" size="small" @click="showRuleDialog = true">
          <el-icon><Plus /></el-icon>添加规则
        </el-button>
      </div>
      <div class="neon-divider"></div>
      <el-table :data="rules" style="margin-top: 12px;" max-height="400">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="规则名称" min-width="180" />
        <el-table-column prop="type" label="类型" width="90" />
        <el-table-column prop="severity" label="严重程度" width="90" />
        <el-table-column prop="description" label="描述" min-width="260" />
      </el-table>
    </div>

    <el-dialog v-model="showRuleDialog" title="添加验证规则" width="500px">
      <el-form :model="ruleForm" label-width="80px">
        <el-form-item label="文档类型"><el-input v-model="ruleForm.doc_type" /></el-form-item>
        <el-form-item label="规则名称"><el-input v-model="ruleForm.rule_name" /></el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="ruleForm.rule_type">
            <el-option label="完整性" value="completeness" />
            <el-option label="合规性" value="compliance" />
            <el-option label="格式" value="format" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="ruleForm.severity">
            <el-option label="错误" value="error" />
            <el-option label="警告" value="warning" />
            <el-option label="信息" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="ruleForm.rule_description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="校验表达式"><el-input v-model="ruleForm.check_expression" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRuleDialog = false">取消</el-button>
        <el-button type="primary" @click="createRule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { generationApi, validationApi } from '@/api'
import { ElMessage } from 'element-plus'

const documents = ref([])
const rules = ref([])
const formData = ref({ document_id: null })
const validationResult = ref(null)
const validating = ref(false)
const showRuleDialog = ref(false)
const ruleForm = ref({
  doc_type: '', rule_name: '', rule_type: 'completeness',
  severity: 'error', rule_description: '', check_expression: ''
})

const levelColor = computed(() => validationResult.value?.level?.color || '#909399')
const levelTagType = computed(() => {
  const color = validationResult.value?.level?.color
  return { green: 'success', blue: '', yellow: 'warning', red: 'danger' }[color] || 'info'
})

const typeLabel = (t) => ({ completeness: '完整性', compliance: '合规性', format: '格式' }[t] || t)
const severityType = (s) => ({ error: 'danger', warning: 'warning', info: 'info' }[s] || 'info')

const validateDocument = async () => {
  if (!formData.value.document_id) {
    ElMessage.warning('请选择文档')
    return
  }
  validating.value = true
  try {
    const res = await validationApi.validate(formData.value.document_id)
    validationResult.value = res
    ElMessage.success('验证完成')
  } finally {
    validating.value = false
  }
}

const createRule = async () => {
  await validationApi.createRule(ruleForm.value)
  ElMessage.success('规则创建成功')
  showRuleDialog.value = false
  loadRules()
}

const loadData = async () => {
  const res = await generationApi.listDocuments({})
  documents.value = res.items || []
}

const loadRules = async () => {
  const res = await validationApi.listRules({})
  rules.value = res.items || []
}

onMounted(() => { loadData(); loadRules() })
</script>

<style scoped>
.val-hero {
  padding: 24px 28px;
  margin-bottom: 16px;
}

.hero-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-summary {
  display: flex;
  align-items: center;
  gap: 24px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--cp-cyan);
  font-family: 'Orbitron', var(--cp-font);
  text-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
}

.score-label {
  font-size: 12px;
  color: var(--cp-text-dim);
  font-family: 'Share Tech Mono', var(--cp-font);
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: var(--cp-text);
  font-family: 'Share Tech Mono', var(--cp-font);
}
</style>
