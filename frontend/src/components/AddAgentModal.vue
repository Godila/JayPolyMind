<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">

          <!-- Header -->
          <div class="modal-header">
            <div class="modal-title">
              <span class="modal-icon">⚡</span>
              <span>Добавить агента в симуляцию</span>
            </div>
            <button class="close-btn" @click="$emit('close')">✕</button>
          </div>

          <!-- Body -->
          <div class="modal-body">

            <!-- Character presets -->
            <div class="field-group">
              <label class="field-label">Пресет персонажа</label>
              <div class="presets-row">
                <button
                  v-for="p in PRESETS"
                  :key="p.id"
                  class="preset-btn"
                  :class="{ active: selectedPreset === p.id }"
                  @click="applyPreset(p)"
                  :title="p.hint"
                >
                  <span class="preset-icon">{{ p.icon }}</span>
                  <span class="preset-name">{{ p.label }}</span>
                </button>
              </div>
            </div>

            <!-- Name -->
            <div class="field-group">
              <label class="field-label">Имя агента <span class="required">*</span></label>
              <input
                v-model="form.name"
                class="field-input"
                type="text"
                placeholder="Например: Иван Петров"
                maxlength="60"
              />
            </div>

            <!-- Description -->
            <div class="field-group">
              <label class="field-label">Описание характера <span class="required">*</span></label>
              <textarea
                v-model="form.description"
                class="field-textarea"
                :placeholder="descriptionPlaceholder"
                rows="3"
                maxlength="400"
              ></textarea>
              <span class="char-count">{{ form.description.length }}/400</span>
            </div>

            <!-- Stance toggle -->
            <div class="field-group">
              <label class="field-label">Позиция в симуляции</label>
              <div class="toggle-row stance-toggle">
                <button
                  v-for="s in STANCES"
                  :key="s.value"
                  class="toggle-btn"
                  :class="['stance-' + s.value, { active: form.stance === s.value }]"
                  @click="form.stance = s.value"
                >{{ s.label }}</button>
              </div>
            </div>

            <!-- Activity toggle -->
            <div class="field-group">
              <label class="field-label">Уровень активности</label>
              <div class="toggle-row">
                <button
                  v-for="a in ACTIVITIES"
                  :key="a.value"
                  class="toggle-btn"
                  :class="{ active: form.activity === a.value }"
                  @click="form.activity = a.value"
                >{{ a.label }}</button>
              </div>
            </div>

            <!-- Interests -->
            <div class="field-group">
              <label class="field-label">Интересы / темы</label>
              <div class="tag-input-wrap">
                <div class="tags-list">
                  <span
                    v-for="(tag, ti) in form.interests"
                    :key="ti"
                    class="tag"
                  >
                    {{ tag }}
                    <button class="tag-remove" @click="removeTag(ti)">×</button>
                  </span>
                  <input
                    v-model="tagInput"
                    class="tag-input"
                    placeholder="Добавить тему..."
                    @keydown.enter.prevent="addTag"
                    @keydown.comma.prevent="addTag"
                  />
                </div>
              </div>
              <span class="field-hint">Enter или запятая для добавления</span>
            </div>

            <!-- Preview result -->
            <Transition name="fade">
              <div v-if="previewData" class="preview-box">
                <div class="preview-header">
                  <span class="preview-label">Предпросмотр профиля</span>
                  <span class="preview-badge">{{ previewData.mbti }}</span>
                  <span class="preview-age">{{ previewData.age }} лет · {{ previewData.country }}</span>
                </div>
                <div class="preview-bio">{{ previewData.bio }}</div>
                <div class="preview-persona">{{ previewData.persona }}</div>
                <div class="preview-meta">
                  <span class="preview-profession">{{ previewData.profession }}</span>
                  <span class="preview-username">@{{ previewData.username }}</span>
                </div>
              </div>
            </Transition>

            <!-- Error -->
            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button
              class="btn-preview"
              :disabled="!canPreview || previewLoading"
              @click="handlePreview"
            >
              <span v-if="previewLoading" class="spinner">⟳</span>
              <span v-else>Посмотреть профиль</span>
            </button>
            <button
              class="btn-add"
              :disabled="!canAdd || addLoading"
              @click="handleAdd"
            >
              <span v-if="addLoading" class="spinner">⟳</span>
              <span v-else>Добавить в симуляцию →</span>
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { previewCustomAgent, addCustomAgent } from '../api/simulation.js'

