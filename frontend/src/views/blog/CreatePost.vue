<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div class="text-red-600 text-lg mb-2">{{ error }}</div>
      <button
        @click="$router.go(-1)"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        返回上一页
      </button>
    </div>

    <!-- 编辑表单 -->
    <div v-else class="bg-white rounded-lg shadow-sm overflow-hidden">
      <header class="p-6 border-b border-gray-200">
        <h1 class="text-2xl font-bold text-gray-900">
          {{ isEditing ? '编辑文章' : '写文章' }}
        </h1>
        <p class="text-gray-600 mt-2">
          {{ isEditing ? '修改您的文章内容' : '分享您的想法和见解' }}
        </p>
      </header>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
        <!-- 标题输入 -->
        <div>
          <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
            文章标题 <span class="text-red-500">*</span>
          </label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            required
            maxlength="200"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="请输入文章标题"
            :disabled="submitting"
          />
          <div class="mt-1 text-right text-sm text-gray-500">
            {{ form.title.length }}/200
          </div>
        </div>

        <!-- 内容输入 -->
        <div>
          <label for="body" class="block text-sm font-medium text-gray-700 mb-2">
            文章内容 <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <!-- 编辑模式切换 -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-4 text-sm">
                <button
                  type="button"
                  @click="editMode = 'wysiwyg'"
                  :class="[
                    'px-3 py-1 rounded-md transition-colors',
                    editMode === 'wysiwyg'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  ]"
                >
                  <i class="fas fa-edit mr-1"></i>
                  可视化编辑
                </button>
                <button
                  type="button"
                  @click="editMode = 'markdown'"
                  :class="[
                    'px-3 py-1 rounded-md transition-colors',
                    editMode === 'markdown'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  ]"
                >
                  <i class="fas fa-code mr-1"></i>
                  Markdown
                </button>
                <button
                  type="button"
                  @click="editMode = 'preview'"
                  :class="[
                    'px-3 py-1 rounded-md transition-colors',
                    editMode === 'preview'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  ]"
                >
                  <i class="fas fa-eye mr-1"></i>
                  预览
                </button>
              </div>

              <div class="text-sm text-gray-500">
                {{ form.body.length }} 字符
              </div>
            </div>

            <!-- 编辑器 -->
            <div class="border border-gray-300 rounded-lg overflow-hidden">
              <!-- 可视化编辑器 -->
              <textarea
                v-if="editMode === 'wysiwyg'"
                v-model="form.body"
                rows="20"
                required
                class="w-full px-3 py-2 border-0 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="请输入文章内容，支持HTML格式..."
                :disabled="submitting"
              ></textarea>

              <!-- Markdown编辑器 -->
              <textarea
                v-else-if="editMode === 'markdown'"
                v-model="form.body"
                rows="20"
                required
                class="w-full px-3 py-2 border-0 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
                placeholder="请输入Markdown格式的内容..."
                :disabled="submitting"
              ></textarea>

              <!-- 预览模式 -->
              <div
                v-else-if="editMode === 'preview'"
                class="p-4 min-h-[200px] prose prose-lg max-w-none"
                v-html="previewHtml"
              ></div>
            </div>

            <!-- Markdown提示 -->
            <div v-if="editMode === 'markdown'" class="mt-2 text-xs text-gray-500">
              <p>支持Markdown语法：</p>
              <div class="flex flex-wrap gap-2 mt-1">
                <code class="px-1 py-0.5 bg-gray-100 rounded"># 标题</code>
                <code class="px-1 py-0.5 bg-gray-100 rounded">**粗体**</code>
                <code class="px-1 py-0.5 bg-gray-100 rounded">*斜体*</code>
                <code class="px-1 py-0.5 bg-gray-100 rounded">`代码`</code>
                <code class="px-1 py-0.5 bg-gray-100 rounded">> 引用</code>
                <code class="px-1 py-0.5 bg-gray-100 rounded">- 列表</code>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-col sm:flex-row gap-4 pt-6 border-t border-gray-200">
          <!-- 取消按钮 -->
          <button
            type="button"
            @click="handleCancel"
            class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            :disabled="submitting"
          >
            取消
          </button>

          <div class="flex-1"></div>

          <!-- 保存草稿按钮 -->
          <button
            type="button"
            @click="handleSaveDraft"
            class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            :disabled="submitting || !form.title.trim() || !form.body.trim()"
          >
            <i class="fas fa-save mr-2"></i>
            保存草稿
          </button>

          <!-- 发布按钮 -->
          <button
            type="submit"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="submitting || !form.title.trim() || !form.body.trim()"
          >
            <i class="fas fa-paper-plane mr-2"></i>
            {{ isEditing ? '更新文章' : '发布文章' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 自动保存提示 -->
    <div
      v-if="autoSaveStatus.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg transition-all duration-300',
        autoSaveStatus.type === 'success'
          ? 'bg-green-500 text-white'
          : 'bg-yellow-500 text-white'
      ]"
    >
      <i class="fas fa-check-circle mr-2"></i>
      {{ autoSaveStatus.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlogStore } from '../../stores/blog'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'

const route = useRoute()
const router = useRouter()
const blogStore = useBlogStore()
const authStore = useAuthStore()
const uiStore = useUIStore()

// 状态
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const editMode = ref('wysiwyg') // 'wysiwyg' | 'markdown' | 'preview'
const autoSaveStatus = ref({
  show: false,
  type: 'success',
  message: ''
})

// 表单数据
const form = ref({
  title: '',
  body: ''
})

// 自动保存定时器
let autoSaveTimer = null

// 计算属性
const isEditing = computed(() => !!route.params.id)
const postId = computed(() => parseInt(route.params.id))

// 预览HTML
const previewHtml = computed(() => {
  if (!form.value.body) return '<p class="text-gray-500">暂无内容</p>'

  // 简单的Markdown转HTML
  return form.value.body
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/`(.*)`/gim, '<code>$1</code>')
    .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
    .replace(/\n\n/gim, '</p><p>')
    .replace(/^\* (.*$)/gim, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/^([^-])/gim, '<p>$1')
    .replace(/\n/gim, '<br>')
})

// 检查权限
const checkPermission = () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return false
  }
  return true
}

