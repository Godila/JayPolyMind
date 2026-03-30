<template>
  <div class="login-root">
    <!-- Ambient bg -->
    <div class="bg-ambient">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="login-wrap">
      <!-- Logo + brand -->
      <div class="login-brand">
        <img src="/logo.png" height="52" alt="JayPolyMind" class="brand-logo">
        <span class="brand-name">Jay<span class="brand-poly">Poly</span>Mind</span>
      </div>

      <!-- Card -->
      <div class="login-card">
        <h1 class="card-title">Вход в систему</h1>
        <p class="card-sub">Введите учётные данные для доступа к платформе</p>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field">
            <label class="field-label">Логин</label>
            <input
              v-model="username"
              type="text"
              class="field-input"
              placeholder="username"
              autocomplete="username"
              :disabled="loading"
              required
            />
          </div>

          <div class="field">
            <label class="field-label">Пароль</label>
            <input
              v-model="password"
              type="password"
              class="field-input"
              placeholder="••••••••"
              autocomplete="current-password"
              :disabled="loading"
              required
            />
          </div>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <button type="submit" class="login-btn" :disabled="loading || !canSubmit">
            <span>{{ loading ? 'Проверка...' : 'Войти' }}</span>
            <span class="btn-arrow">→</span>
          </button>
        </form>
      </div>

      <!-- Footer hint -->
      <p class="login-footer">
        Доступ ограничен. Обратитесь к администратору для получения учётных данных.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import service from '../api/index.js'
import { login } from '../store/auth.js'

const router   = useRouter()
const route    = useRoute()
const username = ref('')
const password = ref('')
const loading  = ref(false)
const errorMsg = ref('')

const canSubmit = computed(() => username.value.trim() && password.value)

async function handleLogin() {
  if (!canSubmit.value || loading.value) return
  loading.value  = true
  errorMsg.value = ''

  try {
    const res = await service.post('/api/auth/login', {
      username: username.value.trim(),
      password: password.value,
    })
    login(res.token, res.username, res.role)
    // Redirect to originally requested page (if any) or default to /app
    const redirect = route.query.redirect || null
    router.push(redirect ? redirect : { name: 'App' })
  } catch (err) {
    const msg = err?.response?.data?.error || 'Ошибка соединения с сервером'
    errorMsg.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;900&family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg:     #060814;
  --bg2:    #0A0F1E;
  --acc1:   #3B82F6;
  --acc2:   #38BDF8;
  --txt:    #EFF6FF;
  --txt2:   #7FA4C4;
  --txt3:   #3A5570;
  --border: rgba(59,130,246,0.18);
  --mono:   'JetBrains Mono', monospace;
  --body:   'Onest', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.login-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--txt);
  font-family: var(--body);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Ambient bg ──────────────────────────────────────────────────────────── */
.bg-ambient { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.orb {
  position: absolute; border-radius: 50%;
  filter: blur(130px); opacity: 0.10;
}
.orb-1 { width: 700px; height: 700px; background: #3B82F6; top: -250px; left: -200px; }
.orb-2 { width: 500px; height: 500px; background: #0EA5E9; bottom: -100px; right: -150px; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
  background-size: 64px 64px;
}

/* ── Layout ──────────────────────────────────────────────────────────────── */
.login-wrap {
  position: relative; z-index: 1;
  width: 100%; max-width: 420px;
  padding: 0 20px;
  display: flex; flex-direction: column;
  align-items: center; gap: 28px;
}

/* ── Brand ───────────────────────────────────────────────────────────────── */
.login-brand {
  display: flex; align-items: center; gap: 12px;
}
.brand-logo { object-fit: contain; }
.brand-name {
  font-family: var(--mono);
  font-size: 1.1rem; font-weight: 800;
  letter-spacing: 0.5px; color: #F1F5F9;
}
.brand-poly { color: var(--acc2); }

/* ── Card ────────────────────────────────────────────────────────────────── */
.login-card {
  width: 100%;
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px 32px 32px;
}

.card-title {
  font-family: 'Unbounded', sans-serif;
  font-size: 1.35rem; font-weight: 700;
  color: var(--txt); margin-bottom: 8px;
  letter-spacing: -0.5px;
}
.card-sub {
  font-size: 0.86rem; color: var(--txt2);
  margin-bottom: 28px; line-height: 1.5;
}

/* ── Form ────────────────────────────────────────────────────────────────── */
.login-form { display: flex; flex-direction: column; gap: 18px; }

.field { display: flex; flex-direction: column; gap: 7px; }
.field-label {
  font-family: var(--mono);
  font-size: 0.7rem; color: var(--txt3);
  letter-spacing: 0.5px; text-transform: uppercase;
}
.field-input {
  background: rgba(6,8,20,0.6);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: var(--mono);
  font-size: 0.9rem; color: var(--txt);
  outline: none;
  transition: border-color .2s;
}
.field-input::placeholder { color: var(--txt3); }
.field-input:focus { border-color: rgba(59,130,246,0.55); }
.field-input:disabled { opacity: 0.5; cursor: not-allowed; }

.error-msg {
  font-size: 0.82rem; color: #F87171;
  font-family: var(--mono);
  background: rgba(248,113,113,0.08);
  border: 1px solid rgba(248,113,113,0.2);
  border-radius: 6px; padding: 10px 14px;
}

.login-btn {
  width: 100%;
  background: linear-gradient(90deg, #1D4ED8 0%, #3B82F6 50%, #0EA5E9 100%);
  color: #fff; border: none;
  border-radius: 8px; padding: 15px 24px;
  font-family: 'Unbounded', sans-serif;
  font-size: 0.9rem; font-weight: 700;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  box-shadow: 0 4px 24px rgba(59,130,246,0.3);
  margin-top: 6px;
}
.login-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.login-btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }
.btn-arrow { font-size: 1.1rem; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.login-footer {
  font-size: 0.75rem; color: var(--txt3);
  text-align: center; line-height: 1.5;
  font-family: var(--mono);
  max-width: 300px;
}
</style>
