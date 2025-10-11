<template>
  <nav class="bg-white shadow-sm border-b sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- 左侧：Logo和主导航 -->
        <div class="flex items-center">
          <!-- Logo -->
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">Sad</h1>
          </router-link>

          <!-- 桌面端主导航 -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              to="/"
              class="text-gray-900 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'Home' }"
            >
              首页
            </router-link>

            <router-link
              to="/blog"
              class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'PostList' }"
            >
              博客
            </router-link>

            <a
              href="http://old.sadscv.com"
              target="_blank"
              class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
            >
              旧版
            </a>

            <!-- 已用户菜单 -->
            <template v-if="authStore.isAuthenticated">
              <router-link
                :to="`/profile`"
                class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'Profile' }"
              >
                {{ authStore.user?.username }}
              </router-link>

              <router-link
                to="/blog/create"
                class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'CreatePost' }"
              >
                写文章
              </router-link>

              <router-link
                to="/thoughts"
                class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'ThoughtList' }"
              >
                想法
              </router-link>

              <router-link
                to="/mood"
                class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
                :class="{ 'text-blue-600 border-b-2 border-blue-600': $route.name === 'MoodIndex' }"
              >
                心情
              </router-link>
            </template>
          </div>
        </div>

        <!-- 右侧：认证状态和操作 -->
        <div class="flex items-center space-x-4">
          <!-- 主题切换 -->
          <button
            @click="uiStore.toggleTheme"
            class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            title="切换主题"
          >
            <SunIcon v-if="uiStore.theme === 'light'" class="w-5 h-5" />
            <MoonIcon v-else class="w-5 h-5" />
          </button>

          <!-- 桌面端认证菜单 -->
          <div class="hidden sm:flex sm:items-center sm:space-x-4">
            <template v-if="authStore.isAuthenticated">
              <!-- 用户头像 -->
              <div class="relative">
                <button
                  @click="showUserMenu = !showUserMenu"
                  class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {{ authStore.user?.username?.[0]?.toUpperCase() }}
                  </div>
                  <ChevronDownIcon class="w-4 h-4 text-gray-500" />
                </button>

                <!-- 用户下拉菜单 -->
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
                  v-click-outside="() => showUserMenu = false"
                >
                  <router-link
                    to="/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    @click="showUserMenu = false"
                  >
                    个人资料
                  </router-link>

                  <div class="border-t border-gray-100">
                    <button
                      @click="handleLogout"
                      class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      退出登录
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <router-link
                to="/login"
                class="text-gray-500 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
              >
                登录
              </router-link>

              <router-link
                to="/register"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors"
              >
                注册
              </router-link>
            </template>
          </div>

          <!-- 移动端菜单按钮 -->
          <button
            @click="uiStore.toggleMobileSidebar"
            class="sm:hidden p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Bars3Icon class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import {
  Bars3Icon,
  ChevronDownIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const showUserMenu = ref(false)

// 退出登录
const handleLogout = async () => {
  showUserMenu.value = false

  const confirmed = await uiStore.confirm('确定要退出登录吗？')
  if (confirmed) {
    await authStore.logout()
    router.push('/')
    uiStore.showFlashMessage('已退出登录', 'success')
  }
}
</script>