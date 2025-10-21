<template>
  <!-- 响应式布局 -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- 移动端顶部操作栏 -->
    <div class="lg:hidden flex justify-between items-center mb-4 sticky top-0 z-20 bg-white/80 backdrop-blur-lg border-b border-white/40 shadow-soft pb-3 pt-3 rounded-2xl px-4">
      <h1 class="text-xl font-bold text-gray-900">主页</h1>
      <button
        @click="toggleMobileSidebar"
        class="p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors touch-manipulation active:scale-95"
      >
        <LightBulbIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
        <span class="ml-2 text-sm font-medium">{{ mobileSidebarOpen ? '关闭' : '想法' }}</span>
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-5 lg:gap-8 justify-center mt-4" style="width: 100%; max-width: 100%;">
      <!-- 左侧：主要内容区域 -->
      <div class="w-full lg:flex-[2] lg:max-w-4xl" style="min-width: 0;">
        <!-- 欢迎卡片 -->
        <div
          v-if="!showSkeleton"
          class="card card-gradient mb-5 min-h-[80px] transition-opacity duration-300"
          :class="{ 'opacity-0': pageLoading, 'opacity-100': !pageLoading }"
        >
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Hello, {{ username }}
            </h1>
            <p class="text-gray-600 text-sm sm:text-base">Welcome to the blog</p>
          </div>
        </div>

        <!-- 欢迎卡片骨架屏 -->
        <div v-if="showSkeleton" class="surface-muted p-4 sm:p-6 mb-5 min-h-[80px] animate-pulse">
          <div>
            <div class="h-8 sm:h-10 bg-gray-200 rounded w-48 animate-pulse mb-2"></div>
            <div class="h-4 bg-gray-200 rounded w-32 animate-pulse"></div>
          </div>
        </div>

        <!-- 文章卡片列表 -->
        <div v-if="blogStore.posts.length > 0" class="card-list space-y-4" style="width: 100%; overflow: hidden;" :class="{ 'opacity-0': pageLoading, 'opacity-100': !pageLoading, 'transition-opacity duration-300': true }">
          <article
            v-for="post in blogStore.posts"
            :key="post.id"
            class="post-card card-hover transition-all duration-300"
            style="width: 100%; max-width: 100%; box-sizing: border-box;"
          >
            <!-- 文章头部 -->
            <div class="card-header p-4 sm:p-6 border-b border-white/60 bg-white/40 backdrop-blur-sm">
              <div class="flex flex-wrap items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0 bg-primary-600 shadow-soft">
                    {{ getAuthorInitial(post.author) }}
                  </div>
                  <div class="min-w-0">
                    <router-link
                      :to="`/blog/${post.id}`"
                      class="font-semibold text-slate-900 hover:text-primary-600 transition-colors"
                    >
                      {{ post.author?.username || 'Anonymous' }}
                    </router-link>
                    <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-neutral-500">
                      <span class="inline-flex items-center gap-1.5">
                        <ClockIcon class="h-4 w-4 text-neutral-400" aria-hidden="true" />
                        {{ formatDateTime(post.timestamp) }}
                      </span>
                      <span
                        v-if="post.edit_date"
                        class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2 py-0.5 text-amber-600 font-medium"
                      >
                        <PencilSquareIcon class="h-4 w-4" aria-hidden="true" />
                        已编辑
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 文章内容 -->
            <div class="card-body p-4 sm:p-5 bg-white/40 space-y-4">
              <h2
                v-if="post.title && post.title.trim()"
                class="text-xl sm:text-2xl font-semibold text-slate-900 leading-snug"
              >
                <router-link
                  :to="`/blog/${post.id}`"
                  class="hover:text-primary-600 transition-colors"
                >
                  {{ post.title }}
                </router-link>
              </h2>
              <div
                class="article-snippet prose prose-sm sm:prose-base max-w-none text-neutral-600"
                v-html="renderPostContent(post)"
              ></div>
            </div>

            <!-- 文章底部 -->
            <div class="card-footer px-4 sm:px-5 py-4 border-t border-white/60 bg-white/30">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div class="flex flex-wrap items-center gap-4 text-xs sm:text-sm text-neutral-500">
                  <span class="inline-flex items-center gap-1.5">
                    <EyeIcon class="h-4 w-4 text-neutral-400" aria-hidden="true" />
                    {{ post.views || 0 }} 阅读
                  </span>
                  <span class="inline-flex items-center gap-1.5">
                    <ChatBubbleLeftEllipsisIcon class="h-4 w-4 text-neutral-400" aria-hidden="true" />
                    {{ post.comments_count || 0 }} 评论
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <router-link
                    :to="`/blog/${post.id}`"
                    class="btn btn-secondary px-5 py-2 text-primary-600 border border-primary-100 hover:border-primary-200 hover:text-primary-700"
                  >
                    <BookOpenIcon class="h-4 w-4 mr-2" aria-hidden="true" />
                    阅读全文
                  </router-link>
                  <router-link
                    v-if="canEditPost(post)"
                    :to="`/blog/${post.id}/edit`"
                    class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/60 bg-white/70 text-neutral-500 hover:text-primary-600 transition-colors"
                    title="编辑文章"
                  >
                    <PencilSquareIcon class="h-4 w-4" aria-hidden="true" />
                  </router-link>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- 骨架屏 -->
        <div v-else-if="showSkeleton" class="space-y-4" style="width: 100%; overflow: hidden;">
          <SkeletonCard v-for="i in (blogStore.pagination.per_page || 10)" :key="i" type="article" />
          <!-- 分页区域骨架屏占位符，确保与实际分页高度一致 -->
          <div class="mt-8 flex justify-center px-2 min-h-[40px]">
            <div class="flex items-center space-x-1 sm:space-x-2">
              <div class="px-3 py-2 text-sm font-medium bg-gray-200 border border-gray-300 rounded-md w-16 h-8 animate-pulse"></div>
              <div class="px-3 py-2 text-sm font-medium bg-gray-200 border border-gray-300 rounded-md w-8 h-8 animate-pulse"></div>
              <div class="px-3 py-2 text-sm font-medium bg-gray-200 border border-gray-300 rounded-md w-8 h-8 animate-pulse"></div>
              <div class="px-3 py-2 text-sm font-medium bg-gray-200 border border-gray-300 rounded-md w-16 h-8 animate-pulse"></div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else-if="shouldShowEmptyPosts" class="surface-glass max-w-xl mx-auto text-center py-16 px-8 space-y-4 shadow-soft">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-600 text-white shadow-soft">
            <InboxStackIcon class="h-8 w-8" aria-hidden="true" />
          </div>
          <h3 class="text-2xl font-bold text-slate-900">暂无文章</h3>
          <p class="text-neutral-500 text-base sm:text-lg">还没有任何文章内容，快去创作第一篇吧！</p>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/blog/create"
            class="btn btn-primary px-6 py-3"
          >
            <PlusIcon class="h-4 w-4 mr-2" aria-hidden="true" />
            创建文章
          </router-link>
          <router-link
            v-else
            to="/register"
            class="inline-flex items-center px-6 py-3 rounded-full bg-white/80 border border-neutral-200 text-neutral-700 font-medium hover:border-neutral-300 hover:-translate-y-0.5 transition-transform"
          >
            <UserPlusIcon class="h-4 w-4 mr-2" aria-hidden="true" />
            注册账号
          </router-link>
        </div>

        <!-- 分页 -->
        <div class="mt-8 flex justify-center px-2 min-h-[40px]">
          <!-- 实际分页 -->
          <nav v-if="!showSkeleton && blogStore.pagination.pages > 1" class="flex items-center space-x-1 sm:space-x-2">
            <!-- 上一页 -->
            <router-link
              v-if="blogStore.pagination.has_prev"
              :to="{ name: 'Home', query: { page: blogStore.pagination.prev_num } }"
              class="px-3 py-2 text-sm font-medium text-neutral-500 bg-white/70 border border-white/60 rounded-full hover:bg-white/90 transition-colors shadow-inner-glow"
            >
              <ChevronLeftIcon class="mr-1 inline h-4 w-4 align-middle" aria-hidden="true" />
              <span class="hidden sm:inline">上一页</span>
            </router-link>

            <!-- 页码 -->
            <template v-for="page in paginationPages" :key="page">
              <router-link
                v-if="page"
                :to="{ name: 'Home', query: { page } }"
                :class="[
                  'px-3 py-2 text-sm font-medium rounded-md transition-colors min-w-[2.5rem] text-center',
                  page === blogStore.pagination.page
                    ? 'text-white bg-primary-600 shadow-soft border border-primary-600'
                    : 'text-neutral-500 bg-white/70 border border-white/60 hover:bg-white/90'
                ]"
              >
                {{ page }}
              </router-link>
              <span
                v-else
                class="px-3 py-2 text-sm font-medium text-gray-500"
              >
                ...
              </span>
            </template>

            <!-- 下一页 -->
            <router-link
              v-if="blogStore.pagination.has_next"
              :to="{ name: 'Home', query: { page: blogStore.pagination.next_num } }"
              class="px-3 py-2 text-sm font-medium text-neutral-500 bg-white/70 border border-white/60 rounded-full hover:bg-white/90 transition-colors shadow-inner-glow"
            >
              <span class="hidden sm:inline">下一页</span>
              <ChevronRightIcon class="ml-1 inline h-4 w-4 align-middle" aria-hidden="true" />
            </router-link>
          </nav>
        </div>
      </div>

      <!-- 右侧：想法展示（移动端折叠） -->
      <div id="sidebarContainer" class="w-full lg:flex-[1] lg:max-w-sm mt-6 lg:mt-0 lg:block hidden">
        <!-- 移动端全屏遮罩层 -->
        <div
          v-if="mobileSidebarOpen"
          @click="closeMobileSidebar"
          class="lg:hidden fixed inset-0 bg-black/60 z-40 transition-opacity duration-300"
        ></div>

        <!-- 移动端侧边栏面板 -->
        <div
          :class="[
            'lg:hidden fixed top-0 right-0 h-full w-80 bg-white z-50 shadow-2xl transform transition-transform duration-300 ease-out overflow-hidden',
            mobileSidebarOpen ? 'translate-x-0' : 'translate-x-full'
          ]"
        >
          <!-- 移动端面板头部 -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 bg-white sticky top-0 z-10">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
              <LightBulbIcon class="h-5 w-5 text-primary-500 mr-2" aria-hidden="true" />
              想法与心情
            </h2>
            <button
              @click="closeMobileSidebar"
              class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <XMarkIcon class="h-5 w-5" aria-hidden="true" />
            </button>
          </div>

          <!-- 移动端面板内容 -->
          <div class="h-[calc(100vh-80px)] overflow-y-auto p-4 space-y-4">
            <!-- 桌面端侧边栏内容（复制到移动端面板） -->
            <div id="mobileSidebarContent" class="space-y-4">
              <div class="surface-glass flex-1 flex flex-col p-4">
                <!-- 固定的标题区域 -->
                <div class="sticky top-6 -m-4 p-4 mb-3 z-10 rounded-t-2xl border-b border-white/50 bg-white/70 backdrop-blur">
                  <div class="flex items-center justify-between">
                    <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
                      <LightBulbIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
                      最新想法
                    </h3>
                    <router-link to="/thoughts" class="text-primary-600 hover:text-primary-700 text-sm">
                      <ArrowRightIcon class="h-4 w-4" aria-hidden="true" />
                    </router-link>
                  </div>
                </div>

                <!-- 快速创建想法 -->
                <div class="surface-muted p-3 sm:p-4 mb-3">
                  <div
                    v-if="!authStore.isAuthenticated"
                    class="text-xs sm:text-sm text-orange-500 mb-2 font-medium"
                  >
                    请先登录后再创建想法
                  </div>
                  <form @submit.prevent="createQuickThought" class="space-y-3">
                    <div>
                      <textarea
                        v-model="quickThoughtContent"
                        class="w-full p-3 sm:p-3 border border-neutral-200 rounded-xl bg-white/80 shadow-inner focus:ring-2 focus:ring-primary-200 focus:border-primary-400 resize-none text-sm touch-manipulation"
                        placeholder="快速记录想法..."
                        rows="3"
                        maxlength="500"
                      ></textarea>
                      <div class="mt-1 text-right text-xs text-gray-500">
                        {{ quickThoughtContent.length }}/500
                      </div>
                    </div>
                    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                      <div class="flex items-center gap-2 w-full sm:w-auto">
                        <select
                          v-model="quickThoughtType"
                          class="text-sm p-2.5 border border-neutral-200 rounded-xl bg-white/80 focus:ring-2 focus:ring-primary-200 focus:border-primary-400 w-full sm:w-auto touch-manipulation"
                        >
                          <option value="note">笔记</option>
                          <option value="quote">引用</option>
                          <option value="idea">想法</option>
                          <option value="task">任务</option>
                        </select>
                      </div>
                      <button
                        type="submit"
                        :disabled="!authStore.isAuthenticated || !quickThoughtContent.trim()"
                        class="w-full sm:w-auto px-4 py-3 rounded-xl text-sm font-medium touch-manipulation active:scale-95 transition-transform"
                        :class="authStore.isAuthenticated && quickThoughtContent.trim()
                          ? 'bg-primary-600 text-white shadow-soft hover:bg-primary-700 focus:ring-2 focus:ring-primary-200 focus:ring-offset-0'
                          : 'bg-white/60 text-neutral-400 border border-neutral-200 cursor-not-allowed'"
                      >
                        {{ authStore.isAuthenticated ? '提交' : '请先登录' }}
                      </button>
                    </div>
                  </form>
                </div>

                <!-- 可滚动的想法列表 -->
                <div class="flex-1 overflow-y-auto space-y-2 pb-4">
                  <!-- 骨架屏 -->
                  <div v-if="showSkeleton" class="space-y-3">
                    <SkeletonCard v-for="i in 3" :key="i" type="thought" />
                    <!-- 占位符确保容器高度一致 -->
                    <div class="h-20 opacity-0"></div>
                  </div>

                  <!-- 想法列表 -->
                  <div v-else-if="!shouldShowEmptyThoughts" class="space-y-2" :class="{ 'opacity-0': isInitialLoading, 'opacity-100': !isInitialLoading, 'transition-opacity duration-500': true }">
                    <div
                      v-for="thought in thoughtsStore.recentThoughts"
                      :key="thought.id"
                      @click="$router.push('/thoughts')"
                      class="thought-card cursor-pointer touch-manipulation active:scale-[0.98]"
                      :class="{ 'opacity-0': isInitialLoading, 'animate-fadeInUp': !isInitialLoading }"
                    >
                      <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
                        <span :class="getThoughtTypeClass(thought.type)">
                          {{ getThoughtTypeLabel(thought.type) }}
                        </span>
                        <span class="text-xs text-gray-500 sm:ml-2 font-medium">
                          {{ formatDateTime(thought.timestamp) }}
                        </span>
                      </div>

                      <div class="text-sm text-gray-700 line-clamp-4 leading-relaxed mb-3">
                        <div v-if="thought.content_html" v-html="thought.content_html"></div>
                        <p v-else>{{ thought.content }}</p>
                      </div>

                      <div v-if="thought.tags" class="flex flex-wrap gap-1">
                        <span
                          v-for="tag in thought.tags.split(',').slice(0, 2)"
                          :key="tag.trim()"
                          class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
                        >
                          #{{ tag.trim() }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 空状态 -->
                  <div v-else-if="shouldShowEmptyThoughts" class="surface-muted text-center py-10 px-6">
                    <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600 text-white shadow-soft">
                      <LightBulbIcon class="h-4 w-4" aria-hidden="true" />
                    </div>
                    <p class="text-neutral-500 text-base mb-4">还没有想法记录</p>
                    <router-link
                      v-if="authStore.isAuthenticated"
                      to="/thoughts"
                      class="btn btn-primary px-4 py-2 text-sm font-medium touch-manipulation"
                    >
                      <PlusIcon class="h-4 w-4 mr-2" aria-hidden="true" />
                      记录第一个想法
                    </router-link>
                  </div>
                </div>

                <!-- 固定的底部区域 -->
                <div
                  v-if="thoughtsStore.recentThoughts.length > 0"
                  class="sticky bottom-0 bg-white/70 -m-4 p-4 mt-4 pt-4 border-t border-white/50 rounded-b-2xl"
                >
                  <router-link
                    to="/thoughts"
                  class="text-primary-600 hover:text-primary-700 text-sm font-medium text-center block touch-manipulation py-2 hover:bg-white/70 rounded-lg transition-colors"
                  >
                    查看所有想法
                    <ArrowRightIcon class="ml-2 inline h-4 w-4 align-middle" aria-hidden="true" />
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 桌面端侧边栏内容 -->
        <div class="hidden lg:block">
          <div class="surface-glass p-4 flex-1 flex flex-col">
            <!-- 固定的标题区域 -->
            <div class="sticky top-6 -m-4 p-4 mb-3 z-10 rounded-t-2xl border-b border-white/50 bg-white/70 backdrop-blur">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <LightBulbIcon class="h-5 w-5 text-primary-500" aria-hidden="true" />
                  最新想法
                </h3>
                <router-link to="/thoughts" class="text-primary-600 hover:text-primary-700 text-sm">
                  <ArrowRightIcon class="h-4 w-4" aria-hidden="true" />
                </router-link>
              </div>
            </div>

            <!-- 快速创建想法 -->
                <div class="surface-muted p-3 sm:p-4 mb-3">
                  <div
                    v-if="!authStore.isAuthenticated"
                    class="text-xs sm:text-sm text-orange-500 mb-2 font-medium"
                  >
                    请先登录后再创建想法
                  </div>
              <form @submit.prevent="createQuickThought" class="space-y-3">
                <div>
              <textarea
                v-model="quickThoughtContent"
                class="w-full p-3 sm:p-3 border border-neutral-200 rounded-xl bg-white/80 shadow-inner focus:ring-2 focus:ring-primary-200 focus:border-primary-400 resize-none text-sm touch-manipulation"
                placeholder="快速记录想法..."
                rows="3"
                maxlength="500"
              ></textarea>
                  <div class="mt-1 text-right text-xs text-gray-500">
                    {{ quickThoughtContent.length }}/500
                  </div>
                </div>
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div class="flex items-center gap-2 w-full sm:w-auto">
                <select
                  v-model="quickThoughtType"
                  class="text-sm p-2.5 border border-neutral-200 rounded-xl bg-white/80 focus:ring-2 focus:ring-primary-200 focus:border-primary-400 w-full sm:w-auto touch-manipulation"
                >
                      <option value="note">笔记</option>
                      <option value="quote">引用</option>
                      <option value="idea">想法</option>
                      <option value="task">任务</option>
                    </select>
                  </div>
                  <button
                    type="submit"
                    :disabled="!authStore.isAuthenticated || !quickThoughtContent.trim()"
                    class="w-full sm:w-auto px-4 py-3 rounded-xl text-sm font-medium touch-manipulation active:scale-95 transition-transform"
                    :class="authStore.isAuthenticated && quickThoughtContent.trim()
                      ? 'bg-primary-600 text-white shadow-soft hover:bg-primary-700 focus:ring-2 focus:ring-primary-200 focus:ring-offset-0'
                      : 'bg-white/60 text-neutral-400 border border-neutral-200 cursor-not-allowed'"
                  >
                    {{ authStore.isAuthenticated ? '提交' : '请先登录' }}
                  </button>
                </div>
              </form>
            </div>

            <!-- 可滚动的想法列表 -->
            <div class="flex-1 overflow-y-auto space-y-2 pb-4">
              <!-- 骨架屏 -->
              <div v-if="showSkeleton" class="space-y-3">
                <SkeletonCard v-for="i in 3" :key="i" type="thought" />
                <!-- 占位符确保容器高度一致 -->
                <div class="h-20 opacity-0"></div>
              </div>

              <!-- 想法列表 -->
              <div v-else-if="!shouldShowEmptyThoughts" class="space-y-2" :class="{ 'opacity-0': isInitialLoading, 'opacity-100': !isInitialLoading, 'transition-opacity duration-500': true }">
                <div
                  v-for="thought in thoughtsStore.recentThoughts"
                  :key="thought.id"
                  @click="$router.push('/thoughts')"
                  class="bg-white rounded-lg p-4 sm:p-4 border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200 cursor-pointer touch-manipulation active:scale-[0.98]"
                  :class="{ 'opacity-0': isInitialLoading, 'animate-fadeInUp': !isInitialLoading }"
                >
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
                    <span :class="getThoughtTypeClass(thought.type)">
                      {{ getThoughtTypeLabel(thought.type) }}
                    </span>
                    <span class="text-xs text-gray-500 sm:ml-2 font-medium">
                      {{ formatDateTime(thought.timestamp) }}
                    </span>
                  </div>

                  <div class="text-sm text-gray-700 line-clamp-4 leading-relaxed mb-3">
                    <div v-if="thought.content_html" v-html="thought.content_html"></div>
                    <p v-else>{{ thought.content }}</p>
                  </div>

                  <div v-if="thought.tags" class="flex flex-wrap gap-1">
                    <span
                      v-for="tag in thought.tags.split(',').slice(0, 2)"
                      :key="tag.trim()"
                      class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
                    >
                      #{{ tag.trim() }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else-if="shouldShowEmptyThoughts" class="surface-muted text-center py-10 px-6">
                <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600 text-white shadow-soft">
                  <LightBulbIcon class="h-5 w-5" aria-hidden="true" />
                </div>
                <p class="text-neutral-500 text-base mb-4">还没有想法记录</p>
                <router-link
                  v-if="authStore.isAuthenticated"
                  to="/thoughts"
                    class="btn btn-primary px-4 py-2 text-sm font-medium touch-manipulation"
                  >
                    <PlusIcon class="h-4 w-4 mr-2" aria-hidden="true" />
                  记录第一个想法
                </router-link>
              </div>
            </div>

            <!-- 固定的底部区域 -->
            <div
              v-if="thoughtsStore.recentThoughts.length > 0"
              class="sticky bottom-0 -m-4 p-4 mt-4 pt-4 border-t border-white/50 bg-white/60 backdrop-blur rounded-b-2xl"
            >
              <router-link
                to="/thoughts"
                class="text-primary-600 hover:text-primary-700 text-sm font-medium text-center block touch-manipulation py-2 hover:bg-white/70 rounded-lg transition-colors"
              >
                查看所有想法
                <ArrowRightIcon class="ml-2 inline h-4 w-4 align-middle" aria-hidden="true" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useBlogStore } from '../stores/blog'
