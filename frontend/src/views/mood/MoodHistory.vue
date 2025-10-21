<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面头部 -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-slate-900">心情历史</h1>
          <p class="mt-2 text-neutral-500">回顾您的心情历程，分析情绪变化趋势</p>
        </div>
        <div class="flex items-center space-x-4">
          <router-link
            to="/mood/calendar"
            class="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            <i class="fas fa-calendar-alt mr-2"></i>
            日历视图
          </router-link>
          <router-link
            to="/mood"
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            <i class="fas fa-plus mr-2"></i>
            记录心情
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="!authStore.isAuthenticated" class="text-center py-16">
      <div class="mb-6">
        <i class="fas fa-chart-line text-8xl text-gray-300"></i>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 mb-3">需要登录</h3>
      <p class="text-gray-500 text-lg mb-6">请先登录以查看心情历史</p>
      <router-link
        to="/login"
        class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
      >
        去登录
      </router-link>
    </div>

    <div v-else class="space-y-8">
      <!-- 筛选和搜索 -->
      <div class="surface-muted p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 搜索 -->
          <div class="lg:col-span-2">
            <label class="block text-sm font-medium text-neutral-600 mb-2">搜索日记</label>
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索日记内容..."
                class="w-full pl-10 pr-3 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
                @input="onSearchChange"
              />
              <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            </div>
          </div>

          <!-- 心情类型筛选 -->
          <div>
            <label class="block text-sm font-medium text-neutral-600 mb-2">心情类型</label>
            <select
              v-model="selectedMoodType"
              @change="onFilterChange"
              class="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
            >
              <option value="">全部心情</option>
              <option v-for="mood in moodTypes" :key="mood.type" :value="mood.type">
                {{ mood.emoji }} {{ mood.label }}
              </option>
            </select>
          </div>

          <!-- 日期范围筛选 -->
          <div>
            <label class="block text-sm font-medium text-neutral-600 mb-2">时间范围</label>
            <select
              v-model="selectedTimeRange"
              @change="onTimeRangeChange"
              class="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
            >
              <option value="7">最近7天</option>
              <option value="30">最近30天</option>
              <option value="90">最近3个月</option>
              <option value="365">最近1年</option>
              <option value="all">全部时间</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 统计概览 -->
      <div class="surface-muted p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">统计概览</h2>

        <div v-if="stats.totalRecords > 0" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="text-center p-4 bg-primary-50 rounded-lg">
            <div class="text-2xl font-bold text-primary-600">{{ stats.totalRecords }}</div>
            <div class="text-sm text-blue-900">总记录数</div>
          </div>

          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ stats.avgIntensity }}/10</div>
            <div class="text-sm text-green-900">平均强度</div>
          </div>

          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-600">{{ stats.mostCommon }}</div>
            <div class="text-sm text-purple-900">最常见心情</div>
          </div>

          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">{{ stats.currentStreak }}天</div>
            <div class="text-sm text-orange-900">连续记录</div>
          </div>
        </div>

        <!-- 心情趋势图 -->
        <div v-if="chartData.length > 0" class="mb-6">
          <h3 class="text-md font-medium text-slate-900 mb-3">心情趋势</h3>
          <div class="p-4 bg-neutral-100 rounded-lg">
            <div class="flex items-end justify-between h-32 space-x-1">
              <div
                v-for="(data, index) in chartData"
                :key="index"
                class="flex-1 bg-primary-500 hover:bg-primary-600 transition-colors rounded-t relative group"
                :style="{ height: `${(data.intensity / 10) * 100}%` }"
                :title="`${data.date}: ${getMoodLabel(data.mood_type)} (${data.intensity}/10)`"
              >
                <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  <div>{{ getMoodEmoji(data.mood_type) }} {{ getMoodLabel(data.mood_type) }}</div>
                  <div>{{ data.intensity }}/10</div>
                  <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                    <div class="w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-800"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex justify-between mt-2 text-xs text-gray-500">
              <span>{{ chartData[0]?.date }}</span>
              <span>{{ chartData[chartData.length - 1]?.date }}</span>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <p class="text-gray-500">暂无统计数据</p>
        </div>
      </div>

      <!-- 心情记录列表 -->
      <div class="surface-muted p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-semibold text-slate-900">心情记录</h2>
          <div class="text-sm text-gray-500">
            显示 {{ filteredMoods.length }} 条记录
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <!-- 记录列表 -->
        <div v-else-if="filteredMoods.length > 0" class="space-y-4">
          <div
            v-for="mood in paginatedMoods"
            :key="mood.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-4">
                <!-- 心情图标 -->
                <div class="text-4xl">
                  {{ getMoodEmoji(mood.mood_type) }}
                </div>

                <!-- 心情详情 -->
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-medium text-slate-900">
                      {{ getMoodLabel(mood.mood_type) }}
                    </h3>
                    <span v-if="mood.custom_mood" class="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                      {{ mood.custom_mood }}
                    </span>
                    <div class="flex items-center space-x-1">
                      <span class="text-sm text-gray-500">强度:</span>
                      <div class="flex space-x-1">
                        <div
                          v-for="i in 5"
                          :key="i"
                          class="w-2 h-2 rounded-full"
                          :class="i <= Math.ceil(mood.intensity / 2) ? 'bg-primary-500' : 'bg-gray-300'"
                        ></div>
                      </div>
                      <span class="text-sm font-medium text-neutral-600">{{ mood.intensity }}/10</span>
                    </div>
                  </div>

                  <!-- 日记内容 -->
                  <div v-if="mood.diary" class="mb-3">
                    <p class="text-neutral-600 leading-relaxed">{{ mood.diary }}</p>
                  </div>

                  <!-- 时间信息 -->
                  <div class="flex items-center space-x-4 text-sm text-gray-500">
                    <div class="flex items-center space-x-1">
                      <i class="fas fa-calendar"></i>
                      <span>{{ formatDate(mood.date) }}</span>
                    </div>
                    <div class="flex items-center space-x-1">
                      <i class="fas fa-clock"></i>
                      <span>{{ formatTime(mood.timestamp) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center space-x-2 ml-4">
                <button
                  @click="editMood(mood)"
                  class="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  title="编辑"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                  @click="deleteMood(mood)"
                  class="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="删除"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="totalPages > 1" class="flex items-center justify-center space-x-2 mt-6">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="px-3 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-chevron-left"></i>
            </button>

            <div class="flex items-center space-x-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'px-3 py-2 text-sm border rounded-lg',
                  page === currentPage
                    ? 'bg-primary-500 text-white border-primary-500'
                    : 'border-neutral-200 hover:bg-neutral-100'
                ]"
              >
                {{ page }}
              </button>
            </div>

            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 text-sm border border-neutral-200 rounded-lg hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-12">
          <div class="mb-6">
            <i class="fas fa-search text-6xl text-gray-300"></i>
          </div>
          <h3 class="text-lg font-medium text-slate-900 mb-2">没有找到相关记录</h3>
          <p class="text-gray-500 mb-4">
            {{ searchQuery || selectedMoodType ? '尝试调整搜索条件' : '开始记录您的第一个心情吧' }}
          </p>
          <router-link
            v-if="!searchQuery && !selectedMoodType"
            to="/mood"
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            <i class="fas fa-plus mr-2"></i>
            记录心情
          </router-link>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeDeleteDialog"
    >
      <div
        class="surface-muted p-6 max-w-md w-full mx-4"
        @click.stop
      >
        <h3 class="text-lg font-semibold text-slate-900 mb-4">确认删除</h3>
        <p class="text-neutral-500 mb-6">
          确定要删除这条心情记录吗？此操作无法撤销。
        </p>
        <div class="flex justify-end space-x-4">
          <button
            @click="closeDeleteDialog"
            class="px-4 py-2 text-neutral-600 border border-neutral-200 rounded-lg hover:bg-neutral-100"
          >
            取消
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import { moodApi } from '../../api/mood'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

// 状态
const moods = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedMoodType = ref('')
const selectedTimeRange = ref('30')
const currentPage = ref(1)
const pageSize = 10
const showDeleteDialog = ref(false)
const moodToDelete = ref(null)

// 心情类型
const moodTypes = [
  { type: 'happy', emoji: '😊', label: '开心' },
  { type: 'excited', emoji: '🎉', label: '兴奋' },
  { type: 'calm', emoji: '😌', label: '平静' },
  { type: 'sad', emoji: '😢', label: '难过' },
  { type: 'angry', emoji: '😠', label: '生气' },
  { type: 'anxious', emoji: '😰', label: '焦虑' },
  { type: 'tired', emoji: '😴', label: '疲惫' },
  { type: 'confused', emoji: '😕', label: '困惑' }
]

// 计算属性
const filteredMoods = computed(() => {
  let filtered = [...moods.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(mood =>
      mood.diary?.toLowerCase().includes(query) ||
      mood.custom_mood?.toLowerCase().includes(query)
    )
  }

  // 心情类型过滤
  if (selectedMoodType.value) {
    filtered = filtered.filter(mood => mood.mood_type === selectedMoodType.value)
  }

  // 时间范围过滤
  if (selectedTimeRange.value !== 'all') {
    const days = parseInt(selectedTimeRange.value)
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - days)

    filtered = filtered.filter(mood => {
      const moodDate = new Date(mood.date)
      return moodDate >= cutoffDate
    })
  }

  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalPages = computed(() => {
  return Math.ceil(filteredMoods.value.length / pageSize)
})

const paginatedMoods = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredMoods.value.slice(start, end)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2

  const range = []
  const rangeWithDots = []

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else {
    rangeWithDots.push(total)
  }

  return rangeWithDots.filter(page => page !== '...' || rangeWithDots.indexOf(page) === rangeWithDots.lastIndexOf(page))
})

