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
        <SibylLogo />
        <span class="brand-name">Jay<span class="brand-accent">Sibyl</span></span>
      </div>
      <div class="nav-right">
        <span class="nav-badge">v0.2 · preview</span>
        <a href="https://github.com/Godila/MiroFish-My" target="_blank" class="nav-link">
          GitHub <span class="link-arrow">↗</span>
        </a>
      </div>
    </nav>

    <main class="main-wrap">
      <!-- Hero -->
      <section class="hero">
        <div class="hero-left">
          <div class="hero-tag">
            <span class="tag-dot"></span>
            Движок мультиагентного прогнозирования
          </div>

          <h1 class="hero-title">
            Загрузите документ.<br>
            <span class="hero-title-accent">Узнайте реакцию.</span>
          </h1>

          <p class="hero-desc">
            <strong>JaySibyl</strong> извлекает смысловые зёрна из вашего документа и создаёт
            параллельный мир из сотен <span class="hl-purple">автономных AI-агентов</span> —
            полностью на вашем сервере. Задайте сценарий, наблюдайте за поведением,
            находите <span class="hl-mono">"оптимальные траектории"</span> в сложных
            социальных динамиках.
          </p>

          <p class="hero-slogan">
            Ваши данные не покидают инфраструктуру. Будущее симулируется локально<span class="cursor">_</span>
          </p>

          <div class="hero-metrics">
            <div class="metric">
              <span class="metric-val">Бесплатно</span>
              <span class="metric-lbl">На вашем железе</span>
            </div>
            <div class="metric-sep"></div>
            <div class="metric">
              <span class="metric-val">Приватно</span>
              <span class="metric-lbl">100% офлайн, без облака</span>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="hero-graphic">
            <HeroGraph />
          </div>
        </div>
      </section>

      <!-- Dashboard -->
      <section class="dashboard">
        <!-- Left: Steps -->
        <div class="steps-panel">
          <div class="panel-label">
            <span class="status-dot"></span> Статус системы
          </div>
          <div class="status-ready">Готово</div>
          <p class="status-desc">
            Движок прогнозирования в режиме ожидания. Загрузите данные для запуска симуляции.
          </p>

          <div class="steps-block">
            <div class="steps-label">◇ Последовательность</div>
            <div class="steps-list">
              <div v-for="(step, i) in steps" :key="i" class="step-item">
                <span class="step-num">{{ step.num }}</span>
                <div class="step-body">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-desc">{{ step.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Console -->
        <div class="console-panel">
          <div class="console-box">
            <!-- Upload -->
            <div class="console-section">
              <div class="console-hdr">
                <span>01 / Исходные данные</span>
                <span class="console-hdr-right">Поддержка: PDF, MD, TXT</span>
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
                  <div class="upload-title">Перетащите файлы сюда</div>
                  <div class="upload-hint">или нажмите для выбора</div>
                </div>
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span>📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="console-divider"><span>Параметры</span></div>

            <!-- Prompt -->
            <div class="console-section">
              <div class="console-hdr">
                <span>&gt;_ 02 / Запрос симуляции</span>
              </div>
              <div class="input-wrap">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  placeholder="// Опишите цель симуляции или прогноза на естественном языке"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">Движок: LLM + Neo4j (локально)</div>
              </div>
            </div>

            <!-- Button -->
            <div class="btn-section">
              <button class="start-btn" @click="startSimulation" :disabled="!canSubmit || loading">
                <span>{{ loading ? 'Инициализация...' : 'Запустить' }}</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
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

// ── Inline SVG components ──────────────────────────────────────────────────

