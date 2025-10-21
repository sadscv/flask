<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面头部 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">博客文章</h1>
      <p class="mt-2 text-gray-600">分享技术心得、生活感悟</p>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
      <!-- 主搜索栏 -->
      <div class="flex flex-col sm:flex-row gap-4 mb-4">
        <div class="flex-1 relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索文章标题、内容、标签..."
            class="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @input="handleSearch"
            @focus="showSearchSuggestions = true"
            @blur="hideSearchSuggestions"
          />
          <div class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            <i v-if="!searching" class="fas fa-search"></i>
            <i v-else class="fas fa-spinner fa-spin"></i>
          </div>

          <!-- 搜索建议下拉框 -->
          <div
            v-if="showSearchSuggestions && searchSuggestions.length > 0"
            class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto"
          >
            <div
              v-for="suggestion in searchSuggestions"
              :key="suggestion"
              @mousedown="selectSuggestion(suggestion)"
              class="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm"
            >
              <i class="fas fa-search mr-2 text-gray-400"></i>
              {{ suggestion }}
            </div>
          </div>
        </div>

        <select
          v-model="sortBy"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          @change="handleSort"
        >
          <option value="latest">最新发布</option>
          <option value="oldest">最早发布</option>
          <option value="popular">最受欢迎</option>
          <option value="most_viewed">浏览最多</option>
          <option value="most_commented">评论最多</option>
        </select>

        <button
          @click="toggleAdvancedSearch"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
        >
          <i class="fas fa-filter mr-2"></i>
          高级筛选
        </button>

        <router-link
          v-if="authStore.isAuthenticated"
          to="/blog/create"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
        >
          <i class="fas fa-plus mr-2"></i>
          写文章
        </router-link>
      </div>

      <!-- 高级筛选选项 -->
      <div v-if="showAdvancedSearch" class="border-t pt-4 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 作者筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">作者</label>
            <select
              v-model="filters.author"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部作者</option>
              <option v-for="author in popularAuthors" :key="author.id" :value="author.id">
                {{ author.username }}
              </option>
            </select>
          </div>

          <!-- 标签筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">标签</label>
            <select
              v-model="filters.tag"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部标签</option>
              <option v-for="tag in popularTags" :key="tag" :value="tag">
                {{ tag }}
              </option>
            </select>
          </div>

          <!-- 时间范围筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">时间范围</label>
            <select
              v-model="filters.dateRange"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部时间</option>
              <option value="1">今天</option>
              <option value="7">最近7天</option>
              <option value="30">最近30天</option>
              <option value="90">最近3个月</option>
              <option value="365">最近1年</option>
            </select>
          </div>

          <!-- 内容类型筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">内容类型</label>
            <select
              v-model="filters.contentType"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部类型</option>
              <option value="tutorial">教程</option>
              <option value="article">文章</option>
              <option value="note">笔记</option>
              <option value="news">新闻</option>
            </select>
          </div>
        </div>

        <!-- 清除筛选按钮 -->
        <div class="flex justify-end">
          <button
            @click="clearFilters"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            <i class="fas fa-times mr-2"></i>
            清除筛选
          </button>
        </div>
      </div>

      <!-- 当前搜索条件显示 -->
      <div v-if="hasActiveFilters" class="border-t pt-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm text-gray-600">当前筛选:</span>
          <span
            v-if="searchQuery"
            class="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
          >
            搜索: "{{ searchQuery }}"
            <button @click="clearSearch" class="ml-2 hover:text-blue-600">
              <i class="fas fa-times"></i>
            </button>
          </span>
          <span
            v-for="(value, key) in activeFilters"
            :key="key"
            class="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-800 text-sm rounded-full"
          >
            {{ getFilterLabel(key, value) }}
            <button @click="removeFilter(key)" class="ml-2 hover:text-gray-600">
              <i class="fas fa-times"></i>
            </button>
          </span>
        </div>
      </div>
    </div>

    <!-- 搜索结果统计 -->
    <div v-if="hasActiveFilters && !loading" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="text-sm text-blue-800">
          <i class="fas fa-info-circle mr-2"></i>
          找到 <span class="font-semibold">{{ blogStore.pagination.total }}</span> 篇相关文章
          <span v-if="searchQuery">
            ，搜索关键词 "<span class="font-semibold">{{ searchQuery }}</span>"
          </span>
        </div>
        <button
          @click="clearAllFilters"
          class="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          清除所有筛选
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- 文章列表 -->
    <div v-else-if="blogStore.posts.length > 0" class="space-y-6">
      <article
        v-for="post in blogStore.posts"
        :key="post.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-200"
      >
        <!-- 文章头部 -->
        <div class="p-6 border-b border-gray-100">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                {{ getAuthorInitial(post.author) }}
              </div>
              <div>
                <h3 class="font-semibold text-gray-900 hover:text-blue-600 cursor-pointer" @click="$router.push(`/blog/${post.id}`)">
                  {{ post.author?.username || 'Anonymous' }}
                </h3>
                <p class="text-sm text-gray-500">
                  <i class="fas fa-clock mr-1"></i>
                  {{ formatDateTime(post.timestamp) }}
                  <span v-if="post.edit_date" class="ml-2">
                    <i class="fas fa-edit mr-1"></i>已编辑
                  </span>
                </p>
              </div>
            </div>
            <div v-if="post.edit_date" class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
              已编辑
            </div>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="p-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-4 hover:text-blue-600 cursor-pointer" @click="$router.push(`/blog/${post.id}`)">
            {{ post.title }}
          </h2>
          <div class="prose prose-sm max-w-none text-gray-600 mb-4">
            <div v-if="post.body_html" v-html="post.body_html" class="line-clamp-3"></div>
            <p v-else class="line-clamp-3">{{ post.body }}</p>
          </div>

          <!-- 标签 -->
          <div v-if="post.tags" class="flex flex-wrap gap-2 mb-4">
            <span
              v-for="tag in post.tags.split(',').slice(0, 3)"
              :key="tag.trim()"
              class="inline-block px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200 cursor-pointer"
            >
              #{{ tag.trim() }}
            </span>
          </div>

          <!-- 文章底部信息 -->
          <div class="flex items-center justify-between pt-4 border-t border-gray-100">
            <div class="flex items-center space-x-6 text-sm text-gray-500">
              <div class="flex items-center">
                <i class="fas fa-eye mr-1"></i>
                <span>{{ post.views || 0 }}</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-comment mr-1"></i>
                <span>{{ post.comments_count || 0 }}</span>
              </div>
            </div>

            <div class="flex items-center space-x-3">
              <router-link
                :to="`/blog/${post.id}`"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                阅读全文
              </router-link>

              <router-link
                v-if="canEditPost(post)"
                :to="`/blog/${post.id}/edit`"
                class="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                title="编辑"
              >
                <i class="fas fa-edit"></i>
              </router-link>
            </div>
          </div>
        </div>
      </article>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-16">
      <div class="mb-6">
        <i class="fas fa-inbox text-8xl text-gray-300"></i>
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-3">暂无文章</h3>
      <p class="text-gray-500 text-lg mb-6">
        {{ searchQuery ? '没有找到匹配的文章' : '还没有任何文章内容，快去创作第一篇吧！' }}
      </p>
      <router-link
        v-if="authStore.isAuthenticated && !searchQuery"
        to="/blog/create"
        class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        <i class="fas fa-plus mr-2"></i>
        创建文章
      </router-link>
    </div>

    <!-- 分页 -->
    <div v-if="blogStore.pagination.pages > 1" class="mt-8 flex justify-center">
      <nav class="flex items-center space-x-2">
        <!-- 上一页 -->
        <button
          v-if="blogStore.pagination.has_prev"
          @click="changePage(blogStore.pagination.prev_num)"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          <i class="fas fa-chevron-left mr-1"></i>
          上一页
        </button>

        <!-- 页码 -->
        <template v-for="page in paginationPages" :key="page">
          <button
            v-if="page"
            @click="changePage(page)"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-md transition-colors min-w-[2.5rem]',
              page === blogStore.pagination.page
                ? 'text-white bg-blue-600 border-blue-600'
                : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
          <span
            v-else
            class="px-3 py-2 text-sm font-medium text-gray-500"
          >
            ...
          </span>
        </template>

        <!-- 下一页 -->
        <button
          v-if="blogStore.pagination.has_next"
          @click="changePage(blogStore.pagination.next_num)"
          class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          下一页
          <i class="fas fa-chevron-right ml-1"></i>
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlogStore } from '../../stores/blog'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const blogStore = useBlogStore()
const authStore = useAuthStore()

