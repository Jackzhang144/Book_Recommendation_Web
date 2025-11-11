<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="logo" :to="{ name: 'home' }">阅荐助手</RouterLink>
      <nav class="nav">
        <RouterLink class="nav__link" :to="{ name: 'home' }">智能搜索</RouterLink>
        <RouterLink class="nav__link" :to="{ name: 'quick-recommend' }">即时推荐</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
    <footer class="app-footer">
      <p>面向课程交付的推荐系统前端，已完成中文文案和状态提示校对。</p>
      <p class="muted">在部署环境中设置 VITE_API_BASE_URL / VITE_API_TIMEOUT 即可指向真实后端。</p>
    </footer>
  </div>
</template>
