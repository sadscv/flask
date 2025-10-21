<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    <div v-if="loading" class="surface-muted p-6 sm:p-8 rounded-2xl space-y-4 animate-pulse">
      <div class="h-8 w-48 bg-neutral-200 rounded"></div>
      <div class="h-4 w-72 bg-neutral-200 rounded"></div>
      <div class="h-28 w-full bg-neutral-200 rounded-xl"></div>
    </div>

    <div v-else-if="!authStore.isAuthenticated" class="surface-muted p-8 rounded-2xl text-center space-y-4">
      <LightBulbIcon class="mx-auto h-12 w-12 text-primary-600" aria-hidden="true" />
      <h1 class="text-2xl font-semibold text-slate-900">请先登录</h1>
      <p class="text-neutral-500">登录后即可查看个人资料、创作文章并管理你的想法记录。</p>
      <div class="flex flex-wrap justify-center gap-3">
        <router-link to="/login" class="btn btn-primary px-5 py-2 inline-flex items-center gap-2">
          <ArrowRightIcon class="h-4 w-4" aria-hidden="true" />
          前往登录
        </router-link>
        <router-link to="/register" class="btn btn-secondary px-5 py-2 inline-flex items-center gap-2">
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          注册账号
        </router-link>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] gap-6">
      <section class="surface-glass rounded-2xl p-6 sm:p-8 space-y-6">
        <header class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <div class="flex h-16 w-16 sm:h-18 sm:w-18 items-center justify-center rounded-full bg-primary-600 text-white text-2xl font-semibold shadow-soft">
              {{ userInitial }}
            </div>
            <div>
              <h1 class="text-2xl font-semibold text-slate-900">
                {{ authStore.user?.username || '未命名用户' }}
              </h1>
              <p class="text-sm text-neutral-500">{{ authStore.user?.email || '未填写邮箱' }}</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <router-link to="/blog/create" class="btn btn-primary px-4 py-2 inline-flex items-center gap-2">
              <PencilSquareIcon class="h-4 w-4" aria-hidden="true" />
              写文章
            </router-link>
            <router-link to="/" class="btn btn-secondary px-4 py-2 inline-flex items-center gap-2">
              <HomeIcon class="h-4 w-4" aria-hidden="true" />
              返回主页
            </router-link>
          </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="surface-muted rounded-2xl p-5 space-y-3">
            <h2 class="text-sm font-semibold uppercase tracking-[0.25em] text-neutral-500">
              账号信息
            </h2>
            <ul class="space-y-2 text-sm text-neutral-600">
              <li class="flex items-center gap-2">
                <UserIcon class="h-4 w-4 text-primary-500" aria-hidden="true" />
                <span>账户角色：{{ authStore.user?.role || '用户' }}</span>
              </li>
              <li class="flex items-center gap-2">
                <EnvelopeIcon class="h-4 w-4 text-primary-500" aria-hidden="true" />
                <span>邮箱状态：{{ authStore.user?.email ? '已绑定' : '未绑定' }}</span>
              </li>
              <li class="flex items-center gap-2">
                <ClockIcon class="h-4 w-4 text-primary-500" aria-hidden="true" />
                <span>加入时间：{{ memberSince }}</span>
              </li>
              <li class="flex items-center gap-2">
                <ClockIcon class="h-4 w-4 text-primary-500" aria-hidden="true" />
                <span>最近活跃：{{ lastSeen }}</span>
              </li>
            </ul>
          </div>

          <div class="surface-muted rounded-2xl p-5 space-y-3">
            <h2 class="text-sm font-semibold uppercase tracking-[0.25em] text-neutral-500">
              个性标签
            </h2>
            <dl class="space-y-3 text-sm">
              <div>
                <dt class="text-neutral-400">所在城市</dt>
                <dd class="font-medium text-neutral-700">{{ authStore.user?.location || '未填写' }}</dd>
              </div>
              <div>
                <dt class="text-neutral-400">一句话签名</dt>
                <dd class="font-medium text-neutral-700">
                  {{ authStore.user?.tagline || '添加一句标语，让大家快速了解你。' }}
                </dd>
              </div>
              <div>
                <dt class="text-neutral-400">个人简介</dt>
                <dd class="text-neutral-600 leading-relaxed">
                  {{ authStore.user?.about_me || '这个人很酷，还没有写简介。' }}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <div class="surface-muted rounded-2xl p-5 space-y-4">
          <h2 class="text-sm font-semibold uppercase tracking-[0.25em] text-neutral-500">
            常用快捷入口
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <router-link
              to="/blog"
              class="quick-link-card"
            >
              <BookOpenIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
              <span>浏览文章</span>
            </router-link>
            <router-link
              to="/thoughts"
              class="quick-link-card"
            >
              <LightBulbIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
              <span>查看想法</span>
            </router-link>
            <router-link
              to="/mood"
              class="quick-link-card"
            >
              <HeartIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
              <span>记录心情</span>
            </router-link>
            <router-link
              to="/"
              class="quick-link-card"
            >
              <ArrowRightIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
              <span>返回主页</span>
            </router-link>
          </div>
        </div>
      </section>

      <aside class="space-y-4">
        <div class="surface-muted rounded-2xl p-5 space-y-3">
          <h2 class="text-sm font-semibold uppercase tracking-[0.25em] text-neutral-500">
            活跃概览
          </h2>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="stat-pill">
              <span class="text-2xl font-semibold text-slate-900">{{ authStore.user?.posts_count ?? '--' }}</span>
              <span class="text-xs text-neutral-500">文章</span>
            </div>
            <div class="stat-pill">
              <span class="text-2xl font-semibold text-slate-900">{{ authStore.user?.thoughts_count ?? '--' }}</span>
              <span class="text-xs text-neutral-500">想法</span>
            </div>
            <div class="stat-pill">
              <span class="text-2xl font-semibold text-slate-900">{{ authStore.user?.moods_count ?? '--' }}</span>
              <span class="text-xs text-neutral-500">心情</span>
            </div>
          </div>
        </div>

        <div class="surface-muted rounded-2xl p-5 space-y-3">
          <h2 class="text-sm font-semibold uppercase tracking-[0.25em] text-neutral-500">
            小贴士
          </h2>
          <ul class="list-disc list-inside text-sm text-neutral-600 space-y-2">
            <li>在首页可以快速记录灵感，并即时同步到想法列表。</li>
            <li>文章支持 Markdown 撰写，富文本功能正在完善中。</li>
            <li>后续会提供资料编辑、数据导出等更多能力，敬请期待！</li>
          </ul>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import {
  ArrowRightIcon,
  BookOpenIcon,
  ClockIcon,
  EnvelopeIcon,
  HeartIcon,
  HomeIcon,
  LightBulbIcon,
  PencilSquareIcon,
  PlusIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const uiStore = useUIStore()
const loading = ref(false)

const userInitial = computed(() => {
  const source = authStore.user?.username || authStore.user?.email || '?'
  return source.charAt(0).toUpperCase()
})

const formatDateTime = (value) => {
  if (!value) return '未记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const memberSince = computed(() => formatDateTime(authStore.user?.member_since))
const lastSeen = computed(() => formatDateTime(authStore.user?.last_seen))

const ensureAuthenticated = async () => {
  if (authStore.isAuthenticated) return
  loading.value = true
  const success = await authStore.checkAuth()
  loading.value = false
  if (!success) {
    uiStore.showFlashMessage('请先登录后再访问个人中心', 'warning')
  }
}

onMounted(() => {
  ensureAuthenticated()
})
</script>

<style scoped>
.quick-link-card {
  @apply flex items-center gap-2 rounded-xl border border-white/60 bg-white/80 px-4 py-3 text-sm font-medium text-neutral-600 transition hover:-translate-y-0.5 hover:shadow-elevated hover:text-primary-600;
}

.stat-pill {
  @apply rounded-xl border border-white/60 bg-white/80 px-3 py-4 flex flex-col gap-1 items-center;
}
</style>
