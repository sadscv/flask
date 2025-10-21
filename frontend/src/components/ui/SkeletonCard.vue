<template>
  <div>
    <!-- 文章骨架屏 -->
    <article
      v-if="type === 'article'"
      class="post-card card-hover transition-all duration-300"
      style="width: 100%; max-width: 100%; box-sizing: border-box;"
    >
      <!-- 文章头部 -->
      <div class="card-header p-4 sm:p-6 border-b border-white/60 bg-white/40 backdrop-blur-sm">
        <div class="flex flex-col sm:flex-row sm:items-start justify-between mb-3 gap-3">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0 animate-pulse"></div>
            <div class="min-w-0 flex-1">
              <div class="h-4 bg-gray-300 rounded w-24 mb-2 animate-pulse"></div>
              <div class="flex items-center text-sm text-gray-500">
                <div class="w-3 h-3 bg-gray-200 rounded mr-1 animate-pulse"></div>
                <div class="h-3 bg-gray-200 rounded w-32 animate-pulse"></div>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2 sm:space-x-3">
            <!-- 随机显示状态标签，模拟实际内容的不确定性 -->
            <div v-if="Math.random() > 0.5" class="px-2 py-1 text-xs font-medium rounded-full bg-gray-200 w-12 h-5 animate-pulse"></div>
            <!-- 占位符确保布局一致 -->
            <div v-else class="px-2 py-1 text-xs font-medium rounded-full opacity-0 select-none w-12 h-5">占位</div>
          </div>
        </div>
      </div>

      <!-- 文章内容 -->
      <div class="card-body p-3 sm:p-5 bg-white/40">
        <div class="article-content text-sm sm:text-base">
          <div class="prose prose-sm max-w-none line-clamp-3">
            <div class="h-4 bg-gray-200 rounded animate-pulse mb-4"></div>
            <div class="h-4 bg-gray-200 rounded w-5/6 animate-pulse mb-4"></div>
            <div class="h-4 bg-gray-200 rounded w-4/6 animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- 文章底部 -->
      <div class="card-footer px-3 sm:px-5 py-3 sm:py-4 border-t border-white/60 bg-white/30">
        <div class="article-stats flex flex-wrap gap-3 sm:gap-4 mb-3 sm:mb-4">
          <div class="article-stat flex items-center">
            <div class="w-3 h-3 bg-gray-200 rounded mr-1 animate-pulse"></div>
            <div class="text-xs sm:text-sm h-3 bg-gray-200 rounded w-6 animate-pulse"></div>
          </div>
          <div class="article-stat flex items-center">
            <div class="w-3 h-3 bg-gray-200 rounded mr-1 animate-pulse"></div>
            <div class="text-xs sm:text-sm h-3 bg-gray-200 rounded w-6 animate-pulse"></div>
          </div>
        </div>

        <div class="article-actions mt-3 sm:mt-4">
          <div class="card-action primary w-full sm:w-auto px-3 sm:px-4 py-2 bg-white/70 border border-white/50 rounded-xl text-sm font-medium inline-flex items-center justify-center animate-pulse">
            <div class="w-4 h-4 bg-gray-300 rounded mr-1 sm:mr-2"></div>
            <div class="w-12 h-4 bg-gray-300 rounded"></div>
          </div>
          <!-- 编辑按钮占位，确保与实际内容布局一致 -->
          <div class="card-action secondary px-3 py-2 bg-white/70 border border-white/50 rounded-xl text-sm ml-2 w-8 h-8 inline-flex items-center justify-center animate-pulse">
            <div class="w-4 h-4 bg-gray-300 rounded"></div>
          </div>
        </div>
      </div>
    </article>

    <!-- 想法骨架屏 -->
    <div
      v-else-if="type === 'thought'"
      class="thought-skeleton surface-muted p-4 sm:p-4 hover:shadow-elevated transition-all duration-200 cursor-pointer touch-manipulation active:scale-[0.98]"
      style="width: 100%; max-width: 100%; box-sizing: border-box;"
    >
      <!-- 头部：类型标签和时间 -->
      <div class="thought-header flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
        <div class="px-2 py-1 text-xs font-medium rounded-full bg-gray-200 w-16 h-5 animate-pulse"></div>
        <div class="text-xs sm:ml-2 font-medium w-20 h-3 bg-gray-200 rounded animate-pulse"></div>
      </div>

      <!-- 内容 -->
      <div class="thought-content text-sm text-gray-700 line-clamp-3 leading-relaxed mb-3">
        <div class="space-y-2">
          <div class="h-4 bg-gray-200 rounded animate-pulse"></div>
          <div class="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
          <div class="h-4 bg-gray-200 rounded w-4/6 animate-pulse"></div>
        </div>
      </div>

      <!-- 标签区域 - 有时显示有时不显示，模拟实际内容 -->
      <div class="flex flex-wrap gap-1 min-h-[20px]">
        <!-- 随机显示0-2个标签，模拟实际内容的不确定性 -->
        <div v-if="Math.random() > 0.3" class="thought-tag inline-block px-2 py-1 text-xs bg-gray-200 rounded-full w-12 h-5 animate-pulse"></div>
        <div v-if="Math.random() > 0.6" class="thought-tag inline-block px-2 py-1 text-xs bg-gray-200 rounded-full w-16 h-5 animate-pulse"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'article', // 'article' | 'thought'
  }
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 确保骨架屏与实际内容尺寸完全匹配 */
.card {
  /* 确保与实际文章卡片完全相同的样式 */
  min-height: 200px; /* 确保最小高度一致 */
  width: 100% !important; /* 确保宽度占满容器 */
  max-width: 100% !important; /* 防止宽度超出 */
  box-sizing: border-box !important;
  overflow: hidden; /* 防止内容溢出 */
}

