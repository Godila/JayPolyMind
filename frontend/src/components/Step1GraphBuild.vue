<template>
  <div class="workbench-panel">
    <div class="scroll-container">
      <!-- Step 01: Ontology -->
      <div class="step-card" :class="{ 'active': currentPhase === 0, 'completed': currentPhase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">Генерация онтологии</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 0" class="badge success">Завершено</span>
            <span v-else-if="currentPhase === 0" class="badge processing">Генерация</span>
            <span v-else class="badge pending">Ожидание</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/graph/ontology/generate</p>
          <p class="description">
            LLM анализирует содержимое документа и требования к симуляции, извлекает смысловые зёрна и автоматически генерирует структуры онтологии
          </p>

          <!-- Loading / Progress -->
          <div v-if="currentPhase === 0 && ontologyProgress" class="progress-section">
            <div class="spinner-sm"></div>
            <span>{{ ontologyProgress.message || 'Анализ документов...' }}</span>
          </div>

          <!-- Detail Overlay -->
          <div v-if="selectedOntologyItem" class="ontology-detail-overlay">
            <div class="detail-header">
               <div class="detail-title-group">
                  <span class="detail-type-badge">{{ selectedOntologyItem.itemType === 'entity' ? 'СУЩНОСТЬ' : 'СВЯЗЬ' }}</span>
                  <span class="detail-name">{{ selectedOntologyItem.name }}</span>
               </div>
               <button class="close-btn" @click="selectedOntologyItem = null">×</button>
            </div>
            <div class="detail-body">
               <div class="detail-desc">{{ selectedOntologyItem.description }}</div>
               
               <!-- Attributes -->
               <div class="detail-section" v-if="selectedOntologyItem.attributes?.length">
                  <span class="section-label">АТРИБУТЫ</span>
                  <div class="attr-list">
                     <div v-for="attr in selectedOntologyItem.attributes" :key="attr.name" class="attr-item">
                        <span class="attr-name">{{ attr.name }}</span>
                        <span class="attr-type">({{ attr.type }})</span>
                        <span class="attr-desc">{{ attr.description }}</span>
                     </div>
                  </div>
               </div>

               <!-- Examples (Entity) -->
               <div class="detail-section" v-if="selectedOntologyItem.examples?.length">
                  <span class="section-label">ПРИМЕРЫ</span>
                  <div class="example-list">
                     <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="example-tag">{{ ex }}</span>
                  </div>
               </div>

               <!-- Source/Target (Relation) -->
               <div class="detail-section" v-if="selectedOntologyItem.source_targets?.length">
                  <span class="section-label">СВЯЗИ</span>
                  <div class="conn-list">
                     <div v-for="(conn, idx) in selectedOntologyItem.source_targets" :key="idx" class="conn-item">
                        <span class="conn-node">{{ conn.source }}</span>
                        <span class="conn-arrow">→</span>
                        <span class="conn-node">{{ conn.target }}</span>
                     </div>
                  </div>
               </div>
            </div>
          </div>

          <!-- Generated Entity Tags -->
          <div v-if="projectData?.ontology?.entity_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">ТИПЫ СУЩНОСТЕЙ</span>
            <div class="tags-list">
              <span 
                v-for="entity in projectData.ontology.entity_types" 
                :key="entity.name" 
                class="entity-tag clickable"
                @click="selectOntologyItem(entity, 'entity')"
              >
                {{ entity.name }}
              </span>
            </div>
          </div>

          <!-- Deep Research v2 Card -->
          <div v-if="researchState !== 'idle'" class="research-card" :class="'research-' + researchState">

            <!-- Running state -->
            <div v-if="researchState === 'running'" class="research-running">
              <div class="research-header">
                <span class="research-icon">
                  <span class="spinner-sm"></span>
                </span>
                <span class="research-title">Deep Research</span>
                <span class="research-badge running">Searching...</span>
              </div>
              <p class="research-desc">Поиск в интернете. Обычно занимает 60-90 секунд.</p>
            </div>

            <!-- Review state -->
            <div v-else-if="researchState === 'review'" class="research-review">
              <div class="research-header">
                <span class="research-title">Deep Research</span>
                <span class="research-badge review">{{ enabledCount }}/{{ researchFindings.length }} selected</span>
              </div>
              <p class="research-desc">Отключите нерелевантные факты перед подтверждением.</p>
              <div class="confidence-legend">
                <span class="legend-item"><span class="legend-dot confirmed"></span>Подтверждено</span>
                <span class="legend-item"><span class="legend-dot unverified"></span>Не проверено</span>
                <span class="legend-item"><span class="legend-dot contradicted"></span>Противоречие</span>
              </div>
              <div class="findings-list">
                <div
                  v-for="finding in researchFindings"
                  :key="finding.id"
                  class="finding-item"
                  :class="{ disabled: !finding.enabled }"
                >
                  <div class="finding-left" :class="'confidence-' + finding.confidence"></div>
                  <div class="finding-body">
                    <div class="finding-top-row">
                      <span class="finding-confidence-tag" :class="'tag-' + finding.confidence">
                        {{ {confirmed: 'Подтверждено', unverified: 'Не проверено', contradicted: 'Противоречие'}[finding.confidence] || finding.confidence }}
                      </span>
                    </div>
                    <span class="finding-fact">{{ finding.fact }}</span>
                    <span class="finding-source">{{ finding.source_title || finding.source_url }}</span>
                  </div>
                  <button class="finding-toggle" @click="emit('research-toggle', finding.id)">
                    {{ finding.enabled ? 'ON' : 'OFF' }}
                  </button>
                </div>
              </div>
              <div class="research-actions">
                <button class="action-btn research-confirm-btn" @click="emit('research-confirm')">
                  Подтвердить {{ enabledCount }} {{ enabledCount === 1 ? 'факт' : 'фактов' }}
                </button>
                <button class="research-skip-link" @click="emit('research-skip')">
                  Пропустить
                </button>
              </div>
            </div>

            <!-- Confirmed state -->
            <div v-else-if="researchState === 'confirmed'" class="research-done">
              <div class="research-header">
                <span class="research-title">Deep Research</span>
                <span class="research-badge confirmed">Confirmed</span>
              </div>
              <p class="research-desc">{{ enabledCount }} {{ enabledCount === 1 ? 'факт применён' : 'фактов применено' }} к генерации онтологии.</p>
            </div>

            <!-- Skipped state -->
            <div v-else-if="researchState === 'skipped'" class="research-done">
              <div class="research-header">
                <span class="research-title">Deep Research</span>
                <span class="research-badge skipped">Skipped</span>
              </div>
              <p class="research-desc">Онтология сгенерирована без веб-контекста.</p>
            </div>

            <!-- Error state -->
            <div v-else-if="researchState === 'error'" class="research-done">
              <div class="research-header">
                <span class="research-title">Deep Research</span>
                <span class="research-badge error">Error</span>
              </div>
              <p class="research-desc">Исследование не удалось. Онтология будет сгенерирована без веб-контекста.</p>
            </div>
          </div>

          <!-- Generated Relation Tags -->
          <div v-if="projectData?.ontology?.edge_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">ТИПЫ СВЯЗЕЙ</span>
            <div class="tags-list">
              <span 
                v-for="rel in projectData.ontology.edge_types" 
                :key="rel.name" 
                class="entity-tag clickable"
                @click="selectOntologyItem(rel, 'relation')"
              >
                {{ rel.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 02: Graph Build -->
      <div class="step-card" :class="{ 'active': currentPhase === 1, 'completed': currentPhase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">Построение GraphRAG</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 1" class="badge success">Завершено</span>
            <span v-else-if="currentPhase === 1" class="badge processing">{{ buildProgress?.progress || 0 }}%</span>
            <span v-else class="badge pending">Ожидание</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/graph/build</p>
          <p class="description">
            На основе сгенерированной онтологии автоматически разбивает документы на фрагменты и строит граф знаний Neo4j, извлекает сущности и связи
          </p>
          
          <!-- Stats Cards -->
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.nodes }}</span>
              <span class="stat-label">Узлы сущностей</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.edges }}</span>
              <span class="stat-label">Рёбра связей</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ graphStats.types }}</span>
              <span class="stat-label">Типы сущностей</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 03: Complete -->
      <div class="step-card" :class="{ 'active': currentPhase === 2, 'completed': currentPhase >= 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">Построение завершено</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase >= 2" class="badge accent">Активно</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/simulation/create</p>
          <p class="description">Граф построен. Перейдите к следующему шагу для настройки среды симуляции</p>
          <button
            class="action-btn"
            :disabled="currentPhase < 2 || creatingSimulation"
            @click="handleEnterEnvSetup"
          >
            <span v-if="creatingSimulation" class="spinner-sm"></span>
            {{ creatingSimulation ? 'Создание...' : 'Перейти к настройке среды ➝' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom Info / Logs -->
    <div class="system-logs" :class="{ 'logs-collapsed': logsCollapsed }">
      <div class="log-header" @click="logsCollapsed = !logsCollapsed">
        <span class="log-title">СИСТЕМНЫЙ ЖУРНАЛ</span>
        <span class="log-id">{{ projectData?.project_id || 'NO_PROJECT' }}</span>
        <button class="log-toggle" :title="logsCollapsed ? 'Развернуть' : 'Свернуть'">
          {{ logsCollapsed ? '▲' : '▼' }}
        </button>
      </div>
      <div class="log-content" ref="logContent" v-show="!logsCollapsed">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createSimulation } from '../api/simulation'

const router = useRouter()

const props = defineProps({
  currentPhase: { type: Number, default: 0 },
  projectData: Object,
  ontologyProgress: Object,
  buildProgress: Object,
  graphData: Object,
  systemLogs: { type: Array, default: () => [] },
  researchState: { type: String, default: 'idle' },
  researchFindings: { type: Array, default: () => [] },
})

const emit = defineEmits(['next-step', 'research-confirm', 'research-skip', 'research-toggle'])

const enabledCount = computed(() => props.researchFindings.filter(f => f.enabled).length)

const selectedOntologyItem = ref(null)
const logContent = ref(null)
const logsCollapsed = ref(localStorage.getItem('logsCollapsed') === 'true')
watch(logsCollapsed, val => localStorage.setItem('logsCollapsed', String(val)))
const creatingSimulation = ref(false)

// Enter environment setup - create simulation and navigate
const handleEnterEnvSetup = async () => {
  if (!props.projectData?.project_id || !props.projectData?.graph_id) {
    console.error('Missing project or graph information')
    return
  }
  
  creatingSimulation.value = true
  
  try {
    const res = await createSimulation({
      project_id: props.projectData.project_id,
      graph_id: props.projectData.graph_id,
      enable_twitter: true,
      enable_reddit: true
    })
    
    if (res.success && res.data?.simulation_id) {
      // Navigate to simulation page
      router.push({
        name: 'Simulation',
        params: { simulationId: res.data.simulation_id }
      })
    } else {
      console.error('Failed to create simulation:', res.error)
      alert('Failed to create simulation: ' + (res.error || 'Unknown error'))
    }
  } catch (err) {
    console.error('Simulation creation exception:', err)
    alert('Simulation creation exception: ' + err.message)
  } finally {
    creatingSimulation.value = false
  }
}

const selectOntologyItem = (item, type) => {
  selectedOntologyItem.value = { ...item, itemType: type }
}

const graphStats = computed(() => {
  const nodes = props.graphData?.node_count || props.graphData?.nodes?.length || 0
  const edges = props.graphData?.edge_count || props.graphData?.edges?.length || 0
  const types = props.projectData?.ontology?.entity_types?.length || 0
  return { nodes, edges, types }
})

const formatDate = (dateStr) => {
  if (!dateStr) return '--:--:--'
  const d = new Date(dateStr)
  return d.toLocaleTimeString('en-US', { hour12: false }) + '.' + d.getMilliseconds()
}

// Auto-scroll logs section
watch(() => props.systemLogs.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.workbench-panel {
  height: 100%;
  background-color: #FAFAFA;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-card {
  background: #FFF;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #EAEAEA;
  transition: all 0.3s ease;
  position: relative; /* For absolute overlay */
}

.step-card.active {
  border-color: #FF5722;
  box-shadow: 0 4px 12px rgba(255, 87, 34, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 700;
  color: #E0E0E0;
}

.step-card.active .step-num,
.step-card.completed .step-num {
  color: #000;
}

.step-title {
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.badge {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.success { background: #E8F5E9; color: #2E7D32; }
.badge.processing { background: #FF5722; color: #FFF; }
.badge.accent { background: #FF5722; color: #FFF; }
.badge.pending { background: #F5F5F5; color: #999; }

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #999;
  margin-bottom: 8px;
}

.description {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 16px;
}

/* Step 01 Tags */
.tags-container {
  margin-top: 12px;
  transition: opacity 0.3s;
}

.tags-container.dimmed {
    opacity: 0.3;
    pointer-events: none;
}

.tag-label {
  display: block;
  font-size: 10px;
  color: #AAA;
  margin-bottom: 8px;
  font-weight: 600;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.entity-tag {
  background: #F5F5F5;
  border: 1px solid #EEE;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  color: #333;
  font-family: 'JetBrains Mono', monospace;
  transition: all 0.2s;
}

.entity-tag.clickable {
    cursor: pointer;
}

.entity-tag.clickable:hover {
    background: #E0E0E0;
    border-color: #CCC;
}

/* Ontology Detail Overlay */
.ontology-detail-overlay {
    position: absolute;
    top: 60px; /* Below header roughly */
    left: 20px;
    right: 20px;
    bottom: 20px;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(4px);
    z-index: 10;
    border: 1px solid #EAEAEA;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #EAEAEA;
    background: #FAFAFA;
}

.detail-title-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.detail-type-badge {
    font-size: 9px;
    font-weight: 700;
    color: #FFF;
    background: #000;
    padding: 2px 6px;
    border-radius: 2px;
    text-transform: uppercase;
}

.detail-name {
    font-size: 14px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.close-btn {
    background: none;
    border: none;
    font-size: 18px;
    color: #999;
    cursor: pointer;
    line-height: 1;
}

.close-btn:hover {
    color: #333;
}

.detail-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.detail-desc {
    font-size: 12px;
    color: #444;
    line-height: 1.5;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px dashed #EAEAEA;
}

.detail-section {
    margin-bottom: 16px;
}

.section-label {
    display: block;
    font-size: 10px;
    font-weight: 600;
    color: #AAA;
    margin-bottom: 8px;
}

.attr-list, .conn-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.attr-item {
    font-size: 11px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: baseline;
    padding: 4px;
    background: #F9F9F9;
    border-radius: 4px;
}

.attr-name {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: #000;
}

.attr-type {
    color: #999;
    font-size: 10px;
}

.attr-desc {
    color: #555;
    flex: 1;
    min-width: 150px;
}

.example-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.example-tag {
    font-size: 11px;
    background: #FFF;
    border: 1px solid #E0E0E0;
    padding: 3px 8px;
    border-radius: 12px;
    color: #555;
}

.conn-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    padding: 6px;
    background: #F5F5F5;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
}

.conn-node {
    font-weight: 600;
    color: #333;
}

.conn-arrow {
    color: #BBB;
}

/* Deep Research v2 Card */
.research-card {
  margin-top: 16px;
  padding: 16px;
  background: #FFF;
  border: 1px solid #EAEAEA;
  border-radius: 6px;
}

.research-card.research-running {
  border-color: #FF5722;
  background: #FFF8F6;
}

.research-card.research-review {
  border-color: #FF5722;
}

.research-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.research-title {
  font-weight: 700;
  font-size: 13px;
  color: #000;
}

.research-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}

.research-badge.running { background: #FF5722; color: #FFF; }
.research-badge.review { background: #FFF3E0; color: #E65100; }
.research-badge.confirmed { background: #E8F5E9; color: #2E7D32; }
.research-badge.skipped { background: #F5F5F5; color: #999; }
.research-badge.error { background: #FFEBEE; color: #C62828; }

.research-desc {
  font-size: 11px;
  color: #888;
  margin-bottom: 12px;
  line-height: 1.4;
}

/* Confidence legend */
.confidence-legend {
  display: flex;
  gap: 14px;
  margin-bottom: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: #999;
  font-family: 'JetBrains Mono', monospace;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 1px;
}

.legend-dot.confirmed { background: #4CAF50; }
.legend-dot.unverified { background: #FF9800; }
.legend-dot.contradicted { background: #F44336; }

/* Confidence tags */
.finding-top-row {
  margin-bottom: 2px;
}

.finding-confidence-tag {
  font-size: 9px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  padding: 1px 6px;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.finding-confidence-tag.tag-confirmed {
  background: #E8F5E9;
  color: #2E7D32;
}

.finding-confidence-tag.tag-unverified {
  background: #FFF3E0;
  color: #E65100;
}

.finding-confidence-tag.tag-contradicted {
  background: #FFEBEE;
  color: #C62828;
}

.findings-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.finding-item {
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 8px;
  background: #FAFAFA;
  border: 1px solid #EAEAEA;
  border-radius: 4px;
  transition: opacity 0.2s;
}

.finding-item.disabled {
  opacity: 0.4;
}

.finding-left {
  width: 3px;
  border-radius: 2px;
  flex-shrink: 0;
}

.finding-left.confidence-confirmed { background: #4CAF50; }
.finding-left.confidence-unverified { background: #FF9800; }
.finding-left.confidence-contradicted { background: #F44336; }

.finding-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.finding-fact {
  font-size: 11px;
  color: #333;
  line-height: 1.4;
}

.finding-source {
  font-size: 10px;
  color: #999;
  font-family: 'JetBrains Mono', monospace;
}

.finding-toggle {
  align-self: center;
  font-size: 10px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  background: none;
  border: 1px solid #DDD;
  border-radius: 3px;
  padding: 2px 8px;
  cursor: pointer;
  color: #666;
  flex-shrink: 0;
}

.finding-toggle:hover {
  border-color: #999;
  color: #000;
}

.research-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.research-confirm-btn {
  flex: 1;
}

.research-skip-link {
  background: none;
  border: none;
  color: #999;
  font-size: 11px;
  cursor: pointer;
  text-decoration: underline;
  flex-shrink: 0;
}

.research-skip-link:hover {
  color: #666;
}

/* Step 02 Stats */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  background: #F9F9F9;
  padding: 16px;
  border-radius: 6px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #000;
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 9px;
  color: #999;
  text-transform: uppercase;
  margin-top: 4px;
  display: block;
}

/* Step 03 Button */
.action-btn {
  width: 100%;
  background: #000;
  color: #FFF;
  border: none;
  padding: 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.action-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.action-btn:disabled {
  background: #CCC;
  cursor: not-allowed;
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #FF5722;
  margin-bottom: 12px;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid #FFCCBC;
  border-top-color: #FF5722;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* System Logs */
.system-logs {
  background: #000;
  color: #DDD;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid #222;
  flex-shrink: 0;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #333;
  padding-bottom: 8px;
  margin-bottom: 8px;
  font-size: 10px;
  color: #888;
  cursor: pointer;
  user-select: none;
}
.log-toggle {
  background: none;
  border: none;
  color: #555;
  font-size: 10px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}
.log-toggle:hover { color: #aaa; }
.system-logs.logs-collapsed { padding: 4px 16px; }
.system-logs.logs-collapsed .log-header { border-bottom: none; padding-bottom: 0; margin-bottom: 0; }

.log-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 80px; /* Approx 4 lines visible */
  overflow-y: auto;
  padding-right: 4px;
}

.log-content::-webkit-scrollbar {
  width: 4px;
}

.log-content::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}

.log-line {
  font-size: 11px;
  display: flex;
  gap: 12px;
  line-height: 1.5;
}

.log-time {
  color: #666;
  min-width: 75px;
}

.log-msg {
  color: #CCC;
  word-break: break-all;
}
</style>
