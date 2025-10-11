<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full text-center">
      <div class="mb-8">
        <div class="text-9xl font-bold text-gray-300">404</div>
        <h1 class="text-3xl font-bold text-gray-900 mt-4 mb-2">页面未找到</h1>
        <p class="text-gray-600 mb-8">
          抱歉，您访问的页面不存在或已被移除。
        </p>
      </div>

      <div class="space-y-4">
        <router-link
          to="/"
          class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <HomeIcon class="w-5 h-5 mr-2" />
          返回首页
        </router-link>

        <div class="text-sm text-gray-500">
          或者您也可以访问：
        </div>

        <div class="flex flex-col sm:flex-row gap-2 justify-center">
          <router-link
            to="/blog"
            class="text-blue-600 hover:text-blue-800 text-sm"
          >
            博客
          </router-link>
          <span class="text-gray-400">•</span>
          <router-link
            to="/thoughts"
            class="text-blue-600 hover:text-blue-800 text-sm"
          >
            想法记录
          </router-link>
          <span class="text-gray-400">•</span>
          <router-link
            to="/mood"
            class="text-blue-600 hover:text-blue-800 text-sm"
          >
            心情记录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { HomeIcon } from '@heroicons/vue/24/outline'
</script>