const loading = ref(false)
const searching = ref(false)
const searchQuery = ref('')
const sortBy = ref('latest')
const showAdvancedSearch = ref(false)
const showSearchSuggestions = ref(false)
const searchSuggestions = ref([])

const filters = ref({
  author: '',
  tag: '',
  dateRange: '',
  contentType: ''
})

const popularAuthors = ref([])
const popularTags = ref([])

// 计算属性
const paginationPages = computed(() => {
  const pagination = blogStore.pagination
  const pages = []

  const current = pagination.page
  const total = pagination.pages

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push(null)
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push(null)
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push(null)
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push(null)
      pages.push(total)
    }
  }

  return pages
})

const hasActiveFilters = computed(() => {
  return searchQuery.value ||
         Object.values(filters.value).some(value => value !== '')
})

const activeFilters = computed(() => {
  const result = {}
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value) {
      result[key] = value
    }
  })
  return result
})

// 方法
const getAuthorInitial = (author) => {
  if (!author || !author.username) return 'A'
  return author.username.charAt(0).toUpperCase()
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const canEditPost = (post) => {
  if (!authStore.isAuthenticated) return false
  if (authStore.user?.role === 'admin') return true
  return post.author_id === authStore.user?.id
}


const changePage = (page) => {
  router.push({ path: '/blog', query: { ...route.query, page } })
}

// 搜索相关方法
const handleSearch = async () => {
  searching.value = true
  try {
    const query = searchQuery.value.trim()
    const page = 1

    if (query) {
      // 如果有搜索关键词，执行搜索
      await blogStore.searchPosts(query, page, sortBy.value)
      // 获取搜索建议
      await getSearchSuggestions(query)
    } else {
      // 如果搜索框为空，加载所有文章
      await blogStore.fetchPosts(page, 10, sortBy.value)
      searchSuggestions.value = []
    }

    // 更新URL参数
    router.push({
      path: '/blog',
      query: {
        ...route.query,
        search: query || undefined,
        page: query ? page : route.query.page
      }
    })
  } finally {
    searching.value = false
  }
}

const getSearchSuggestions = async (query) => {
  if (query.length < 2) {
    searchSuggestions.value = []
    return
  }

  try {
    // 这里可以调用API获取搜索建议
    // const result = await blogApi.getSearchSuggestions(query)
    // searchSuggestions.value = result.suggestions

    // 模拟搜索建议
    const mockSuggestions = [
      `${query} 教程`,
      `${query} 最佳实践`,
      `${query} 入门指南`,
      `Vue 3 ${query}`,
      `JavaScript ${query}`
    ].filter(suggestion => suggestion.toLowerCase().includes(query.toLowerCase()))

    searchSuggestions.value = mockSuggestions
  } catch (error) {
    console.error('Failed to get search suggestions:', error)
    searchSuggestions.value = []
  }
}

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  searchSuggestions.value = []
  handleSearch()
}

