import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Public ──────────────────────────────────────────────
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/events/:id',
      name: 'event-detail',
      component: () => import('@/views/EventDetailView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guestOnly: true },
    },

    // ── Admin ────────────────────────────────────────────────────
{
  path: '/admin/login',
  name: 'admin-login',
  component: () => import('@/views/admin/LoginView.vue'),
},
{
  path: '/admin/dashboard',
  name: 'admin-dashboard',
  component: () => import('@/views/admin/DashboardView.vue'),
},

    // ── User (connecté) ─────────────────────────────────────
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/user/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard/orders',
      name: 'orders',
      component: () => import('@/views/user/OrdersView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard/profile',
      name: 'profile',
      component: () => import('@/views/user/ProfileView.vue'),
      meta: { requiresAuth: true },
    },

    // ── Organizer ───────────────────────────────────────────
    {
      path: '/organizer/login',
      name: 'organizer-login',
      component: () => import('@/views/organizer/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/organizer/dashboard',
      name: 'organizer-dashboard',
      component: () => import('@/views/organizer/DashboardView.vue'),
      meta: { requiresOrganizer: true },
    },

    // ── 404 ─────────────────────────────────────────────────
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

// Navigation Guards
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router