<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面头部 -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-slate-900">心情日历</h1>
          <p class="mt-2 text-neutral-500">查看您的心情变化轨迹，了解情绪模式</p>
        </div>
        <router-link
          to="/mood"
          class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          <i class="fas fa-arrow-left mr-2"></i>
          返回心情记录
        </router-link>
      </div>
    </div>

    <div v-if="!authStore.isAuthenticated" class="text-center py-16">
      <div class="mb-6">
        <i class="fas fa-calendar-alt text-8xl text-gray-300"></i>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 mb-3">需要登录</h3>
      <p class="text-gray-500 text-lg mb-6">请先登录以查看心情日历</p>
      <router-link
        to="/login"
        class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
      >
        去登录
      </router-link>
    </div>

    <div v-else class="space-y-8">
      <!-- 月份导航 -->
      <div class="surface-muted p-6">
        <div class="flex items-center justify-between mb-6">
          <button
            @click="previousMonth"
            class="p-2 text-gray-500 hover:text-neutral-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <i class="fas fa-chevron-left text-xl"></i>
          </button>

          <div class="text-center">
            <h2 class="text-2xl font-bold text-slate-900">
              {{ currentYear }}年{{ currentMonth + 1 }}月
            </h2>
            <p class="text-sm text-gray-500 mt-1">
              共记录 {{ Object.keys(moodData).length }} 天心情
            </p>
          </div>

          <button
            @click="nextMonth"
            class="p-2 text-gray-500 hover:text-neutral-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <i class="fas fa-chevron-right text-xl"></i>
          </button>
        </div>

        <!-- 快速跳转 -->
        <div class="flex items-center justify-center space-x-4">
          <button
            @click="goToToday"
            class="px-4 py-2 text-sm bg-primary-50 text-blue-700 rounded-lg hover:bg-primary-100 transition-colors"
          >
            今天
          </button>
          <select
            v-model="selectedMonth"
            @change="onMonthChange"
            class="px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
          >
            <option v-for="(month, index) in monthNames" :key="index" :value="index">
              {{ month }}
            </option>
          </select>
          <select
            v-model="selectedYear"
            @change="onYearChange"
            class="px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
          >
            <option v-for="year in availableYears" :key="year" :value="year">
              {{ year }}年
            </option>
          </select>
        </div>
      </div>

      <!-- 日历网格 -->
      <div class="surface-muted p-6">
        <!-- 星期标题 -->
        <div class="grid grid-cols-7 gap-1 mb-4">
          <div
            v-for="day in weekDays"
            :key="day"
            class="text-center text-sm font-medium text-neutral-600 py-2"
          >
            {{ day }}
          </div>
        </div>

        <!-- 日期网格 -->
        <div class="grid grid-cols-7 gap-1">
          <div
            v-for="date in calendarDates"
            :key="date.key"
            :class="[
              'relative min-h-[80px] p-2 border rounded-lg transition-all duration-200',
              getDateClasses(date)
            ]"
            @click="selectDate(date)"
            @mouseenter="hoveredDate = date.date"
            @mouseleave="hoveredDate = null"
          >
            <!-- 日期数字 -->
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium" :class="getTextColor(date)">
                {{ date.day }}
              </span>
              <span v-if="isToday(date)" class="text-xs bg-primary-500 text-white px-1 rounded">
                今天
              </span>
            </div>

            <!-- 心情图标 -->
            <div v-if="getMoodForDate(date.date)" class="flex items-center justify-center">
              <div class="text-2xl">
                {{ getMoodEmoji(getMoodForDate(date.date).mood_type) }}
              </div>
            </div>

            <!-- 强度指示器 -->
            <div
              v-if="getMoodForDate(date.date)?.intensity"
              class="absolute bottom-1 left-0 right-0 flex justify-center"
            >
              <div class="flex space-x-1">
                <div
                  v-for="i in Math.ceil(getMoodForDate(date.date).intensity / 2)"
                  :key="i"
                  class="w-1 h-1 bg-blue-400 rounded-full"
                ></div>
              </div>
            </div>

            <!-- 悬停提示 -->
            <div
              v-if="hoveredDate === date.date && getMoodForDate(date.date)"
              class="absolute z-10 bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-2 bg-gray-800 text-white text-xs rounded-lg whitespace-nowrap"
            >
              <div class="font-medium">
                {{ getMoodLabel(getMoodForDate(date.date).mood_type) }}
              </div>
              <div v-if="getMoodForDate(date.date).intensity">
                强度: {{ getMoodForDate(date.date).intensity }}/10
              </div>
              <div v-if="getMoodForDate(date.date).diary" class="max-w-[200px] truncate">
                {{ getMoodForDate(date.date).diary }}
              </div>
              <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                <div class="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 选中日期详情 -->
      <div v-if="selectedDateMood" class="surface-muted p-6">
        <h3 class="text-lg font-semibold text-slate-900 mb-4">
          {{ formatDate(selectedDate) }} 的心情详情
        </h3>

        <div class="flex items-start space-x-6">
          <div class="text-6xl">
            {{ getMoodEmoji(selectedDateMood.mood_type) }}
          </div>

          <div class="flex-1">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 class="text-sm font-medium text-gray-500">心情类型</h4>
                <p class="text-lg font-medium text-slate-900">
                  {{ getMoodLabel(selectedDateMood.mood_type) }}
                </p>
              </div>

              <div v-if="selectedDateMood.intensity">
                <h4 class="text-sm font-medium text-gray-500">强度</h4>
                <div class="flex items-center space-x-2">
                  <div class="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-primary-500 h-2 rounded-full"
                      :style="{ width: `${selectedDateMood.intensity * 10}%` }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-neutral-600">
                    {{ selectedDateMood.intensity }}/10
                  </span>
                </div>
              </div>

              <div v-if="selectedDateMood.custom_mood">
                <h4 class="text-sm font-medium text-gray-500">自定义心情</h4>
                <p class="text-lg font-medium text-slate-900">
                  {{ selectedDateMood.custom_mood }}
                </p>
              </div>

              <div>
                <h4 class="text-sm font-medium text-gray-500">记录时间</h4>
                <p class="text-sm text-neutral-600">
                  {{ formatDateTime(selectedDateMood.timestamp) }}
                </p>
              </div>
            </div>

            <div v-if="selectedDateMood.diary" class="mt-4">
              <h4 class="text-sm font-medium text-gray-500 mb-2">日记</h4>
              <div class="p-3 bg-neutral-100 rounded-lg">
                <p class="text-neutral-600">{{ selectedDateMood.diary }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 月度统计 -->
      <div class="surface-muted p-6">
        <h3 class="text-lg font-semibold text-slate-900 mb-4">月度统计</h3>

        <div v-if="monthlyStats.totalDays > 0" class="space-y-4">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-primary-50 rounded-lg">
              <div class="text-2xl font-bold text-primary-600">{{ monthlyStats.totalDays }}</div>
              <div class="text-sm text-blue-900">记录天数</div>
            </div>

            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-600">{{ monthlyStats.avgIntensity }}/10</div>
              <div class="text-sm text-green-900">平均强度</div>
            </div>

            <div class="text-center p-4 bg-purple-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-600">{{ monthlyStats.mostCommon }}</div>
              <div class="text-sm text-purple-900">最常见心情</div>
            </div>

            <div class="text-center p-4 bg-orange-50 rounded-lg">
              <div class="text-2xl font-bold text-orange-600">{{ monthlyStats.streak }}天</div>
              <div class="text-sm text-orange-900">连续记录</div>
            </div>
          </div>

          <!-- 心情分布 -->
          <div>
            <h4 class="text-md font-medium text-slate-900 mb-3">心情分布</h4>
            <div class="space-y-2">
              <div
                v-for="stat in monthlyStats.distribution"
                :key="stat.type"
                class="flex items-center space-x-3"
              >
                <div class="text-xl">{{ getMoodEmoji(stat.type) }}</div>
                <div class="flex-1">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-sm font-medium text-neutral-600">
                      {{ getMoodLabel(stat.type) }}
                    </span>
                    <span class="text-sm text-gray-500">{{ stat.count }}天</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-primary-500 h-2 rounded-full"
                      :style="{ width: `${(stat.count / monthlyStats.totalDays) * 100}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <p class="text-gray-500">本月暂无心情记录</p>
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
const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth())
const selectedYear = ref(currentYear.value)
const selectedMonth = ref(currentMonth.value)
const hoveredDate = ref(null)
const selectedDate = ref(null)
const selectedDateMood = ref(null)
const moodData = ref({})
const loading = ref(false)

