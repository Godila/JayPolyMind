<template>
  <div class="home-root">
    <!-- Ambient background -->
    <div class="bg-ambient">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-brand">
        <img src="/logo.png" height="36" class="nav-logo" alt="JayPolyMind">
        <span class="brand-name">Jay<span class="brand-poly">Poly</span>Mind</span>
      </div>
      <div class="nav-right">
        <button class="nav-login-btn" @click="goToApp">Войти →</button>
      </div>
    </nav>

    <!-- ── HERO: full-bleed split ───────────────────────────────────────── -->
    <section class="hero">
      <div class="hero-left">
        <div class="hero-inner">
          <div class="hero-tag">
            <span class="tag-dot"></span>
            Предиктивная аналитика поведения аудитории
          </div>
          <h1 class="hero-title">
            Узнайте реакцию рынка —<br>
            <span class="hero-accent">до того, как решение принято.</span>
          </h1>
          <p class="hero-desc">
            <strong>JayPolyMind</strong> моделирует поведение вашей аудитории на основе
            загруженной документации. Платформа создаёт сотни
            <span class="hl-blue">AI-агентов</span> — каждый с уникальным профилем,
            убеждениями и логикой поведения — и запускает полноценную симуляцию
            социальных реакций. Результат: структурированный прогноз за часы,
            а не месяцы исследований.
          </p>
          <p class="hero-slogan">
            Принимайте стратегические решения с данными, а не догадками<span class="cursor">_</span>
          </p>
          <div class="hero-kpi">
            <div class="kpi-item">
              <span class="kpi-val">В 10×</span>
              <span class="kpi-lbl">быстрее традиционных исследований</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-item">
              <span class="kpi-val">1000+</span>
              <span class="kpi-lbl">агентов в одной симуляции</span>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-item">
              <span class="kpi-val">Часы</span>
              <span class="kpi-lbl">от документа до отчёта</span>
            </div>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <div class="hero-orb hero-orb-1"></div>
        <div class="hero-orb hero-orb-2"></div>
        <div class="logo-showcase">
          <div class="logo-glow"></div>
          <img src="/logo.png" class="logo-img" alt="JayPolyMind">
        </div>
      </div>
    </section>

    <main class="main-wrap">

      <!-- ── USE CASES ──────────────────────────────────────────────────── -->
      <section class="use-cases">
        <div class="section-head">
          <span class="section-eyebrow">Применение</span>
          <h2 class="section-title">Где работает JayPolyMind</h2>
        </div>
        <div class="cases-grid">
          <div v-for="(uc, i) in useCases" :key="i" class="case-card">
            <div class="case-num">{{ String(i + 1).padStart(2, '0') }}</div>
            <h3 class="case-title">{{ uc.title }}</h3>
            <p class="case-desc">{{ uc.desc }}</p>
          </div>
        </div>
      </section>

      <!-- ── HOW IT WORKS ───────────────────────────────────────────────── -->
      <section class="how-it-works">
        <div class="section-head">
          <span class="section-eyebrow">Процесс</span>
          <h2 class="section-title">Пять шагов от документа до прогноза</h2>
        </div>
        <div class="steps-row">
          <div v-for="(step, i) in steps" :key="i" class="step-card" :style="{ '--i': i }">
            <div class="step-num-badge">{{ step.num }}</div>
            <h4 class="step-name">{{ step.title }}</h4>
            <p class="step-detail">{{ step.desc }}</p>
          </div>
        </div>
      </section>

      <!-- ── CTA ──────────────────────────────────────────────────────────── -->
      <section class="cta-section">
        <div class="cta-inner">
          <span class="section-eyebrow">Готовы к запуску?</span>
          <h2 class="cta-title">Начните симуляцию прямо сейчас</h2>
          <p class="cta-desc">Войдите в платформу, загрузите документы и получите аналитику за часы.</p>
          <button class="cta-btn" @click="goToApp">
            <span>Войти в приложение</span>
            <span class="btn-arrow">→</span>
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { isAuthenticated } from '../store/auth.js'

// ── Static data ────────────────────────────────────────────────────────────

