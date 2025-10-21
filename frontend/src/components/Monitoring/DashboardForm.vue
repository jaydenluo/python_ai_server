<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
    <!-- 基本信息 -->
    <el-form-item label="仪表板名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入仪表板名称" />
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input
        v-model="formData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入仪表板描述"
      />
    </el-form-item>

    <!-- 布局配置 -->
    <el-divider>布局配置</el-divider>

    <el-form-item label="列数">
      <el-input-number
        v-model="formData.layout.columns"
        :min="1"
        :max="12"
        controls-position="right"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="行数">
      <el-input-number
        v-model="formData.layout.rows"
        :min="1"
        :max="20"
        controls-position="right"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="间距">
      <el-input-number
        v-model="formData.layout.gap"
        :min="0"
        :max="50"
        controls-position="right"
        style="width: 100%"
      />
    </el-form-item>

    <!-- 组件配置 -->
    <el-divider>组件配置</el-divider>

    <div class="widgets-section">
      <div class="widgets-header">
        <span>仪表板组件</span>
        <el-button size="small" @click="addWidget">
          <el-icon><Plus /></el-icon>
          添加组件
        </el-button>
      </div>

      <div v-for="(widget, index) in formData.widgets" :key="index" class="widget-item">
        <el-form-item :label="`组件${index + 1}`">
          <el-space>
            <el-input v-model="widget.title" placeholder="组件标题" style="width: 120px" />
            <el-select v-model="widget.type" placeholder="类型" style="width: 100px">
              <el-option label="图表" value="chart" />
              <el-option label="指标" value="metric" />
              <el-option label="表格" value="table" />
              <el-option label="日志" value="log" />
            </el-select>
            <el-input-number
              v-model="widget.position.w"
              :min="1"
              :max="12"
              controls-position="right"
              style="width: 80px"
              placeholder="宽度"
            />
            <el-input-number
              v-model="widget.position.h"
              :min="1"
              :max="10"
              controls-position="right"
              style="width: 80px"
              placeholder="高度"
            />
            <el-button size="small" type="danger" @click="removeWidget(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-space>
        </el-form-item>
      </div>
    </div>

    <!-- 操作按钮 -->
    <el-form-item>
      <el-space>
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="$emit('cancel')">取消</el-button>
      </el-space>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElDivider, ElInputNumber, ElSpace, ElIcon } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { Dashboard, DashboardWidget, DashboardLayout } from '@/stores/monitoring'

interface Props {
  dashboard?: Partial<Dashboard>
}

interface Emits {
  (e: 'submit', dashboard: Partial<Dashboard>): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()

// 表单数据
const formData = reactive<Partial<Dashboard>>({
  name: '',
  description: '',
  layout: {
    columns: 4,
    rows: 3,
    gap: 16
  },
  widgets: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入仪表板名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入仪表板描述', trigger: 'blur' }
  ]
}

// 监听props变化
watch(() => props.dashboard, (newDashboard) => {
  if (newDashboard) {
    Object.assign(formData, newDashboard)
  }
}, { immediate: true, deep: true })

// 组件管理
const addWidget = () => {
  const newWidget: DashboardWidget = {
    id: `widget_${Date.now()}`,
    type: 'chart',
    title: '新组件',
    config: {},
    position: {
      x: 0,
      y: 0,
      w: 2,
      h: 2
    }
  }
  formData.widgets!.push(newWidget)
}

const removeWidget = (index: number) => {
  formData.widgets!.splice(index, 1)
}

// 表单提交
const submitForm = async () => {
  try {
    await formRef.value.validate()
    emit('submit', { ...formData })
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
}
</script>

<style scoped>
.widgets-section {
  margin-top: 16px;
}

.widgets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
  color: #303133;
}

.widget-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  background: #fafafa;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-divider) {
  margin: 20px 0 16px 0;
}
</style>
