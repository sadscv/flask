import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // 全局加载状态
  const globalLoading = ref(false)

  // 侧边栏状态
  const sidebarOpen = ref(false)
  const mobileSidebarOpen = ref(false)

  // 模态框状态
  const modalOpen = ref(false)
  const modalConfig = ref({
    title: '',
    content: '',
    type: 'info', // info, success, warning, error
    showCancel: true,
    confirmText: '确认',
    cancelText: '取消',
    onConfirm: null,
    onCancel: null
  })

  // Flash消息
  const flashMessages = ref([])

  // 主题模式
  const theme = ref(localStorage.getItem('theme') || 'light')

  // 页面标题
  const pageTitle = ref('Sad Blog')

  // 面包屑导航
  const breadcrumbs = ref([])

  // 设置全局加载状态
  const setGlobalLoading = (loading) => {
    globalLoading.value = loading
  }

  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
    localStorage.setItem('sidebarOpen', sidebarOpen.value.toString())
  }

  // 切换移动端侧边栏
  const toggleMobileSidebar = () => {
    mobileSidebarOpen.value = !mobileSidebarOpen.value
  }

  // 关闭移动端侧边栏
  const closeMobileSidebar = () => {
    mobileSidebarOpen.value = false
  }

  // 显示模态框
  const showModal = (config) => {
    modalConfig.value = {
      title: config.title || '提示',
      content: config.content || '',
      type: config.type || 'info',
      showCancel: config.showCancel !== false,
      confirmText: config.confirmText || '确认',
      cancelText: config.cancelText || '取消',
      onConfirm: config.onConfirm || null,
      onCancel: config.onCancel || null
    }
    modalOpen.value = true
  }

  // 隐藏模态框
  const hideModal = () => {
    modalOpen.value = false
    // 执行取消回调
    if (modalConfig.value.onCancel) {
      modalConfig.value.onCancel()
    }
  }

  // 确认模态框
  const confirmModal = () => {
    modalOpen.value = false
    // 执行确认回调
    if (modalConfig.value.onConfirm) {
      modalConfig.value.onConfirm()
    }
  }

  // 显示Flash消息
  const showFlashMessage = (message, type = 'info', duration = 3000) => {
    const id = Date.now() + Math.random()
    const flashMessage = {
      id,
      message,
      type,
      duration,
      show: false
    }

    flashMessages.value.push(flashMessage)

    // 触发显示动画
    setTimeout(() => {
      flashMessage.show = true
    }, 10)

    // 自动隐藏
    if (duration > 0) {
      setTimeout(() => {
        hideFlashMessage(id)
      }, duration)
    }

    return id
  }

  // 隐藏Flash消息
  const hideFlashMessage = (id) => {
    const message = flashMessages.value.find(msg => msg.id === id)
    if (message) {
      message.show = false
      setTimeout(() => {
        flashMessages.value = flashMessages.value.filter(msg => msg.id !== id)
      }, 300)
    }
  }

  // 清除所有Flash消息
  const clearFlashMessages = () => {
    flashMessages.value.forEach(message => {
      message.show = false
    })
    setTimeout(() => {
      flashMessages.value = []
    }, 300)
  }

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.classList.toggle('dark', theme.value === 'dark')
  }

  // 设置主题
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', theme.value)
    document.documentElement.classList.toggle('dark', theme.value === 'dark')
  }

  // 设置页面标题
  const setPageTitle = (title) => {
    pageTitle.value = title
    document.title = title ? `${title} - Sad Blog` : 'Sad Blog'
  }

  // 设置面包屑
  const setBreadcrumbs = (items) => {
    breadcrumbs.value = items
  }

  // 添加面包屑项
  const addBreadcrumb = (item) => {
    breadcrumbs.value.push(item)
  }

  // 初始化UI状态
  const initializeUI = () => {
    // 初始化侧边栏状态
    const savedSidebarState = localStorage.getItem('sidebarOpen')
    if (savedSidebarState !== null) {
      sidebarOpen.value = savedSidebarState === 'true'
    }

    // 初始化主题
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      theme.value = savedTheme
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    }

    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light')
      }
    })
  }

  // 确认对话框
  const confirm = (message, title = '确认操作') => {
    return new Promise((resolve) => {
      showModal({
        title,
        content: message,
        type: 'warning',
        showCancel: true,
        onConfirm: () => resolve(true),
        onCancel: () => resolve(false)
      })
    })
  }

  // 警告对话框
  const alert = (message, title = '提示', type = 'info') => {
    return new Promise((resolve) => {
      showModal({
        title,
        content: message,
        type,
        showCancel: false,
        onConfirm: () => resolve()
      })
    })
  }

  return {
    // 状态
    globalLoading,
    sidebarOpen,
    mobileSidebarOpen,
    modalOpen,
    modalConfig,
    flashMessages,
    theme,
    pageTitle,
    breadcrumbs,

    // 方法
    setGlobalLoading,
    toggleSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    showModal,
    hideModal,
    confirmModal,
    showFlashMessage,
    hideFlashMessage,
    clearFlashMessages,
    toggleTheme,
    setTheme,
    setPageTitle,
    setBreadcrumbs,
    addBreadcrumb,
    initializeUI,
    confirm,
    alert
  }
})