const useCases = [
  {
    title: 'Регуляторные изменения',
    desc: 'Оцените восприятие новых норм до их введения — по каждому сегменту аудитории'
  },
  {
    title: 'Внутренние трансформации',
    desc: 'Смоделируйте реакцию команды на реструктуризацию, слияние или смену стратегии'
  },
  {
    title: 'Запуск коммуникаций',
    desc: 'Протестируйте месседжи и позиционирование до публичного выхода'
  },
  {
    title: 'Вывод продукта на рынок',
    desc: 'Предскажите поведение сегментов и выявите точки сопротивления заранее'
  },
]

const steps = [
  { num: '01', title: 'Граф знаний',        desc: 'Платформа анализирует документ, выделяет сущности и связи' },
  { num: '02', title: 'Профили агентов',     desc: 'LLM создаёт психологические портреты стейкхолдеров' },
  { num: '03', title: 'Симуляция',           desc: 'Агенты взаимодействуют в среде, поведение фиксируется в реальном времени' },
  { num: '04', title: 'Аналитический отчёт', desc: 'ReportAgent синтезирует итоги и формирует структурированный прогноз' },
  { num: '05', title: 'Углублённый диалог',  desc: 'Уточняйте результаты в диалоге с любым агентом или с ReportAgent' },
]

// ── Navigation ─────────────────────────────────────────────────────────────

const router = useRouter()

