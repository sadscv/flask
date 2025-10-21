<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-4">
    <div class="surface-muted rounded-2xl border border-white/60 bg-white/70 px-4 py-3 sm:px-5 sm:py-4 shadow-inner-glow">
      <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div class="relative flex-1">
          <input
            v-model.trim="search"
            type="text"
            placeholder="搜索内容、标签或关键字"
            class="w-full rounded-xl border border-neutral-200 px-4 py-2.5 pr-10 focus:border-primary-400 focus:ring-2 focus:ring-primary-200 transition"
            @input="handleSearchInput"
            @keyup.enter.prevent="applyFilters()"
            @blur="handleSearchBlur"
          />
          <MagnifyingGlassIcon
            class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
            aria-hidden="true"
          />
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <select
            v-model="typeFilter"
            class="rounded-xl border border-neutral-200 bg-white/80 px-4 py-2 focus:border-primary-400 focus:ring-2 focus:ring-primary-200 transition"
            @change="handleTypeChange"
          >
            <option value="">全部类型</option>
            <option value="note">笔记</option>
            <option value="idea">想法</option>
            <option value="quote">引用</option>
            <option value="task">任务</option>
          </select>
          <button
            type="button"
            class="btn btn-secondary px-4 py-2"
            @click="resetFilters"
            :disabled="!search && !typeFilter && !tagFilter"
          >
            重置
          </button>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/"
            class="btn btn-primary inline-flex items-center gap-2 px-4 py-2"
          >
            <PlusIcon class="h-4 w-4" aria-hidden="true" />
            记录新想法
          </router-link>
        </div>
      </div>
      <p
        v-if="paginationSummary"
        class="mt-3 text-xs sm:text-sm text-neutral-500"
      >
        {{ paginationSummary }}
      </p>
      <div
        v-if="tagFilter"
        class="mt-3 flex flex-wrap items-center gap-2 text-xs sm:text-sm text-primary-600"
      >
        <span class="inline-flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1 text-primary-600">
          <TagIcon class="h-4 w-4" aria-hidden="true" />
          #{{ tagFilter }}
        </span>
        <button
          type="button"
          class="text-xs text-primary-500 hover:text-primary-600"
          @click="clearTagFilter"
        >
          清除标签筛选
        </button>
      </div>
    </div>

    <div class="space-y-4">
      <section class="space-y-4">
        <div
          v-if="pageLoading"
          class="surface-muted flex flex-col items-center justify-center gap-3 rounded-2xl border border-white/60 bg-white/70 px-6 py-16 text-center text-neutral-500"
        >
          <ArrowPathIcon class="h-6 w-6 animate-spin text-primary-500" aria-hidden="true" />
          <p class="text-sm sm:text-base">正在载入想法，请稍候…</p>
        </div>
        <template v-else>
          <div v-if="thoughts.length" class="space-y-4">
            <article
              v-for="thought in thoughts"
              :key="thought.id"
              class="surface-muted rounded-2xl border border-white/60 bg-white/80 p-4 sm:p-5 transition-shadow hover:shadow-elevated"
            >
              <header class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div class="flex items-start gap-3">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-sm font-semibold text-primary-600 shadow-inner"
                  >
                    {{ getAuthorInitial(thought.author) }}
                  </div>
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-slate-900">
                      {{ getAuthorName(thought.author) }}
                    </p>
                    <div class="flex flex-wrap items-center gap-3 text-xs text-neutral-500">
                      <span class="inline-flex items-center gap-1.5">
                        <ClockIcon class="h-4 w-4 text-neutral-400" aria-hidden="true" />
                        {{ formatDateTime(thought.timestamp) }}
                      </span>
                      <span class="inline-flex items-center gap-1.5 text-primary-600">
                        <LightBulbIcon class="h-4 w-4" aria-hidden="true" />
                        {{ getThoughtTypeConfig(thought.thought_type || thought.type).label }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-3 self-start">
                  <span
                    v-if="thought.is_public"
                    class="badge-soft-success"
                  >
                    公开可见
                  </span>
                  <span
                    v-else
                    class="badge-soft-warning"
                  >
                    私密记录
                  </span>
                  <button
                    v-if="canDeleteThought(thought)"
                    type="button"
                    class="inline-flex items-center gap-1 rounded-full border border-rose-100 bg-rose-50 px-3 py-1 text-xs font-medium text-rose-600 hover:bg-rose-100 hover:text-rose-700 transition-colors"
                    @click="handleDeleteThought(thought)"
                    title="删除想法"
                  >
                    <TrashIcon class="h-4 w-4" aria-hidden="true" />
                    删除
                  </button>
                </div>
              </header>

              <div
                class="thought-content text-neutral-700 leading-relaxed space-y-4"
                v-html="renderThoughtContent(thought)"
              ></div>

              <footer class="mt-6 space-y-2 border-t border-white/60 pt-4">
                <template v-if="getThoughtTags(thought).length">
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="tag in getThoughtTags(thought)"
                      :key="`${thought.id}-${tag}`"
                      class="chip-muted hover:border-primary-200 hover:text-primary-600 transition text-xs"
                      type="button"
                      @click="handleTagClick(tag)"
                    >
                      # {{ tag }}
                    </button>
                  </div>
                  <p class="text-xs text-neutral-400">
                    点击标签即可筛选相关想法
                  </p>
                </template>
                <div
                  v-else
                  class="inline-flex items-center gap-2 rounded-full border border-dashed border-neutral-200 px-3 py-1 text-xs text-neutral-400"
                >
                  暂无标签
                </div>
              </footer>
            </article>

            <nav
              v-if="paginationPages.length > 1"
              class="flex flex-wrap items-center justify-center gap-2 pt-2"
              aria-label="Thought pagination"
            >
              <button
                type="button"
                class="px-3 py-2 text-sm font-medium text-neutral-500 bg-white/70 border border-white/60 rounded-full hover:bg-white/90 transition-colors shadow-inner-glow disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!thoughtPagination.has_prev"
                @click="goToPage(thoughtPagination.prev_num)"
              >
                <ChevronLeftIcon class="mr-1 inline h-4 w-4 align-middle" aria-hidden="true" />
                <span class="hidden sm:inline">上一页</span>
              </button>

              <template v-for="page in paginationPages" :key="`thought-page-${page ?? 'gap'}`">
                <button
                  v-if="page"
                  type="button"
                  :class="[
                    'px-3 py-2 text-sm font-medium rounded-md transition-colors min-w-[2.5rem]',
                    page === thoughtPagination.page
                      ? 'text-white bg-primary-600 shadow-soft border border-primary-600'
                      : 'text-neutral-500 bg-white/70 border border-white/60 hover:bg-white/90'
                  ]"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </button>
                <span v-else class="px-3 py-2 text-sm font-medium text-neutral-400">...</span>
              </template>

              <button
                type="button"
                class="px-3 py-2 text-sm font-medium text-neutral-500 bg-white/70 border border-white/60 rounded-full hover:bg-white/90 transition-colors shadow-inner-glow disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!thoughtPagination.has_next"
                @click="goToPage(thoughtPagination.next_num)"
              >
                <span class="hidden sm:inline">下一页</span>
                <ChevronRightIcon class="ml-1 inline h-4 w-4 align-middle" aria-hidden="true" />
              </button>
            </nav>
          </div>

          <div class="surface-muted rounded-2xl border border-white/60 bg-white/80 py-16 px-6 text-center text-neutral-500" v-else>
            <LightBulbIcon class="mx-auto h-12 w-12 text-primary-500" aria-hidden="true" />
            <h3 class="mt-4 text-xl font-semibold text-slate-900">还没有匹配的想法</h3>
            <p class="mt-2 text-sm sm:text-base">
              调整筛选条件，或去首页记录你的第一条灵感。
            </p>
            <div class="mt-6 flex flex-wrap items-center justify-center gap-3">
              <router-link
                v-if="authStore.isAuthenticated"
                to="/"
                class="btn btn-primary inline-flex items-center gap-2 px-5 py-2"
              >
                <PlusIcon class="h-4 w-4" aria-hidden="true" />
                返回首页速记
              </router-link>
              <router-link
                v-else
                to="/login"
                class="btn btn-primary inline-flex items-center gap-2 px-5 py-2"
              >
                <ArrowRightIcon class="h-4 w-4" aria-hidden="true" />
                登录后开始记录
              </router-link>
            </div>
          </div>
        </template>
      </section>

      <section class="space-y-4">
        <div
          v-if="!authStore.isAuthenticated"
          class="surface-muted rounded-2xl border border-white/60 bg-white/70 p-4 sm:p-5 text-center"
        >
          <LightBulbIcon class="mx-auto h-10 w-10 text-primary-500" aria-hidden="true" />
          <p class="mt-3 text-sm text-neutral-500">登录后即可快速记录想法并参与讨论。</p>
          <router-link to="/login" class="btn btn-primary mt-4 inline-flex items-center gap-2 px-4 py-2">
            <ArrowRightIcon class="h-4 w-4" aria-hidden="true" />
            前往登录
          </router-link>
        </div>

        <div class="surface-muted rounded-2xl border border-white/60 bg-white/70 p-4 sm:p-5">
          <h3 class="text-sm font-semibold text-slate-900 uppercase tracking-[0.25em]">
            常用标签
          </h3>
          <div v-if="popularTags.length" class="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              v-for="tag in popularTags"
              :key="`popular-${tag.name}`"
              class="chip-muted hover:border-primary-200 hover:text-primary-600 transition text-xs"
              @click="handleTagClick(tag.name)"
            >
              # {{ tag.name }}
              <span class="ml-1 text-neutral-400">×{{ tag.count }}</span>
            </button>
          </div>
          <p v-else class="text-xs text-neutral-400">
            暂无标签统计，记录几条想法试试看吧。
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import MarkdownIt from 'markdown-it'
import { useThoughtsStore } from '../../stores/thoughts'
import { useAuthStore } from '../../stores/auth'
import { useUIStore } from '../../stores/ui'
import {
  ArrowPathIcon,
  ArrowRightIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  LightBulbIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  TagIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const thoughtsStore = useThoughtsStore()
const authStore = useAuthStore()
const uiStore = useUIStore()
const { thoughts, pagination: thoughtPagination } = storeToRefs(thoughtsStore)
const getThoughtTypeConfig = thoughtsStore.getThoughtTypeConfig
const currentPage = computed(() => thoughtPagination.value?.page || 1)

const search = ref('')
const typeFilter = ref('')
const tagFilter = ref('')
const pageLoading = ref(false)
const perPage = 10
let searchDebounceTimer = null

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

const extractTags = (value) => {
  if (!value) return []
  if (Array.isArray(value)) {
    return value
      .map(tag => String(tag).trim())
      .filter(Boolean)
  }
  return String(value)
    .split(/[,，;；、\s]+/)
    .map(tag => tag.trim())
    .filter(Boolean)
}

const popularTags = computed(() => {
  const counts = new Map()
  for (const thought of thoughts.value) {
    for (const tag of extractTags(thought.tags)) {
      counts.set(tag, (counts.get(tag) || 0) + 1)
    }
  }
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, count]) => ({ name, count }))
})