// 加载文章数据（编辑模式）
const loadPost = async () => {
  if (!isEditing.value || !postId.value) return

  loading.value = true
  error.value = ''

  try {
    const result = await blogStore.fetchPost(postId.value)
    if (result.success && blogStore.currentPost) {
      const post = blogStore.currentPost

      // 检查权限
      if (post.author_id !== authStore.user?.id && !authStore.user?.role?.includes('Admin')) {
        error.value = '您没有权限编辑这个文章'
        return
      }

      form.value = {
        title: post.title || '',
        body: post.body || ''
      }
    } else {
      error.value = result.message || '文章加载失败'
    }
  } catch (err) {
    console.error('加载文章失败:', err)
    error.value = '加载文章时出现错误'
  } finally {
    loading.value = false
  }
}

// 自动保存
const autoSave = () => {
  if (!form.value.title.trim() || !form.value.body.trim()) return

  // 清除之前的定时器
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }

  // 设置新的定时器
  autoSaveTimer = setTimeout(async () => {
    try {
      if (isEditing.value) {
        await blogStore.updatePost(postId.value, form.value)
      } else {
        // 对于新文章，可以保存到localStorage
        localStorage.setItem('draft_post', JSON.stringify(form.value))
      }

      showAutoSaveStatus('success', '已自动保存')
    } catch (err) {
      showAutoSaveStatus('error', '自动保存失败')
    }
  }, 3000) // 3秒后自动保存
}

// 显示自动保存状态
const showAutoSaveStatus = (type, message) => {
  autoSaveStatus.value = { show: true, type, message }
  setTimeout(() => {
    autoSaveStatus.value.show = false
  }, 2000)
}

