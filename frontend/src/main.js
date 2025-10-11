import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 导入样式
import './assets/css/main.css'

// 导入指令
import { setupClickOutside } from './directives/clickOutside'

// 创建应用实例
const app = createApp(App)

// 使用插件
app.use(createPinia())
app.use(router)

// 注册全局指令
setupClickOutside(app)

// 初始化UI状态
import { useUIStore } from './stores/ui'

// 挂载应用
app.mount('#app')

// 在应用挂载后初始化UI
const uiStore = useUIStore()
uiStore.initializeUI()