// 配置
const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const monthNames = [
  '一月', '二月', '三月', '四月', '五月', '六月',
  '七月', '八月', '九月', '十月', '十一月', '十二月'
]

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
const calendarDates = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())

  const dates = []
  const current = new Date(startDate)

  for (let i = 0; i < 42; i++) {
    dates.push({
      key: `${current.getFullYear()}-${current.getMonth()}-${current.getDate()}`,
      date: formatDateForApi(current),
      day: current.getDate(),
      month: current.getMonth(),
      year: current.getFullYear(),
      isCurrentMonth: current.getMonth() === currentMonth.value
    })
    current.setDate(current.getDate() + 1)
  }

  return dates
})

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let year = currentYear - 3; year <= currentYear + 1; year++) {
    years.push(year)
  }
  return years
})

const monthlyStats = computed(() => {
  const days = Object.keys(moodData.value)
  if (days.length === 0) {
    return { totalDays: 0, avgIntensity: 0, mostCommon: '-', streak: 0, distribution: [] }
  }

  const moods = Object.values(moodData.value)
  const totalIntensity = moods.reduce((sum, mood) => sum + (mood.intensity || 0), 0)
  const avgIntensity = Math.round(totalIntensity / moods.length)

  // 统计心情类型分布
  const moodCounts = {}
  moods.forEach(mood => {
    moodCounts[mood.mood_type] = (moodCounts[mood.mood_type] || 0) + 1
  })

  const distribution = Object.entries(moodCounts)
    .map(([type, count]) => ({ type, count }))
    .sort((a, b) => b.count - a.count)

  const mostCommon = distribution.length > 0
    ? getMoodLabel(distribution[0].type)
    : '-'

  // 计算连续记录天数
  const streak = calculateStreak()

  return {
    totalDays: days.length,
    avgIntensity,
    mostCommon,
    streak,
    distribution
  }
})

