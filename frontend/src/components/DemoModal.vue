<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-card">
          <div class="modal-header">
            <div class="modal-title">
              <span class="file-icon">📄</span>
              <span class="file-name">{{ filename }}</span>
            </div>
            <button class="close-btn" @click="$emit('close')">✕</button>
          </div>
          <div class="modal-body">
            <pre class="file-content">{{ content }}</pre>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  show:     { type: Boolean, default: false },
  filename: { type: String,  default: '' },
  content:  { type: String,  default: '' },
})
defineEmits(['close'])
</script>

<style scoped>
/* ── Overlay ────────────────────────────────────────────────────────────── */
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
  background: #0A0F1E;
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 16px;
  width: 100%;
  max-width: 780px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(59, 130, 246, 0.1);
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
  min-width: 0;
}

.file-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.file-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  font-weight: 600;
  color: #CBD5E1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  background: none;
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  color: #64748B;
  font-size: 0.9rem;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}

.close-btn:hover {
  border-color: rgba(59, 130, 246, 0.5);
  color: #EFF6FF;
  background: rgba(59, 130, 246, 0.08);
}

/* ── Body ────────────────────────────────────────────────────────────────── */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.25) transparent;
}

.modal-body::-webkit-scrollbar { width: 6px; }
.modal-body::-webkit-scrollbar-track { background: transparent; }
.modal-body::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.25);
  border-radius: 3px;
}

.file-content {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.75;
  color: #94A3B8;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

/* ── Transition ──────────────────────────────────────────────────────────── */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-card,
.modal-leave-to .modal-card {
  transform: translateY(16px);
  opacity: 0;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .modal-overlay { padding: 12px; align-items: flex-end; }
  .modal-card { max-height: 90vh; border-radius: 16px 16px 0 0; }
}
</style>
