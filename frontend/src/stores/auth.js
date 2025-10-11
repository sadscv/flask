import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const canModerate = computed(() => user.value?.permissions?.includes('moderate'))

  // 登录
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await authApi.login(credentials)

      if (response.success) {
        token.value = response.token
        user.value = response.user
        localStorage.setItem('token', response.token)

        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.token}`

        return { success: true }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    loading.value = true
    try {
      const response = await authApi.register(userData)

      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }

  // 检查认证状态
  const checkAuth = async () => {
    if (!token.value) return false

    try {
      const response = await authApi.getCurrentUser()
      if (response.success) {
        user.value = response.user
        axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        return true
      } else {
        // token无效，清除状态
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        return false
      }
    } catch (error) {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      return false
    }
  }

  // 更新用户信息
  const updateProfile = async (userData) => {
    loading.value = true
    try {
      const response = await authApi.updateProfile(userData)

      if (response.success) {
        user.value = { ...user.value, ...response.user }
        return { success: true }
      } else {
        throw new Error(response.message || '更新失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (passwordData) => {
    loading.value = true
    try {
      const response = await authApi.changePassword(passwordData)

      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || '修改密码失败')
      }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    user,
    token,
    loading,

    // 计算属性
    isAuthenticated,
    isAdmin,
    canModerate,

    // 方法
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    changePassword
  }
})