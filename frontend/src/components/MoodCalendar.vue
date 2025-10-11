<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900 flex items-center">
        <CalendarDaysIcon class="w-5 h-5 text-blue-500 mr-2" />
        心情日历
      </h2>
      <router-link
        to="/mood/calendar"
        class="text-sm text-blue-600 hover:text-blue-800 font-medium"
      >
        查看全部
      </router-link>
    </div>

    <!-- 月份导航 -->
    <div class="flex items-center justify-between mb-4">
      <button
        @click="previousMonth"
        class="p-1 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </button>
      <h3 class="text-sm font-medium text-gray-900">
        {{ currentMonth }} {{ currentYear }}
      </h3>
      <button
        @click="nextMonth"
        class="p-1 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ChevronRightIcon class="w-5 h-5" />
      </button>
    </div>

    <!-- 星期标题 -->
    <div class="grid grid-cols-7 gap-1 mb-2">
      <div
        v-for="day in weekDays"
        :key="day"
        class="text-xs text-center text-gray-500 font-medium"
      >
        {{ day }}
      </div>
    </div>

    <!-- 日期网格 -->
    <div class="grid grid-cols-7 gap-1">
      <button
        v-for="date in calendarDates"
        :key="date.key"
        @click="selectDate(date)"
        :class="[
          'relative h-8 w-8 rounded-md text-xs font-medium transition-all duration-200',
          date.isCurrentMonth
            ? 'text-gray-900 hover:bg-gray-100'
            : 'text-gray-400 hover:text-gray-600',
          date.isToday
            ? 'bg-blue-100 text-blue-900 font-bold ring-2 ring-blue-500'
            : '',
          date.isSelected
            ? 'bg-blue-500 text-white hover:bg-blue-600'
            : '',
          date.mood
            ? 'ring-2 ring-opacity-50'
            : '',
          getMoodColor(date.mood)
        ]"
        :disabled="date.isCurrentMonth === false"
      >
        {{ date.day }}
        <span
          v-if="date.mood"
          :class="[
            'absolute bottom-0 right-0 w-2 h-2 rounded-full',
            getMoodDotColor(date.mood)
          ]"
        ></span>
      </button>
    </div>

    <!-- 心情统计 -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-600">本月记录</span>
        <span class="font-medium text-gray-900">{{ monthlyMoodCount }} 天</span>
      </div>
      <div class="flex items-center justify-between text-sm mt-1">
        <span class="text-gray-600">当前心情</span>
        <div class="flex items-center">
          <span v-if="todayMood" :class="['text-lg', getMoodEmoji(todayMood.mood)]"></span>
          <span v-else class="text-gray-400 text-xs">未记录</span>
        </div>
      </div>
    </div>

    <!-- 快速记录按钮 -->
    <div class="mt-4">
      <button
        @click="quickRecord"
        class="w-full flex items-center justify-center px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
      >
        <PlusIcon class="w-4 h-4 mr-1" />
        快速记录
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMoodStore } from '../stores/mood'
import {
  CalendarDaysIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const moodStore = useMoodStore()

// 状态管理
const currentDate = ref(new Date())
const selectedDate = ref(new Date())

// 星期标题
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

// 月份名称
const monthNames = [
  '一月', '二月', '三月', '四月', '五月', '六月',
  '七月', '八月', '九月', '十月', '十一月', '十二月'
]

// 计算属性
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => monthNames[currentDate.value.getMonth()])

const calendarDates = computed(() => {
  const dates = []
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  // 获取当月第一天和最后一天
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())

  // 生成6周的日期（42天）
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)

    const isCurrentMonth = date.getMonth() === month
    const isToday = isSameDay(date, new Date())
    const isSelected = isSameDay(date, selectedDate.value)
    const mood = moodStore.getMoodByDate(formatDate(date))

    dates.push({
      key: `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`,
      day: date.getDate(),
      date: new Date(date),
      isCurrentMonth,
      isToday,
      isSelected,
      mood
    })

    // 如果已经到了下个月且完成了完整周，提前结束
    if (i > 27 && date.getMonth() !== month && date.getDay() === 6) {
      break
    }
  }

  return dates
})

const monthlyMoodCount = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  return moodStore.getMoodsByMonth(year, month).length
})

const todayMood = computed(() => {
  return moodStore.getMoodByDate(formatDate(new Date()))
})

// 方法
const isSameDay = (date1, date2) => {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate()
}

const formatDate = (date) => {
  return date.toISOString().split('T')[0]
}

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1)
}

const selectDate = (date) => {
  if (date.isCurrentMonth) {
    selectedDate.value = date.date
    if (date.mood) {
      // 跳转到该日期的心情详情
      router.push(`/mood/date/${formatDate(date.date)}`)
    } else {
      // 快速记录该日期的心情
      quickRecordForDate(date.date)
    }
  }
}

const quickRecord = () => {
  quickRecordForDate(new Date())
}

const quickRecordForDate = (date) => {
  // 这里可以打开一个快速记录模态框，或者跳转到记录页面
  router.push({
    path: '/mood',
    query: { date: formatDate(date) }
  })
}

const getMoodEmoji = (mood) => {
  const emojiMap = {
    'happy': '😊',
    'excited': '🤗',
    'calm': '😌',
    'neutral': '😐',
    'sad': '😢',
    'angry': '😠',
    'anxious': '😰',
    'tired': '😴',
    'stressed': '😫',
    'love': '😍'
  }
  return emojiMap[mood] || '😐'
}

const getMoodColor = (mood) => {
  const colorMap = {
    'happy': 'ring-green-200',
    'excited': 'ring-yellow-200',
    'calm': 'ring-blue-200',
    'neutral': 'ring-gray-200',
    'sad': 'ring-indigo-200',
    'angry': 'ring-red-200',
    'anxious': 'ring-orange-200',
    'tired': 'ring-purple-200',
    'stressed': 'ring-pink-200',
    'love': 'ring-rose-200'
  }
  return colorMap[mood] || ''
}

const getMoodDotColor = (mood) => {
  const colorMap = {
    'happy': 'bg-green-500',
    'excited': 'bg-yellow-500',
    'calm': 'bg-blue-500',
    'neutral': 'bg-gray-500',
    'sad': 'bg-indigo-500',
    'angry': 'bg-red-500',
    'anxious': 'bg-orange-500',
    'tired': 'bg-purple-500',
    'stressed': 'bg-pink-500',
    'love': 'bg-rose-500'
  }
  return colorMap[mood] || 'bg-gray-400'
}

// 初始化
onMounted(async () => {
  await moodStore.fetchRecentMoods()
})
</script>

<style scoped>
/* 自定义样式 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>