const stats = computed(() => {
  if (filteredMoods.value.length === 0) {
    return { totalRecords: 0, avgIntensity: 0, mostCommon: '-', currentStreak: 0 }
  }

  const totalIntensity = filteredMoods.value.reduce((sum, mood) => sum + (mood.intensity || 0), 0)
  const avgIntensity = Math.round(totalIntensity / filteredMoods.value.length)

  // 统计最常见心情
  const moodCounts = {}
  filteredMoods.value.forEach(mood => {
    moodCounts[mood.mood_type] = (moodCounts[mood.mood_type] || 0) + 1
  })

  const mostCommonType = Object.entries(moodCounts)
    .sort(([,a], [,b]) => b - a)[0]?.[0]

  const mostCommon = mostCommonType ? getMoodLabel(mostCommonType) : '-'

  // 计算连续记录天数
  const currentStreak = calculateCurrentStreak()

  return {
    totalRecords: filteredMoods.value.length,
    avgIntensity,
    mostCommon,
    currentStreak
  }
})

const chartData = computed(() => {
  // 取最近30条记录用于图表显示
  return filteredMoods.value
    .slice(-30)
    .reverse()
    .map(mood => ({
      date: formatDate(mood.date),
      mood_type: mood.mood_type,
      intensity: mood.intensity || 5
    }))
})

