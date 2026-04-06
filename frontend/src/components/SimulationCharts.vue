<template>
  <div class="charts-section">
    <div class="charts-header">
      <span class="charts-title">Аналитика симуляции</span>
      <span class="charts-sub">Данные по {{ analyticsData?.completed_rounds || 0 }} раундам</span>
    </div>

    <div v-if="loading" class="charts-loading">
      <div class="loading-dots"><span></span><span></span><span></span></div>
      <span>Загрузка данных...</span>
    </div>

    <div v-else-if="error" class="charts-error">
      Не удалось загрузить данные аналитики
    </div>

    <div v-else-if="analyticsData" class="charts-grid">
      <!-- Chart 1: Activity by round -->
      <div class="chart-card">
        <div class="chart-label">Динамика активности по раундам</div>
        <canvas ref="activityChart"></canvas>
      </div>

      <!-- Chart 2: Action types donut -->
      <div class="chart-card">
        <div class="chart-label">Типы действий</div>
        <canvas ref="typesChart"></canvas>
      </div>

      <!-- Chart 3: Platform comparison bar -->
      <div class="chart-card">
        <div class="chart-label">Сравнение платформ</div>
        <canvas ref="platformChart"></canvas>
      </div>

      <!-- Chart 4: Stacked intensity per round -->
      <div class="chart-card">
        <div class="chart-label">Интенсивность по раундам</div>
        <canvas ref="intensityChart"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Chart,
  LineController, BarController, DoughnutController,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend
} from 'chart.js'
import { getSimulationAnalytics } from '../api/simulation'

Chart.register(
  LineController, BarController, DoughnutController,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend
)

const props = defineProps({
  simulationId: { type: String, required: true }
})

const loading = ref(true)
const error = ref(false)
const analyticsData = ref(null)

const activityChart = ref(null)
const typesChart = ref(null)
const platformChart = ref(null)
const intensityChart = ref(null)

const chartInstances = []

const ACTION_COLORS = {
  CREATE_POST:    '#1a1a1a',
  LIKE_POST:      '#6366f1',
  REPOST:         '#0ea5e9',
  FOLLOW:         '#10b981',
  DO_NOTHING:     '#d1d5db',
  QUOTE_POST:     '#f59e0b',
  CREATE_COMMENT: '#8b5cf6',
  DISLIKE_POST:   '#ef4444',
  SEARCH_POSTS:   '#64748b',
  UPVOTE_POST:    '#22c55e',
  DOWNVOTE_POST:  '#f97316',
  MUTE_USER:      '#94a3b8',
  REFRESH_FEED:   '#a78bfa',
  TREND_TOPICS:   '#2dd4bf',
}

const getColor = (key) => ACTION_COLORS[key] || '#9ca3af'

const buildCharts = (data) => {
  const rounds = data.rounds || []
  const labels = rounds.map(r => `R${r.round_num}`)

  // Chart 1 — Area: twitter + reddit activity per round
  const c1 = new Chart(activityChart.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Новостная лента',
          data: rounds.map(r => r.twitter_actions),
          borderColor: '#1a1a1a',
          backgroundColor: 'rgba(26,26,26,0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
        },
        {
          label: 'Сообщество',
          data: rounds.map(r => r.reddit_actions),
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 12 } } },
      scales: {
        x: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 10 } } },
        y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 10 } }, beginAtZero: true }
      }
    }
  })
  chartInstances.push(c1)

  // Chart 2 — Donut: action types
  const types = data.action_types || {}
  const typeKeys = Object.keys(types).filter(k => types[k] > 0)
  const c2 = new Chart(typesChart.value, {
    type: 'doughnut',
    data: {
      labels: typeKeys,
      datasets: [{
        data: typeKeys.map(k => types[k]),
        backgroundColor: typeKeys.map(k => getColor(k)),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '62%',
      plugins: {
        legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 10, padding: 8 } }
      }
    }
  })
  chartInstances.push(c2)

  // Chart 3 — Grouped bar: platform totals + avg per round
  const pt = data.platform_totals || {}
  const avg = data.avg_actions_per_round || {}
  const c3 = new Chart(platformChart.value, {
    type: 'bar',
    data: {
      labels: ['Новостная лента', 'Сообщество'],
      datasets: [
        {
          label: 'Всего действий',
          data: [pt.twitter || 0, pt.reddit || 0],
          backgroundColor: ['rgba(26,26,26,0.85)', 'rgba(99,102,241,0.85)'],
          borderRadius: 4
        },
        {
          label: 'Среднее за раунд',
          data: [avg.twitter || 0, avg.reddit || 0],
          backgroundColor: ['rgba(26,26,26,0.25)', 'rgba(99,102,241,0.25)'],
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 12 } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 10 } }, beginAtZero: true }
      }
    }
  })
  chartInstances.push(c3)

  // Chart 4 — Stacked bar: total actions per round (twitter + reddit stacked)
  const c4 = new Chart(intensityChart.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Новостная лента',
          data: rounds.map(r => r.twitter_actions),
          backgroundColor: 'rgba(26,26,26,0.8)',
          borderRadius: 2
        },
        {
          label: 'Сообщество',
          data: rounds.map(r => r.reddit_actions),
          backgroundColor: 'rgba(99,102,241,0.7)',
          borderRadius: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 12 } } },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { stacked: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 10 } }, beginAtZero: true }
      }
    }
  })
  chartInstances.push(c4)
}

onMounted(async () => {
  try {
    const res = await getSimulationAnalytics(props.simulationId)
    if (res.success && res.data) {
      analyticsData.value = res.data
      loading.value = false       // Must be before buildCharts so v-else-if renders canvases
      await nextTick()            // Wait for DOM to update with canvas elements
      buildCharts(res.data)
    } else {
      error.value = true
      loading.value = false
    }
  } catch {
    error.value = true
    loading.value = false
  }
})

onUnmounted(() => {
  chartInstances.forEach(c => c.destroy())
})
</script>

<style scoped>
.charts-section {
  margin: 0 0 32px 0;
  padding: 28px 32px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.charts-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.charts-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #111;
}

.charts-sub {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 400;
}

.charts-loading,
.charts-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 80px;
  color: #9ca3af;
  font-size: 13px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #9ca3af;
  border-radius: 50%;
  animation: dot-bounce 1.2s infinite ease-in-out both;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px 18px;
}

.chart-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #6b7280;
  margin-bottom: 14px;
}

canvas {
  max-height: 200px;
}

@media (max-width: 700px) {
  .charts-grid { grid-template-columns: 1fr; }
  .charts-section { padding: 20px 16px; }
}
</style>
