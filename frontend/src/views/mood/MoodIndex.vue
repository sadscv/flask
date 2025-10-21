<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面头部 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900">心情记录</h1>
      <p class="mt-2 text-neutral-500">记录每天的心情变化，追踪情绪状态</p>
    </div>

    <div v-if="!authStore.isAuthenticated" class="text-center py-16">
      <div class="mb-6">
        <i class="fas fa-heart text-8xl text-gray-300"></i>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 mb-3">需要登录</h3>
      <p class="text-gray-500 text-lg mb-6">请先登录以记录心情</p>
      <router-link
        to="/login"
        class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
      >
        去登录
      </router-link>
    </div>

    <div v-else class="space-y-8">
      <!-- 今日心情卡片 -->
      <div class="surface-muted p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-6">今日心情</h2>

        <div v-if="!todayMood" class="text-center py-8">
          <p class="text-gray-500 mb-4">今天还没有记录心情</p>
          <p class="text-sm text-gray-400">点击下方选择今天的心情</p>
        </div>

        <div v-else class="text-center py-6">
          <div class="text-6xl mb-4">{{ getMoodEmoji(todayMood.mood_type) }}</div>
          <h3 class="text-lg font-medium text-slate-900">{{ getMoodLabel(todayMood.mood_type) }}</h3>
          <p v-if="todayMood.intensity" class="text-sm text-neutral-500 mt-2">
            强度: {{ todayMood.intensity }}/10
          </p>
          <p v-if="todayMood.diary" class="text-sm text-neutral-500 mt-2 max-w-md mx-auto">
            {{ todayMood.diary }}
          </p>
        </div>

        <!-- 心情选择器 -->
        <div class="mt-6">
          <h3 class="text-md font-medium text-slate-900 mb-4">记录今天的心情</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <button
              v-for="mood in moodTypes"
              :key="mood.type"
              @click="selectMood(mood.type)"
              :class="[
                'p-4 text-center rounded-lg border-2 transition-all duration-200 hover:scale-105',
                selectedMood === mood.type ? 'border-primary-500 bg-primary-50' : 'border-gray-200 bg-white/80 hover:border-neutral-200'
              ]"
            >
              <div class="text-3xl mb-2">{{ mood.emoji }}</div>
              <div class="text-sm font-medium">{{ mood.label }}</div>
            </button>
          </div>
        </div>

        <!-- 心情表单 -->
        <div v-if="showMoodForm" class="mt-6 p-6 bg-neutral-100 rounded-lg">
          <form @submit.prevent="saveMood" class="space-y-4">
            <div v-if="selectedMood">
              <label class="block text-sm font-medium text-neutral-600 mb-2">
                当前选择: {{ getMoodLabel(selectedMood) }}
              </label>
            </div>

            <div>
              <label class="block text-sm font-medium text-neutral-600 mb-2">强度 (1-10)</label>
              <div class="flex items-center space-x-2">
                <input
                  v-model="moodForm.intensity"
                  type="range"
                  min="1"
                  max="10"
                  class="flex-1"
                />
                <span class="w-8 text-center text-sm font-medium text-neutral-600">
                  {{ moodForm.intensity }}
                </span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-neutral-600 mb-2">日记 (可选)</label>
              <textarea
                v-model="moodForm.diary"
                rows="3"
                class="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent resize-none"
                placeholder="记录今天的感受..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-neutral-600 mb-2">自定义心情 (可选)</label>
              <input
                v-model="moodForm.custom_mood"
                type="text"
                class="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-200 focus:border-transparent"
                placeholder="例如：开心、激动"
              />
            </div>

            <div class="flex space-x-4">
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 btn btn-primary focus:outline-none focus:ring-2 focus:ring-primary-200 focus:ring-offset-2 disabled:opacity-50"
              >
                {{ saving ? '保存中...' : '保存心情' }}
              </button>
              <button
                type="button"
                @click="cancelMood"
                class="px-4 py-2 bg-gray-300 text-neutral-600 rounded-lg hover:bg-gray-400"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 快速链接 -->
      <div class="surface-muted p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">心情统计</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <router-link
            to="/mood/calendar"
            class="block p-4 text-center bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <i class="fas fa-calendar-alt text-2xl text-primary-600 mb-2"></i>
            <div class="text-sm font-medium text-blue-900">心情日历</div>
          </router-link>
          <router-link
            to="/mood/history"
            class="block p-4 text-center bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <i class="fas fa-chart-line text-2xl text-green-600 mb-2"></i>
            <div class="text-sm font-medium text-green-900">历史记录</div>
          </router-link>
          <div class="block p-4 text-center bg-purple-50 rounded-lg">
            <i class="fas fa-chart-pie text-2xl text-purple-600 mb-2"></i>
            <div class="text-sm font-medium text-purple-900">数据分析</div>
          </div>
        </div>
      </div>

      <!-- 最近心情记录 -->
      <div class="surface-muted p-6">
        <h2 class="text-lg font-semibold text-slate-900 mb-4">最近心情</h2>
        <div v-if="recentMoods.length > 0" class="space-y-4">
          <div
            v-for="mood in recentMoods"
            :key="mood.id"
            class="flex items-center justify-between p-4 bg-neutral-100 rounded-lg"
          >
            <div class="flex items-center space-x-4">
              <div class="text-2xl">{{ getMoodEmoji(mood.mood_type) }}</div>
              <div>
                <div class="font-medium text-slate-900">{{ getMoodLabel(mood.mood_type) }}</div>
                <div class="text-sm text-gray-500">
                  {{ formatDateTime(mood.date) }}
                  <span v-if="mood.intensity" class="ml-2">
                    强度: {{ mood.intensity }}/10
                  </span>
                </div>
                <div v-if="mood.diary" class="text-sm text-neutral-500 mt-1 max-w-xs">
                  {{ mood.diary }}
                </div>
              </div>
            </div>
            <div class="text-sm text-gray-500">
              {{ formatDateTime(mood.timestamp) }}
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <p class="text-gray-500">还没有心情记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import { moodApi } from '../../api/mood'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const todayMood = ref(null)
const recentMoods = ref([])
const selectedMood = ref('')
const showMoodForm = ref(false)
const saving = ref(false)

