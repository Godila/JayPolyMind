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

      <!-- ── LAUNCH FORM ───────────────────────────────────────────────── -->
      <section class="launch-section">
        <div class="launch-head">
          <span class="section-eyebrow">Новая симуляция</span>
          <h1 class="launch-title">Запустить симуляцию</h1>
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
import { getUser, logout } from '../store/auth.js'

// ── Auth ────────────────────────────────────────────────────────────────────
const router      = useRouter()
const currentUser = ref(getUser())

function handleLogout() {
  logout()
  router.push({ name: 'Login' })
}

// ── Simulation form ─────────────────────────────────────────────────────────
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

/* ── Section eyebrow ─────────────────────────────────────────────────────── */
.section-eyebrow {
  font-family: var(--mono);
  font-size: 0.7rem; color: var(--acc1);
  letter-spacing: 2px; text-transform: uppercase;
  display: block; margin-bottom: 10px;
}

/* ── LAUNCH SECTION ──────────────────────────────────────────────────────── */
.launch-section { padding-bottom: 72px; }
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
@media (max-width: 1024px) {
  .form-grid { grid-template-columns: 1fr; }
  .form-col:first-child { border-right: none; border-bottom: 1px solid rgba(59,130,246,0.1); }
}
@media (max-width: 640px) {
  .main-wrap { padding: 48px 20px 64px; }
  .navbar { padding: 0 20px; }
  .user-badge { display: none; }
}
</style>