// 工具函数
const getMoodEmoji = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.emoji : '😐'
}

const getMoodLabel = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.label : '未知'
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateCurrentStreak = () => {
  const sortedMoods = [...filteredMoods.value].sort((a, b) => new Date(b.date) - new Date(a.date))
  if (sortedMoods.length === 0) return 0

  let streak = 0
  const today = new Date()
  const current = new Date(today)

  for (let i = 0; i < 365; i++) {
    const dateStr = current.toISOString().split('T')[0]
    const hasMood = sortedMoods.some(mood => mood.date.startsWith(dateStr))

    if (hasMood) {
      streak++
    } else if (i > 0) {
      break
    }
    current.setDate(current.getDate() - 1)
  }

  return streak
}

// 事件处理
const onSearchChange = () => {
  currentPage.value = 1
}

const onFilterChange = () => {
  currentPage.value = 1
}

const onTimeRangeChange = () => {
  currentPage.value = 1
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const goToPage = (page) => {
  if (typeof page === 'number') {
    currentPage.value = page
  }
}

const editMood = (mood) => {
  // TODO: 实现编辑功能
  uiStore.showFlashMessage('编辑功能开发中', 'info')
}

const deleteMood = (mood) => {
  moodToDelete.value = mood
  showDeleteDialog.value = true
}

const closeDeleteDialog = () => {
  showDeleteDialog.value = false
  moodToDelete.value = null
}

const confirmDelete = async () => {
  if (!moodToDelete.value) return

  try {
    const result = await moodApi.deleteMood(moodToDelete.value.id)
    if (result.success) {
      uiStore.showFlashMessage('心情记录已删除', 'success')
      await loadMoodHistory()
    } else {
      uiStore.showFlashMessage(result.message || '删除失败', 'error')
    }
  } catch (error) {
    console.error('Failed to delete mood:', error)
    uiStore.showFlashMessage('删除失败，请重试', 'error')
  } finally {
    closeDeleteDialog()
  }
}

// 加载心情历史
const loadMoodHistory = async () => {
  loading.value = true
  try {
    const result = await moodApi.getMoodHistory(1, 1000) // 获取最多1000条记录

    if (result.success && result.moods) {
      moods.value = result.moods
    } else {
      console.error('Failed to load mood history:', result.message)
      moods.value = []
    }
  } catch (error) {
    console.error('Failed to load mood history:', error)
    uiStore.showFlashMessage('加载心情历史失败', 'error')
    moods.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadMoodHistory()
  }
})
</script>

<style scoped>
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
</style>