const SibylLogo = {
  template: `
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#6C63FF"/>
          <stop offset="100%" stop-color="#FF4D8D"/>
        </linearGradient>
      </defs>
      <!-- Outer ring nodes -->
      <circle cx="16" cy="3"  r="2.2" fill="url(#sg)" opacity="0.9"/>
      <circle cx="28" cy="10" r="2.2" fill="url(#sg)" opacity="0.9"/>
      <circle cx="28" cy="22" r="2.2" fill="url(#sg)" opacity="0.9"/>
      <circle cx="16" cy="29" r="2.2" fill="url(#sg)" opacity="0.9"/>
      <circle cx="4"  cy="22" r="2.2" fill="url(#sg)" opacity="0.9"/>
      <circle cx="4"  cy="10" r="2.2" fill="url(#sg)" opacity="0.9"/>
      <!-- Center -->
      <circle cx="16" cy="16" r="3.5" fill="url(#sg)"/>
      <!-- Edges -->
      <line x1="16" y1="3"  x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <line x1="28" y1="10" x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <line x1="28" y1="22" x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <line x1="16" y1="29" x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <line x1="4"  cy="22" x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <line x1="4"  y1="10" x2="16" y2="16" stroke="url(#sg)" stroke-width="0.8" opacity="0.5"/>
      <!-- Hex ring -->
      <polygon points="16,3 28,10 28,22 16,29 4,22 4,10"
        fill="none" stroke="url(#sg)" stroke-width="0.6" opacity="0.3"/>
    </svg>
  `
}

const HeroGraph = {
  template: `
    <svg width="420" height="360" viewBox="0 0 420 360" fill="none" xmlns="http://www.w3.org/2000/svg" style="max-width:100%">
      <defs>
        <linearGradient id="hg1" x1="0" y1="0" x2="420" y2="360" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#6C63FF" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#FF4D8D" stop-opacity="0.8"/>
        </linearGradient>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#6C63FF" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#6C63FF" stop-opacity="0"/>
        </radialGradient>
        <filter id="blur"><feGaussianBlur stdDeviation="8"/></filter>
      </defs>

      <!-- Glow bg -->
      <ellipse cx="210" cy="180" rx="160" ry="120" fill="url(#glow)" filter="url(#blur)"/>

      <!-- Edge lines -->
      <line x1="210" y1="180" x2="100" y2="80"  stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="210" y1="180" x2="320" y2="80"  stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="210" y1="180" x2="60"  y2="210" stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="210" y1="180" x2="360" y2="210" stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="210" y1="180" x2="130" y2="310" stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="210" y1="180" x2="290" y2="310" stroke="url(#hg1)" stroke-width="1.2" opacity="0.4"/>
      <line x1="100" y1="80"  x2="320" y2="80"  stroke="#6C63FF" stroke-width="0.6" opacity="0.25"/>
      <line x1="60"  y1="210" x2="130" y2="310" stroke="#FF4D8D" stroke-width="0.6" opacity="0.25"/>
      <line x1="360" y1="210" x2="290" y2="310" stroke="#FF4D8D" stroke-width="0.6" opacity="0.25"/>

      <!-- Satellite nodes -->
      <circle cx="100" cy="80"  r="8"  fill="#6C63FF" opacity="0.85"/>
      <circle cx="320" cy="80"  r="6"  fill="#7C6FFF" opacity="0.75"/>
      <circle cx="60"  cy="210" r="7"  fill="#FF4D8D" opacity="0.75"/>
      <circle cx="360" cy="210" r="9"  fill="#6C63FF" opacity="0.8"/>
      <circle cx="130" cy="310" r="6"  fill="#FF4D8D" opacity="0.7"/>
      <circle cx="290" cy="310" r="8"  fill="#6C63FF" opacity="0.8"/>

      <!-- Small secondary nodes -->
      <circle cx="170" cy="110" r="3.5" fill="#9D97FF" opacity="0.6"/>
      <circle cx="280" cy="140" r="3"   fill="#FF7BAD" opacity="0.5"/>
      <circle cx="85"  cy="140" r="3"   fill="#6C63FF" opacity="0.5"/>
      <circle cx="340" cy="150" r="3.5" fill="#9D97FF" opacity="0.6"/>
      <circle cx="190" cy="280" r="3"   fill="#FF4D8D" opacity="0.5"/>
      <line x1="170" y1="110" x2="100" y2="80"  stroke="#6C63FF" stroke-width="0.5" opacity="0.3"/>
      <line x1="280" y1="140" x2="320" y2="80"  stroke="#6C63FF" stroke-width="0.5" opacity="0.3"/>
      <line x1="280" y1="140" x2="360" y2="210" stroke="#6C63FF" stroke-width="0.5" opacity="0.3"/>

      <!-- Central node with rings -->
      <circle cx="210" cy="180" r="22" fill="#080810" stroke="url(#hg1)" stroke-width="2"/>
      <circle cx="210" cy="180" r="14" fill="url(#hg1)" opacity="0.9"/>
      <circle cx="210" cy="180" r="6"  fill="#fff" opacity="0.95"/>

      <!-- Orbit ring -->
      <circle cx="210" cy="180" r="36" fill="none" stroke="url(#hg1)" stroke-width="0.5" stroke-dasharray="4 6" opacity="0.35"/>
    </svg>
  `
}

