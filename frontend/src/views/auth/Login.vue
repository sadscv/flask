<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
    <div class="mx-auto flex min-h-screen items-center justify-center px-4 py-12">
      <div class="w-full max-w-md space-y-6">
        <div class="space-y-2 text-center">
          <h1 class="text-3xl font-semibold text-slate-900">欢迎回来</h1>
          <p class="text-sm text-slate-500">登录账号，继续记录灵感与思考。</p>
        </div>

        <div class="rounded-3xl border border-white/80 bg-white/90 p-8 shadow-xl shadow-slate-200/50 backdrop-blur">
          <form class="space-y-5" @submit.prevent="handleLogin">
            <div class="space-y-2">
              <label for="email" class="text-sm font-medium text-slate-700">邮箱</label>
              <input
                id="email"
                v-model="form.email"
                name="email"
                type="email"
                autocomplete="email"
                required
                class="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
                placeholder="请输入邮箱地址"
              />
            </div>

            <div class="space-y-2">
              <label for="password" class="text-sm font-medium text-slate-700">密码</label>
              <input
                id="password"
                v-model="form.password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                class="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
                placeholder="请输入密码"
              />
            </div>

            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 text-sm text-slate-600">
                <input
                  id="remember-me"
                  v-model="form.rememberMe"
                  name="remember-me"
                  type="checkbox"
                  class="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-300"
                />
                记住我
              </label>
              <router-link to="/register" class="text-sm font-medium text-primary-600 hover:text-primary-500">
                还没有账号？
              </router-link>
            </div>

            <div class="space-y-3">
              <button
                type="submit"
                :disabled="loading"
                class="group relative flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-medium text-white shadow-lg shadow-primary-600/20 transition hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:cursor-not-allowed disabled:bg-primary-300"
              >
                <svg
                  v-if="loading"
                  class="h-5 w-5 animate-spin text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V2C5.373 2 2 5.373 2 10h2zm2 5.291A7.962 7.962 0 014 12H2c0 3.042 1.135 5.824 3 7.938l1-.647z"></path>
                </svg>
                <span>{{ loading ? '登录中...' : '登录' }}</span>
              </button>

              <p class="text-center text-xs text-slate-400">忘记密码？请联系管理员协助重置。</p>
            </div>

            <transition name="fade">
              <div
                v-if="error"
                class="rounded-xl border border-rose-100 bg-rose-50/80 px-3 py-2 text-sm text-rose-600"
              >
                {{ error }}
              </div>
            </transition>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const form = ref({
  email: '',
  password: '',
  rememberMe: false
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (loading.value) return
  loading.value = true
  error.value = ''

  try {
    const result = await authStore.login({
      email: form.value.email.trim(),
      password: form.value.password
    })

    if (result.success) {
      uiStore.showFlashMessage('登录成功，欢迎回来！', 'success')
      router.push('/')
    } else {
      error.value = result.message || '登录失败，请检查邮箱或密码是否正确'
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = '登录失败，请稍后再试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
