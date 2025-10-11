<template>
  <footer class="bg-white border-t mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 关于我们 -->
        <div class="col-span-1 md:col-span-2">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Sad Blog</h3>
          <p class="text-gray-600 mb-4">
            一个记录生活、分享想法的地方。在这里，你可以记录博客文章、捕捉灵感瞬间、追踪心情变化。
          </p>
          <div class="flex space-x-4">
            <a href="#" class="text-gray-400 hover:text-gray-600">
              <GitHubIcon class="w-6 h-6" />
            </a>
            <a href="#" class="text-gray-400 hover:text-gray-600">
              <TwitterIcon class="w-6 h-6" />
            </a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 mb-4">快速链接</h3>
          <ul class="space-y-2">
            <li>
              <router-link to="/" class="text-gray-600 hover:text-gray-900">
                首页
              </router-link>
            </li>
            <li>
              <router-link to="/blog" class="text-gray-600 hover:text-gray-900">
                博客
              </router-link>
            </li>
            <li>
              <router-link to="/thoughts" class="text-gray-600 hover:text-gray-900">
                想法记录
              </router-link>
            </li>
            <li>
              <router-link to="/mood" class="text-gray-600 hover:text-gray-900">
                心情记录
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 其他链接 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 mb-4">其他</h3>
          <ul class="space-y-2">
            <li>
              <a href="http://old.sadscv.com" target="_blank" class="text-gray-600 hover:text-gray-900">
                旧版网站
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900">
                隐私政策
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900">
                使用条款
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-gray-900">
                联系我们
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- 底部版权信息 -->
      <div class="mt-8 pt-8 border-t border-gray-200">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-500 text-sm">
            © {{ new Date().getFullYear() }} Sad Blog. All rights reserved.
          </p>
          <p class="text-gray-500 text-sm mt-2 md:mt-0">
            Made with ❤️ using Vue 3 & Flask
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { GitHubIcon, TwitterIcon } from '@heroicons/vue/24/outline'
</script>