<script setup>
import { RouterLink, RouterView } from 'vue-router'
import LanguageToggle from './components/LanguageToggle.vue'
import { useI18n } from './i18n'

const { t } = useI18n()
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="logo" :to="{ name: 'home' }">{{ t('app.name') }}</RouterLink>
      <div class="app-header__actions">
        <nav class="nav">
          <RouterLink class="nav__link" :to="{ name: 'home' }">{{ t('app.nav.home') }}</RouterLink>
          <RouterLink class="nav__link" :to="{ name: 'quick-recommend' }">
            {{ t('app.nav.quick') }}
          </RouterLink>
        </nav>
        <LanguageToggle />
      </div>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
    <footer class="app-footer">
      <p>{{ t('app.footer') }}</p>
    </footer>
  </div>
</template>
