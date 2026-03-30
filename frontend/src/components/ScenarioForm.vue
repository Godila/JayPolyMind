<template>
  <div class="form-wrap">

    <!-- Header -->
    <div class="form-header">
      <button class="back-btn" @click="$emit('back')">← Назад</button>
      <div class="form-scenario-info">
        <span class="scenario-icon">{{ scenario.icon }}</span>
        <div>
          <span class="eyebrow">Выбранный сценарий</span>
          <h1 class="form-title">{{ scenario.title }}</h1>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="form-body">

      <!-- ── File slots ─────────────────────────────────────────────────── -->
      <div class="slots-section">
        <h2 class="section-label">Что загрузить</h2>

        <div class="slots-list">
          <div
            v-for="(slot, idx) in scenario.fileSlots"
            :key="idx"
            class="file-slot"
          >
            <!-- Slot header -->
            <div class="slot-header">
              <div class="slot-meta">
                <span class="slot-num">{{ String(idx + 1).padStart(2, '0') }}</span>
                <span class="slot-label">{{ slot.label }}</span>
                <span v-if="!slot.required" class="optional-badge">необязательно</span>
              </div>
              <span class="slot-hint">{{ slot.hint }}</span>
            </div>

            <!-- Tips (collapsible) -->
            <div v-if="slot.tips?.length" class="tips-block">
              <button class="tips-toggle" @click="toggleTips(idx)">
                <span class="tips-icon">{{ openTips[idx] ? '▾' : '▸' }}</span>
                {{ openTips[idx] ? 'Скрыть рекомендации' : 'Как заполнить для лучшего результата' }}
              </button>
              <ul v-if="openTips[idx]" class="tips-list">
                <li v-for="(tip, ti) in slot.tips" :key="ti" class="tip-item">
                  <span class="tip-dot">◆</span>
                  {{ tip }}
                </li>
              </ul>
            </div>

            <!-- Upload zone -->
            <div
              class="upload-zone"
              :class="{ 'drag-over': dragOver[idx], 'has-files': slotFiles[idx]?.length > 0 }"
              @dragover.prevent="dragOver[idx] = true"
              @dragleave.prevent="dragOver[idx] = false"
              @drop.prevent="handleDrop($event, idx)"
              @click="triggerInput(idx)"
            >
              <input
                :ref="el => inputRefs[idx] = el"
                type="file"
                multiple
                accept=".pdf,.md,.txt"
                style="display:none"
                @change="handleFileSelect($event, idx)"
              />
              <div v-if="!slotFiles[idx]?.length" class="upload-placeholder">
                <div class="upload-icon-box">↑</div>
                <div class="upload-text">Перетащите файл сюда</div>
                <div class="upload-fmt">PDF · MD · TXT</div>
              </div>
              <div v-else class="file-list">
                <div v-for="(f, fi) in slotFiles[idx]" :key="fi" class="file-item">
                  <span class="file-emoji">📄</span>
                  <span class="file-name">{{ f.name }}</span>
                  <button @click.stop="removeFile(idx, fi)" class="remove-btn">×</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Research question ──────────────────────────────────────────── -->
      <div class="question-section">
        <div class="section-header-row">
          <h2 class="section-label">&gt;_ Исследовательский вопрос</h2>
          <span class="edit-hint">{{ scenario.id === 'custom' ? 'Введите свой вопрос' : 'Предзаполнен — можете отредактировать' }}</span>
        </div>
        <div class="prompt-wrap">
          <textarea
            v-model="requirement"
            class="prompt-input"
            :placeholder="scenario.id === 'custom'
              ? 'Например: «Как различные группы отреагируют на запуск этого продукта?»'
              : ''"
            rows="5"
          ></textarea>
          <div class="engine-badge">Движок: LLM + Neo4j</div>
        </div>
      </div>

      <!-- ── Outcomes ───────────────────────────────────────────────────── -->
      <div v-if="scenario.outcomes?.length" class="outcomes-section">
        <h2 class="section-label">Что вы получите</h2>
        <ul class="outcomes-list">
          <li v-for="(o, oi) in scenario.outcomes" :key="oi" class="outcome-item">
            <span class="outcome-check">✓</span>
            {{ o }}
          </li>
        </ul>
      </div>

      <!-- ── CTA ───────────────────────────────────────────────────────── -->
      <div class="cta-row">
        <div v-if="!canSubmit" class="validation-hint">
          <span v-if="missingRequired">Загрузите обязательные файлы</span>
          <span v-else-if="!requirement.trim()">Заполните исследовательский вопрос</span>
        </div>
        <button
          class="start-btn"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          <span>Запустить симуляцию</span>
          <span class="btn-arrow">→</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  scenario: { type: Object, required: true },
})

