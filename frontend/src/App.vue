<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <nav class="sticky top-0 z-40 border-b border-white/40 bg-white/60 backdrop-blur-2xl shadow-soft">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between">
          <div class="flex items-center gap-6">
            <router-link to="/" class="flex items-center gap-2 group">
              <div class="flex flex-col leading-tight">
                <span class="text-base font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
                  Sad Studio
                </span>
                <span class="text-[11px] uppercase tracking-[0.35em] text-neutral-500">ideas · moods · writing</span>
              </div>
            </router-link>
            <div class="hidden lg:flex items-center gap-1">
              <router-link
                to="/"
                class="px-4 py-2 text-sm font-medium text-neutral-500 rounded-full transition-all duration-200 hover:text-primary-600 hover:bg-white/80"
                exact-active-class="text-slate-900 bg-white/90 shadow-soft"
              >
                首页
              </router-link>
              <router-link
                to="/thoughts"
                class="px-4 py-2 text-sm font-medium text-neutral-500 rounded-full transition-all duration-200 hover:text-primary-600 hover:bg-white/80"
                exact-active-class="text-slate-900 bg-white/90 shadow-soft"
              >
                想法
              </router-link>
              <router-link
                to="/mood"
                class="px-4 py-2 text-sm font-medium text-neutral-500 rounded-full transition-all duration-200 hover:text-primary-600 hover:bg-white/80"
                exact-active-class="text-slate-900 bg-white/90 shadow-soft"
              >
                心情
              </router-link>
              <router-link
                v-if="authStore.isAuthenticated"
                to="/profile"
                class="px-4 py-2 text-sm font-medium text-neutral-500 rounded-full transition-all duration-200 hover:text-primary-600 hover:bg-white/80"
                exact-active-class="text-slate-900 bg-white/90 shadow-soft"
              >
                个人中心
              </router-link>
              <a
                href="http://old.sadscv.com"
                class="px-4 py-2 text-sm font-medium text-neutral-500 rounded-full transition-all duration-200 hover:text-primary-600 hover:bg-white/80"
              >
                旧站
              </a>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <router-link
              v-if="authStore.isAuthenticated"
              to="/blog/create"
              class="hidden sm:inline-flex btn btn-primary px-5 py-2"
            >
              <PencilSquareIcon class="h-4 w-4" aria-hidden="true" />
              创作
            </router-link>
            <div v-if="authStore.isAuthenticated" class="hidden sm:flex items-center gap-3 px-3 py-2 rounded-full border border-white/50 bg-white/65 backdrop-blur-md shadow-inner-glow">
              <div class="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-white font-semibold">
                {{ userInitial }}
              </div>
              <div class="hidden md:block">
                <p class="text-sm font-semibold text-slate-900 leading-tight">{{ authStore.user?.username }}</p>
                <p class="text-[11px] text-neutral-500 leading-tight">保持灵感</p>
              </div>
              <button
                type="button"
                @click="handleLogout"
                class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-white/70 text-neutral-500 hover:text-rose-500 transition-colors"
                aria-label="Sign out"
              >
                <ArrowRightOnRectangleIcon class="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <div v-else class="hidden sm:flex items-center gap-2">
              <router-link to="/login" class="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-primary-600 transition-colors">
                登录
              </router-link>
              <router-link to="/register" class="btn btn-primary">
                立即加入
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Flash Messages -->
    <transition-group
      v-if="uiStore.flashMessages.length > 0"
      name="fade"
      tag="div"
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-2 space-y-3"
    >
      <div
        v-for="message in uiStore.flashMessages"
        :key="message.id"
        class="surface-glass border border-primary-100/60 px-6 py-4 flex items-start gap-3 shadow-soft"
      >
        <span class="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 text-white shadow-soft">
          <InformationCircleIcon class="h-4 w-4" aria-hidden="true" />
        </span>
        <div class="flex-1">
          <p class="text-sm font-medium text-slate-900">{{ message.message }}</p>
        </div>
      </div>
    </transition-group>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-3 px-2 sm:px-3 lg:px-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from './stores/ui'
import { useAuthStore } from './stores/auth'
import { PencilSquareIcon, ArrowRightOnRectangleIcon, InformationCircleIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()

const userInitial = computed(() => {
  const username = authStore.user?.username || authStore.user?.email || ''
  return username ? username.charAt(0).toUpperCase() : 'S'
})

// 处理登出
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// 初始化应用
onMounted(async () => {
  uiStore.initializeUI()

  // 检查认证状态
  await authStore.checkAuth()
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