const totalThoughts = computed(() => thoughtPagination.value?.total ?? thoughts.value.length)

const paginationSummary = computed(() => {
  const total = totalThoughts.value
  const filtersActive = Boolean(search.value || typeFilter.value || tagFilter.value)

  if (!total) {
    return filtersActive ? '没有匹配的想法，试试调整筛选条件。' : ''
  }

  const per = thoughtPagination.value?.per_page || perPage
  const page = thoughtPagination.value?.page || 1
  const start = (page - 1) * per + 1
  const end = start + thoughts.value.length - 1
  const rangeText = thoughts.value.length ? `，当前显示第 ${start}-${end} 条` : ''
  const filterText = filtersActive ? '（筛选结果）' : ''

  return `共 ${total} 条想法${rangeText}${filterText}`
})

const paginationPages = computed(() => {
  const pagination = thoughtPagination.value || {
    page: 1,
    pages: 0
  }
  const pages = []
  const current = pagination.page || 1
  const total = pagination.pages || 1

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else if (current <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i)
    pages.push(null, total)
  } else if (current >= total - 3) {
    pages.push(1, null)
    for (let i = total - 4; i <= total; i++) pages.push(i)
  } else {
    pages.push(1, null, current - 1, current, current + 1, null, total)
  }

  return pages
})