const hideSearchSuggestions = () => {
  setTimeout(() => {
    showSearchSuggestions.value = false
  }, 200)
}

// 高级搜索相关方法
const toggleAdvancedSearch = () => {
  showAdvancedSearch.value = !showAdvancedSearch.value
  if (showAdvancedSearch.value) {
    loadFilterOptions()
  }
}

const loadFilterOptions = async () => {
  try {
    // 这里可以调用API获取筛选选项
    // const authors = await blogApi.getPopularAuthors()
    // const tags = await blogApi.getPopularTags()

    // 模拟数据
    popularAuthors.value = [
      { id: 1, username: 'DemoUser' },
      { id: 2, username: 'Admin' },
      { id: 3, username: 'VueLover' }
    ]

    popularTags.value = [
      'Vue 3', 'JavaScript', 'CSS', 'HTML', 'Tailwind CSS',
      '前端开发', '教程', '最佳实践', '入门指南', '项目实战'
    ]
  } catch (error) {
    console.error('Failed to load filter options:', error)
  }
}

const applyFilters = async () => {
  const page = 1
  await loadPosts(page, searchQuery.value, sortBy.value)

  // 更新URL参数
  const query = { page }
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value) query[key] = value
  })

  router.push({
    path: '/blog',
    query: {
      ...route.query,
      ...query
    }
  })
}

