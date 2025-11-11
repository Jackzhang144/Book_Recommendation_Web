import { createRouter, createWebHistory } from 'vue-router'

const HomeView = () => import('../views/HomeView.vue')
const BookDetailView = () => import('../views/BookDetailView.vue')
const QuickRecommendView = () => import('../views/QuickRecommendView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/books/:bookId',
      name: 'book-detail',
      component: BookDetailView,
      props: true,
    },
    {
      path: '/recommendations/by-title',
      name: 'quick-recommend',
      component: QuickRecommendView,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
