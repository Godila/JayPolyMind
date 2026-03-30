<template>
  <div class="picker-wrap">
    <div class="picker-head">
      <span class="eyebrow">Новая симуляция</span>
      <h1 class="picker-title">С чего начнём?</h1>
      <p class="picker-sub">Выберите сценарий — система объяснит что загрузить, предложит вопрос и покажет что вы получите на выходе.</p>
    </div>

    <div class="scenarios-grid">
      <button
        v-for="s in SCENARIOS"
        :key="s.id"
        class="scenario-card"
        :class="{ 'is-custom': s.id === 'custom' }"
        @click="$emit('select', s)"
      >
        <span class="card-icon">{{ s.icon }}</span>
        <div class="card-body">
          <h3 class="card-title">{{ s.title }}</h3>
          <p class="card-desc">{{ s.desc }}</p>
        </div>
        <span class="card-arrow">→</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { SCENARIOS } from '../data/scenarios.js'

defineEmits(['select'])
</script>

<style scoped>
.picker-wrap {
  padding-bottom: 72px;
}

.picker-head {
  margin-bottom: 48px;
}

.eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #3B82F6;
  letter-spacing: 2px;
  text-transform: uppercase;
  display: block;
  margin-bottom: 14px;
}

.picker-title {
  font-family: 'Unbounded', sans-serif;
  font-size: clamp(1.6rem, 2.8vw, 2.4rem);
  font-weight: 700;
  color: #EFF6FF;
  letter-spacing: -1px;
  margin-bottom: 14px;
}

.picker-sub {
  font-size: 1rem;
  color: #7FA4C4;
  max-width: 600px;
  line-height: 1.7;
}

/* ── Grid ──────────────────────────────────────────────────────────────────── */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

/* ── Card ──────────────────────────────────────────────────────────────────── */
.scenario-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #0A0F1E;
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 14px;
  padding: 24px 28px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
  width: 100%;
}

.scenario-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
  transform: translateY(-2px);
}

.scenario-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(3px);
}

/* Custom card — dashed border, slightly different style */
.scenario-card.is-custom {
  border-style: dashed;
  border-color: rgba(59, 130, 246, 0.2);
}

.scenario-card.is-custom:hover {
  border-color: rgba(59, 130, 246, 0.45);
  border-style: dashed;
}

.card-icon {
  font-size: 2rem;
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.15);
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-family: 'Unbounded', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: #EFF6FF;
  margin-bottom: 5px;
  line-height: 1.3;
}

.card-desc {
  font-size: 0.83rem;
  color: #7FA4C4;
  line-height: 1.5;
}

.card-arrow {
  font-size: 1.1rem;
  color: #3B82F6;
  opacity: 0.4;
  flex-shrink: 0;
  transition: opacity 0.2s, transform 0.2s;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .scenarios-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .scenario-card {
    padding: 18px 20px;
    gap: 14px;
  }
  .card-icon {
    width: 42px;
    height: 42px;
    font-size: 1.5rem;
  }
}
</style>
