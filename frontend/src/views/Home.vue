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
      <div class="nav-right"></div>
    </nav>

    <main class="main-wrap">

      <!-- ── HERO ───────────────────────────────────────────────────────── -->
      <section class="hero">
        <div class="hero-left">
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
        <div class="hero-right">
          <div class="logo-showcase">
            <div class="logo-glow"></div>
            <img src="/logo.png" class="logo-img" alt="JayPolyMind">
          </div>
        </div>
      </section>

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

      <!-- ── LAUNCH FORM ────────────────────────────────────────────────── -->
      <section class="launch-section">
        <div class="launch-head">
          <h2 class="launch-title">Запустить симуляцию</h2>
          <p class="launch-sub">Загрузите документ с описанием контекста и задайте исследовательский вопрос.</p>
        </div>
        <div class="launch-card">
          <div class="form-grid">
            <!-- Upload -->
            <div class="form-col">
              <div class="field-hdr">
                <span class="field-label">01 / Исходная документация</span>
                <span class="field-hint">PDF · MD · TXT</span>
              </div>
              <div
                class="upload-zone"
                :class="{ 'drag-over': isDragOver }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input ref="fileInput" type="file" multiple accept=".pdf,.md,.txt"
                  @change="handleFileSelect" style="display:none" :disabled="loading" />
                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">Перетащите документы сюда</div>
                  <div class="upload-hint">или нажмите для выбора</div>
                </div>
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Prompt -->
            <div class="form-col">
              <div class="field-hdr">
                <span class="field-label">&gt;_ 02 / Исследовательский вопрос</span>
              </div>
              <div class="prompt-wrap">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="prompt-input"
                  placeholder="Например: «Как сотрудники и профсоюзы отреагируют на переход к четырёхдневной рабочей неделе в производственном секторе?»"
                  rows="7"
                  :disabled="loading"
                ></textarea>
                <div class="engine-badge">Движок: LLM + Neo4j</div>
              </div>
            </div>
          </div>

          <div class="cta-row">
            <button class="start-btn" @click="startSimulation" :disabled="!canSubmit || loading">
              <span>{{ loading ? 'Инициализация...' : 'Запустить симуляцию' }}</span>
              <span class="btn-arrow">→</span>
            </button>
          </div>
        </div>
      </section>

      <HistoryDatabase />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'

// ── Data ───────────────────────────────────────────────────────────────────

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

// ── Logic ──────────────────────────────────────────────────────────────────

const router     = useRouter()
const formData   = ref({ simulationRequirement: '' })
const files      = ref([])
const loading    = ref(false)
const isDragOver = ref(false)
const fileInput  = ref(null)

const canSubmit = computed(() =>
  formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
)

const triggerFileInput = () => { if (!loading.value) fileInput.value?.click() }
const handleFileSelect = (e) => addFiles(Array.from(e.target.files))
const handleDragOver   = () => { isDragOver.value = true }
const handleDragLeave  = () => { isDragOver.value = false }
const handleDrop       = (e) => { isDragOver.value = false; addFiles(Array.from(e.dataTransfer.files)) }

const addFiles = (newFiles) => {
  const allowed = ['.pdf', '.md', '.txt']
  const valid = newFiles.filter(f => allowed.some(ext => f.name.toLowerCase().endsWith(ext)))
  files.value = [...files.value, ...valid]
}

const removeFile = (index) => { files.value.splice(index, 1) }

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
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
  border-bottom: 1px solid rgba(59,130,246,0.1);
  background: rgba(6,8,20,0.88);
  backdrop-filter: blur(16px);
}
.nav-brand { display: flex; align-items: center; gap: 14px; }
.nav-logo { object-fit: contain; }
.brand-name {
  font-family: var(--display);
  font-size: 1.1rem; font-weight: 700;
  letter-spacing: -0.3px; color: var(--txt);
}
.brand-poly { color: var(--acc2); }
.nav-right { display: flex; align-items: center; gap: 20px; }
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

/* ── HERO ────────────────────────────────────────────────────────────────── */
.hero {
  display: flex; align-items: center;
  gap: 72px;
  margin-bottom: 112px;
}
.hero-left { flex: 1; }
.hero-right { flex: 0 0 420px; display: flex; justify-content: center; }

