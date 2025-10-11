import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { blogApi } from '../api/blog'

export const useBlogStore = defineStore('blog', () => {
  // 状态
  const posts = ref([])
  const currentPost = ref(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    pages: 0,
    per_page: 10,
    total: 0,
    has_prev: false,
    has_next: false,
    prev_num: null,
    next_num: null
  })

  // 计算属性
  const hasPosts = computed(() => posts.value.length > 0)
  const hasNextPage = computed(() => pagination.value.has_next)
  const hasPrevPage = computed(() => pagination.value.has_prev)

  // 获取文章列表
  const fetchPosts = async (page = 1, perPage = 10) => {
    loading.value = true
    try {
      const response = await blogApi.getPosts(page, perPage)

      if (response.success) {
        posts.value = response.posts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '获取文章列表失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 获取单篇文章
  const fetchPost = async (id) => {
    loading.value = true
    try {
      const response = await blogApi.getPost(id)

      if (response.success) {
        currentPost.value = response.post
        return { success: true }
      } else {
        throw new Error(response.message || '获取文章失败')
      }
    } catch (error) {
      currentPost.value = null
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 创建文章
  const createPost = async (postData) => {
    loading.value = true
    try {
      const response = await blogApi.createPost(postData)

      if (response.success) {
        // 将新文章添加到列表开头
        posts.value.unshift(response.post)
        return { success: true, post: response.post }
      } else {
        throw new Error(response.message || '创建文章失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 更新文章
  const updatePost = async (id, postData) => {
    loading.value = true
    try {
      const response = await blogApi.updatePost(id, postData)

      if (response.success) {
        // 更新列表中的文章
        const index = posts.value.findIndex(post => post.id === id)
        if (index !== -1) {
          posts.value[index] = response.post
        }
        // 更新当前文章
        if (currentPost.value?.id === id) {
          currentPost.value = response.post
        }
        return { success: true, post: response.post }
      } else {
        throw new Error(response.message || '更新文章失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 删除文章
  const deletePost = async (id) => {
    loading.value = true
    try {
      const response = await blogApi.deletePost(id)

      if (response.success) {
        // 从列表中移除文章
        posts.value = posts.value.filter(post => post.id !== id)
        // 清除当前文章
        if (currentPost.value?.id === id) {
          currentPost.value = null
        }
        return { success: true }
      } else {
        throw new Error(response.message || '删除文章失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 搜索文章
  const searchPosts = async (query, page = 1) => {
    loading.value = true
    try {
      const response = await blogApi.searchPosts(query, page)

      if (response.success) {
        posts.value = response.posts
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

  // 获取用户文章
  const fetchUserPosts = async (username, page = 1) => {
    loading.value = true
    try {
      const response = await blogApi.getUserPosts(username, page)

      if (response.success) {
        posts.value = response.posts
        pagination.value = response.pagination
        return { success: true }
      } else {
        throw new Error(response.message || '获取用户文章失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 清空当前文章
  const clearCurrentPost = () => {
    currentPost.value = null
  }

  // 重置状态
  const resetState = () => {
    posts.value = []
    currentPost.value = null
    loading.value = false
    pagination.value = {
      page: 1,
      pages: 0,
      per_page: 10,
      total: 0,
      has_prev: false,
      has_next: false,
      prev_num: null,
      next_num: null
    }
  }

  return {
    // 状态
    posts,
    currentPost,
    loading,
    pagination,

    // 计算属性
    hasPosts,
    hasNextPage,
    hasPrevPage,

    // 方法
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    searchPosts,
    fetchUserPosts,
    clearCurrentPost,
    resetState
  }
})