const props = defineProps({
  show:                  { type: Boolean, default: false },
  simulationId:          { type: String,  required: true },
  simulationRequirement: { type: String,  default: '' },
})
const emit = defineEmits(['close', 'added'])

// ── Presets ──────────────────────────────────────────────────────────────────
const PRESETS = [
  {
    id: 'skeptic',
    icon: '🎯',
    label: 'Скептик',
    stance: 'opposing',
    activity: 0.25,
    hint: 'Критически настроенный участник, сомневается в официальных позициях',
    descHint: 'Аналитический скептик, склонный подвергать сомнению заявления и искать противоречия. Любит задавать острые вопросы.',
  },
  {
    id: 'enthusiast',
    icon: '🚀',
    label: 'Энтузиаст',
    stance: 'supportive',
    activity: 0.85,
    hint: 'Активный сторонник, разделяет и продвигает идеи',
    descHint: 'Увлечённый сторонник с позитивным взглядом на мир. Активно комментирует, делится контентом и вдохновляет других.',
  },
  {
    id: 'expert',
    icon: '📊',
    label: 'Эксперт',
    stance: 'neutral',
    activity: 0.5,
    hint: 'Профессиональный голос с аргументами и фактами',
    descHint: 'Профессионал с глубокими знаниями в области. Пишет взвешенно, опирается на данные и исследования.',
  },
  {
    id: 'influencer',
    icon: '💬',
    label: 'Инфлюенсер',
    stance: 'neutral',
    activity: 0.9,
    hint: 'Популярный пользователь с широкой аудиторией',
    descHint: 'Известная в сети личность с большим количеством подписчиков. Любит горячие темы, высказывается часто и уверенно.',
  },
  {
    id: 'observer',
    icon: '🧘',
    label: 'Наблюдатель',
    stance: 'observer',
    activity: 0.2,
    hint: 'Пассивный участник, редко высказывается',
    descHint: 'Тихий наблюдатель, предпочитающий следить за дискуссией со стороны. Редко публикует, но внимательно читает.',
  },
]

const STANCES = [
  { value: 'supportive', label: '🟢 Поддерживает' },
  { value: 'neutral',    label: '⚪ Нейтрален' },
  { value: 'opposing',   label: '🔴 Против' },
  { value: 'observer',   label: '👁 Наблюдает' },
]

const ACTIVITIES = [
  { value: 0.2,  label: 'Низкая' },
  { value: 0.5,  label: 'Средняя' },
  { value: 0.85, label: 'Высокая' },
]

// ── State ────────────────────────────────────────────────────────────────────
const selectedPreset  = ref(null)
const tagInput        = ref('')
const previewData     = ref(null)
const previewLoading  = ref(false)
const addLoading      = ref(false)
const errorMsg        = ref('')

const form = ref({
  name:        '',
  description: '',
  stance:      'neutral',
  activity:    0.5,
  interests:   [],
})

// ── Computed ─────────────────────────────────────────────────────────────────
const canPreview = computed(() => form.value.name.trim() && form.value.description.trim())
const canAdd     = computed(() => canPreview.value && !!previewData.value)

const descriptionPlaceholder = computed(() => {
  const preset = PRESETS.find(p => p.id === selectedPreset.value)
  return preset?.descHint || 'Опишите характер, ценности и манеру общения этого персонажа...'
})