.hero-tag {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--mono); font-size: 0.72rem;
  color: var(--acc2);
  border: 1px solid rgba(56,189,248,0.3);
  padding: 5px 16px; border-radius: 20px;
  margin-bottom: 32px;
}
.tag-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--acc2);
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.hero-title {
  font-family: var(--display);
  font-size: clamp(2.2rem, 3.8vw, 3.4rem);
  font-weight: 700; line-height: 1.15;
  letter-spacing: -1.5px;
  color: var(--txt);
  margin-bottom: 28px;
}
.hero-accent {
  background: linear-gradient(90deg, var(--acc1) 0%, var(--acc2) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 1.05rem; line-height: 1.85;
  color: var(--txt2); max-width: 580px;
  margin-bottom: 28px;
}
.hero-desc strong { color: var(--txt); font-weight: 600; }
.hl-blue { color: var(--acc1); font-weight: 500; }

.hero-slogan {
  font-size: 0.95rem; color: var(--txt);
  border-left: 2px solid var(--acc1);
  padding-left: 16px; margin-bottom: 40px;
  font-weight: 500;
}
.cursor { color: var(--acc2); animation: blink 1.2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.hero-kpi { display: flex; align-items: center; gap: 32px; }
.kpi-item { display: flex; flex-direction: column; gap: 4px; }
.kpi-val {
  font-family: var(--display);
  font-size: 1.4rem; font-weight: 700; color: var(--txt);
}
.kpi-lbl { font-size: 0.78rem; color: var(--txt3); max-width: 120px; line-height: 1.4; }
.kpi-sep { width: 1px; height: 36px; background: rgba(59,130,246,0.2); }

/* Logo showcase */
.logo-showcase {
  position: relative;
  width: 380px; height: 380px;
  display: flex; align-items: center; justify-content: center;
}
.logo-glow {
  position: absolute; inset: -20px;
  background: radial-gradient(circle at 50% 50%,
    rgba(59,130,246,0.22) 0%,
    rgba(14,165,233,0.07) 50%,
    transparent 70%
  );
  border-radius: 50%;
  animation: glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse {
  0%,100% { opacity: 0.7; transform: scale(1); }
  50%     { opacity: 1;   transform: scale(1.08); }
}
.logo-img {
  width: 340px; height: 340px;
  object-fit: contain;
  animation: float 6s ease-in-out infinite;
  filter: drop-shadow(0 0 48px rgba(59,130,246,0.35));
}
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-14px); }
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

/* ── LAUNCH SECTION ──────────────────────────────────────────────────────── */
.launch-section {
  padding: 72px 0 0;
  border-top: 1px solid rgba(59,130,246,0.1);
}
.launch-head { margin-bottom: 40px; }
.launch-title {
  font-family: var(--display);
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  font-weight: 700; color: var(--txt);
  letter-spacing: -0.5px; margin-bottom: 10px;
}
.launch-sub { font-size: 0.95rem; color: var(--txt2); }

.launch-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.form-col { padding: 28px 32px; }
.form-col:first-child { border-right: 1px solid rgba(59,130,246,0.1); }

.field-hdr {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
  font-family: var(--mono); font-size: 0.72rem;
  color: var(--txt3); letter-spacing: 0.5px;
}
.field-label { color: var(--txt3); }
.field-hint { color: var(--txt2); }

/* Upload zone */
.upload-zone {
  border: 1px dashed rgba(59,130,246,0.25);
  border-radius: 8px;
  min-height: 200px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  background: rgba(6,8,20,0.5);
  transition: border-color .2s, background .2s;
  overflow-y: auto;
}
.upload-zone:hover,
.upload-zone.drag-over {
  border-color: rgba(59,130,246,0.6);
  background: rgba(59,130,246,0.04);
}
.upload-placeholder { text-align: center; }
.upload-icon {
  width: 36px; height: 36px;
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 14px;
  color: var(--acc1); font-size: 1.1rem;
}
.upload-title { font-size: 0.88rem; font-weight: 500; color: var(--txt2); margin-bottom: 5px; }
.upload-hint { font-family: var(--mono); font-size: 0.7rem; color: var(--txt3); }

.file-list { width: 100%; padding: 14px; display: flex; flex-direction: column; gap: 8px; }
.file-item {
  display: flex; align-items: center; gap: 10px;
  background: rgba(59,130,246,0.07);
  border: 1px solid rgba(59,130,246,0.15);
  border-radius: 6px; padding: 8px 12px;
  font-family: var(--mono); font-size: 0.8rem; color: var(--txt2);
}
.file-name { flex: 1; color: var(--txt); }
.remove-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1.1rem; color: var(--txt3);
  transition: color .15s;
}
.remove-btn:hover { color: var(--acc2); }

/* Prompt */
.prompt-wrap { position: relative; }
.prompt-input {
  width: 100%;
  background: rgba(6,8,20,0.5);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 8px;
  padding: 16px 18px;
  font-family: var(--mono);
  font-size: 0.86rem; line-height: 1.7;
  color: var(--txt);
  resize: vertical; outline: none;
  min-height: 200px;
  transition: border-color .2s;
}
.prompt-input::placeholder { color: var(--txt3); }
.prompt-input:focus { border-color: rgba(59,130,246,0.5); }
.engine-badge {
  position: absolute; bottom: 10px; right: 12px;
  font-family: var(--mono);
  font-size: 0.65rem; color: var(--txt3);
}

/* CTA */
.cta-row {
  padding: 24px 32px 32px;
  border-top: 1px solid rgba(59,130,246,0.08);
}
.start-btn {
  width: 100%;
  background: linear-gradient(90deg, #1D4ED8 0%, #3B82F6 50%, #0EA5E9 100%);
  color: #fff; border: none;
  border-radius: 8px; padding: 18px 28px;
  font-family: var(--display);
  font-size: 0.95rem; font-weight: 700;
  letter-spacing: 0.3px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  box-shadow: 0 4px 32px rgba(59,130,246,0.3);
}
.start-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.start-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-arrow { font-size: 1.2rem; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1200px) {
  .cases-grid { grid-template-columns: repeat(2, 1fr); }
  .steps-row { grid-template-columns: repeat(3, 1fr); row-gap: 32px; }
  .steps-row::before { display: none; }
}
@media (max-width: 1024px) {
  .hero { flex-direction: column; gap: 48px; }
  .hero-right { display: none; }
  .form-grid { grid-template-columns: 1fr; }
  .form-col:first-child { border-right: none; border-bottom: 1px solid rgba(59,130,246,0.1); }
}
@media (max-width: 640px) {
  .main-wrap { padding: 48px 20px 64px; }
  .navbar { padding: 0 20px; }
  .hero-title { font-size: 2rem; }
  .cases-grid { grid-template-columns: 1fr; }
  .steps-row { grid-template-columns: 1fr 1fr; }
  .hero-kpi { flex-wrap: wrap; gap: 20px; }
}
</style>