.card-header,
.card-body,
.card-footer {
  /* 确保与实际内容相同的布局结构 */
  box-sizing: border-box;
  width: 100%;
}

/* 确保按钮尺寸一致 */
.card-action {
  min-height: 32px; /* 与真实按钮高度一致 */
  box-sizing: border-box;
  flex-shrink: 0; /* 防止按钮被压缩 */
}

/* 确保统计信息尺寸一致 */
.article-stat {
  min-height: 20px; /* 与真实统计信息高度一致 */
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

/* 确保文章内容区域宽度一致 */
.article-content {
  width: 100%;
  box-sizing: border-box;
}

/* 确保文章操作区域布局一致 */
.article-actions {
  display: flex;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 移动端优化 */
@media (hover: none) {
  .active\:scale-\[0\.98\]:active {
    transform: scale(0.98);
  }
}

/* 确保标签样式匹配 */
.rounded-full {
  border-radius: 9999px;
}

/* 文本大小和行高匹配 */
.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.leading-relaxed {
  line-height: 1.625;
}

/* 添加更精确的文章内容样式 */
.prose {
  color: #4b5563;
  line-height: 1.6;
}

.prose p {
  margin-bottom: 1rem;
}

/* 确保骨架屏元素有正确的尺寸 */
.article-stat {
  display: flex;
  align-items: center;
}

.card-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 文章元数据图标样式 */
.article-meta-icon {
  /* 匹配原始HTML中的图标样式 */
}

/* 想法骨架屏尺寸保证 */
.thought-skeleton {
  min-height: 120px; /* 确保想法卡片最小高度一致 */
  width: 100% !important; /* 确保宽度占满容器 */
  max-width: 100% !important; /* 防止宽度超出 */
  box-sizing: border-box !important;
  overflow: hidden; /* 防止内容溢出 */
}

/* 确保想法标签尺寸一致 */
.thought-tag {
  min-height: 20px; /* 与真实标签高度一致 */
  box-sizing: border-box;
  flex-shrink: 0;
}

/* 确保想法内容区域宽度一致 */
.thought-content {
  width: 100%;
  box-sizing: border-box;
}

/* 确保想法头部区域布局一致 */
.thought-header {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