const buildQuery = (page = 1) => {
  const query = {}
  const trimmed = search.value.trim()
  if (trimmed) query.q = trimmed
  if (typeFilter.value) query.type = typeFilter.value
  if (tagFilter.value) query.tag = tagFilter.value
  if (page > 1) query.page = page
  return query
}

const loadThoughts = async (page, query) => {
  pageLoading.value = true
  try {
    const filters = {}
    if (query?.type) filters.type = query.type
    if (query?.tag) filters.tag = query.tag
    if (query?.q) {
      await thoughtsStore.searchThoughts(query.q, page, filters)
    } else {
      await thoughtsStore.fetchThoughts(page, perPage, filters)
    }
  } catch (error) {
    console.error('Failed to fetch thoughts:', error)
    uiStore.showFlashMessage('想法加载失败，请稍后重试', 'error')
  } finally {
    pageLoading.value = false
  }
}

const applyFilters = (page = 1) => {
  const targetQuery = buildQuery(page)
  router.replace({ name: 'ThoughtList', query: targetQuery }).catch(() => {})
}

const resetFilters = () => {
  if (!search.value && !typeFilter.value && !tagFilter.value) return
  search.value = ''
  typeFilter.value = ''
  tagFilter.value = ''
  applyFilters()
}

const goToPage = (page) => {
  if (!page || page === (thoughtPagination.value?.page || 1)) return
  router.push({ name: 'ThoughtList', query: buildQuery(page) })
}

