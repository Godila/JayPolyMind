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
      <!-- Chart 1: Agent activity stacked by platform -->
      <div class="chart-card">
        <div class="chart-label">Активность агентов по платформам</div>
        <canvas ref="activityChart"></canvas>
      </div>

      <!-- Chart 2: Action types donut -->
      <div class="chart-card">
        <div class="chart-label">Типы действий</div>
        <canvas ref="typesChart"></canvas>
      </div>

      <!-- Chart 3: Activity per round -->
      <div class="chart-card">
        <div class="chart-label">Активность по раундам</div>
        <canvas ref="platformChart"></canvas>
      </div>

      <!-- Chart 4: Per-agent action type breakdown -->
      <div class="chart-card">
        <div class="chart-label">Состав действий по агентам</div>
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

const ACTION_LABELS = {
  CREATE_POST: 'Публикация',
  LIKE_POST: 'Лайк',
  REPOST: 'Репост',
  FOLLOW: 'Подписка',
  DO_NOTHING: 'Пропуск',
  QUOTE_POST: 'Цитата',
  CREATE_COMMENT: 'Комментарий',
  DISLIKE_POST: 'Дизлайк',
  SEARCH_POSTS: 'Поиск',
  UPVOTE_POST: 'Голос+',
  DOWNVOTE_POST: 'Голос-',
  MUTE_USER: 'Мут',
  REFRESH_FEED: 'Обновление',
  TREND_TOPICS: 'Тренды',
}

const buildCharts = (data) => {
  const rounds = data.rounds || []
  const roundLabels = rounds.map(r => `Р${r.round_num + 1}`)
  const agents = data.agent_actions || {}
  const agentNames = Object.keys(agents)
  const PALETTE = ['#1a1a1a','#6366f1','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6','#2dd4bf','#f97316','#64748b']

  // Chart 1 — Horizontal bar: top agents by total activity
  const c1 = new Chart(activityChart.value, {
    type: 'bar',
    data: {
      labels: agentNames.length ? agentNames : ['Нет данных'],
      datasets: [
        {
          label: 'Новостная лента',
          data: agentNames.map(n => agents[n].twitter || 0),
          backgroundColor: 'rgba(26,26,26,0.8)',
          borderRadius: 3
        },
        {
          label: 'Сообщество',
          data: agentNames.map(n => agents[n].reddit || 0),
          backgroundColor: 'rgba(99,102,241,0.75)',
          borderRadius: 3
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 10 } } },
      scales: {
        x: { stacked: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } }, beginAtZero: true },
        y: { stacked: true, grid: { display: false }, ticks: { font: { size: 9 } } }
      }
    }
  })
  chartInstances.push(c1)

  // Chart 2 — Donut: action type distribution
  const types = data.action_types || {}
  const typeKeys = Object.keys(types).filter(k => types[k] > 0)
  const c2 = new Chart(typesChart.value, {
    type: 'doughnut',
    data: {
      labels: typeKeys.map(k => ACTION_LABELS[k] || k),
      datasets: [{
        data: typeKeys.map(k => types[k]),
        backgroundColor: typeKeys.map((_, i) => PALETTE[i % PALETTE.length]),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '60%',
      plugins: {
        legend: { position: 'right', labels: { font: { size: 10 }, boxWidth: 10, padding: 8 } }
      }
    }
  })
  chartInstances.push(c2)

  // Chart 3 — Stacked bar: activity dynamics per round (twitter + reddit)
  const c3 = new Chart(platformChart.value, {
    type: 'bar',
    data: {
      labels: roundLabels.length ? roundLabels : ['Р1'],
      datasets: [
        {
          label: 'Новостная лента',
          data: rounds.length ? rounds.map(r => r.twitter_actions) : [data.platform_totals?.twitter || 0],
          backgroundColor: 'rgba(26,26,26,0.8)',
          borderRadius: 3
        },
        {
          label: 'Сообщество',
          data: rounds.length ? rounds.map(r => r.reddit_actions) : [data.platform_totals?.reddit || 0],
          backgroundColor: 'rgba(99,102,241,0.75)',
          borderRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 10 } } },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { stacked: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } }, beginAtZero: true }
      }
    }
  })
  chartInstances.push(c3)

  // Chart 4 — Grouped bar: per-agent action type breakdown (top-5 agents)
  const top5 = agentNames.slice(0, 5)
  const allTypes = [...new Set(top5.flatMap(n => Object.keys(agents[n]?.types || {})))]
  const c4 = new Chart(intensityChart.value, {
    type: 'bar',
    data: {
      labels: top5.length ? top5 : ['Нет данных'],
      datasets: allTypes.map((t, i) => ({
        label: ACTION_LABELS[t] || t,
        data: top5.map(n => agents[n]?.types?.[t] || 0),
        backgroundColor: PALETTE[i % PALETTE.length],
        borderRadius: 2
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 10 } } },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { font: { size: 9 } } },
        y: { stacked: true, grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 9 } }, beginAtZero: true }
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
