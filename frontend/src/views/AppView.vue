<template>
  <div class="app-root">
    <!-- Ambient background -->
    <div class="bg-ambient">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- Navbar -->
    <nav class="navbar">
      <router-link :to="{ name: 'Home' }" class="nav-brand">
        <img src="/logo.png" height="36" class="nav-logo" alt="JayPolyMind">
        <span class="brand-name">Jay<span class="brand-poly">Poly</span>Mind</span>
      </router-link>
      <div class="nav-right">
        <div class="user-badge">
          <span class="user-icon">◉</span>
          <span class="user-name">{{ currentUser?.username }}</span>
          <span class="role-chip" :class="currentUser?.role">{{ currentUser?.role }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">Выйти →</button>
      </div>
    </nav>

    <main class="main-wrap">

      <!-- ── Step: pick scenario ─────────────────────────────────────────── -->
      <ScenarioPicker
        v-if="step === 'pick'"
        @select="onSelect"
      />

      <!-- ── Step: guided form ───────────────────────────────────────────── -->
      <ScenarioForm
        v-else-if="step === 'form' && selectedScenario"
        :scenario="selectedScenario"
        :is-demo-user="currentUser?.role === 'demo'"
        @back="onBack"
        @submit="onSubmit"
      />

      <!-- History is always visible below the active step -->
      <HistoryDatabase />

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import ScenarioPicker from '../components/ScenarioPicker.vue'
import ScenarioForm from '../components/ScenarioForm.vue'
import { getUser, logout } from '../store/auth.js'

// ── Auth ────────────────────────────────────────────────────────────────────
const router      = useRouter()
const currentUser = ref(getUser())

function handleLogout() {
  logout()
  router.push({ name: 'Login' })
}

// ── Scenario flow ────────────────────────────────────────────────────────────
// step: 'pick' → show ScenarioPicker
//       'form' → show ScenarioForm for selectedScenario
const step             = ref('pick')
const selectedScenario = ref(null)

function onSelect(scenario) {
  selectedScenario.value = scenario
  step.value = 'form'
}

function onBack() {
  step.value = 'pick'
  selectedScenario.value = null
}

async function onSubmit({ files, requirement }) {
  const { setPendingUpload } = await import('../store/pendingUpload.js')
  setPendingUpload(files, requirement)
  router.push({ name: 'Process', params: { projectId: 'new' } })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;900&family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Tokens ──────────────────────────────────────────────────────────────── */
:root {
  --bg:       #f4f5f7;
  --bg2:      #eef0f4;
  --acc1:     #3B82F6;
  --acc2:     #38BDF8;
  --txt:      #111827;
  --txt2:     #6B7280;
  --txt3:     #9CA3AF;
  --border:   rgba(0,0,0,0.08);
  --mono:     'JetBrains Mono', monospace;
  --display:  'Unbounded', sans-serif;
  --body:     'Onest', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.app-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--txt);
  font-family: var(--body);
  overflow-x: hidden;
}

/* ── Ambient bg ──────────────────────────────────────────────────────────── */
.bg-ambient { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.orb {
  position: absolute; border-radius: 50%;
  filter: blur(160px); opacity: 0.06;
}
.orb-1 { width: 900px; height: 900px; background: #3B82F6; top: -400px; left: -300px; }
.orb-2 { width: 700px; height: 700px; background: #0EA5E9; bottom: -200px; right: -200px; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0,0,0,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.025) 1px, transparent 1px);
  background-size: 64px 64px;
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: relative; z-index: 10;
  height: 68px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 52px;
  border-bottom: 1px solid #EAEAEA;
  background: #FFFFFF;
}
.nav-brand {
  display: flex; align-items: center; gap: 12px;
  text-decoration: none;
}
.nav-logo { object-fit: contain; }
.brand-name {
  font-family: var(--mono);
  font-size: 1.05rem; font-weight: 800;
  letter-spacing: 0.5px; color: #111111;
}
.brand-poly { color: #38BDF8; }
.nav-right { display: flex; align-items: center; gap: 16px; }

/* User badge */
.user-badge {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 0.78rem; color: #555;
}
.user-icon { color: #38BDF8; font-size: 0.7rem; }
.user-name { color: #222; font-weight: 600; }
.role-chip {
  font-size: 0.65rem; padding: 2px 8px; border-radius: 12px;
  font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
}
.role-chip.admin { background: rgba(59,130,246,0.12); color: #2563EB; }
.role-chip.demo  { background: rgba(14,165,233,0.12); color: #0EA5E9; }

/* Logout */
.logout-btn {
  font-family: var(--mono); font-size: 0.78rem;
  color: #666; background: none; border: 1px solid #E5E5E5;
  border-radius: 6px; padding: 6px 14px; cursor: pointer;
  transition: all .2s;
}
.logout-btn:hover { border-color: #3B82F6; color: #3B82F6; }

/* ── Main wrap ───────────────────────────────────────────────────────────── */
.main-wrap {
  position: relative; z-index: 1;
  max-width: 1360px; margin: 0 auto;
  padding: 80px 52px 100px;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .main-wrap { padding: 48px 20px 64px; }
  .navbar { padding: 0 20px; }
  .user-badge { display: none; }
}
</style>
