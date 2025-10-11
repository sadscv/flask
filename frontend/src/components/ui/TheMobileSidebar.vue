<template>
  <div
    class="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-out lg:hidden"
    :class="className"
  >
    <!-- 侧边栏头部 -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-900">菜单</h2>
      <button
        @click="uiStore.closeMobileSidebar"
        class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <XMarkIcon class="w-6 h-6" />
      </button>
    </div>

    <!-- 用户信息区域 -->
    <div v-if="authStore.isAuthenticated" class="p-4 border-b border-gray-200">
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
          {{ authStore.user?.username?.[0]?.toUpperCase() }}
        </div>
        <div>
          <p class="font-medium text-gray-900">{{ authStore.user?.username }}</p>
          <p class="text-sm text-gray-500">{{ authStore.user?.email }}</p>
        </div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <nav class="p-4 space-y-2">
      <router-link
        v-for="item in menuItems"
        :key="item.name"
        :to="item.to"
        class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        :class="{ 'bg-blue-50 text-blue-600': $route.name === item.name }"
        @click="uiStore.closeMobileSidebar"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="font-medium">{{ item.label }}</span>
      </router-link>

      <!-- 分割线 -->
      <div class="border-t border-gray-200 my-4"></div>

      <!-- 功能快捷入口 -->
      <template v-if="authStore.isAuthenticated">
        <router-link
          to="/blog/create"
          class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <PlusIcon class="w-5 h-5" />
          <span class="font-medium">写文章</span>
        </router-link>

        <router-link
          to="/thoughts"
          class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <LightBulbIcon class="w-5 h-5" />
          <span class="font-medium">快速想法</span>
        </router-link>

        <router-link
          to="/mood"
          class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <HeartIcon class="w-5 h-5" />
          <span class="font-medium">心情打卡</span>
        </router-link>

        <!-- 分割线 -->
        <div class="border-t border-gray-200 my-4"></div>

        <!-- 个人相关 -->
        <router-link
          to="/profile"
          class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <UserIcon class="w-5 h-5" />
          <span class="font-medium">个人资料</span>
        </router-link>

        <button
          @click="handleLogout"
          class="w-full flex items-center space-x-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <ArrowRightOnRectangleIcon class="w-5 h-5" />
          <span class="font-medium">退出登录</span>
        </button>
      </template>

      <template v-else>
        <router-link
          to="/login"
          class="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <ArrowLeftOnRectangleIcon class="w-5 h-5" />
          <span class="font-medium">登录</span>
        </router-link>

        <router-link
          to="/register"
          class="flex items-center space-x-3 px-4 py-3 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
          @click="uiStore.closeMobileSidebar"
        >
          <UserPlusIcon class="w-5 h-5" />
          <span class="font-medium">注册账号</span>
        </router-link>
      </template>
    </nav>

    <!-- 侧边栏底部 -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-500">主题</span>
        <button
          @click="uiStore.toggleTheme"
          class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <SunIcon v-if="uiStore.theme === 'light'" class="w-5 h-5" />
          <MoonIcon v-else class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import {
  XMarkIcon,
  HomeIcon,
  DocumentTextIcon,
  LightBulbIcon,
  HeartIcon,
  PlusIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon,
  UserPlusIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

// 计算类名
const className = computed(() => {
  return uiStore.mobileSidebarOpen ? 'translate-x-0' : 'translate-x-full'
})

// 菜单项
const menuItems = [
  {
    name: 'Home',
    label: '首页',
    to: '/',
    icon: HomeIcon
  },
  {
    name: 'PostList',
    label: '博客',
    to: '/blog',
    icon: DocumentTextIcon
  },
  {
    name: 'ThoughtList',
    label: '想法记录',
    to: '/thoughts',
    icon: LightBulbIcon
  },
  {
    name: 'MoodIndex',
    label: '心情记录',
    to: '/mood',
    icon: HeartIcon
  }
]

// 退出登录
const handleLogout = async () => {
  const confirmed = await uiStore.confirm('确定要退出登录吗？')
  if (confirmed) {
    await authStore.logout()
    uiStore.closeMobileSidebar()
    router.push('/')
    uiStore.showFlashMessage('已退出登录', 'success')
  }
}
</script>