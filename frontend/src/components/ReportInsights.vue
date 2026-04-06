<template>
  <div class="insights-section">
    <div class="insights-header">
      <span class="insights-title">Аналитика вердикта</span>
      <span class="insights-sub" v-if="metricsData">На основе LLM-анализа отчёта</span>
    </div>

    <div v-if="loading" class="insights-loading">
      <div class="loading-dots"><span></span><span></span><span></span></div>
      <span>Загрузка аналитики...</span>
    </div>

    <template v-else-if="metricsData">
      <div class="charts-grid">
        <!-- Chart 1: Actor positions (diverging bar) -->
        <div class="chart-card">
          <div class="chart-label">Позиции акторов</div>
          <canvas ref="positionsChart"></canvas>
        </div>

        <!-- Chart 2: Outcome probabilities (donut) -->
        <div class="chart-card">
          <div class="chart-label">Вероятность исходов</div>
          <canvas ref="outcomesChart"></canvas>
        </div>

        <!-- Chart 3: Key themes (horizontal bar) -->
        <div class="chart-card">
          <div class="chart-label">Ключевые темы</div>
          <canvas ref="themesChart"></canvas>
        </div>

        <!-- Chart 4: Agent activity from simulation -->
        <div class="chart-card">
          <div class="chart-label">Активность акторов в симуляции</div>
          <canvas ref="activityChart"></canvas>
        </div>
      </div>
    </template>

    <template v-else-if="fallbackOnly">
      <!-- Only simulation data available — no LLM metrics -->
      <div class="fallback-notice">Детальный анализ недоступен для этой симуляции</div>
      <div class="charts-grid charts-grid--single">
        <div class="chart-card">
          <div class="chart-label">Активность акторов в симуляции</div>
          <canvas ref="activityChart"></canvas>
        </div>
      </div>
    </template>

    <div v-else-if="error" class="insights-error">
      Не удалось загрузить аналитику
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Chart,
  LineController, BarController, DoughnutController,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend
} from 'chart.js'
import { getReportMetrics } from '../api/report'
import { getSimulationAnalytics } from '../api/simulation'

Chart.register(
  LineController, BarController, DoughnutController,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend
)

const props = defineProps({
  reportId: { type: String, required: true },
  simulationId: { type: String, required: true },
  reportComplete: { type: Boolean, default: false }
})

const loading = ref(true)
const error = ref(false)
const metricsData = ref(null)
const fallbackOnly = ref(false)

const positionsChart = ref(null)
const outcomesChart = ref(null)
const themesChart = ref(null)
const activityChart = ref(null)

const chartInstances = []

const sentimentColor = (s) => ({
  positive: 'rgba(16,185,129,0.8)',
  negative: 'rgba(239,68,68,0.75)',
  neutral: 'rgba(156,163,175,0.7)'
})[s] || 'rgba(156,163,175,0.7)'

const stanceColor = (v) => {
  if (v > 2) return 'rgba(16,185,129,0.8)'
  if (v < -2) return 'rgba(239,68,68,0.75)'
  return 'rgba(156,163,175,0.7)'
}

const DONUT_PALETTE = ['#1a1a1a','#6366f1','#0ea5e9','#10b981','#f59e0b','#ef4444']