// ── Data ───────────────────────────────────────────────────────────────────

const steps = [
  { num: '01', title: 'Построение графа',  desc: 'Извлечение смысловых зёрен из документа, построение графа знаний Neo4j + GraphRAG' },
  { num: '02', title: 'Настройка среды',   desc: 'Генерация персон агентов, настройка параметров симуляции через LLM' },
  { num: '03', title: 'Симуляция',         desc: 'Запуск мультиагентной симуляции с динамическим обновлением памяти' },
  { num: '04', title: 'Отчёт',             desc: 'ReportAgent анализирует результаты и генерирует детальный прогнозный отчёт' },
  { num: '05', title: 'Взаимодействие',    desc: 'Чат с любым агентом симулированного мира или обсуждение выводов с ReportAgent' },
]

// ── Logic (unchanged) ──────────────────────────────────────────────────────

const router = useRouter()
const formData = ref({ simulationRequirement: '' })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)

const canSubmit = computed(() =>
  formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
)

const triggerFileInput = () => { if (!loading.value) fileInput.value?.click() }
const handleFileSelect = (e) => addFiles(Array.from(e.target.files))
const handleDragOver  = () => { isDragOver.value = true }
const handleDragLeave = () => { isDragOver.value = false }
const handleDrop      = (e) => { isDragOver.value = false; addFiles(Array.from(e.dataTransfer.files)) }

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

/* ── Tokens ─────────────────────────────────────────────────────────────── */
:root {
  --bg:          #080810;
  --bg2:         #0F0F1A;
  --bg3:         #16162A;
  --acc1:        #6C63FF;
  --acc2:        #FF4D8D;
  --txt:         #F0F0FF;
  --txt2:        #8888AA;
  --txt3:        #55556A;
  --border:      rgba(108,99,255,0.18);
  --border-h:    rgba(108,99,255,0.45);
  --mono:        'JetBrains Mono', monospace;
  --display:     'Unbounded', sans-serif;
  --body:        'Onest', sans-serif;
}