function goToApp() {
  // If already logged in → go straight to app, otherwise → login
  router.push(isAuthenticated() ? { name: 'App' } : { name: 'Login' })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;700;900&family=Onest:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Tokens ──────────────────────────────────────────────────────────────── */
:root {
  --bg:       #060814;
  --bg2:      #0A0F1E;
  --bg3:      #0F1625;
  --acc1:     #3B82F6;
  --acc2:     #38BDF8;
  --txt:      #EFF6FF;
  --txt2:     #7FA4C4;
  --txt3:     #3A5570;
  --border:   rgba(59,130,246,0.15);
  --border-h: rgba(59,130,246,0.4);
  --mono:     'JetBrains Mono', monospace;
  --display:  'Unbounded', sans-serif;
  --body:     'Onest', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.home-root {
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
  filter: blur(130px); opacity: 0.10;
}
.orb-1 { width: 800px; height: 800px; background: #3B82F6; top: -300px; left: -200px; }
.orb-2 { width: 600px; height: 600px; background: #0EA5E9; bottom: -100px; right: -150px; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
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
.nav-brand { display: flex; align-items: center; gap: 12px; }
.nav-logo { object-fit: contain; }
.brand-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.05rem; font-weight: 800;
  letter-spacing: 0.5px; color: #111111;
}
.brand-poly { color: #38BDF8; }
.nav-right { display: flex; align-items: center; gap: 20px; }
.nav-login-btn {
  font-family: var(--mono); font-size: 0.8rem;
  color: #1D4ED8; background: rgba(29,78,216,0.06);
  border: 1px solid rgba(29,78,216,0.25);
  border-radius: 6px; padding: 7px 18px; cursor: pointer;
  transition: all .2s; font-weight: 600;
}
.nav-login-btn:hover { background: rgba(29,78,216,0.12); border-color: #1D4ED8; }
.nav-badge {
  font-family: var(--mono);
  font-size: 0.7rem; color: var(--txt3);
  border: 1px solid rgba(59,130,246,0.2);
  padding: 3px 10px; border-radius: 20px;
}
.nav-link {
  font-family: var(--mono);
  font-size: 0.8rem; color: var(--txt2);
  text-decoration: none;
  display: flex; align-items: center; gap: 4px;
  transition: color .2s;
}
.nav-link:hover { color: var(--acc1); }

/* ── Main wrap ───────────────────────────────────────────────────────────── */
.main-wrap {
  position: relative; z-index: 1;
  max-width: 1360px; margin: 0 auto;
  padding: 80px 52px 100px;
}

/* ── HERO: split layout ──────────────────────────────────────────────────── */
.hero {
  display: flex;
  min-height: 600px;
  position: relative;
  z-index: 1;
}

/* Left: light side */
.hero-left {
  flex: 1;
  background: #F8FAFF;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 88px 80px 88px max(52px, calc(50vw - 720px));
}
.hero-inner { max-width: 600px; width: 100%; }

/* Right: dark side */
.hero-right {
  flex: 0 0 44%;
  background: #060E1C;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.hero-orb {
  position: absolute; border-radius: 50%;
  filter: blur(100px); pointer-events: none;
}
.hero-orb-1 {
  width: 520px; height: 520px;
  background: #1D4ED8; opacity: 0.45;
  top: -160px; left: -120px;
}
.hero-orb-2 {
  width: 380px; height: 380px;
  background: #0EA5E9; opacity: 0.3;
  bottom: -80px; right: -80px;
}

/* Tag */
.hero-tag {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--mono); font-size: 0.72rem;
  color: #2563EB;
  border: 1px solid rgba(37,99,235,0.25);
  padding: 5px 16px; border-radius: 20px;
  margin-bottom: 32px;
  background: rgba(37,99,235,0.05);
}
.tag-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #3B82F6;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Title */
.hero-title {
  font-family: var(--display);
  font-size: clamp(2.2rem, 3.4vw, 3.2rem);
  font-weight: 700; line-height: 1.15;
  letter-spacing: -1.5px;
  color: #0F172A;
  margin-bottom: 28px;
}
/* A: тёмно-синий акцент без градиента */
.hero-accent {
  color: #1E40AF;
  display: block;
}

/* Description */
.hero-desc {
  font-size: 1.02rem; line-height: 1.9;
  color: #475569; max-width: 560px;
  margin-bottom: 28px;
}
.hero-desc strong { color: #0F172A; font-weight: 600; }
.hl-blue { color: #2563EB; font-weight: 500; }

/* Slogan */
.hero-slogan {
  font-size: 0.9rem; color: #374151;
  border-left: 2px solid #3B82F6;
  padding-left: 16px; margin-bottom: 44px;
  font-weight: 500;
}
.cursor { color: #3B82F6; animation: blink 1.2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* KPI */
.hero-kpi { display: flex; align-items: center; gap: 32px; }
.kpi-item { display: flex; flex-direction: column; gap: 4px; }
.kpi-val {
  font-family: var(--display);
  font-size: 1.4rem; font-weight: 700; color: #0F172A;
}
.kpi-lbl { font-size: 0.78rem; color: #94A3B8; max-width: 120px; line-height: 1.4; }
.kpi-sep { width: 1px; height: 36px; background: rgba(0,0,0,0.1); }

/* Logo showcase */
.logo-showcase {
  position: relative;
  width: 460px; height: 460px;
  display: flex; align-items: center; justify-content: center;
  z-index: 1;
}
.logo-glow {
  position: absolute; inset: -40px;
  background: radial-gradient(circle at 50% 50%,
    rgba(59,130,246,0.55) 0%,
    rgba(14,165,233,0.25) 45%,
    transparent 70%
  );
  border-radius: 50%;
  animation: glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse {
  0%,100% { opacity: 0.75; transform: scale(1); }
  50%     { opacity: 1;    transform: scale(1.1); }
}
.logo-img {
  width: 460px; height: 460px;
  object-fit: contain;
  animation: float 6s ease-in-out infinite;
  filter:
    drop-shadow(0 0 40px rgba(59,130,246,0.75))
    drop-shadow(0 0 100px rgba(14,165,233,0.45));
}
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-16px); }
}

/* ── Section head (shared) ───────────────────────────────────────────────── */
.section-head { margin-bottom: 48px; }
.section-eyebrow {
  font-family: var(--mono);
  font-size: 0.7rem; color: var(--acc1);
  letter-spacing: 2px; text-transform: uppercase;
  display: block; margin-bottom: 12px;
}
.section-title {
  font-family: var(--display);
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  font-weight: 700; color: var(--txt);
  letter-spacing: -0.5px;
}

/* ── USE CASES ───────────────────────────────────────────────────────────── */
.use-cases {
  padding: 72px 0;
  border-top: 1px solid rgba(59,130,246,0.1);
}
.cases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.case-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px 24px;
  position: relative;
  overflow: hidden;
  transition: border-color .25s, transform .2s;
}
.case-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--acc1), var(--acc2));
  opacity: 0; transition: opacity .25s;
}
.case-card:hover { border-color: var(--border-h); transform: translateY(-3px); }
.case-card:hover::before { opacity: 1; }
.case-num {
  font-family: var(--mono); font-size: 0.7rem;
  color: var(--acc1); margin-bottom: 16px; font-weight: 600;
}
.case-title {
  font-family: var(--display);
  font-size: 0.92rem; font-weight: 700;
  color: var(--txt); margin-bottom: 10px; line-height: 1.3;
}
.case-desc { font-size: 0.85rem; color: var(--txt2); line-height: 1.6; }

/* ── HOW IT WORKS ────────────────────────────────────────────────────────── */
.how-it-works {
  padding: 72px 0;
  border-top: 1px solid rgba(59,130,246,0.1);
}
.steps-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  position: relative;
}
.steps-row::before {
  content: '';
  position: absolute; top: 19px; left: 60px; right: 60px; height: 1px;
  background: linear-gradient(90deg,
    transparent,
    rgba(59,130,246,0.3) 10%,
    rgba(59,130,246,0.3) 90%,
    transparent
  );
}
.step-card {
  padding: 0 16px;
  text-align: center;
  animation: fadeUp .5s ease both;
  animation-delay: calc(var(--i, 0) * 0.1s);
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.step-num-badge {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--bg2);
  border: 1px solid rgba(59,130,246,0.4);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 0.72rem; font-weight: 600;
  color: var(--acc1);
  margin: 0 auto 20px;
  position: relative; z-index: 1;
  transition: background .2s, border-color .2s;
}
.step-card:hover .step-num-badge {
  background: rgba(59,130,246,0.12);
  border-color: var(--acc1);
}
.step-name {
  font-family: var(--display);
  font-size: 0.82rem; font-weight: 700;
  color: var(--txt); margin-bottom: 8px; line-height: 1.3;
}
.step-detail { font-size: 0.78rem; color: var(--txt2); line-height: 1.6; }

/* ── CTA SECTION ─────────────────────────────────────────────────────────── */
.cta-section {
  padding: 80px 0 0;
  border-top: 1px solid rgba(59,130,246,0.1);
}
.cta-inner {
  background: linear-gradient(135deg, rgba(29,78,216,0.12) 0%, rgba(14,165,233,0.08) 100%);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 20px;
  padding: 60px 52px;
  text-align: center;
}
.cta-title {
  font-family: var(--display);
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 700; color: var(--txt);
  letter-spacing: -0.5px; margin-bottom: 16px;
}
.cta-desc {
  font-size: 1rem; color: var(--txt2);
  margin-bottom: 36px; line-height: 1.6;
}
.cta-btn {
  display: inline-flex; align-items: center; gap: 12px;
  background: linear-gradient(90deg, #1D4ED8 0%, #3B82F6 50%, #0EA5E9 100%);
  color: #fff; border: none;
  border-radius: 8px; padding: 16px 36px;
  font-family: var(--display);
  font-size: 0.95rem; font-weight: 700;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  box-shadow: 0 4px 32px rgba(59,130,246,0.35);
}
.cta-btn:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-arrow { font-size: 1.1rem; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1200px) {
  .cases-grid { grid-template-columns: repeat(2, 1fr); }
  .steps-row { grid-template-columns: repeat(3, 1fr); row-gap: 32px; }
  .steps-row::before { display: none; }
}
@media (max-width: 1024px) {
  .hero { flex-direction: column; min-height: auto; }
  .hero-left { padding: 60px 40px; justify-content: flex-start; }
  .hero-right { flex: none; width: 100%; min-height: 340px; }
  .logo-img { width: 280px; height: 280px; }
  .logo-showcase { width: 280px; height: 280px; }
  .form-grid { grid-template-columns: 1fr; }
  .form-col:first-child { border-right: none; border-bottom: 1px solid rgba(59,130,246,0.1); }
}
@media (max-width: 640px) {
  .main-wrap { padding: 48px 20px 64px; }
  .navbar { padding: 0 20px; }
  .hero-left { padding: 48px 20px; }
  .hero-title { font-size: 2rem; }
  .cases-grid { grid-template-columns: 1fr; }
  .steps-row { grid-template-columns: 1fr 1fr; }
  .hero-kpi { flex-wrap: wrap; gap: 20px; }
}
</style>
