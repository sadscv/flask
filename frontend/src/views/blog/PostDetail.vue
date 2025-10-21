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

    <!-- 文章内容 -->
    <article v-else-if="post" class="bg-white rounded-lg shadow-sm overflow-hidden">
      <!-- 文章头部 -->
      <header class="p-6 border-b border-gray-200">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ post.title }}</h1>

        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600">
          <!-- 作者信息 -->
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
              {{ post.author?.username?.charAt(0).toUpperCase() || 'A' }}
            </div>
            <span>{{ post.author?.name || post.author?.username || '匿名' }}</span>
          </div>

          <!-- 发布时间 -->
          <div class="flex items-center gap-1">
            <i class="fas fa-clock"></i>
            <span>{{ formatDate(post.timestamp) }}</span>
          </div>

          <!-- 编辑时间 -->
          <div v-if="post.edit_date" class="flex items-center gap-1">
            <i class="fas fa-edit"></i>
            <span>{{ formatDate(post.edit_date) }} 编辑</span>
          </div>

          <!-- 阅读数 -->
          <div class="flex items-center gap-1">
            <i class="fas fa-eye"></i>
            <span>{{ post.views || 0 }} 阅读</span>
          </div>

          <!-- 评论数 -->
          <div class="flex items-center gap-1">
            <i class="fas fa-comment"></i>
            <span>{{ post.comments_count || 0 }} 评论</span>
          </div>
        </div>
      </header>

      <!-- 文章正文 -->
      <div class="p-6">
        <div
          class="prose prose-lg max-w-none"
          v-html="post.body_html || formatBody(post.body)"
        ></div>
      </div>

      <!-- 文章底部操作 -->
      <footer class="p-6 border-t border-gray-200 bg-gray-50">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <!-- 返回按钮 -->
          <button
            @click="$router.go(-1)"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            返回
          </button>

          <!-- 操作按钮组 -->
          <div class="flex items-center gap-3">
            <!-- 编辑按钮 (仅作者可见) -->
            <router-link
              v-if="canEditPost"
              :to="`/blog/${post.id}/edit`"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <i class="fas fa-edit mr-2"></i>
              编辑
            </router-link>

            <!-- 删除按钮 (仅作者可见) -->
            <button
              v-if="canEditPost"
              @click="handleDeletePost"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <i class="fas fa-trash mr-2"></i>
              删除
            </button>

            
            <!-- 分享按钮 -->
            <button
              @click="handleSharePost"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <i class="fas fa-share mr-2"></i>
              分享
            </button>
          </div>
        </div>
      </footer>
    </article>

    <!-- 相关文章推荐 (可选) -->
    <section v-if="relatedPosts.length > 0" class="mt-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">相关文章</h2>
      <div class="grid gap-6 md:grid-cols-2">
        <article
          v-for="relatedPost in relatedPosts"
          :key="relatedPost.id"
          class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="$router.push(`/blog/${relatedPost.id}`)"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
            {{ relatedPost.title }}
          </h3>
          <p class="text-gray-600 text-sm mb-3 line-clamp-3">
            {{ relatedPost.body }}
          </p>
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>{{ formatDate(relatedPost.timestamp) }}</span>
            <span>{{ relatedPost.views || 0 }} 阅读</span>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
const loading = ref(true)
const error = ref('')
const relatedPosts = ref([])

// 计算属性
const post = computed(() => blogStore.currentPost)

const canEditPost = computed(() => {
  return authStore.isAuthenticated &&
         post.value &&
         post.value.author_id === authStore.user?.id
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化文章内容
const formatBody = (body) => {
  if (!body) return ''
  // 简单的换行处理
  return body.replace(/\n/g, '<br>')
}

// 加载文章
const loadPost = async (postId) => {
  if (!postId) return

  loading.value = true
  error.value = ''

  try {
    const result = await blogStore.fetchPost(postId)
    if (!result.success) {
      error.value = result.message || '文章加载失败'
    }
  } catch (err) {
    console.error('加载文章失败:', err)
    error.value = '加载文章时出现错误'
  } finally {
    loading.value = false
  }
}

// 处理删除文章
const handleDeletePost = async () => {
  if (!post.value) return

  if (!confirm(`确定要删除文章"${post.value.title}"吗？此操作无法撤销。`)) {
    return
  }

  try {
    const result = await blogStore.deletePost(post.value.id)
    if (result.success) {
      uiStore.showFlashMessage('文章已删除', 'success')
      router.push('/blog')
    } else {
      uiStore.showFlashMessage(result.message || '删除失败', 'error')
    }
  } catch (err) {
    console.error('删除文章失败:', err)
    uiStore.showFlashMessage('删除文章时出现错误', 'error')
  }
}


// 处理分享文章
const handleSharePost = () => {
  const url = window.location.href
  if (navigator.share) {
    navigator.share({
      title: post.value?.title,
      text: post.value?.body,
      url: url
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(url).then(() => {
      uiStore.showFlashMessage('链接已复制到剪贴板', 'success')
    }).catch(() => {
      uiStore.showFlashMessage('复制链接失败', 'error')
    })
  }
}

// 加载相关文章 (模拟)
const loadRelatedPosts = () => {
  // 这里可以调用API获取相关文章，暂时使用模拟数据
  relatedPosts.value = []
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadPost(newId)
  }
}, { immediate: true })

onMounted(() => {
  // 设置页面标题
  if (post.value) {
    document.title = `${post.value.title} - Sad Blog`
  }

  // 加载相关文章
  loadRelatedPosts()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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

.prose pre {
  background-color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin-bottom: 1em;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.125em 0.25em;
  border-radius: 0.25em;
  font-size: 0.875em;
}

.prose pre code {
  background-color: transparent;
  padding: 0;
}
</style>