// ── Methods ──────────────────────────────────────────────────────────────────
function applyPreset(preset) {
  selectedPreset.value      = preset.id
  form.value.stance         = preset.stance
  form.value.activity       = preset.activity
  previewData.value         = null
  errorMsg.value            = ''
}

function addTag() {
  const val = tagInput.value.replace(/,$/, '').trim()
  if (val && !form.value.interests.includes(val)) {
    form.value.interests.push(val)
  }
  tagInput.value = ''
}

function removeTag(idx) {
  form.value.interests.splice(idx, 1)
}

async function handlePreview() {
  if (!canPreview.value || previewLoading.value) return
  previewLoading.value = true
  errorMsg.value       = ''
  previewData.value    = null
  try {
    const res = await previewCustomAgent(props.simulationId, {
      name:        form.value.name.trim(),
      description: form.value.description.trim(),
      stance:      form.value.stance,
      activity:    form.value.activity,
      interests:   form.value.interests,
    })
    if (res.success) {
      previewData.value = res.data
    } else {
      errorMsg.value = res.error || 'Ошибка генерации превью'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || e.message || 'Ошибка сети'
  } finally {
    previewLoading.value = false
  }
}

async function handleAdd() {
  if (!canAdd.value || addLoading.value) return
  addLoading.value = true
  errorMsg.value   = ''
  try {
    const res = await addCustomAgent(props.simulationId, {
      name:        form.value.name.trim(),
      description: form.value.description.trim(),
      stance:      form.value.stance,
      activity:    form.value.activity,
      interests:   form.value.interests,
    })
    if (res.success) {
      emit('added', res.data)
      // Reset form
      form.value      = { name: '', description: '', stance: 'neutral', activity: 0.5, interests: [] }
      selectedPreset.value = null
      previewData.value    = null
      tagInput.value       = ''
      emit('close')
    } else {
      errorMsg.value = res.error || 'Ошибка добавления агента'
    }
  } catch (e) {
    errorMsg.value = e?.response?.data?.error || e.message || 'Ошибка сети'
  } finally {
    addLoading.value = false
  }
}
</script>

<style scoped>
/* ── Overlay ─────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(6, 8, 20, 0.82);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* ── Card ────────────────────────────────────────────────────────────────── */
.modal-card {
  background: #0D1424;
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 16px;
  width: 100%;
  max-width: 640px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(59, 130, 246, 0.08);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.12);
  flex-shrink: 0;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Unbounded', sans-serif;
  font-size: 0.88rem;
  font-weight: 700;
  color: #EFF6FF;
}

.modal-icon { font-size: 1.1rem; }

.close-btn {
  background: none;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  color: #64748B;
  font-size: 0.9rem;
  width: 32px; height: 32px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.close-btn:hover { border-color: rgba(59, 130, 246, 0.5); color: #EFF6FF; }

/* ── Body ────────────────────────────────────────────────────────────────── */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.25) transparent;
}

.modal-body::-webkit-scrollbar { width: 5px; }
.modal-body::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.25); border-radius: 3px; }

/* ── Field ───────────────────────────────────────────────────────────────── */
.field-group { display: flex; flex-direction: column; gap: 8px; }

.field-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: #7FA4C4;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.required { color: #F87171; }

.field-input,
.field-textarea {
  background: rgba(6, 8, 20, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 10px 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.84rem;
  color: #EFF6FF;
  outline: none;
  transition: border-color 0.2s;
  resize: vertical;
}
.field-input:focus,
.field-textarea:focus { border-color: rgba(59, 130, 246, 0.55); }
.field-input::placeholder,
.field-textarea::placeholder { color: #3A5570; }

.char-count {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: #3A5570;
  align-self: flex-end;
}

.field-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: #3A5570;
}

/* ── Presets ─────────────────────────────────────────────────────────────── */
.presets-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 8px;
  padding: 7px 12px;
  cursor: pointer;
  transition: all 0.15s;
  color: #7FA4C4;
}

.preset-btn:hover {
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.1);
  color: #EFF6FF;
}

