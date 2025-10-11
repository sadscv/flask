<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900 flex items-center">
        <LightBulbIcon class="w-5 h-5 text-yellow-500 mr-2" />
        最近想法
      </h2>
      <div class="flex items-center space-x-2">
        <!-- 筛选器 -->
        <select
          v-model="selectedType"
          @change="filterThoughts"
          class="text-xs border border-gray-300 rounded-md px-2 py-1 focus:ring-1 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">全部类型</option>
          <option v-for="type in thoughtTypes" :key="type.value" :value="type.value">
            {{ type.emoji }} {{ type.label }}
          </option>
        </select>
        <router-link
          to="/thoughts"
          class="text-sm text-yellow-600 hover:text-yellow-800 font-medium"
        >
          查看全部
        </router-link>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="thoughtStore.loading" class="flex justify-center py-8">
      <div class="w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
    </div>

    <!-- 想法列表 -->
    <div v-else-if="filteredThoughts.length > 0" class="space-y-3">
      <div
        v-for="thought in paginatedThoughts"
        :key="thought.id"
        class="group p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
        @click="viewThought(thought)"
      >
        <!-- 想法头部 -->
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center space-x-2">
            <span class="text-lg">{{ getTypeEmoji(thought.type) }}</span>
            <span class="text-xs text-gray-500">{{ formatDate(thought.timestamp) }}</span>
            <span
              v-if="!thought.is_public"
              class="text-xs text-gray-400 flex items-center"
              title="仅自己可见"
            >
              <LockClosedIcon class="w-3 h-3" />
            </span>
          </div>
          <!-- 操作按钮 -->
          <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click.stop="editThought(thought)"
              class="p-1 text-gray-400 hover:text-blue-600 transition-colors"
              title="编辑"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button
              @click.stop="deleteThought(thought)"
              class="p-1 text-gray-400 hover:text-red-600 transition-colors"
              title="删除"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 想法内容 -->
        <div class="text-sm text-gray-900 mb-2 line-clamp-3">
          {{ thought.content }}
        </div>

        <!-- 标签 -->
        <div v-if="thought.tags" class="flex flex-wrap gap-1 mb-2">
          <span
            v-for="tag in thought.tags.split(',')"
            :key="tag"
            class="inline-flex items-center px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded-full"
          >
            {{ tag.trim() }}
          </span>
        </div>

        <!-- 来源链接 -->
        <div v-if="thought.source_url" class="flex items-center text-xs text-blue-600 hover:text-blue-800">
          <LinkIcon class="w-3 h-3 mr-1" />
          <a
            :href="thought.source_url"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
            class="truncate"
          >
            {{ getDomain(thought.source_url) }}
          </a>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-8">
      <LightBulbIcon class="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-500 text-sm mb-3">还没有想法记录</p>
      <router-link
        to="/thoughts"
        class="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
      >
        <PlusIcon class="w-4 h-4 mr-1" />
        记录第一个想法
      </router-link>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="mt-4 flex justify-center">
      <nav class="flex items-center space-x-1">
        <button
          v-if="currentPage > 1"
          @click="currentPage--"
          class="p-1 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ChevronLeftIcon class="w-4 h-4" />
        </button>

        <span class="text-xs text-gray-500 px-2">
          {{ currentPage }} / {{ totalPages }}
        </span>

        <button
          v-if="currentPage < totalPages"
          @click="currentPage++"
          class="p-1 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ChevronRightIcon class="w-4 h-4" />
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThoughtStore } from '../stores/thoughts'
import { useUIStore } from '../stores/ui'
import {
  LightBulbIcon,
  LockClosedIcon,
  PencilIcon,
  TrashIcon,
  LinkIcon,
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const thoughtStore = useThoughtStore()
const uiStore = useUIStore()

// 状态管理
const selectedType = ref('')
const currentPage = ref(1)
const itemsPerPage = 5

// 想法类型
const thoughtTypes = [
  { value: 'note', label: '笔记', emoji: '📝' },
  { value: 'idea', label: '想法', emoji: '💡' },
  { value: 'quote', label: '引用', emoji: '💬' },
  { value: 'task', label: '任务', emoji: '✅' }
]

// 计算属性
const filteredThoughts = computed(() => {
  let thoughts = thoughtStore.recentThoughts || []

  if (selectedType.value) {
    thoughts = thoughts.filter(thought => thought.type === selectedType.value)
  }

  return thoughts
})

const paginatedThoughts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredThoughts.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredThoughts.value.length / itemsPerPage)
})

// 方法
const getTypeEmoji = (type) => {
  const typeObj = thoughtTypes.find(t => t.value === type)
  return typeObj ? typeObj.emoji : '📝'
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

const getDomain = (url) => {
  try {
    const domain = new URL(url).hostname
    return domain.replace('www.', '')
  } catch {
    return url
  }
}

const filterThoughts = () => {
  currentPage.value = 1
}

const viewThought = (thought) => {
  router.push(`/thoughts/${thought.id}`)
}

const editThought = (thought) => {
  router.push(`/thoughts/${thought.id}/edit`)
}

const deleteThought = async (thought) => {
  const confirmed = await uiStore.confirm(
    `确定要删除这个想法吗？\n\n"${thought.content.substring(0, 50)}..."`,
    '删除想法'
  )

  if (confirmed) {
    try {
      await thoughtStore.deleteThought(thought.id)
      uiStore.showFlashMessage('想法已删除', 'success')

      // 如果当前页没有数据了，返回上一页
      if (paginatedThoughts.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
      }
    } catch (error) {
      console.error('删除想法失败:', error)
      uiStore.showFlashMessage('删除失败，请重试', 'error')
    }
  }
}

// 监听筛选器变化，重置分页
watch(selectedType, () => {
  currentPage.value = 1
})

// 初始化
onMounted(async () => {
  await thoughtStore.fetchRecentThoughts()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 悬停效果 */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>