const buildMetricsCharts = (metrics, agentData) => {
  // Chart 1 — Actor positions (diverging horizontal bar)
  const actors = metrics.actor_positions || []
  if (positionsChart.value && actors.length) {
    const c1 = new Chart(positionsChart.value, {
      type: 'bar',
      data: {
        labels: actors.map(a => a.name),
        datasets: [{
          label: 'Позиция',
          data: actors.map(a => a.stance),
          backgroundColor: actors.map(a => stanceColor(a.stance)),
          borderRadius: 4,
          barThickness: 18
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const actor = actors[ctx.dataIndex]
                return ` ${actor.label}  (${ctx.raw > 0 ? '+' : ''}${ctx.raw})`
              }
            }
          }
        },
        scales: {
          x: {
            min: -10, max: 10,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { font: { size: 9 }, callback: (v) => v === 0 ? '0' : (v > 0 ? `+${v}` : v) }
          },
          y: { grid: { display: false }, ticks: { font: { size: 9 } } }
        }
      }
    })
    chartInstances.push(c1)
  }

  // Chart 2 — Outcome probabilities (donut)
  const scenarios = metrics.outcome_scenarios || []
  if (outcomesChart.value && scenarios.length) {
    const c2 = new Chart(outcomesChart.value, {
      type: 'doughnut',
      data: {
        labels: scenarios.map(s => s.name),
        datasets: [{
          data: scenarios.map(s => s.probability),
          backgroundColor: DONUT_PALETTE.slice(0, scenarios.length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '60%',
        plugins: {
          legend: { position: 'right', labels: { font: { size: 9 }, boxWidth: 10, padding: 8 } },
          tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}%` } }
        }
      }
    })
    chartInstances.push(c2)
  }

  // Chart 3 — Key themes (horizontal bar, color by sentiment)
  const themes = metrics.key_themes || []
  if (themesChart.value && themes.length) {
    const c3 = new Chart(themesChart.value, {
      type: 'bar',
      data: {
        labels: themes.map(t => t.name),
        datasets: [{
          label: 'Интенсивность',
          data: themes.map(t => t.intensity),
          backgroundColor: themes.map(t => sentimentColor(t.sentiment)),
          borderRadius: 4,
          barThickness: 16
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { min: 0, max: 10, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 9 } }, beginAtZero: true },
          y: { grid: { display: false }, ticks: { font: { size: 9 } } }
        }
      }
    })
    chartInstances.push(c3)
  }

  // Chart 4 — Agent activity from simulation
  buildActivityChart(agentData)
}

const buildActivityChart = (agentData) => {
  if (!activityChart.value) return
  const agents = agentData ? Object.entries(agentData) : []
  const c4 = new Chart(activityChart.value, {
    type: 'bar',
    data: {
      labels: agents.length ? agents.map(([name]) => name) : ['Нет данных'],
      datasets: [
        {
          label: 'Новостная лента',
          data: agents.map(([, d]) => d.twitter || 0),
          backgroundColor: 'rgba(26,26,26,0.8)',
          borderRadius: 3
        },
        {
          label: 'Сообщество',
          data: agents.map(([, d]) => d.reddit || 0),
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
  chartInstances.push(c4)
}

const loadData = async () => {
  const [metricsRes, analyticsRes] = await Promise.allSettled([
    getReportMetrics(props.reportId),
    getSimulationAnalytics(props.simulationId)
  ])

  const metrics = metricsRes.status === 'fulfilled' && metricsRes.value?.success
    ? metricsRes.value.data : null
  const agentActions = analyticsRes.status === 'fulfilled' && analyticsRes.value?.success
    ? analyticsRes.value.data?.agent_actions : null

  return { metrics, agentActions }
}

const destroyCharts = () => {
  chartInstances.forEach(c => c.destroy())
  chartInstances.length = 0
}

onMounted(async () => {
  try {
    const { metrics, agentActions } = await loadData()
    if (metrics) {
      metricsData.value = metrics
      loading.value = false
      await nextTick()
      buildMetricsCharts(metrics, agentActions)
    } else if (agentActions) {
      fallbackOnly.value = true
      loading.value = false
      await nextTick()
      buildActivityChart(agentActions)
    } else {
      error.value = true
      loading.value = false
    }
  } catch (e) {
    error.value = true
    loading.value = false
  }
})

watch(() => props.reportComplete, async (complete) => {
  if (!complete || metricsData.value) return
  try {
    const { metrics, agentActions } = await loadData()
    if (!metrics) return
    destroyCharts()
    metricsData.value = metrics
    fallbackOnly.value = false
    error.value = false
    await nextTick()
    buildMetricsCharts(metrics, agentActions)
  } catch (e) {
    // silent — fallback already shown
  }
})

onUnmounted(() => {
  destroyCharts()
})
</script>

<style scoped>
.insights-section {
  margin: 0 0 32px 0;
  padding: 28px 32px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.insights-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.insights-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #111;
}

.insights-sub {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 400;
}

.insights-loading,
.insights-error {
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

.charts-grid--single {
  grid-template-columns: 1fr;
  max-width: 500px;
}

.fallback-notice {
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 16px;
  font-style: italic;
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
  max-height: 220px;
}

@media (max-width: 700px) {
  .charts-grid { grid-template-columns: 1fr; }
  .insights-section { padding: 20px 16px; }
}
</style>