const handleDeleteThought = async (thought) => {
  if (!canDeleteThought(thought)) return
  const confirmed = window.confirm('确定要删除这条想法吗？此操作无法撤销。')
  if (!confirmed) return

  try {
    const result = await thoughtsStore.deleteThought(thought.id)
    if (result.success) {
      uiStore.showFlashMessage('想法已删除', 'success')
      await loadThoughts(currentPage.value, {
        q: search.value.trim(),
        type: typeFilter.value,
        tag: tagFilter.value
      })
    } else if (result.message) {
      uiStore.showFlashMessage(result.message, 'error')
    }
  } catch (error) {
    console.error('删除想法失败:', error)
    uiStore.showFlashMessage('删除失败，请稍后重试', 'error')
  }
}

const handleTagClick = (tag) => {
  tagFilter.value = tag
  search.value = ''
  typeFilter.value = ''
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
  applyFilters()
}

const handleSearchInput = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    applyFilters()
    searchDebounceTimer = null
  }, 400)
}

const handleSearchBlur = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
  applyFilters()
}

const handleTypeChange = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
  applyFilters()
}

const renderThoughtContent = (thought) => {
  if (!thought) return ''
  if (thought.content_html && thought.content_html.trim()) {
    return thought.content_html
  }
  return md.render(thought.content || '')
}

const getThoughtTags = (thought) => {
  return extractTags(thought?.tags)
}

const getAuthorInitial = (author) => {
  if (!author) return '匿'
  const name = String(author).trim()
  if (!name) return '匿'
  return name.charAt(0).toUpperCase()
}

const getAuthorName = (author) => {
  if (!author) return '匿名用户'
  const name = String(author).trim()
  return name || '匿名用户'
}

const canDeleteThought = (thought) => {
  if (!authStore.isAuthenticated) return false
  const isOwner = authStore.user?.username && thought?.author && authStore.user.username === thought.author
  const isAdmin = authStore.user?.role === 'admin'
  return isOwner || isAdmin
}

onBeforeUnmount(() => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
})

const formatDateTime = (timestamp) => {
  if (!timestamp) return '刚刚'
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return timestamp
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const clearTagFilter = () => {
  if (!tagFilter.value) return
  tagFilter.value = ''
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
    searchDebounceTimer = null
  }
  applyFilters()
}

watch(
  () => route.query,
  async (query) => {
    const rawPage = Number.parseInt(query.page, 10)
    const page = Number.isFinite(rawPage) && rawPage > 0 ? rawPage : 1
    const q = typeof query.q === 'string' ? query.q : ''
    const type = typeof query.type === 'string' ? query.type : ''
    const tag = typeof query.tag === 'string' ? query.tag : ''

    if (page !== rawPage && query.page !== undefined) {
      router.replace({
        name: 'ThoughtList',
        query: {
          ...(q ? { q } : {}),
          ...(type ? { type } : {}),
          ...(tag ? { tag } : {}),
          ...(page > 1 ? { page } : {})
        }
      })
      return
    }

    search.value = q
    typeFilter.value = type
    tagFilter.value = tag
    await loadThoughts(page, { q, type, tag })
  },
  { immediate: true }
)
</script>

<style scoped>
.thought-content :deep(p) {
  margin-bottom: 1rem;
}

.thought-content :deep(p:last-child) {
  margin-bottom: 0;
}

.thought-content :deep(img) {
  max-width: 100%;
  border-radius: 0.75rem;
}

.badge-soft-success,
.badge-soft-warning {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
}

.badge-soft-success {
  background-color: #ecfdf5;
  color: #047857;
}

.badge-soft-warning {
  background-color: #fef3c7;
  color: #b45309;
}
</style>