const moodForm = ref({
  intensity: 5,
  diary: '',
  custom_mood: ''
})

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

const getMoodEmoji = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.emoji : '😐'
}

const getMoodLabel = (type) => {
  const mood = moodTypes.find(m => m.type === type)
  return mood ? mood.label : '未知'
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

const selectMood = (moodType) => {
  selectedMood.value = moodType
  showMoodForm.value = true
  // 重置表单
  moodForm.value = {
    intensity: 5,
    diary: '',
    custom_mood: ''
  }
}

const cancelMood = () => {
  selectedMood.value = ''
  showMoodForm.value = false
}

const saveMood = async () => {
  if (!selectedMood.value) return

  saving.value = true
  try {
    // 准备心情数据
    const moodData = {
      mood_type: selectedMood.value,
      intensity: moodForm.value.intensity,
      diary: moodForm.value.diary,
      custom_mood: moodForm.value.custom_mood
    }

    // 调用API保存心情
    const result = await moodApi.createMood(moodData)

    if (result.success) {
      uiStore.showFlashMessage('心情已保存！', 'success')

      // 重置状态
      selectedMood.value = ''
      showMoodForm.value = false
      moodForm.value = {
        intensity: 5,
        diary: '',
        custom_mood: ''
      }

      // 重新加载数据
      await loadMoodData()
    } else {
      uiStore.showFlashMessage(result.message || '保存失败', 'error')
    }
  } catch (error) {
    console.error('Failed to save mood:', error)
    uiStore.showFlashMessage('保存失败，请重试', 'error')
  } finally {
    saving.value = false
  }
}

const loadMoodData = async () => {
  try {
    // 并行加载今日心情和最近心情
    const [todayResult, recentResult] = await Promise.all([
      moodApi.getTodayMood(),
      moodApi.getMoodHistory(1, 10) // 获取最近10条记录
    ])

    // 设置今日心情
    if (todayResult.success) {
      todayMood.value = todayResult.mood
    } else {
      console.error('Failed to load today mood:', todayResult.message)
      todayMood.value = null
    }

    // 设置最近心情
    if (recentResult.success && recentResult.moods) {
      recentMoods.value = recentResult.moods
    } else {
      console.error('Failed to load recent moods:', recentResult.message)
      recentMoods.value = []
    }
  } catch (error) {
    console.error('Failed to load mood data:', error)
    // 如果API失败，设置为空数组以避免界面错误
    todayMood.value = null
    recentMoods.value = []
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadMoodData()
  }
})
</script>