.preset-btn.active {
  border-color: #38BDF8;
  background: rgba(56, 189, 248, 0.12);
  color: #38BDF8;
}

.preset-icon { font-size: 1rem; }
.preset-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
}

/* ── Toggles ─────────────────────────────────────────────────────────────── */
.toggle-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.toggle-btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.04);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 7px;
  padding: 7px 14px;
  cursor: pointer;
  color: #7FA4C4;
  transition: all 0.15s;
}

.toggle-btn:hover { border-color: rgba(59, 130, 246, 0.4); color: #CBD5E1; }

.toggle-btn.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3B82F6;
  color: #EFF6FF;
}

.stance-toggle .toggle-btn.stance-supportive.active {
  background: rgba(34, 197, 94, 0.12);
  border-color: #22C55E;
  color: #86EFAC;
}
.stance-toggle .toggle-btn.stance-opposing.active {
  background: rgba(239, 68, 68, 0.12);
  border-color: #EF4444;
  color: #FCA5A5;
}
.stance-toggle .toggle-btn.stance-observer.active {
  background: rgba(148, 163, 184, 0.1);
  border-color: #94A3B8;
  color: #CBD5E1;
}

/* ── Tag input ───────────────────────────────────────────────────────────── */
.tag-input-wrap {
  background: rgba(6, 8, 20, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 8px 12px;
  min-height: 42px;
  cursor: text;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 5px;
  padding: 2px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #93C5FD;
}

.tag-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748B;
  font-size: 0.9rem;
  padding: 0;
  line-height: 1;
  transition: color 0.1s;
}
.tag-remove:hover { color: #F87171; }

.tag-input {
  background: none;
  border: none;
  outline: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  color: #EFF6FF;
  min-width: 120px;
  flex: 1;
}
.tag-input::placeholder { color: #3A5570; }

/* ── Preview box ─────────────────────────────────────────────────────────── */
.preview-box {
  background: rgba(56, 189, 248, 0.05);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.preview-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #38BDF8;
  font-weight: 700;
}

.preview-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 5px;
  padding: 1px 7px;
  color: #93C5FD;
}

.preview-age {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #7FA4C4;
}

.preview-bio {
  font-size: 0.84rem;
  color: #CBD5E1;
  line-height: 1.5;
}

.preview-persona {
  font-size: 0.8rem;
  color: #7FA4C4;
  line-height: 1.6;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
  padding-left: 10px;
}

.preview-meta {
  display: flex;
  gap: 12px;
}

.preview-profession {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #38BDF8;
}

.preview-username {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #3A5570;
}

/* ── Error ───────────────────────────────────────────────────────────────── */
.error-msg {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  color: #F87171;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 7px;
  padding: 9px 12px;
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.modal-footer {
  display: flex;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid rgba(59, 130, 246, 0.12);
  flex-shrink: 0;
}

.btn-preview {
  flex: 1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  padding: 11px 18px;
  color: #93C5FD;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-preview:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.16);
  border-color: rgba(59, 130, 246, 0.6);
}
.btn-preview:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-add {
  flex: 1.4;
  font-family: 'Unbounded', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  background: linear-gradient(90deg, #1D4ED8, #3B82F6);
  border: none;
  border-radius: 8px;
  padding: 11px 18px;
  color: #fff;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);
}
.btn-add:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.btn-add:disabled { opacity: 0.3; cursor: not-allowed; transform: none; }

.spinner {
  display: inline-block;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transition ──────────────────────────────────────────────────────────── */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal-card,
.modal-leave-active .modal-card { transition: transform 0.2s ease, opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card,
.modal-leave-to .modal-card { transform: translateY(16px); opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .modal-overlay { padding: 0; align-items: flex-end; }
  .modal-card { max-height: 92vh; border-radius: 16px 16px 0 0; }
  .presets-row { gap: 6px; }
  .preset-btn { padding: 6px 10px; }
}
</style>
