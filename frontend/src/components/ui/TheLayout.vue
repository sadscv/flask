<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <TheNavbar />

    <!-- 主要内容区域 -->
    <main class="container-responsive py-6">
      <!-- 面包屑导航 -->
      <nav
        v-if="uiStore.breadcrumbs.length > 0"
        class="flex mb-6"
        aria-label="Breadcrumb"
      >
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li
            v-for="(item, index) in uiStore.breadcrumbs"
            :key="index"
            class="inline-flex items-center"
          >
            <component
              :is="item.to ? 'router-link' : 'span'"
              :to="item.to"
              :class="[
                'text-sm font-medium',
                index === uiStore.breadcrumbs.length - 1
                  ? 'text-gray-700'
                  : 'text-gray-500 hover:text-blue-600'
              ]"
            >
              {{ item.label }}
            </component>
            <ChevronRightIcon
              v-if="index < uiStore.breadcrumbs.length - 1"
              class="w-4 h-4 text-gray-400 mx-1"
            />
          </li>
        </ol>
      </nav>

      <!-- 页面内容 -->
      <slot />
    </main>

    <!-- 页脚 -->
    <TheFooter />

    <!-- 移动端侧边栏遮罩 -->
    <div
      v-if="uiStore.mobileSidebarOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      @click="uiStore.closeMobileSidebar"
    ></div>

    <!-- 移动端侧边栏 -->
    <TheMobileSidebar
      :class="{
        'translate-x-0': uiStore.mobileSidebarOpen,
        'translate-x-full': !uiStore.mobileSidebarOpen
      }"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUIStore } from '../../stores/ui'
import TheNavbar from './TheNavbar.vue'
import TheFooter from './TheFooter.vue'
import TheMobileSidebar from './TheMobileSidebar.vue'
import { ChevronRightIcon } from '@heroicons/vue/20/solid'

const uiStore = useUIStore()

onMounted(() => {
  // 初始化面包屑
  updateBreadcrumbs()
})

// 监听路由变化，更新面包屑
const updateBreadcrumbs = () => {
  const route = useRoute()
  const pathSegments = route.path.split('/').filter(Boolean)
  const breadcrumbs = []

  // 添加首页
  breadcrumbs.push({
    label: '首页',
    to: '/'
  })

  // 根据路径添加面包屑
  if (pathSegments.length > 0) {
    switch (pathSegments[0]) {
      case 'blog':
        breadcrumbs.push({ label: '博客', to: '/blog' })
        if (pathSegments[1]) {
          if (pathSegments[1] === 'create') {
            breadcrumbs.push({ label: '写文章' })
          } else if (pathSegments[1] !== 'edit') {
            breadcrumbs.push({ label: '文章详情' })
          }
        }
        break

      case 'thoughts':
        breadcrumbs.push({ label: '想法记录' })
        break

      case 'mood':
        breadcrumbs.push({ label: '心情记录' })
        if (pathSegments[1]) {
          switch (pathSegments[1]) {
            case 'calendar':
              breadcrumbs.push({ label: '心情日历' })
              break
            case 'history':
              breadcrumbs.push({ label: '心情历史' })
              break
            case 'date':
              breadcrumbs.push({ label: '心情详情' })
              break
          }
        }
        break

      case 'auth':
        breadcrumbs.push({ label: '认证' })
        if (pathSegments[1] === 'login') {
          breadcrumbs.push({ label: '登录' })
        } else if (pathSegments[1] === 'register') {
          breadcrumbs.push({ label: '注册' })
        }
        break

      case 'profile':
        breadcrumbs.push({ label: '个人资料' })
        break
    }
  }

  uiStore.setBreadcrumbs(breadcrumbs)
}

// 监听路由变化
watch(() => route.path, updateBreadcrumbs)
</script>

<script>
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>