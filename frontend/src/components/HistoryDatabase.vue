<template>
  <div class="history-database">
    <!-- Title -->
    <div class="section-header">
      <div class="section-line"></div>
      <span class="section-title">История симуляций</span>
      <div class="section-line"></div>
    </div>

    <!-- Toolbar -->
    <div v-if="projects.length > 0" class="toolbar">
      <div class="toolbar-left">
        <label class="checkbox-label">
          <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
          <span>Выбрать все</span>
        </label>
        <select v-model="sortBy" class="sort-select">
          <option value="date">По дате</option>
          <option value="status">По статусу</option>
          <option value="name">По названию</option>
        </select>
      </div>
      <div class="toolbar-right">
        <button
          v-if="hasProjectId"
          class="btn btn-danger-outline"
          @click="confirmDeleteProject"
        >Удалить проект</button>
      </div>
    </div>

    <!-- Table -->
    <div v-if="projects.length > 0" class="sim-table">
      <div class="sim-table-header">
        <div class="col-check"></div>
        <div class="col-name">Название</div>
        <div class="col-status">Статус</div>
        <div class="col-date">Дата</div>
        <div class="col-rounds">Раунды</div>
        <div class="col-stages">Этапы</div>
        <div class="col-actions">Действия</div>
      </div>
      <div
        v-for="(project, index) in sortedProjects"
        :key="project.simulation_id"
        class="sim-table-row"
        :class="{ selected: selectedIds.has(project.simulation_id) }"
        @click="navigateToProject(project)"
      >
        <div class="col-check" @click.stop>
          <input
            type="checkbox"
            :checked="selectedIds.has(project.simulation_id)"
            @change="toggleSelect(project.simulation_id)"
          />
        </div>
        <div class="col-name">
          <span class="sim-id">{{ formatSimulationId(project.simulation_id) }}</span>
          <span class="sim-title">{{ truncateText(project.simulation_requirement, 60) || 'Без названия' }}</span>
        </div>
        <div class="col-status">
          <span class="status-dot" :class="getStatusClass(project)"></span>
          <span class="status-text">{{ getStatusLabel(project) }}</span>
        </div>
        <div class="col-date">
          <span class="date-main">{{ formatDate(project.created_at) }}</span>
          <span class="date-time">{{ formatTime(project.created_at) }}</span>
        </div>
        <div class="col-rounds">
          <span class="rounds-text">{{ project.current_round || 0 }}/{{ project.total_rounds || 0 }}</span>
          <div class="rounds-bar">
            <div class="rounds-fill" :style="{ width: getRoundsPercent(project) + '%' }"></div>
          </div>
        </div>
        <div class="col-stages">
          <span class="stage-icon" :class="{ done: project.project_id }" title="Граф">&#9671;</span>
          <span class="stage-icon" :class="{ done: project.status !== 'created' }" title="Среда">&#9672;</span>
          <span class="stage-icon" :class="{ done: project.report_id }" title="Отчёт">&#9670;</span>
        </div>
        <div class="col-actions" @click.stop>
          <button class="action-btn" title="Открыть" @click="navigateToProject(project)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
          <button class="action-btn delete" title="Удалить" @click="confirmDeleteOne(project)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!loading" class="empty-state">
      <span class="empty-icon">&#9671;</span>
      <span class="empty-title">Нет симуляций</span>
      <span class="empty-desc">Создайте новый сценарий выше</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <span class="loading-dot"></span>
      <span>Загрузка...</span>
    </div>

    <!-- Bulk action bar -->
    <Transition name="slide-up">
      <div v-if="selectedIds.size > 0" class="bulk-bar">
        <span class="bulk-count">Выбрано: {{ selectedIds.size }}</span>
        <button class="btn btn-link" @click="clearSelection">Снять выделение</button>
        <button class="btn btn-danger" @click="confirmDeleteBulk">
          Удалить ({{ selectedIds.size }})
        </button>
      </div>
    </Transition>

    <!-- Delete confirmation modal -->
    <Transition name="fade">
      <div v-if="deleteModal.visible" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-box">
          <h3 class="modal-title">{{ deleteModal.title }}</h3>
          <p v-if="deleteModal.subtitle" class="modal-subtitle">{{ deleteModal.subtitle }}</p>
          <div class="modal-body">
            <p>Будет удалено:</p>
            <ul>
              <li v-for="item in deleteModal.items" :key="item">{{ item }}</li>
            </ul>
            <p class="modal-warning">Это действие необратимо.</p>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeDeleteModal">Отмена</button>
            <button class="btn btn-danger" :disabled="deleteModal.loading" @click="executeDelete">
              {{ deleteModal.loading ? 'Удаление...' : deleteModal.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import { getSimulationHistory, deleteSimulation, bulkDeleteSimulations, deleteProjectFull } from '../api/simulation'

const router = useRouter()
const emit = defineEmits(['refresh'])

const projects = ref([])
const loading = ref(false)
const selectedIds = ref(new Set())
const sortBy = ref('date')

// Delete modal state
const deleteModal = ref({
  visible: false,
  title: '',
  subtitle: '',
  items: [],
  confirmText: '',
  loading: false,
  action: null
})

// Computed
const allSelected = computed(() =>
  projects.value.length > 0 && selectedIds.value.size === projects.value.length
)

const hasProjectId = computed(() =>
  projects.value.some(p => p.project_id)
)

const sortedProjects = computed(() => {
  const list = [...projects.value]
  switch (sortBy.value) {
    case 'status':
      return list.sort((a, b) => getStatusOrder(a) - getStatusOrder(b))
    case 'name':
      return list.sort((a, b) => (a.simulation_requirement || '').localeCompare(b.simulation_requirement || ''))
    default:
      return list // already sorted by date from backend
  }
})

// Selection
const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(projects.value.map(p => p.simulation_id))
  }
}

