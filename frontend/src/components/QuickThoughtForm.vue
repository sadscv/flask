<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900 flex items-center">
        <PencilSquareIcon class="w-5 h-5 text-green-500 mr-2" />
        快速记录
      </h2>
      <router-link
        to="/thoughts"
        class="text-sm text-green-600 hover:text-green-800 font-medium"
      >
        查看全部
      </router-link>
    </div>

    <!-- 快速记录表单 -->
    <form @submit.prevent="submitThought" class="space-y-3">
      <!-- 想法类型选择 -->
      <div class="flex items-center space-x-2">
        <label class="text-xs text-gray-600 font-medium">类型:</label>
        <div class="flex space-x-1">
          <button
            v-for="type in thoughtTypes"
            :key="type.value"
            type="button"
            @click="selectedType = type.value"
            :class="[
              'flex items-center px-2 py-1 text-xs rounded-md transition-colors',
              selectedType === type.value
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-transparent'
            ]"
          >
            <span class="mr-1">{{ type.emoji }}</span>
            {{ type.label }}
          </button>
        </div>
      </div>

      <!-- 想法内容输入 -->
      <div>
        <textarea
          v-model="content"
          placeholder="记录你的想法..."
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="3"
          maxlength="200"
          @input="updateCharCount"
        ></textarea>
        <div class="flex items-center justify-between mt-1">
          <span class="text-xs text-gray-500">{{ charCount }}/200</span>
          <div class="flex items-center space-x-2">
            <!-- 标签输入 -->
            <input
              v-model="tagInput"
              @keyup.enter.prevent="addTag"
              placeholder="添加标签..."
              class="px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-transparent"
              maxlength="20"
            >
            <button
              type="button"
              @click="addTag"
              class="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              添加
            </button>
          </div>
        </div>
      </div>

      <!-- 标签显示 -->
      <div v-if="tags.length > 0" class="flex flex-wrap gap-1">
        <span
          v-for="(tag, index) in tags"
          :key="index"
          class="inline-flex items-center px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded-full"
        >
          {{ tag }}
          <button
            type="button"
            @click="removeTag(index)"
            class="ml-1 text-blue-500 hover:text-blue-700"
          >
            ×
          </button>
        </span>
      </div>

      <!-- 来源URL -->
      <div>
        <input
          v-model="sourceUrl"
          type="url"
          placeholder="来源链接 (可选)"
          class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
      </div>

      <!-- 隐私设置 -->
      <div class="flex items-center">
        <input
          v-model="isPublic"
          type="checkbox"
          id="isPublic"
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        >
        <label for="isPublic" class="ml-2 text-sm text-gray-700">
          公开显示
        </label>
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        :disabled="!content.trim() || submitting"
        class="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-sm font-medium"
      >
        <div v-if="submitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
        <PencilSquareIcon v-else class="w-4 h-4 mr-2" />
        {{ submitting ? '保存中...' : '保存想法' }}
      </button>
    </form>

    <!-- 快速想法模板 -->
    <div v-if="!content" class="mt-4 pt-4 border-t border-gray-200">
      <p class="text-xs text-gray-500 mb-2">快速模板:</p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="template in thoughtTemplates"
          :key="template.id"
          type="button"
          @click="useTemplate(template)"
          class="text-left px-2 py-2 text-xs bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
        >
          <div class="font-medium text-gray-700">{{ template.title }}</div>
          <div class="text-gray-500 truncate">{{ template.content }}</div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThoughtStore } from '../stores/thoughts'
import { useAuthStore } from '../stores/auth'
import { PencilSquareIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const thoughtStore = useThoughtStore()
const authStore = useAuthStore()

// 表单数据
const content = ref('')
const selectedType = ref('note')
const tags = ref([])
const tagInput = ref('')
const sourceUrl = ref('')
const isPublic = ref(false)
const submitting = ref(false)

// 想法类型
const thoughtTypes = [
  { value: 'note', label: '笔记', emoji: '📝' },
  { value: 'idea', label: '想法', emoji: '💡' },
  { value: 'quote', label: '引用', emoji: '💬' },
  { value: 'task', label: '任务', emoji: '✅' }
]

// 快速模板
const thoughtTemplates = [
  {
    id: 1,
    title: '今日感悟',
    content: '今天学到了...',
    type: 'note'
  },
  {
    id: 2,
    title: '灵感记录',
    content: '突然想到...',
    type: 'idea'
  },
  {
    id: 3,
    title: '待办事项',
    content: '需要完成...',
    type: 'task'
  },
  {
    id: 4,
    title: '金句摘录',
    content: '读到一句好话...',
    type: 'quote'
  }
]

// 计算属性
const charCount = computed(() => content.value.length)

// 方法
const updateCharCount = () => {
  // 字符计数会自动更新
}

const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !tags.value.includes(tag) && tags.value.length < 5) {
    tags.value.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index) => {
  tags.value.splice(index, 1)
}

const useTemplate = (template) => {
  content.value = template.content
  selectedType.value = template.type
}

const submitThought = async () => {
  if (!content.value.trim() || submitting.value) return

  submitting.value = true

  try {
    const thoughtData = {
      content: content.value.trim(),
      type: selectedType.value,
      tags: tags.value.join(','),
      source_url: sourceUrl.value.trim() || null,
      is_public: isPublic.value
    }

    const newThought = await thoughtStore.createThought(thoughtData)

    if (newThought) {
      // 重置表单
      content.value = ''
      tags.value = []
      tagInput.value = ''
      sourceUrl.value = ''
      isPublic.value = false
      selectedType.value = 'note'

      // 显示成功消息
      showSuccessMessage('想法已保存！')

      // 刷新想法列表
      await thoughtStore.fetchRecentThoughts()
    }
  } catch (error) {
    console.error('保存想法失败:', error)
    showErrorMessage('保存失败，请重试')
  } finally {
    submitting.value = false
  }
}

const showSuccessMessage = (message) => {
  // 这里可以集成全局消息提示系统
  console.log('Success:', message)
}

const showErrorMessage = (message) => {
  // 这里可以集成全局消息提示系统
  console.error('Error:', message)
}
</script>

<style scoped>
/* 自定义样式 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 文本域自动调整高度 */
textarea {
  min-height: 60px;
}

textarea:focus {
  outline: none;
}
</style>