// 处理表单提交
const handleSubmit = async () => {
  if (!checkPermission()) return

  if (!form.value.title.trim() || !form.value.body.trim()) {
    uiStore.showFlashMessage('请填写标题和内容', 'error')
    return
  }

  submitting.value = true

  try {
    let result
    if (isEditing.value) {
      result = await blogStore.updatePost(postId.value, form.value)
      if (result.success) {
        uiStore.showFlashMessage('文章更新成功', 'success')
        router.push(`/blog/${postId.value}`)
      }
    } else {
      result = await blogStore.createPost(form.value)
      if (result.success) {
        uiStore.showFlashMessage('文章发布成功', 'success')
        router.push(`/blog/${result.post.id}`)
      }
    }

    if (!result.success) {
      uiStore.showFlashMessage(result.message || '操作失败', 'error')
    }
  } catch (err) {
    console.error('提交失败:', err)
    uiStore.showFlashMessage('提交时出现错误', 'error')
  } finally {
    submitting.value = false
  }
}

// 处理取消
const handleCancel = () => {
  if (isEditing.value) {
    router.push(`/blog/${postId.value}`)
  } else {
    router.push('/blog')
  }
}

// 处理保存草稿
const handleSaveDraft = async () => {
  if (!checkPermission()) return

  if (!form.value.title.trim() || !form.value.body.trim()) {
    uiStore.showFlashMessage('请填写标题和内容', 'error')
    return
  }

  try {
    if (isEditing.value) {
      const result = await blogStore.updatePost(postId.value, form.value)
      if (result.success) {
        uiStore.showFlashMessage('草稿已保存', 'success')
      }
    } else {
      // 保存到localStorage
      localStorage.setItem('draft_post', JSON.stringify(form.value))
      uiStore.showFlashMessage('草稿已保存到本地', 'success')
    }
  } catch (err) {
    console.error('保存草稿失败:', err)
    uiStore.showFlashMessage('保存草稿失败', 'error')
  }
}

// 监听表单变化，触发自动保存
watch([() => form.value.title, () => form.value.body], () => {
  if (!submitting.value) {
    autoSave()
  }
}, { deep: true })

// 页面加载时恢复草稿
const restoreDraft = () => {
  if (!isEditing.value) {
    const draft = localStorage.getItem('draft_post')
    if (draft) {
      try {
        const draftData = JSON.parse(draft)
        form.value = {
          title: draftData.title || '',
          body: draftData.body || ''
        }
        showAutoSaveStatus('success', '已恢复上次编辑的草稿')
      } catch (err) {
        console.error('恢复草稿失败:', err)
      }
    }
  }
}

onMounted(async () => {
  if (!checkPermission()) return

  // 设置页面标题
  document.title = isEditing.value ? '编辑文章 - Sad Blog' : '写文章 - Sad Blog'

  // 如果是编辑模式，加载文章数据
  if (isEditing.value) {
    await loadPost()
  } else {
    // 如果是新建模式，尝试恢复草稿
    restoreDraft()
  }
})

onUnmounted(() => {
  // 清理自动保存定时器
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})
</script>

<style scoped>
.prose {
  line-height: 1.8;
}

.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.prose h1 { font-size: 2.25em; }
.prose h2 { font-size: 1.875em; }
.prose h3 { font-size: 1.5em; }
.prose h4 { font-size: 1.25em; }
.prose h5 { font-size: 1.125em; }
.prose h6 { font-size: 1em; }

.prose p {
  margin-bottom: 1em;
}

.prose ul, .prose ol {
  margin-bottom: 1em;
  padding-left: 2em;
}

.prose li {
  margin-bottom: 0.5em;
}

.prose blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1em;
  margin: 1em 0;
  font-style: italic;
  color: #6b7280;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.125em 0.25em;
  border-radius: 0.25em;
  font-size: 0.875em;
}

.prose pre {
  background-color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin-bottom: 1em;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
}
</style>