const toggleSelect = (id) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

// Status helpers
const getStatusClass = (sim) => {
  const status = sim.runner_status || 'idle'
  if (status === 'completed') return 'status-complete'
  if (status === 'running' || status === 'starting') return 'status-running'
  if (status === 'failed') return 'status-error'
  return 'status-idle'
}

const getStatusLabel = (sim) => {
  const status = sim.runner_status || 'idle'
  if (status === 'completed') return 'Завершена'
  if (status === 'running' || status === 'starting') return 'В процессе'
  if (status === 'failed') return 'Ошибка'
  return 'Не запущена'
}

const getStatusOrder = (sim) => {
  const status = sim.runner_status || 'idle'
  if (status === 'running' || status === 'starting') return 0
  if (status === 'failed') return 1
  if (status === 'completed') return 2
  return 3
}

const getRoundsPercent = (sim) => {
  const current = sim.current_round || 0
  const total = sim.total_rounds || 0
  if (total === 0) return 0
  return Math.min(100, Math.round((current / total) * 100))
}

// Formatting
const formatSimulationId = (id) => {
  if (!id) return 'SIM_???'
  return 'SIM_' + id.replace('sim_', '').substring(0, 6).toUpperCase()
}

const truncateText = (text, maxLen) => {
  if (!text) return ''
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch { return dateStr.substring(0, 10) }
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

// Navigation
const navigateToProject = (project) => {
  router.push({ name: 'Simulation', params: { simulationId: project.simulation_id } })
}

// Delete actions
const confirmDeleteOne = (project) => {
  deleteModal.value = {
    visible: true,
    title: 'Удалить симуляцию?',
    subtitle: truncateText(project.simulation_requirement, 80) || formatSimulationId(project.simulation_id),
    items: ['Данные симуляции (конфиг, логи, БД)', 'Связанный отчёт (если есть)'],
    confirmText: 'Удалить',
    loading: false,
    action: async () => {
      await deleteSimulation(project.simulation_id)
    }
  }
}

const confirmDeleteBulk = () => {
  const count = selectedIds.value.size
  deleteModal.value = {
    visible: true,
    title: `Удалить ${count} симуляций?`,
    subtitle: '',
    items: [`${count} симуляций (конфиги, логи, БД)`, 'Связанные отчёты (если есть)'],
    confirmText: `Удалить (${count})`,
    loading: false,
    action: async () => {
      await bulkDeleteSimulations([...selectedIds.value])
      selectedIds.value = new Set()
    }
  }
}

const confirmDeleteProject = () => {
  const projectId = projects.value.find(p => p.project_id)?.project_id
  if (!projectId) return
  const simCount = projects.value.filter(p => p.project_id === projectId).length
  const reportCount = projects.value.filter(p => p.project_id === projectId && p.report_id).length
  deleteModal.value = {
    visible: true,
    title: 'Удалить проект полностью?',
    subtitle: '',
    items: [
      'Проект и загруженные файлы',
      `Все симуляции (${simCount} шт.)`,
      `Все отчёты (${reportCount} шт.)`,
      'Граф знаний из Neo4j'
    ],
    confirmText: 'Удалить проект',
    loading: false,
    action: async () => {
      await deleteProjectFull(projectId)
    }
  }
}

const executeDelete = async () => {
  if (!deleteModal.value.action) return
  deleteModal.value.loading = true
  try {
    await deleteModal.value.action()
    closeDeleteModal()
    await loadHistory()
    emit('refresh')
  } catch (error) {
    console.error('Delete failed:', error)
    deleteModal.value.loading = false
  }
}

const closeDeleteModal = () => {
  deleteModal.value.visible = false
}

// Load data
const loadHistory = async () => {
  try {
    loading.value = true
    const response = await getSimulationHistory(50)
    if (response.success) {
      projects.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load history:', error)
    projects.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-database {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px 80px;
  font-family: 'JetBrains Mono', monospace;
}

/* Section header */
.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.section-line {
  flex: 1;
  height: 1px;
  background: #E0E0E0;
}
.section-title {
  font-size: 11px;
  letter-spacing: 4px;
  color: #9E9E9E;
  text-transform: uppercase;
  white-space: nowrap;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  margin-bottom: 2px;
  background: #FAFAFA;
  border: 1px solid #E0E0E0;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #616161;
  cursor: pointer;
}
.checkbox-label input {
  cursor: pointer;
}
.sort-select {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  padding: 4px 8px;
  border: 1px solid #E0E0E0;
  background: #fff;
  color: #424242;
  cursor: pointer;
}

/* Table */
.sim-table {
  border: 1px solid #E0E0E0;
  background: #fff;
}
.sim-table-header {
  display: grid;
  grid-template-columns: 36px 1fr 120px 110px 100px 80px 80px;
  align-items: center;
  padding: 8px 12px;
  background: #F5F5F5;
  border-bottom: 1px solid #E0E0E0;
  font-size: 10px;
  letter-spacing: 1px;
  color: #9E9E9E;
  text-transform: uppercase;
}
.sim-table-row {
  display: grid;
  grid-template-columns: 36px 1fr 120px 110px 100px 80px 80px;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #F5F5F5;
  cursor: pointer;
  transition: background 0.15s, border-left 0.15s;
  border-left: 3px solid transparent;
}
.sim-table-row:hover {
  background: #FAFAFA;
  border-left-color: #FF5722;
}
.sim-table-row.selected {
  background: #FFF3E0;
}

/* Column: name */
.col-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}
.sim-id {
  font-size: 9px;
  color: #BDBDBD;
  letter-spacing: 1px;
}
.sim-title {
  font-size: 12px;
  color: #212121;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Column: status */
.col-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #616161;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.status-complete { background: #4CAF50; }
.status-dot.status-running { background: #FF9800; }
.status-dot.status-error { background: #F44336; }
.status-dot.status-idle { background: #9E9E9E; }

/* Column: date */
.col-date {
  display: flex;
  flex-direction: column;
  font-size: 11px;
  color: #757575;
}
.date-time {
  font-size: 10px;
  color: #BDBDBD;
}

/* Column: rounds */
.col-rounds {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.rounds-text {
  font-size: 11px;
  color: #424242;
}
.rounds-bar {
  width: 100%;
  height: 3px;
  background: #EEEEEE;
}
.rounds-fill {
  height: 100%;
  background: #FF5722;
  transition: width 0.3s;
}

/* Column: stages */
.col-stages {
  display: flex;
  gap: 4px;
  font-size: 14px;
}
.stage-icon {
  color: #E0E0E0;
}
.stage-icon.done {
  color: #FF5722;
}

/* Column: actions */
.col-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
}
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid #E0E0E0;
  background: #fff;
  color: #757575;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover {
  background: #F5F5F5;
  color: #212121;
  border-color: #BDBDBD;
}
.action-btn.delete:hover {
  background: #FFEBEE;
  color: #F44336;
  border-color: #F44336;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 60px 20px;
  color: #BDBDBD;
}
.empty-icon {
  font-size: 32px;
}
.empty-title {
  font-size: 14px;
  color: #9E9E9E;
}
.empty-desc {
  font-size: 11px;
}

/* Loading */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  font-size: 12px;
  color: #9E9E9E;
}
.loading-dot {
  width: 6px;
  height: 6px;
  background: #FF5722;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Bulk action bar */
.bulk-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px 24px;
  background: #212121;
  color: #fff;
  font-size: 12px;
  z-index: 100;
}
.bulk-count {
  color: #BDBDBD;
}

/* Buttons */
.btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  padding: 6px 14px;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  letter-spacing: 0.5px;
}
.btn-danger {
  background: #F44336;
  color: #fff;
}
.btn-danger:hover {
  background: #D32F2F;
}
.btn-danger:disabled {
  background: #BDBDBD;
  cursor: not-allowed;
}
.btn-danger-outline {
  background: transparent;
  color: #F44336;
  border: 1px solid #F44336;
}
.btn-danger-outline:hover {
  background: #FFEBEE;
}
.btn-secondary {
  background: #F5F5F5;
  color: #424242;
  border: 1px solid #E0E0E0;
}
.btn-secondary:hover {
  background: #EEEEEE;
}
.btn-link {
  background: none;
  color: #BDBDBD;
  text-decoration: underline;
  padding: 6px 8px;
}
.btn-link:hover {
  color: #fff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal-box {
  background: #fff;
  border: 1px solid #E0E0E0;
  width: 420px;
  max-width: 90vw;
  padding: 24px;
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px;
}
.modal-subtitle {
  font-size: 12px;
  color: #757575;
  margin: 0 0 16px;
  word-break: break-word;
}
.modal-body {
  font-size: 12px;
  color: #424242;
  margin-bottom: 20px;
}
.modal-body p {
  margin: 0 0 8px;
}
.modal-body ul {
  margin: 0;
  padding-left: 18px;
}
.modal-body li {
  margin-bottom: 4px;
}
.modal-warning {
  color: #F44336;
  font-weight: 500;
  margin-top: 12px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.25s ease, opacity 0.25s;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