import { useThoughtsStore } from '../stores/thoughts'
import { useUIStore } from '../stores/ui'
import SkeletonCard from '../components/ui/SkeletonCard.vue'
import MarkdownIt from 'markdown-it'
import { LightBulbIcon, ClockIcon, PencilSquareIcon, EyeIcon, ChatBubbleLeftEllipsisIcon, BookOpenIcon, InboxStackIcon, PlusIcon, UserPlusIcon, ChevronLeftIcon, ChevronRightIcon, ArrowRightIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const blogStore = useBlogStore()
const thoughtsStore = useThoughtsStore()
const uiStore = useUIStore()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

// 响应式数据
const mobileSidebarOpen = ref(false)
const quickThoughtContent = ref('')
const quickThoughtType = ref('note')

// 页面加载状态
const pageLoading = ref(true)
const hasLoadedOnce = ref(false)

// 计算属性
const username = computed(() => {
  return authStore.isAuthenticated ? authStore.user?.username || 'User' : 'Stranger'
})

const currentPage = computed(() => {
  const raw = Number.parseInt(route.query.page, 10)
  return Number.isFinite(raw) && raw > 0 ? raw : 1
})

// 加载状态计算属性
const showSkeleton = computed(() => pageLoading.value && !hasLoadedOnce.value)

const isInitialLoading = computed(() => pageLoading.value && !hasLoadedOnce.value)

const shouldShowEmptyPosts = computed(() => {
  return !pageLoading.value && hasLoadedOnce.value && blogStore.posts.length === 0
})

const shouldShowEmptyThoughts = computed(() => {
  return !pageLoading.value && hasLoadedOnce.value && thoughtsStore.recentThoughts.length === 0
})

const paginationPages = computed(() => {
  const pagination = blogStore.pagination || {}
  const pages = []

  const current = pagination.page || 1
  const total = pagination.pages || 1

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else if (current <= 4) {
    for (let i = 1; i <= 5; i++) {
      pages.push(i)
    }
    pages.push(null)
    pages.push(total)
  } else if (current >= total - 3) {
    pages.push(1)
    pages.push(null)
    for (let i = total - 4; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)
    pages.push(null)
    for (let i = current - 1; i <= current + 1; i++) {
      pages.push(i)
    }
    pages.push(null)
    pages.push(total)
  }

  return pages
})

// 方法
const renderPostContent = (post) => {
  if (!post) return ''
  if (post.body_html && post.body_html.trim()) {
    return post.body_html
  }
  return md.render(post.body || '')
}
const getAuthorInitial = (author) => {
  if (!author || !author.username) return 'A'
  return author.username.charAt(0).toUpperCase()
}

const formatDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const canEditPost = (post) => {
  if (!authStore.isAuthenticated) return false
  if (authStore.user?.role === 'admin') return true
  return post.author_id === authStore.user?.id
}

// 移动端侧边栏控制
const toggleMobileSidebar = () => {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
  if (mobileSidebarOpen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const closeMobileSidebar = () => {
  mobileSidebarOpen.value = false
  document.body.style.overflow = ''
}

// ESC键关闭移动端侧边栏
const handleEscapeKey = (e) => {
  if (e.key === 'Escape' && mobileSidebarOpen.value) {
    closeMobileSidebar()
  }
}

// 获取文章列表
const loadPosts = async (page = 1) => {
  pageLoading.value = true
  try {
    await blogStore.fetchPosts(page)
  } catch (error) {
    console.error('Failed to fetch posts:', error)
    uiStore.showFlashMessage('文章加载失败，请稍后再试', 'error')
  } finally {
    hasLoadedOnce.value = true
    pageLoading.value = false
  }
}

// 获取想法类型样式
const getThoughtTypeClass = (type) => {
  const typeClasses = {
    note: 'badge-pill bg-primary-50 text-primary-600',
    quote: 'badge-pill bg-emerald-50 text-emerald-600',
    idea: 'badge-pill bg-sky-50 text-sky-600',
    task: 'badge-pill bg-amber-50 text-amber-600'
  }
  return typeClasses[type] || typeClasses.note
}

// 获取想法类型标签
const getThoughtTypeLabel = (type) => {
  const typeLabels = {
    'note': '笔记',
    'quote': '引用',
    'idea': '想法',
    'task': '任务'
  }
  return typeLabels[type] || '笔记'
}

// 创建快速想法
const createQuickThought = async () => {
  if (!authStore.isAuthenticated || !quickThoughtContent.value.trim()) {
    return
  }

  try {
    const result = await thoughtsStore.quickCreateThought(
      quickThoughtContent.value.trim(),
      quickThoughtType.value,
      true // is_public
    )

    if (result.success) {
      uiStore.showFlashMessage('想法创建成功！', 'success')
      quickThoughtContent.value = ''
      quickThoughtType.value = 'note'
    } else {
      uiStore.showFlashMessage(result.message || '创建失败，请重试', 'error')
    }
  } catch (error) {
    console.error('创建想法失败:', error)
    uiStore.showFlashMessage('创建失败，请重试', 'error')
  }
}

// 监听路由变化获取页面参数
onMounted(async () => {
  document.addEventListener('keydown', handleEscapeKey)

  try {
    await Promise.all([
      loadPosts(currentPage.value),
      thoughtsStore.fetchRecentThoughts()
    ])
  } catch (error) {
    console.error('Failed to load initial data:', error)
  }
})

watch(
  () => route.query.page,
  (newVal, oldVal) => {
    const target = Number.parseInt(newVal, 10)
    const page = Number.isFinite(target) && target > 0 ? target : 1
    if (page !== (Number.isFinite(Number.parseInt(oldVal, 10)) ? Number.parseInt(oldVal, 10) : 1) || !hasLoadedOnce.value) {
      loadPosts(page)
    }
  }
)

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
  document.body.style.overflow = '' // 确保恢复滚动
})
</script>

<style scoped>
.line-clamp-4 {
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

/* 渐进式加载动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.6s ease-out forwards;
}

.animate-fadeInUp {
  animation: fadeInUp 0.6s ease-out forwards;
}

/* 为不同元素添加延迟效果 */
.space-y-4 > div:nth-child(1) { animation-delay: 0.1s; }
.space-y-4 > div:nth-child(2) { animation-delay: 0.2s; }
.space-y-4 > div:nth-child(3) { animation-delay: 0.3s; }
.space-y-4 > div:nth-child(4) { animation-delay: 0.4s; }
.space-y-4 > div:nth-child(5) { animation-delay: 0.5s; }

/* 平滑过渡 */
.transition-opacity {
  transition-property: opacity;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

.transition-opacity-500 {
  transition-property: opacity;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 500ms;
}

/* 移动端优化 */
@media (hover: none) {
  .active\:scale-95:active {
    transform: scale(0.95);
  }
  .active\:scale-\[0\.98\]:active {
    transform: scale(0.98);
  }
}

.article-snippet {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-snippet :deep(p) {
  margin-bottom: 0.75rem;
}

.article-snippet :deep(p:last-child) {
  margin-bottom: 0;
}

.line-clamp-4 {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-5 {
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
/* 文章内容样式 */
.prose {
  color: #4b5563;
  line-height: 1.6;
}

.prose p {
  margin-bottom: 1rem;
}

.prose h1,
.prose h2,
.prose h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

/* 移动端侧边栏动画 */
.transform {
  transition: transform 0.3s ease-out;
}

.translate-x-full {
  transform: translateX(100%);
}

/* 确保卡片列表宽度一致 */
.card-list {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  overflow: hidden;
}

/* 确保文章卡片宽度一致 */
.card {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  overflow: hidden;
}

/* 确保想法卡片宽度一致 */
.thought-card {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  overflow: hidden;
}

/* 防止内容溢出导致宽度变化 */
.article-content {
  overflow: hidden;
  word-wrap: break-word;
  word-break: break-word;
}

/* 确保所有文本内容不会导致宽度变化 */
.prose {
  overflow: hidden;
  word-wrap: break-word;
  word-break: break-word;
}

/* 强制所有元素使用相同的宽度计算方式 */
* {
  box-sizing: border-box;
}

/* 防止任何元素导致宽度变化 */
.card, .card-list, .thought-skeleton, .thought-card {
  contain: layout style;
}

/* 确保flex容器不会因为内容变化而改变宽度 */
.flex {
  min-width: 0;
}
</style>