const emit = defineEmits(['back', 'submit'])

// ── State ───────────────────────────────────────────────────────────────────

// Files per slot: [slotIndex] → File[]
const slotFiles = reactive(props.scenario.fileSlots.map(() => []))
// Tips open state per slot
const openTips = reactive(props.scenario.fileSlots.map(() => false))
// Drag over state per slot
const dragOver = reactive(props.scenario.fileSlots.map(() => false))
// Hidden file inputs refs
const inputRefs = ref([])
// Research question (pre-filled from scenario)
const requirement = ref(props.scenario.defaultPrompt)

// Reset state when scenario changes (e.g. user went back and picked another)
watch(() => props.scenario, (newS) => {
  slotFiles.splice(0, slotFiles.length, ...newS.fileSlots.map(() => []))
  openTips.splice(0, openTips.length, ...newS.fileSlots.map(() => false))
  dragOver.splice(0, dragOver.length, ...newS.fileSlots.map(() => false))
  requirement.value = newS.defaultPrompt
})

// ── Validation ──────────────────────────────────────────────────────────────

const missingRequired = computed(() =>
  props.scenario.fileSlots.some((slot, i) => slot.required && !slotFiles[i]?.length)
)

const canSubmit = computed(() =>
  !missingRequired.value && requirement.value.trim() !== ''
)

// ── Helpers ─────────────────────────────────────────────────────────────────

const ALLOWED = ['.pdf', '.md', '.txt']

function filterFiles(files) {
  return files.filter(f => ALLOWED.some(ext => f.name.toLowerCase().endsWith(ext)))
}

function triggerInput(idx) {
  inputRefs.value[idx]?.click()
}

function addToSlot(idx, newFiles) {
  const valid = filterFiles(newFiles)
  slotFiles[idx] = [...(slotFiles[idx] || []), ...valid]
}

function handleFileSelect(e, idx) {
  addToSlot(idx, Array.from(e.target.files))
  e.target.value = ''  // allow re-selecting same file
}

function handleDrop(e, idx) {
  dragOver[idx] = false
  addToSlot(idx, Array.from(e.dataTransfer.files))
}

function removeFile(slotIdx, fileIdx) {
  slotFiles[slotIdx].splice(fileIdx, 1)
}

function toggleTips(idx) {
  openTips[idx] = !openTips[idx]
}

// ── Submit ───────────────────────────────────────────────────────────────────

function handleSubmit() {
  if (!canSubmit.value) return
  // Flatten all slot files into single array (backend accepts files[])
  const allFiles = slotFiles.flat()
  emit('submit', { files: allFiles, requirement: requirement.value.trim() })
}
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.form-wrap {
  padding-bottom: 80px;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.form-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 44px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #7FA4C4;
  background: none;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 6px;
  padding: 7px 16px;
  cursor: pointer;
  width: fit-content;
  transition: color 0.2s, border-color 0.2s;
}
.back-btn:hover { color: #38BDF8; border-color: rgba(59, 130, 246, 0.5); }

.form-scenario-info {
  display: flex;
  align-items: center;
  gap: 18px;
}

.scenario-icon {
  font-size: 2.4rem;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 14px;
  flex-shrink: 0;
}

.eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: #3B82F6;
  letter-spacing: 2px;
  text-transform: uppercase;
  display: block;
  margin-bottom: 6px;
}

.form-title {
  font-family: 'Unbounded', sans-serif;
  font-size: clamp(1.3rem, 2.2vw, 1.8rem);
  font-weight: 700;
  color: #EFF6FF;
  letter-spacing: -0.5px;
}

/* ── Body ────────────────────────────────────────────────────────────────── */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.section-label {
  font-family: 'Unbounded', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  color: #EFF6FF;
  margin-bottom: 18px;
}

