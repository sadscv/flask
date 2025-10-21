<template>
  <div class="surface-glass flex flex-col rounded-2xl border border-white/60 bg-white/70 p-4 shadow-soft">
    <header class="mb-3 flex items-center justify-between">
      <div class="flex items-center gap-2 text-slate-900">
        <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600 text-white shadow-soft">
          <LightBulbIcon class="h-5 w-5" aria-hidden="true" />
        </span>
        <h3 class="text-lg font-semibold">快速记录想法</h3>
      </div>
      <router-link
        to="/thoughts"
        class="text-sm font-medium text-primary-600 transition-colors hover:text-primary-500"
      >
        查看全部
        <ArrowRightIcon class="ml-1 inline h-4 w-4 align-middle" aria-hidden="true" />
      </router-link>
    </header>

    <form class="space-y-3" @submit.prevent="submitThought">
      <div>
        <textarea
          v-model="content"
          :disabled="!authStore.isAuthenticated || submitting"
          rows="3"
          class="w-full resize-none rounded-xl border border-neutral-200 bg-white/90 px-3 py-3 text-sm text-neutral-800 shadow-inner focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:cursor-not-allowed disabled:bg-neutral-100"
          placeholder="写下此刻的灵感、记录或提醒..."
          @input="updateCharCount"
        ></textarea>
        <div class="mt-1 flex items-center justify-between text-xs text-neutral-400">
          <label class="flex items-center gap-2 text-neutral-500">
            <span>类型</span>
            <select
              v-model="selectedType"
              :disabled="!authStore.isAuthenticated || submitting"
              class="rounded-lg border border-neutral-200 bg-white/90 px-2.5 py-1.5 text-xs focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:bg-neutral-100"
            >
              <option value="note">笔记</option>
              <option value="idea">想法</option>
              <option value="quote">引用</option>
              <option value="task">任务</option>
            </select>
          </label>
          <span :class="charCount > maxChars ? 'text-rose-500' : 'text-neutral-400'">
            {{ charCount }}/{{ maxChars }}
          </span>
        </div>
      </div>

      <transition name="fade">
        <p
          v-if="errorMessage"
          class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600"
        >
          {{ errorMessage }}
        </p>
      </transition>

      <button
        v-if="authStore.isAuthenticated"
        type="submit"
        :disabled="submitting || !content.trim() || charCount > maxChars"
        class="w-full rounded-xl bg-primary-600 py-2.5 text-sm font-medium text-white shadow-soft transition hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:cursor-not-allowed disabled:bg-primary-300"
      >
        {{ submitting ? '发布中...' : '发布想法' }}
      </button>
      <router-link
        v-else
        to="/login"
        class="block w-full rounded-xl border border-neutral-200 bg-white py-2.5 text-center text-sm font-medium text-neutral-500 transition hover:border-primary-200 hover:text-primary-600"
      >
        登录后发布想法
      </router-link>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useThoughtsStore } from '../stores/thoughts'
import { useAuthStore } from '../stores/auth'
import { useUIStore } from '../stores/ui'
import { ArrowRightIcon, LightBulbIcon } from '@heroicons/vue/24/outline'

const thoughtsStore = useThoughtsStore()
const authStore = useAuthStore()
const uiStore = useUIStore()

const content = ref('')
const selectedType = ref('note')
const charCount = ref(0)
const maxChars = 500
const submitting = ref(false)
const errorMessage = ref('')

watch(content, (value) => {
  if (!value) {
    errorMessage.value = ''
  }
})

const updateCharCount = () => {
  charCount.value = content.value.length
  if (charCount.value <= maxChars) {
    errorMessage.value = ''
  }
}

const submitThought = async () => {
  if (!authStore.isAuthenticated || submitting.value) return

  const trimmed = content.value.trim()
  if (!trimmed) {
    errorMessage.value = '内容不能为空'
    return
  }
  if (charCount.value > maxChars) {
    errorMessage.value = '内容过长，请控制在 ' + maxChars + ' 字以内'
    return
  }

  submitting.value = true
  errorMessage.value = ''

  try {
    const result = await thoughtsStore.quickCreateThought(trimmed, selectedType.value, true)

    if (result?.success) {
      uiStore.showFlashMessage('想法创建成功！', 'success')
      content.value = ''
      selectedType.value = 'note'
      charCount.value = 0
      await thoughtsStore.fetchRecentThoughts()
    } else {
      errorMessage.value = result?.message || '创建失败，请稍后再试'
    }
  } catch (error) {
    console.error('Quick thought create failed:', error)
    errorMessage.value = '创建失败，请检查网络或稍后重试'
  } finally {
    submitting.value = false
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
