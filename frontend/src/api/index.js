import axios from 'axios'
import { useUIStore } from '../stores/ui'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 获取token
const getToken = () => {
  return localStorage.getItem('token')
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求标识
    config.headers['X-Requested-With'] = 'XMLHttpRequest'

    // 显示全局加载状态
    const uiStore = useUIStore()
    if (config.showLoading !== false) {
      uiStore.setGlobalLoading(true)
    }

    return config
  },
  (error) => {
    const uiStore = useUIStore()
    uiStore.setGlobalLoading(false)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 隐藏全局加载状态
    const uiStore = useUIStore()
    uiStore.setGlobalLoading(false)

    // 检查响应格式
    const data = response.data

    // 如果是标准的API响应格式
    if (data && typeof data === 'object') {
      return data
    }

    // 包装成标准格式
    return {
      success: true,
      data: data,
      message: 'success'
    }
  },
  async (error) => {
    // 隐藏全局加载状态
    const uiStore = useUIStore()
    uiStore.setGlobalLoading(false)

    const { response } = error

    if (response) {
      const status = response.status
      const data = response.data

      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token')
          const authStore = useAuthStore()
          if (authStore) {
            authStore.logout()
          }

          // 显示登录提示
          uiStore.showFlashMessage('请先登录', 'warning')

          // 跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break

        case 403:
          // 权限不足
          uiStore.showFlashMessage('权限不足', 'error')
          break

        case 404:
          // 资源不存在
          uiStore.showFlashMessage('请求的资源不存在', 'error')
          break

        case 422:
          // 验证错误
          const errorMessage = data?.message || '请求参数有误'
          uiStore.showFlashMessage(errorMessage, 'error')
          break

        case 429:
          // 请求过于频繁
          uiStore.showFlashMessage('请求过于频繁，请稍后再试', 'warning')
          break

        case 500:
          // 服务器错误
          uiStore.showFlashMessage('服务器错误，请稍后再试', 'error')
          break

        default:
          // 其他错误
          const message = data?.message || `请求失败 (${status})`
          uiStore.showFlashMessage(message, 'error')
      }

      // 返回错误信息
      return {
        success: false,
        message: data?.message || `请求失败 (${status})`,
        errors: data?.errors || null,
        status
      }
    } else if (error.request) {
      // 网络错误
      uiStore.showFlashMessage('网络连接失败，请检查网络设置', 'error')
      return {
        success: false,
        message: '网络连接失败'
      }
    } else {
      // 其他错误
      uiStore.showFlashMessage('请求配置错误', 'error')
      return {
        success: false,
        message: '请求配置错误'
      }
    }
  }
)

// 导出api实例和一些工具方法
export { api }

// 导出请求方法
export const request = {
  get: (url, config = {}) => api.get(url, config),
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),
  patch: (url, data = {}, config = {}) => api.patch(url, data, config)
}

// 导出默认
export default api