/* ── File slots ──────────────────────────────────────────────────────────── */
.slots-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.file-slot {
  background: #0A0F1E;
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 12px;
  overflow: hidden;
}

/* Slot header */
.slot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 18px 22px 0;
  gap: 12px;
}

.slot-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.slot-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: #3B82F6;
  font-weight: 700;
}

.slot-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #EFF6FF;
  font-weight: 600;
}

.optional-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: #3A5570;
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 10px;
  padding: 2px 8px;
}

.slot-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: #3A5570;
  text-align: right;
  flex-shrink: 0;
}

/* Tips */
.tips-block {
  padding: 10px 22px 0;
}

.tips-toggle {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #38BDF8;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: opacity 0.2s;
}
.tips-toggle:hover { opacity: 0.75; }
.tips-icon { font-size: 0.65rem; }

.tips-list {
  list-style: none;
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tip-item {
  display: flex;
  gap: 10px;
  font-size: 0.82rem;
  color: #7FA4C4;
  line-height: 1.55;
}

.tip-dot {
  color: #3B82F6;
  font-size: 0.5rem;
  flex-shrink: 0;
  margin-top: 5px;
}

/* Upload zone */
.upload-zone {
  margin: 14px 22px 20px;
  border: 1px dashed rgba(59, 130, 246, 0.25);
  border-radius: 8px;
  min-height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(6, 8, 20, 0.4);
  transition: border-color 0.2s, background 0.2s;
  overflow-y: auto;
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: rgba(59, 130, 246, 0.55);
  background: rgba(59, 130, 246, 0.04);
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-placeholder { text-align: center; }

.upload-icon-box {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  color: #3B82F6;
  font-size: 1rem;
}

.upload-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #7FA4C4;
  margin-bottom: 4px;
}

.upload-fmt {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: #3A5570;
}

.file-list {
  width: 100%;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 9px;
  background: rgba(59, 130, 246, 0.07);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 6px;
  padding: 7px 11px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #7FA4C4;
}

.file-emoji { flex-shrink: 0; }
.file-name { flex: 1; color: #EFF6FF; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #3A5570;
  flex-shrink: 0;
  transition: color 0.15s;
  line-height: 1;
}
.remove-btn:hover { color: #38BDF8; }

/* ── Question section ────────────────────────────────────────────────────── */
.question-section { }

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.edit-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: #3A5570;
  flex-shrink: 0;
}

.prompt-wrap { position: relative; }

.prompt-input {
  width: 100%;
  background: #0A0F1E;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 10px;
  padding: 16px 18px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.86rem;
  line-height: 1.75;
  color: #EFF6FF;
  resize: vertical;
  outline: none;
  min-height: 130px;
  transition: border-color 0.2s;
}
.prompt-input::placeholder { color: #3A5570; }
.prompt-input:focus { border-color: rgba(59, 130, 246, 0.5); }

.engine-badge {
  position: absolute;
  bottom: 10px;
  right: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: #3A5570;
}

/* ── Outcomes section ────────────────────────────────────────────────────── */
.outcomes-section { }

.outcomes-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.outcome-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.12);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 0.85rem;
  color: #7FA4C4;
  line-height: 1.4;
}

.outcome-check {
  color: #3B82F6;
  font-size: 0.75rem;
  flex-shrink: 0;
  margin-top: 2px;
}

/* ── CTA ─────────────────────────────────────────────────────────────────── */
.cta-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.validation-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #F87171;
  text-align: center;
}

.start-btn {
  width: 100%;
  background: linear-gradient(90deg, #1D4ED8 0%, #3B82F6 50%, #0EA5E9 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 18px 28px;
  font-family: 'Unbounded', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  box-shadow: 0 4px 32px rgba(59, 130, 246, 0.3);
}
.start-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.start-btn:disabled { opacity: 0.3; cursor: not-allowed; transform: none; }
.btn-arrow { font-size: 1.2rem; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 860px) {
  .outcomes-list { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .slot-header { flex-direction: column; gap: 6px; }
  .slot-hint { text-align: left; }
  .section-header-row { flex-direction: column; gap: 4px; }
  .form-title { font-size: 1.2rem; }
}
</style>
