<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- 移动端顶部操作栏 -->
    <div class="lg:hidden flex justify-between items-center mb-4 sticky top-0 z-20 bg-white/95 backdrop-blur-sm border-b border-gray-200 pb-3 pt-3">
      <h1 class="text-xl font-bold text-gray-900">主页</h1>
      <button
        @click="uiStore.toggleMobileSidebar"
        class="p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors touch-manipulation active:scale-95"
      >
        <LightBulbIcon class="w-5 h-5" />
        <span class="ml-2 text-sm font-medium">想法</span>
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 justify-center">
      <!-- 左侧：主要内容区域 -->
      <div class="w-full lg:flex-[2] lg:max-w-4xl">
        <!-- 欢迎卡片 -->
        <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-6">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Hello, {{ authStore.isAuthenticated ? authStore.user.username : 'Stranger' }}
            </h1>
            <p class="text-gray-600 text-sm sm:text-base">Welcome to the blog</p>
          </div>
        </div>

        <!-- 博客文章列表 -->
        <div class="space-y-4">
          <div v-if="blogStore.loading" class="flex justify-center py-8">
            <div class="loading-spinner w-8 h-8"></div>
          </div>

          <div v-else-if="blogStore.hasPosts" class="space-y-4">
            <article
              v-for="post in blogStore.posts"
              :key="post.id"
              class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200"
            >
              <div class="p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-3 line-clamp-2">
                  {{ post.title }}
                </h2>
                <div class="text-gray-600 text-sm mb-4 line-clamp-3">
                  {{ post.content }}
                </div>
                <div class="flex items-center justify-between text-sm text-gray-500">
                  <span>{{ formatDate(post.timestamp) }}</span>
                  <router-link
                    :to="`/blog/${post.id}`"
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    阅读更多
                  </router-link>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <DocumentTextIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500 text-lg mb-4">还没有博客文章</p>
            <router-link
              v-if="authStore.isAuthenticated"
              to="/blog/create"
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              写第一篇文章
              <PlusIcon class="w-4 h-4 ml-2" />
            </router-link>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="blogStore.pagination.pages > 1" class="mt-8 flex justify-center px-2">
          <nav class="flex items-center space-x-1 sm:space-x-2">
            <!-- 上一页 -->
            <button
              v-if="blogStore.pagination.has_prev"
              @click="fetchPosts(blogStore.pagination.prev_num)"
              class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <ChevronLeftIcon class="w-4 h-4 mr-1" />
              <span class="hidden sm:inline">上一页</span>
            </button>

            <!-- 页码 -->
            <template v-for="page in paginationPages" :key="page">
              <button
                v-if="page"
                @click="fetchPosts(page)"
                :class="[
                  'px-3 py-2 text-sm font-medium rounded-md transition-colors min-w-[2.5rem] text-center',
                  page === blogStore.pagination.page
                    ? 'text-white bg-blue-600 border border-blue-600'
                    : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
              <span
                v-else
                class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md"
              >
                ...
              </span>
            </template>

            <!-- 下一页 -->
            <button
              v-if="blogStore.pagination.has_next"
              @click="fetchPosts(blogStore.pagination.next_num)"
              class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <span class="hidden sm:inline">下一页</span>
              <ChevronRightIcon class="w-4 h-4 ml-1" />
            </button>
          </nav>
        </div>
      </div>

      <!-- 右侧：想法展示（移动端折叠） -->
      <div class="w-full lg:flex-[1] lg:max-w-sm mt-6 lg:mt-0">
        <!-- 移动端全屏遮罩层 -->
        <div
          v-if="uiStore.mobileSidebarOpen"
          @click="uiStore.closeMobileSidebar"
          class="lg:hidden fixed inset-0 bg-black/60 z-40 transition-opacity duration-300"
        ></div>

        <!-- 移动端侧边栏面板 -->
        <div
          :class="[
            'lg:hidden fixed top-0 right-0 h-full w-80 bg-white z-50 shadow-2xl transform transition-transform duration-300 ease-out overflow-hidden',
            uiStore.mobileSidebarOpen ? 'translate-x-0' : 'translate-x-full'
          ]"
        >
          <!-- 移动端面板头部 -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-white sticky top-0 z-10">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <LightBulbIcon class="w-5 h-5 text-yellow-500 mr-2" />
              想法与心情
            </h2>
            <button
              @click="uiStore.closeMobileSidebar"
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- 移动端面板内容 -->
          <div class="h-[calc(100vh-80px)] overflow-y-auto p-4 space-y-4">
            <!-- 复制桌面端侧边栏内容 -->
            <div class="space-y-4">
              <!-- 心情日历组件 -->
              <MoodCalendar />

              <!-- 快速想法记录组件 -->
              <QuickThoughtForm />

              <!-- 想法列表组件 -->
              <ThoughtList />
            </div>
          </div>
        </div>

        <!-- 桌面端侧边栏内容 -->
        <div class="hidden lg:block space-y-4">
          <!-- 心情日历组件 -->
          <MoodCalendar />

          <!-- 快速想法记录组件 -->
          <QuickThoughtForm />

          <!-- 想法列表组件 -->
          <ThoughtList />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useBlogStore } from '../stores/blog'
import { useUIStore } from '../stores/ui'
import {
  LightBulbIcon,
  DocumentTextIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import MoodCalendar from '../components/MoodCalendar.vue'
import QuickThoughtForm from '../components/QuickThoughtForm.vue'
import ThoughtList from '../components/ThoughtList.vue'

const authStore = useAuthStore()
const blogStore = useBlogStore()
const uiStore = useUIStore()

// 计算分页页码
const paginationPages = computed(() => {
  const pagination = blogStore.pagination
  const pages = []

  if (pagination.has_prev) {
    pages.push(pagination.prev_num)
  }

  for (let page of pagination.iter_pages) {
    if (page) {
      pages.push(page)
    } else {
      pages.push(null)
    }
  }

  if (pagination.has_next) {
    pages.push(pagination.next_num)
  }

  return pages
})

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文章列表
const fetchPosts = async (page = 1) => {
  await blogStore.fetchPosts(page)
}

// 初始化
onMounted(async () => {
  await fetchPosts()
})
</script>

<style scoped>
.loading-spinner {
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
</style>