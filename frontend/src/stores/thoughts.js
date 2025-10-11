import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { thoughtsApi } from '../api/thoughts'

export const useThoughtsStore = defineStore('thoughts', () => {
  // 状态
  const thoughts = ref([])
  const recentThoughts = ref([])
  const currentThought = ref(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    pages: 0,
    per_page: 20,
    total: 0,
    has_prev: false,
    has_next: false,
    prev_num: null,
    next_num: null
  })

  // 计算属性
  const hasThoughts = computed(() => thoughts.value.length > 0)
  const hasRecentThoughts = computed(() => recentThoughts.value.length > 0)
  const thoughtTypes = computed(() => [
    { value: 'note', label: '笔记', color: 'blue' },
    { value: 'quote', label: '引用', color: 'green' },
    { value: 'idea', label: '想法', color: 'purple' },
    { value: 'task', label: '任务', color: 'orange' }
  ])

  // 获取想法列表
  const fetchThoughts = async (page = 1, perPage = 20) => {
    loading.value = true
    try {
      const response = await thoughtsApi.getThoughts(page, perPage)

      if (response.success) {
        thoughts.value = response.thoughts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '获取想法列表失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取最近想法
  const fetchRecentThoughts = async (limit = 5) => {
    try {
      const response = await thoughtsApi.getRecentThoughts(limit)

      if (response.success) {
        recentThoughts.value = response.thoughts
        return { success: true }
      } else {
        throw new Error(response.message || '获取最近想法失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }

  // 获取单条想法
  const fetchThought = async (id) => {
    loading.value = true
    try {
      const response = await thoughtsApi.getThought(id)

      if (response.success) {
        currentThought.value = response.thought
        return { success: true }
      } else {
        throw new Error(response.message || '获取想法失败')
      }
    } catch (error) {
      currentThought.value = null
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 创建想法
  const createThought = async (thoughtData) => {
    loading.value = true
    try {
      const response = await thoughtsApi.createThought(thoughtData)

      if (response.success) {
        // 将新想法添加到列表开头
        thoughts.value.unshift(response.thought)
        recentThoughts.value.unshift(response.thought)
        // 限制最近想法数量
        if (recentThoughts.value.length > 10) {
          recentThoughts.value = recentThoughts.value.slice(0, 10)
        }
        return { success: true, thought: response.thought }
      } else {
        throw new Error(response.message || '创建想法失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 快速创建想法
  const quickCreateThought = async (content, thoughtType = 'note', isPublic = true) => {
    const thoughtData = {
      content,
      thought_type: thoughtType,
      is_public: isPublic ? 'y' : 'n'
    }

    return await createThought(thoughtData)
  }

  // 删除想法
  const deleteThought = async (id) => {
    loading.value = true
    try {
      const response = await thoughtsApi.deleteThought(id)

      if (response.success) {
        // 从列表中移除想法
        thoughts.value = thoughts.value.filter(thought => thought.id !== id)
        recentThoughts.value = recentThoughts.value.filter(thought => thought.id !== id)
        // 清除当前想法
        if (currentThought.value?.id === id) {
          currentThought.value = null
        }
        return { success: true }
      } else {
        throw new Error(response.message || '删除想法失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 搜索想法
  const searchThoughts = async (query, page = 1) => {
    loading.value = true
    try {
      const response = await thoughtsApi.searchThoughts(query, page)

      if (response.success) {
        thoughts.value = response.thoughts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '搜索失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 根据标签获取想法
  const fetchThoughtsByTag = async (tag, page = 1) => {
    loading.value = true
    try {
      const response = await thoughtsApi.getThoughtsByTag(tag, page)

      if (response.success) {
        thoughts.value = response.thoughts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '获取标签想法失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取用户想法
  const fetchUserThoughts = async (username, page = 1) => {
    loading.value = true
    try {
      const response = await thoughtsApi.getUserThoughts(username, page)

      if (response.success) {
        thoughts.value = response.thoughts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '获取用户想法失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取想法类型配置
  const getThoughtTypeConfig = (type) => {
    const config = thoughtTypes.value.find(t => t.value === type)
    return config || { value: 'note', label: '笔记', color: 'blue' }
  }

  // 格式化想法内容
  const formatThoughtContent = (content) => {
    if (!content) return ''
    // 简单的markdown格式化
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>')
  }

  // 清空当前想法
  const clearCurrentThought = () => {
    currentThought.value = null
  }

  // 重置状态
  const resetState = () => {
    thoughts.value = []
    recentThoughts.value = []
    currentThought.value = null
    loading.value = false
    pagination.value = {
      page: 1,
      pages: 0,
      per_page: 20,
      total: 0,
      has_prev: false,
      has_next: false,
      prev_num: null,
      next_num: null
    }
  }

  return {
    // 状态
    thoughts,
    recentThoughts,
    currentThought,
    loading,
    pagination,

    // 计算属性
    hasThoughts,
    hasRecentThoughts,
    thoughtTypes,

    // 方法
    fetchThoughts,
    fetchRecentThoughts,
    fetchThought,
    createThought,
    quickCreateThought,
    deleteThought,
    searchThoughts,
    fetchThoughtsByTag,
    fetchUserThoughts,
    getThoughtTypeConfig,
    formatThoughtContent,
    clearCurrentThought,
    resetState
  }
})