// 工具函数
const formatDateForApi = (date) => {
  return date.toISOString().split('T')[0]
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
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

const getMoodEmoji = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.emoji : '😐'
}

const getMoodLabel = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.label : '未知'
}

const isToday = (date) => {
  const today = new Date()
  const dateObj = new Date(date.date + 'T00:00:00')
  return dateObj.toDateString() === today.toDateString()
}

const isOtherMonth = (date) => {
  return date.month !== currentMonth.value
}

const getDateClasses = (date) => {
  const mood = getMoodForDate(date.date)
  const classes = []

  if (isOtherMonth(date)) {
    classes.push('bg-neutral-100 text-gray-400 border-gray-200')
  } else if (isToday(date)) {
    classes.push('bg-primary-50 border-blue-300')
  } else {
    classes.push('bg-white/80 border-gray-200 hover:border-neutral-200')
  }

  if (mood) {
    classes.push('cursor-pointer hover:shadow-md')
    if (mood.mood_type === 'happy' || mood.mood_type === 'excited') {
      classes.push('border-yellow-300')
    } else if (mood.mood_type === 'sad' || mood.mood_type === 'angry') {
      classes.push('border-red-300')
    } else if (mood.mood_type === 'anxious' || mood.mood_type === 'confused') {
      classes.push('border-orange-300')
    } else {
      classes.push('border-green-300')
    }
  } else {
    classes.push('cursor-pointer')
  }

  return classes.join(' ')
}

const getTextColor = (date) => {
  if (isOtherMonth(date)) return 'text-gray-400'
  if (isToday(date)) return 'text-primary-600'
  return 'text-slate-900'
}

const getMoodForDate = (dateStr) => {
  return moodData.value[dateStr]
}

const calculateStreak = () => {
  const days = Object.keys(moodData.value).sort().reverse()
  if (days.length === 0) return 0

  let streak = 0
  const today = new Date()
  const current = new Date(today)

  for (let i = 0; i < 365; i++) {
    const dateStr = formatDateForApi(current)
    if (moodData.value[dateStr]) {
      streak++
    } else if (i > 0) {
      break
    }
    current.setDate(current.getDate() - 1)
  }

  return streak
}

// 事件处理
const previousMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
  selectedMonth.value = currentMonth.value
  selectedYear.value = currentYear.value
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  selectedMonth.value = currentMonth.value
  selectedYear.value = currentYear.value
}

const onMonthChange = () => {
  currentMonth.value = selectedMonth.value
}

const onYearChange = () => {
  currentYear.value = selectedYear.value
}

const goToToday = () => {
  const today = new Date()
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth()
  selectedYear.value = currentYear.value
  selectedMonth.value = currentMonth.value
}

const selectDate = (date) => {
  if (isOtherMonth(date)) return

  selectedDate.value = date.date
  selectedDateMood.value = getMoodForDate(date.date)
}

// 加载月度数据
const loadMonthlyData = async () => {
  loading.value = true
  try {
    const startDate = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-01`
    const endDate = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-31`

    const result = await moodApi.getMoodCalendar(currentYear.value, currentMonth.value + 1)

    if (result.success && result.moods) {
      const newMoodData = {}
      result.moods.forEach(mood => {
        const dateStr = mood.date.split(' ')[0] // 只取日期部分
        newMoodData[dateStr] = mood
      })
      moodData.value = newMoodData
    } else {
      console.error('Failed to load monthly mood data:', result.message)
      moodData.value = {}
    }
  } catch (error) {
    console.error('Failed to load monthly mood data:', error)
    uiStore.showFlashMessage('加载月度数据失败', 'error')
    moodData.value = {}
  } finally {
    loading.value = false
  }
}

// 监听月份和年份变化
watch([currentYear, currentMonth], () => {
  loadMonthlyData()
})

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadMonthlyData()
  }
})
</script>

<style scoped>
.min-h-\[80px\] {
  min-height: 80px;
}
</style>