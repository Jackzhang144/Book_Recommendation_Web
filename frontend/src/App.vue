<script setup>
import { RouterLink, RouterView } from 'vue-router'
import LanguageToggle from './components/LanguageToggle.vue'
import { useI18n } from './i18n'

const { t } = useI18n()
</script>

<template>
  <div class="app-shell">
    <!-- 全局液态玻璃滤镜定义：由噪声 + 位移映射叠加出折射效果 -->
    <svg class="app-filters" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <filter
          id="liquid-glass"
          x="-20%"
          y="-20%"
          width="140%"
          height="140%"
          color-interpolation-filters="sRGB"
        >
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.012 0.018"
            numOctaves="3"
            seed="8"
            result="noise"
          />
          <feGaussianBlur in="noise" stdDeviation="12" result="blurredNoise" />
          <feDisplacementMap
            in="SourceGraphic"
            in2="blurredNoise"
            scale="22"
            xChannelSelector="R"
            yChannelSelector="B"
          />
        </filter>
      </defs>
    </svg>
    <div class="app-background" aria-hidden="true">
      <div class="app-background__gradient app-background__gradient--primary"></div>
      <div class="app-background__gradient app-background__gradient--secondary"></div>
      <div class="app-background__orbit"></div>
    </div>
    <header class="app-header">
      <div class="app-header__brand">
        <RouterLink class="logo" :to="{ name: 'home' }">
          <span class="logo__label">{{ t('app.name') }}</span>
        </RouterLink>
      </div>
      <div class="app-header__actions">
        <nav class="nav" aria-label="Primary">
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
