<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <div class="container-responsive py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">Vue 3 App</h1>
      <p class="text-gray-600 mb-4">如果你看到这个页面，说明Vue 3基础架构工作正常！</p>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold mb-3">当前路由</h2>
        <p class="text-gray-600">{{ $route.path }}</p>

        <div class="mt-6 space-x-4">
          <router-link to="/" class="btn btn-primary">首页</router-link>
          <router-link to="/blog" class="btn btn-secondary">博客</router-link>
          <router-link to="/thoughts" class="btn btn-secondary">想法</router-link>
          <router-link to="/mood" class="btn btn-secondary">心情</router-link>
        </div>
      </div>

      <!-- 路由视图 -->
      <div class="mt-8">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

console.log('App.vue 已加载 - 测试')

onMounted(() => {
  console.log('App.vue 已挂载 - 测试')
})
</script>

<style>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500;
}
</style>