const clearFilters = () => {
  filters.value = {
    author: '',
    tag: '',
    dateRange: '',
    contentType: ''
  }
  applyFilters()
}

const clearSearch = () => {
  searchQuery.value = ''
  searchSuggestions.value = []
  handleSearch()
}

const clearAllFilters = () => {
  searchQuery.value = ''
  searchSuggestions.value = []
  filters.value = {
    author: '',
    tag: '',
    dateRange: '',
    contentType: ''
  }
  sortBy.value = 'latest'

  // 重置到第一页
  router.push({ path: '/blog' })
}

const removeFilter = (key) => {
  filters.value[key] = ''
  applyFilters()
}

const getFilterLabel = (key, value) => {
  const labels = {
    author: `作者: ${popularAuthors.value.find(a => a.id === parseInt(value))?.username || value}`,
    tag: `标签: ${value}`,
    dateRange: `时间: ${getDateRangeLabel(value)}`,
    contentType: `类型: ${getContentTypeLabel(value)}`
  }
  return labels[key] || `${key}: ${value}`
}

const getDateRangeLabel = (value) => {
  const labels = {
    '1': '今天',
    '7': '最近7天',
    '30': '最近30天',
    '90': '最近3个月',
    '365': '最近1年'
  }
  return labels[value] || value
}

const getContentTypeLabel = (value) => {
  const labels = {
    'tutorial': '教程',
    'article': '文章',
    'note': '笔记',
    'news': '新闻'
  }
  return labels[value] || value
}

const handleSort = async () => {
  // 根据排序方式重新加载数据
  const page = 1
  const query = searchQuery.value.trim()

  if (query) {
    // 如果有搜索关键词，重新搜索
    await blogStore.searchPosts(query, page, sortBy.value)
  } else {
    // 否则加载所有文章
    await blogStore.fetchPosts(page, 10, sortBy.value)
  }

  // 更新URL参数
  router.push({
    path: '/blog',
    query: {
      ...route.query,
      sort: sortBy.value !== 'latest' ? sortBy.value : undefined,
      page: page
    }
  })
}

// 加载文章的统一方法
const loadPosts = async (page = 1, query = '', sort = 'latest') => {
  if (query.trim()) {
    await blogStore.searchPosts(query.trim(), page, sort)
  } else {
    await blogStore.fetchPosts(page, 10, sort)
  }
}

// 监听路由变化
watch(
  () => [
    route.query.page,
    route.query.search,
    route.query.sort,
    route.query.author,
    route.query.tag,
    route.query.dateRange,
    route.query.contentType
  ],
  async ([
    newPage,
    searchQuery,
    sortBy,
    author,
    tag,
    dateRange,
    contentType
  ]) => {
    const page = parseInt(newPage) || 1
    const query = searchQuery || ''
    const sort = sortBy || 'latest'

    // 更新组件状态
    searchQuery.value = query
    sortBy.value = sort
    filters.value = {
      author: author || '',
      tag: tag || '',
      dateRange: dateRange || '',
      contentType: contentType || ''
    }

    await loadPosts(page, query, sort)
  }
)

onMounted(async () => {
  // 从URL参数中获取初始状态
  const page = parseInt(route.query.page) || 1
  const query = route.query.search || ''
  const sort = route.query.sort || 'latest'

  searchQuery.value = query
  sortBy.value = sort
  filters.value = {
    author: route.query.author || '',
    tag: route.query.tag || '',
    dateRange: route.query.dateRange || '',
    contentType: route.query.contentType || ''
  }

  // 如果有筛选参数，显示高级搜索
  if (hasActiveFilters.value) {
    showAdvancedSearch.value = true
    await loadFilterOptions()
  }

  await loadPosts(page, query, sort)
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>