/* ── Reset ───────────────────────────────────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Root ────────────────────────────────────────────────────────────────── */
.home-root {
  min-height: 100vh;
  background: #080810;
  color: #F0F0FF;
  font-family: 'Onest', sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* ── Ambient bg ──────────────────────────────────────────────────────────── */
.bg-ambient { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.12;
}
.orb-1 { width: 700px; height: 700px; background: #6C63FF; top: -200px; left: -200px; }
.orb-2 { width: 500px; height: 500px; background: #FF4D8D; bottom: -100px; right: -100px; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(108,99,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(108,99,255,0.04) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: relative; z-index: 10;
  height: 64px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px;
  border-bottom: 1px solid rgba(108,99,255,0.12);
  background: rgba(8,8,16,0.85);
  backdrop-filter: blur(12px);
}
.nav-brand { display: flex; align-items: center; gap: 12px; }
.brand-name {
  font-family: 'Unbounded', sans-serif;
  font-size: 1.15rem; font-weight: 700;
  letter-spacing: -0.5px; color: #F0F0FF;
}
.brand-accent { color: #6C63FF; }
.nav-right { display: flex; align-items: center; gap: 20px; }
.nav-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: #55556A;
  border: 1px solid rgba(108,99,255,0.15);
  padding: 3px 10px; border-radius: 20px;
}
.nav-link {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem; color: #8888AA;
  text-decoration: none;
  display: flex; align-items: center; gap: 5px;
  transition: color .2s;
}
.nav-link:hover { color: #6C63FF; }
.link-arrow { font-size: 0.75rem; }

/* ── Main wrap ───────────────────────────────────────────────────────────── */
.main-wrap {
  position: relative; z-index: 1;
  max-width: 1320px; margin: 0 auto;
  padding: 72px 48px 80px;
}

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
  display: flex; gap: 64px;
  align-items: center;
  margin-bottom: 96px;
}
.hero-left { flex: 1; }
.hero-right { flex: 0 0 420px; }

.hero-tag {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: #6C63FF;
  border: 1px solid rgba(108,99,255,0.3);
  padding: 5px 14px; border-radius: 20px;
  margin-bottom: 28px; letter-spacing: 0.5px;
}
.tag-dot {
  width: 6px; height: 6px;
  border-radius: 50%; background: #6C63FF;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.3; }
}

.hero-title {
  font-family: 'Unbounded', sans-serif;
  font-size: clamp(2.4rem, 4vw, 3.6rem);
  font-weight: 700; line-height: 1.15;
  letter-spacing: -1.5px;
  color: #F0F0FF;
  margin-bottom: 28px;
}
.hero-title-accent {
  background: linear-gradient(90deg, #6C63FF 0%, #FF4D8D 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 1.05rem; line-height: 1.8;
  color: #8888AA; max-width: 580px;
  margin-bottom: 32px;
}
.hero-desc strong { color: #F0F0FF; font-weight: 600; }
.hl-purple { color: #6C63FF; font-weight: 500; }
.hl-mono {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(108,99,255,0.12);
  border: 1px solid rgba(108,99,255,0.2);
  padding: 2px 7px; border-radius: 4px;
  font-size: 0.9em; color: #9D97FF;
}

.hero-slogan {
  font-size: 0.95rem; color: #F0F0FF;
  border-left: 2px solid #6C63FF;
  padding-left: 16px; margin-bottom: 40px;
  font-weight: 500; letter-spacing: 0.3px;
}
.cursor { color: #FF4D8D; animation: blink 1.2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.hero-metrics { display: flex; align-items: center; gap: 28px; }
.metric { display: flex; flex-direction: column; gap: 4px; }
.metric-val {
  font-family: 'Unbounded', sans-serif;
  font-size: 1.3rem; font-weight: 700; color: #F0F0FF;
}
.metric-lbl { font-size: 0.8rem; color: #55556A; }
.metric-sep { width: 1px; height: 36px; background: rgba(108,99,255,0.2); }

.hero-graphic { display: flex; justify-content: center; align-items: center; }

/* ── Dashboard ───────────────────────────────────────────────────────────── */
.dashboard {
  display: flex; gap: 56px;
  align-items: flex-start;
  padding-top: 56px;
  border-top: 1px solid rgba(108,99,255,0.12);
}

/* Steps panel */
.steps-panel { flex: 0 0 340px; }
.panel-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem; color: #55556A;
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 16px;
}
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%; background: #6C63FF;
  animation: pulse 2s infinite;
}
.status-ready {
  font-family: 'Unbounded', sans-serif;
  font-size: 2rem; font-weight: 700;
  color: #F0F0FF; margin-bottom: 10px;
}
.status-desc { font-size: 0.9rem; color: #8888AA; line-height: 1.6; margin-bottom: 28px; }

.steps-block {
  border: 1px solid rgba(108,99,255,0.15);
  border-radius: 8px; padding: 24px;
  background: rgba(15,15,26,0.6);
}
.steps-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: #55556A;
  margin-bottom: 20px; letter-spacing: 1px;
}
.steps-list { display: flex; flex-direction: column; gap: 18px; }
.step-item { display: flex; gap: 16px; align-items: flex-start; }
.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem; font-weight: 600;
  color: #6C63FF; opacity: 0.6;
  min-width: 24px; padding-top: 2px;
}
.step-body { flex: 1; }
.step-title { font-size: 0.9rem; font-weight: 600; color: #F0F0FF; margin-bottom: 3px; }
.step-desc { font-size: 0.8rem; color: #55556A; line-height: 1.5; }

/* Console panel */
.console-panel { flex: 1; }
.console-box {
  border: 1px solid rgba(108,99,255,0.2);
  border-radius: 10px; overflow: hidden;
  background: rgba(15,15,26,0.8);
  backdrop-filter: blur(8px);
}
.console-section { padding: 20px 24px; }
.console-hdr {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: #55556A; letter-spacing: 0.5px;
}
.console-hdr-right { color: #8888AA; }

.upload-zone {
  border: 1px dashed rgba(108,99,255,0.25);
  border-radius: 6px;
  height: 180px; overflow-y: auto;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  background: rgba(8,8,16,0.6);
  transition: border-color .2s, background .2s;
}
.upload-zone:hover,
.upload-zone.drag-over {
  border-color: rgba(108,99,255,0.6);
  background: rgba(108,99,255,0.05);
}
.upload-placeholder { text-align: center; }
.upload-icon {
  width: 36px; height: 36px;
  border: 1px solid rgba(108,99,255,0.3);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
  color: #6C63FF; font-size: 1.1rem;
}
.upload-title { font-size: 0.88rem; font-weight: 500; color: #8888AA; margin-bottom: 5px; }
.upload-hint { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #55556A; }

.file-list { width: 100%; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.file-item {
  display: flex; align-items: center;
  background: rgba(108,99,255,0.08);
  border: 1px solid rgba(108,99,255,0.15);
  border-radius: 5px; padding: 7px 12px;
  font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #8888AA;
}
.file-name { flex: 1; margin: 0 10px; color: #F0F0FF; }
.remove-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1.1rem; color: #55556A;
  transition: color .15s;
}
.remove-btn:hover { color: #FF4D8D; }

.console-divider {
  border-top: 1px solid rgba(108,99,255,0.1);
  display: flex; align-items: center;
  padding: 0 24px;
}
.console-divider span {
  position: relative; top: -0.5em;
  background: #0F0F1A;
  padding: 0 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem; color: #55556A; letter-spacing: 1.5px;
}

.input-wrap { position: relative; }
.code-input {
  width: 100%;
  background: rgba(8,8,16,0.6);
  border: 1px solid rgba(108,99,255,0.2);
  border-radius: 6px;
  padding: 16px 18px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.88rem; line-height: 1.7;
  color: #F0F0FF;
  resize: vertical; outline: none;
  min-height: 140px;
  transition: border-color .2s;
}
.code-input::placeholder { color: #55556A; }
.code-input:focus { border-color: rgba(108,99,255,0.5); }
.model-badge {
  position: absolute; bottom: 10px; right: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.67rem; color: #55556A;
}

.btn-section { padding: 0 24px 24px; }
.start-btn {
  width: 100%;
  background: linear-gradient(90deg, #6C63FF 0%, #8B5CF6 50%, #FF4D8D 100%);
  color: #fff; border: none;
  border-radius: 7px; padding: 18px 24px;
  font-family: 'Unbounded', sans-serif;
  font-size: 0.95rem; font-weight: 700;
  letter-spacing: 0.5px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  box-shadow: 0 4px 32px rgba(108,99,255,0.3);
}
.start-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.start-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-arrow { font-size: 1.2rem; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .hero { flex-direction: column; gap: 40px; }
  .hero-right { display: none; }
  .dashboard { flex-direction: column; }
  .steps-panel { flex: none; width: 100%; }
}
@media (max-width: 640px) {
  .main-wrap { padding: 40px 20px 60px; }
  .navbar { padding: 0 20px; }
  .hero-title { font-size: 2rem; }
}
</style>
