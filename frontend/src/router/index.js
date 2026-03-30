import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../store/auth.js'

import Home           from '../views/Home.vue'
import LoginView      from '../views/LoginView.vue'
import AppView        from '../views/AppView.vue'
import Process        from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView     from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

const routes = [
  // ── Public ─────────────────────────────────────────────────────────────
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },

  // ── Protected ──────────────────────────────────────────────────────────
  {
    path: '/app',
    name: 'App',
    component: AppView,
    meta: { requiresAuth: true }
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ── Navigation guard ───────────────────────────────────────────────────────
router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    // Not logged in → redirect to login, remembering intended destination
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && isAuthenticated()) {
    // Already logged in → skip login page
    next({ name: 'App' })
  } else {
    next()
  }
})

export default router
