import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { moodApi } from '../api/mood'

export const useMoodStore = defineStore('mood', () => {
  // 状态
  const moods = ref([])
  const todayMood = ref(null)
  const moodStats = ref(null)
  const calendarData = ref(null)
  const loading = ref(false)

  // 心情配置
  const moodConfig = ref({
    happy: { color: '#FCD34D', icon: '😊', label: '开心', gradient: 'from-yellow-100 to-yellow-200' },
    calm: { color: '#93C5FD', icon: '😌', label: '平静', gradient: 'from-blue-100 to-blue-200' },
    anxious: { color: '#C4B5FD', icon: '😰', label: '焦虑', gradient: 'from-purple-100 to-purple-200' },
    sad: { color: '#9CA3AF', icon: '😢', label: '伤心', gradient: 'from-gray-100 to-gray-200' },
    angry: { color: '#F87171', icon: '😠', label: '愤怒', gradient: 'from-red-100 to-red-200' },
    custom: { color: '#86EFAC', icon: '💭', label: '自定义', gradient: 'from-green-100 to-green-200' }
  })

  // 计算属性
  const hasMoods = computed(() => moods.value.length > 0)
  const hasTodayMood = computed(() => !!todayMood.value)
  const moodTypes = computed(() => Object.keys(moodConfig.value))

  // 获取今日心情
  const fetchTodayMood = async () => {
    try {
      const response = await moodApi.getTodayMood()

      if (response.success) {
        todayMood.value = response.mood
        return { success: true }
      } else {
        todayMood.value = null
        return { success: false }
      }
    } catch (error) {
      todayMood.value = null
      return { success: false }
    }
  }

  // 创建心情记录
  const createMood = async (moodData) => {
    loading.value = true
    try {
      const response = await moodApi.createMood(moodData)

      if (response.success) {
        todayMood.value = response.mood
        moods.value.unshift(response.mood)
        return { success: true, mood: response.mood }
      } else {
        throw new Error(response.message || '记录心情失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 更新心情记录
  const updateMood = async (id, moodData) => {
    loading.value = true
    try {
      const response = await moodApi.updateMood(id, moodData)

      if (response.success) {
        // 更新今日心情
        if (todayMood.value?.id === id) {
          todayMood.value = response.mood
        }
        // 更新列表中的心情
        const index = moods.value.findIndex(mood => mood.id === id)
        if (index !== -1) {
          moods.value[index] = response.mood
        }
        return { success: true, mood: response.mood }
      } else {
        throw new Error(response.message || '更新心情失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取心情历史
  const fetchMoodHistory = async (page = 1, limit = 30) => {
    loading.value = true
    try {
      const response = await moodApi.getMoodHistory(page, limit)

      if (response.success) {
        if (page === 1) {
          moods.value = response.moods
        } else {
          moods.value.push(...response.moods)
        }
        return { success: true, moods: response.moods, hasMore: response.has_more }
      } else {
        throw new Error(response.message || '获取心情历史失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取心情统计
  const fetchMoodStats = async (period = 'week') => {
    try {
      const response = await moodApi.getMoodStats(period)

      if (response.success) {
        moodStats.value = response.stats
        return { success: true }
      } else {
        throw new Error(response.message || '获取心情统计失败')
      }
    } catch (error) {
      moodStats.value = null
      return { success: false, message: error.message }
    }
  }

  // 获取心情日历数据
  const fetchMoodCalendar = async (year, month) => {
    try {
      const response = await moodApi.getMoodCalendar(year, month)

      if (response.success) {
        calendarData.value = response.calendar_data
        return { success: true, calendarData: response.calendar_data }
      } else {
        throw new Error(response.message || '获取心情日历失败')
      }
    } catch (error) {
      calendarData.value = null
      return { success: false, message: error.message }
    }
  }

  // 获取特定日期的心情
  const fetchMoodByDate = async (date) => {
    try {
      const response = await moodApi.getMoodByDate(date)

      if (response.success) {
        return { success: true, moods: response.moods }
      } else {
        throw new Error(response.message || '获取日期心情失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }

  // 删除心情记录
  const deleteMood = async (id) => {
    loading.value = true
    try {
      const response = await moodApi.deleteMood(id)

      if (response.success) {
        // 从列表中移除
        moods.value = moods.value.filter(mood => mood.id !== id)
        // 如果删除的是今日心情，清空今日心情
        if (todayMood.value?.id === id) {
          todayMood.value = null
        }
        return { success: true }
      } else {
        throw new Error(response.message || '删除心情记录失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取心情配置
  const getMoodConfig = (moodType) => {
    return moodConfig.value[moodType] || moodConfig.value.custom
  }

  // 获取心情强度文本
  const getIntensityText = (intensity) => {
    if (intensity <= 3) return '平静'
    if (intensity <= 6) return '中等'
    if (intensity <= 8) return '较强'
    return '强烈'
  }

  // 获取心情强度颜色
  const getIntensityColor = (intensity) => {
    if (intensity <= 3) return 'text-blue-500'
    if (intensity <= 6) return 'text-yellow-500'
    if (intensity <= 8) return 'text-orange-500'
    return 'text-red-500'
  }

  // 计算心情分布
  const calculateMoodDistribution = (moodList) => {
    const distribution = {}
    const total = moodList.length

    moodList.forEach(mood => {
      if (!distribution[mood.mood_type]) {
        distribution[mood.mood_type] = 0
      }
      distribution[mood.mood_type]++
    })

    // 转换为百分比
    Object.keys(distribution).forEach(type => {
      distribution[type] = Math.round((distribution[type] / total) * 100)
    })

    return distribution
  }

  // 计算平均心情强度
  const calculateAverageIntensity = (moodList) => {
    if (moodList.length === 0) return 0

    const totalIntensity = moodList.reduce((sum, mood) => sum + mood.intensity, 0)
    return Math.round(totalIntensity / moodList.length)
  }

  // 格式化日期
  const formatDate = (date, format = 'YYYY-MM-DD') => {
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')

    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
  }

  // 重置状态
  const resetState = () => {
    moods.value = []
    todayMood.value = null
    moodStats.value = null
    calendarData.value = null
    loading.value = false
  }

  return {
    // 状态
    moods,
    todayMood,
    moodStats,
    calendarData,
    loading,
    moodConfig,

    // 计算属性
    hasMoods,
    hasTodayMood,
    moodTypes,

    // 方法
    fetchTodayMood,
    createMood,
    updateMood,
    fetchMoodHistory,
    fetchMoodStats,
    fetchMoodCalendar,
    fetchMoodByDate,
    deleteMood,
    getMoodConfig,
    getIntensityText,
    getIntensityColor,
    calculateMoodDistribution,
    calculateAverageIntensity,
    formatDate,
    resetState
  }
})