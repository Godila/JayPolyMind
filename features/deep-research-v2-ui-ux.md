# Deep Research v2 -- UI/UX спецификация

## Ревью предыдущей версии

### Что было правильно
- Research как карточка внутри Step1GraphBuild, а не отдельный шаг -- сохраняет 5-шаговую структуру
- Review gate с ручным подтверждением перед онтологией
- Async polling через TaskManager (существующий паттерн)
- Карточка скрывается когда research выключен

### Что было неправильно

| Проблема | Почему | Исправление |
|----------|--------|-------------|
| Фиолетовый акцент `#A78BFA` | Workspace использует оранжевый `#FF5722` как primary accent. Фиолетовый -- чужеродный цвет, нет нигде кроме тогла в ScenarioForm | Использовать `#FF5722` для активных состояний, зеленый/оранжевый/красный для статусов фактов -- стандартная палитра приложения |
| `currentPhase = -0.5` или `'research'` string | Текущий enum числовой (-1, 0, 1, 2). Строка или дробное число ломает `>=`, `>` сравнения по всему коду | Отдельный `researchPhase` ref. `currentPhase` не трогаем |
| Review gate перегружен | Чекбоксы + кнопки удаления + раскрытие + категории + 2 CTA -- cognitive overload для пользователя | Упростить: toggle per finding + одна CTA "Продолжить". "Пропустить" = ссылка, не кнопка |
| Citation ноды = ромбы | D3 force layout оптимизирован под круги. Ромбы требуют кастомного path + collision detection | Круги с иконкой-бейджем (маленький значок ссылки) + пунктирные ребра |
| Не учтены шрифты | Приложение использует JetBrains Mono / Unbounded / Onest -- характерная типографика | Прописать конкретные font-family для каждого элемента |
| Пустой GraphPanel во время research | Левая панель пустая 60-90 секунд -- потеря пространства | Показать preview: текущие поисковые запросы как анимированные теги |
| Нет error/retry состояний | Research может упасть (SearXNG недоступен, LLM timeout) | Добавить состояние ошибки с retry |

---

## Дизайн-система (из анализа кодовой базы)

### Цвета workspace
```
Фон:          #FFFFFF, #FAFAFA, #F5F5F5
Текст:        #000 (primary), #333 (secondary), #666 (tertiary), #999 (muted)
Границы:      #EAEAEA (default), #D0D0D0 (emphasis)
Акцент:       #FF5722 (orange-red, active/processing)
Success:      #2E7D32 text, #E8F5E9 bg
Pending:      #999 text, #F5F5F5 bg
Error:        #F44336
```

### Шрифты
```
Числа/код:    JetBrains Mono (400, 600, 700)
Заголовки:    Onest (500, 600)
Бейджи:       JetBrains Mono (600, 10px, uppercase)
```

### Карточки (step-card)
```
Background:   #FFFFFF
Border:       1px solid #EAEAEA
Border-radius: 8px
Padding:      20px
Shadow:       0 2px 8px rgba(0,0,0,0.04)
Active:       border-color #FF5722, shadow 0 4px 12px rgba(255,87,34,0.08)
Completed:    border-color #E8F5E9
```

### Бейджи (badge)
```
Success:      bg #E8F5E9, color #2E7D32, 4px padding, 4px radius
Processing:   bg #FF5722, color #FFF
Pending:      bg #F5F5F5, color #999
```

---

## Архитектура состояний

### Принцип: раздельные state machines

```javascript
// Не трогаем currentPhase -- он управляет Ontology/Build/Complete
const currentPhase = ref(-1)  // -1: Upload, 0: Ontology, 1: Build, 2: Complete

// Новый state для research
const researchState = ref('idle')
// Значения: 'idle' | 'running' | 'review' | 'confirmed' | 'skipped' | 'error'

const researchTaskId = ref(null)
const researchFindings = ref([])
const researchRound = ref({ current: 0, total: 3 })
const researchQuery = ref('')  // текущий поисковый запрос
```

### Переходы состояний

```
enableResearch = false:
  Upload -> Ontology -> Build -> Complete
  (researchState остается 'idle', карточка скрыта)

enableResearch = true:
  Upload -> researchState: running -> review -> confirmed -> Ontology -> Build -> Complete
                                        |
                                    (skip) -> Ontology -> Build -> Complete

Ошибка:
  running -> error -> (retry) -> running
                   -> (skip)  -> Ontology
```

---

## UI Flow

### Экран 1: ScenarioForm.vue (без изменений)

Тогл Deep Research уже реализован. Единственное уточнение -- тогл должен
использовать `#FF5722` вместо `#A78BFA` чтобы быть консистентным с workspace:

```
  Deep Research
  [●━━━━━━━━━━●] Вкл        <- slider цвет: #FF5722 когда вкл
  Проверка фактов документа через веб-поиск
```

---

### Экран 2: Research Phase (researchState = 'running')

```
Header: [JayPolyMind]  [Граф | Сплит | Рабочий стол]  [Шаг 1/5 Построение графа ● Исследование]

+----------------------------------+-----------------------------------------------+
|                                  |                                               |
|  GraphPanel                      |  .step-card.active  (border: #FF5722)         |
|  +----------------------------+  |  +-------------------------------------------+|
|  |                            |  |  | 01    Веб-исследование      [Раунд 2/3]  ||
|  |  Текущие запросы:          |  |  |       JetBrains Mono 600     badge orange ||
|  |                            |  |  +-------------------------------------------+|
|  |  ┌─────────────────────┐   |  |                                               |
|  |  │ JPMorgan CEO 2024   │   |  |  POST /api/graph/research/start               |
|  |  └─────────────────────┘   |  |  Onest 400, 12px, color #666                  |
|  |       ↕ fade swap          |  |                                               |
|  |  ┌─────────────────────┐   |  |  Поиск фактов и верификация утверждений       |
|  |  │ M&A strategy bank   │   |  |  документа через SearXNG                      |
|  |  └─────────────────────┘   |  |                                               |
|  |       ↕ fade swap          |  |  ── Прогресс ──────────────────────────────   |
|  |  ┌─────────────────────┐   |  |                                               |
|  |  │ First Republic acq  │   |  |  [████████████████░░░░░░░░░░░] 62%            |
|  |  └─────────────────────┘   |  |  #FF5722 fill, #F5F5F5 track, 4px radius     |
|  |                            |  |                                               |
|  |  Onest 400, 13px          |  |  Ищем: "JPMorgan M&A strategy 2024"           |
|  |  bg #FAFAFA               |  |  JetBrains Mono 400, 11px, color #999         |
|  |  border 1px #EAEAEA       |  |                                               |
|  |  tags с fade анимацией    |  |  ── Найдено (4) ────────────────────────────   |
|  |                            |  |                                               |
|  +----------------------------+  |  ┌ finding-item ─────────────────────────────┐|
|                                  |  │ ● Jamie Dimon -- CEO JPMorgan Chase       │|
|                                  |  │   reuters.com              Подтверждено   │|
|                                  |  └───────────────────────────────────────────┘|
|                                  |  ┌ finding-item (fadeIn 300ms) ──────────────┐|
|                                  |  │ ● Выручка $162.4B в 2023 году             │|
|                                  |  │   wsj.com                  Подтверждено   │|
|                                  |  └───────────────────────────────────────────┘|
|                                  |                                               |
|                                  |  .step-card (border: #EAEAEA, opacity 0.5)    |
|                                  |  02 Генерация онтологии        [Ожидание]     |
|                                  |                                               |
|                                  |  .step-card (border: #EAEAEA, opacity 0.5)    |
|                                  |  03 Построение графа            [Ожидание]     |
|                                  |                                               |
+----------------------------------+-----------------------------------------------+
```

**Детали компонентов:**

**Progress bar:**
```css
.research-progress-bar {
  height: 4px;
  background: #F5F5F5;
  border-radius: 4px;
  overflow: hidden;
}
.research-progress-fill {
  height: 100%;
  background: #FF5722;
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}
```

**Finding item:**
```css
.finding-item {
  padding: 10px 12px;
  background: #FAFAFA;
  border: 1px solid #EAEAEA;
  border-radius: 6px;
  margin-bottom: 6px;
  animation: fadeSlideIn 300ms ease-out;
  font-family: 'Onest', sans-serif;
  font-size: 13px;
}
.finding-item .fact-text {
  color: #333;
  font-weight: 500;
}
.finding-item .source-url {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #999;
}
.finding-item .status-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 3px;
}
.status-confirmed { background: #E8F5E9; color: #2E7D32; }
.status-unverified { background: #FFF3E0; color: #E65100; }
.status-contradicted { background: #FFEBEE; color: #C62828; }
```

**GraphPanel во время research:**

Вместо пустого "Ожидание построения графа" показываем
анимированный preview текущих поисковых запросов. Это заполняет
пустое пространство и дает пользователю контекст:

```css
.research-queries-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  padding: 40px;
}
.query-tag {
  font-family: 'Onest', sans-serif;
  font-size: 13px;
  color: #666;
  padding: 8px 16px;
  background: #FFFFFF;
  border: 1px solid #EAEAEA;
  border-radius: 20px;
  animation: queryFade 3s ease-in-out infinite;
}
@keyframes queryFade {
  0%, 100% { opacity: 0.3; transform: scale(0.97); }
  50% { opacity: 1; transform: scale(1); }
}
```

---

### Экран 3: Review Gate (researchState = 'review')

```
+----------------------------------+-----------------------------------------------+
|                                  |                                               |
|  GraphPanel                      |  .step-card.active  (border: #FF5722)         |
|  (queries preview               |  +-------------------------------------------+|
|   переходит в summary)          |  | 01    Веб-исследование      [Проверка]    ||
|                                  |  +-------------------------------------------+|
|  +----------------------------+  |                                               |
|  |                            |  |  Найдено 14 фактов из 18 источников          |
|  |   14 фактов                |  |  Onest 400, 13px, color #333                 |
|  |   18 источников            |  |                                               |
|  |   3 раунда поиска          |  |  ── Факты ────────────────────────────────   |
|  |                            |  |                                               |
|  |   ● 9 подтверждено         |  |  ┌ finding-review ──────────────────────────┐|
|  |   ● 3 не проверено         |  |  │ [toggle ON]  Jamie Dimon -- CEO          │|
|  |   ● 2 противоречия         |  |  │              JPMorgan Chase              │|
|  |                            |  |  │     reuters.com     ● Подтверждено       │|
|  |   Onest 400, 14px          |  |  └──────────────────────────────────────────┘|
|  |   Цвета по статусам        |  |  ┌ finding-review ──────────────────────────┐|
|  |                            |  |  │ [toggle ON]  Выручка $162.4B             │|
|  +----------------------------+  |  │              в 2023 финансовом году       │|
|                                  |  │     wsj.com         ● Подтверждено       │|
|                                  |  └──────────────────────────────────────────┘|
|                                  |  ┌ finding-review (border-left: #E65100) ───┐|
|                                  |  │ [toggle ON]  Открытие AI Research Lab    │|
|                                  |  │              в 2024                       │|
|                                  |  │     techcrunch.com  ○ Не проверено       │|
|                                  |  └──────────────────────────────────────────┘|
|                                  |  ┌ finding-review (border-left: #C62828) ───┐|
|                                  |  │ [toggle OFF] Капитализация $500B+        │|
|                                  |  │              (не соответствует данным)    │|
|                                  |  │     ft.com          ✗ Противоречие       │|
|                                  |  └──────────────────────────────────────────┘|
|                                  |                                               |
|                                  |  ┌ actions-bar ─────────────────────────────┐|
|                                  |  │                                          │|
|                                  |  │  пропустить    [ Продолжить (11 фактов) ]│|
|                                  |  │  ↑ text link    ↑ primary button #FF5722 │|
|                                  |  │                                          │|
|                                  |  └──────────────────────────────────────────┘|
|                                  |                                               |
|                                  |  02 Генерация онтологии        [Ожидание]     |
|                                  |  03 Построение графа            [Ожидание]     |
+----------------------------------+-----------------------------------------------+
```

**Упрощенный review (vs предыдущая версия):**

Предыдущая версия имела: чекбоксы + кнопки удаления [x] + раскрытие по клику +
группировку по статусам в 3 секции + 2 равнозначных CTA кнопки.

Исправлено:
- **Один toggle** вместо чекбокс + delete -- включить/выключить факт
- **Единый список** вместо 3 секций -- статус показан цветом left-border + бейджем
- **Одна primary CTA** "Продолжить (N фактов)" -- число обновляется при toggle
- **"пропустить"** -- text link, не кнопка. Визуально менее значимый
- **По умолчанию**: confirmed = ON, unverified = ON, contradicted = OFF
- **Клик на факт** раскрывает деталь (полный текст + дата публикации)

**Finding review item:**
```css
.finding-review {
  padding: 12px 14px;
  background: #FFFFFF;
  border: 1px solid #EAEAEA;
  border-left: 3px solid #2E7D32;  /* цвет по статусу */
  border-radius: 6px;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: opacity 0.2s ease;
}
.finding-review.excluded {
  opacity: 0.4;
}
.finding-review[data-status="unverified"] { border-left-color: #E65100; }
.finding-review[data-status="contradicted"] { border-left-color: #C62828; }

/* Toggle switch (маленький, 32x18px) */
.finding-toggle {
  width: 32px;
  height: 18px;
  border-radius: 9px;
  background: #CCC;
  flex-shrink: 0;
  margin-top: 2px;
  cursor: pointer;
  transition: background 0.2s;
}
.finding-toggle.on { background: #FF5722; }
```

**Actions bar:**
```css
.actions-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
  padding: 16px 0 8px;
  border-top: 1px solid #EAEAEA;
  margin-top: 16px;
}
.skip-link {
  font-family: 'Onest', sans-serif;
  font-size: 13px;
  color: #999;
  cursor: pointer;
  text-decoration: none;
  border: none;
  background: none;
}
.skip-link:hover { color: #666; text-decoration: underline; }

.confirm-btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  padding: 10px 20px;
  background: #FF5722;
  color: #FFF;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.confirm-btn:hover { background: #E64A19; }
```

---

### Экран 4: Research завершен, Ontology генерируется

```
+----------------------------------+-----------------------------------------------+
|                                  |                                               |
|  GraphPanel                      |  .step-card.completed  (border: #E8F5E9)      |
|  (пустой, ждет граф)             |  +-------------------------------------------+|
|                                  |  | 01  Веб-исследование   [Завершено]        ||
|                                  |  |     11 фактов подтверждено                ||
|                                  |  +-------------------------------------------+|
|                                  |   ↑ свернутая карточка, 1 строка summary      |
|                                  |                                               |
|                                  |  .step-card.active  (border: #FF5722)         |
|                                  |  +-------------------------------------------+|
|                                  |  | 02  Генерация онтологии   [● Генерация]   ||
|                                  |  +-------------------------------------------+|
|                                  |  [spinner-sm] Анализ документов + research... |
|                                  |                                               |
|                                  |  ТИПЫ СУЩНОСТЕЙ: [Person] [Organization] ... |
|                                  |  ТИПЫ СВЯЗЕЙ: [WORKS_AT] [ACQUIRED] ...      |
|                                  |                                               |
|                                  |  03 Построение графа            [Ожидание]    |
|                                  |                                               |
+----------------------------------+-----------------------------------------------+
```

**Свернутая карточка research:**
```css
.step-card.completed .card-content {
  max-height: 0;
  overflow: hidden;
  padding: 0 20px;
  transition: max-height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
              padding 0.4s ease;
}
/* Summary строка показывается в card-header */
.research-summary {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #666;
}
```

---

### Экран 5: Graph Build (с Citations)

```
+----------------------------------+-----------------------------------------------+
|                                  |                                               |
|  GraphPanel                      |  01  Веб-исследование  [Завершено]   11       |
|  +----------------------------+  |  02  Генерация онтологии [Завершено]          |
|  |                            |  |                                               |
|  |  ◉ JPMorgan ─── ◉ Dimon   |  |  .step-card.active (border: #FF5722)          |
|  |  │                        |  |  +-------------------------------------------+|
|  |  ◉ First Republic         |  |  | 03  Построение графа    [● 45%]           ||
|  |       │                   |  |  +-------------------------------------------+|
|  |  ◎ reuters.com            |  |  [████████░░░░░░░░░] 45%                      |
|  |  ◎ wsj.com                |  |  Обработано: 12/26 чанков                     |
|  |   (Citations: меньший     |  |                                               |
|  |    размер, пунктир)       |  |  Entities: 89 | Relations: 134                |
|  |                            |  |  Citations: 11  <- новый счетчик             |
|  +----------------------------+  |                                               |
|                                  |  04  Готово                     [Ожидание]    |
|  Legend:                         |                                               |
|  ● Person  ● Organization       |                                               |
|  ● Event   ◎ Citation            |                                               |
|                                  |                                               |
+----------------------------------+-----------------------------------------------+
```

**Citation ноды в D3:**
```javascript
// В GraphPanel.vue -- рендеринг citation нод
// Круги (не ромбы) но меньшего размера + пунктирная обводка

node.filter(d => d.type === 'Citation')
  .select('circle')
  .attr('r', 6)                    // меньше обычных (8-12px)
  .attr('fill', '#FAFAFA')         // светлый фон
  .attr('stroke', '#3B82F6')       // синий из палитры landing page
  .attr('stroke-width', 1.5)
  .attr('stroke-dasharray', '3,2') // пунктир

// SOURCED_FROM ребра
link.filter(d => d.type === 'SOURCED_FROM')
  .attr('stroke', '#3B82F6')
  .attr('stroke-dasharray', '4,3')
  .attr('stroke-opacity', 0.4)

// Легенда
{ name: 'Citation', color: '#3B82F6', count: 11 }
```

Почему `#3B82F6` (синий) вместо `#A78BFA` (фиолетовый):
- Синий уже в палитре (landing page `--acc1`)
- Семантически "ссылка/источник" ассоциируется с синим
- Не конфликтует с оранжевым акцентом workspace

---

### Экран 6: Error State (researchState = 'error')

```
  .step-card (border: #F44336)
  +-------------------------------------------+
  | 01  Веб-исследование      [Ошибка]        |
  +-------------------------------------------+
  |                                            |
  |  ⚠ Не удалось выполнить поиск             |
  |  SearXNG недоступен или превышен таймаут   |
  |                                            |
  |  [Повторить]    пропустить                 |
  +--------------------------------------------+
```

```css
.step-card.error {
  border-color: #F44336;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.08);
}
.error-badge {
  background: #FFEBEE;
  color: #C62828;
}
```

---

## Компонентная архитектура

### Что модифицируем (НЕ создаем новые компоненты)

```
Step1GraphBuild.vue  -- добавить research карточку + review gate
                        (не выносить в отдельный компонент -- это одна карточка
                        в ряду с остальными, единый scroll-container)

MainView.vue         -- добавить researchState, polling, confirmResearch()
                        НЕ менять currentPhase enum

GraphPanel.vue       -- добавить rendering Citation нод + легенду
                        + research queries preview (когда researchState = running)

graph.js             -- 3 новых endpoint функции
```

### Почему НЕ отдельный StepResearch.vue

1. **Консистентность**: все карточки в Step1 живут в одном scroll-container с единой стилизацией
2. **Простота**: Step1GraphBuild уже управляет phase-зависимыми карточками через v-if/v-else
3. **Минимум props**: не нужно пробрасывать researchState, findings, progress через родителя
4. **Анимации**: collapse/expand карточек работают через единый CSS контекст

### Props для Step1GraphBuild.vue (дополнения)

```javascript
const props = defineProps({
  // Существующие
  currentPhase: Number,
  projectData: Object,
  ontologyProgress: Object,
  buildProgress: Object,
  graphData: Object,
  systemLogs: Array,
  // Новые
  researchState: String,        // 'idle'|'running'|'review'|'confirmed'|'skipped'|'error'
  researchFindings: Array,      // [{ id, fact, status, confidence, source_url, source_title }]
  researchProgress: Object,     // { percent, round, totalRounds, currentQuery }
})

const emit = defineEmits([
  'next-step',
  // Новые
  'confirm-research',   // (includedFindingIds: string[])
  'skip-research',
  'retry-research',
])
```

### Новые API функции (graph.js)

```javascript
export const startResearchTask = (projectId) =>
  api.post('/graph/research/start', { project_id: projectId })

export const getResearchStatus = (taskId) =>
  api.get(`/graph/research/status/${taskId}`)

export const confirmResearchFindings = (taskId, includedFindings) =>
  api.post(`/graph/research/confirm/${taskId}`, {
    included_findings: includedFindings
  })
```

### Polling в MainView.vue

```javascript
// Research polling -- тот же паттерн что и graph build polling
const startResearchPolling = () => {
  researchPollTimer = setInterval(async () => {
    const res = await getResearchStatus(researchTaskId.value)
    if (!res.success) return

    researchProgress.value = res.data.progress
    // Findings обновляются инкрементально
    if (res.data.findings?.length > researchFindings.value.length) {
      researchFindings.value = res.data.findings
    }

    if (res.data.status === 'completed') {
      clearInterval(researchPollTimer)
      researchState.value = 'review'
    } else if (res.data.status === 'failed') {
      clearInterval(researchPollTimer)
      researchState.value = 'error'
    }
  }, 2000)
}
```

---

## Анимации

### Finding item появление
```css
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.finding-item {
  animation: fadeSlideIn 300ms ease-out;
}
/* Стагерация: каждый следующий факт с задержкой */
.finding-item:nth-child(1) { animation-delay: 0ms; }
.finding-item:nth-child(2) { animation-delay: 50ms; }
.finding-item:nth-child(3) { animation-delay: 100ms; }
```

### Progress bar
```css
.research-progress-fill {
  transition: width 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}
```

### Карточка collapse после confirm
```css
.step-card.completed .card-content {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
              padding 0.3s ease;
}
```

### Query tag в GraphPanel
```css
@keyframes queryPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.97); }
  50% { opacity: 1; transform: scale(1); }
}
.query-tag {
  animation: queryPulse 2.5s ease-in-out infinite;
}
.query-tag:nth-child(odd) { animation-delay: 0.8s; }
```

---

## Адаптивность к view modes

| View Mode | GraphPanel (левая) | Research (правая) |
|-----------|-------------------|-------------------|
| Сплит | Queries preview / summary | Полная карточка |
| Рабочий стол | Скрыт | Карточка на всю ширину |
| Граф | Queries preview на весь экран | Скрыт, статус только в header |

В режиме "Граф" когда research активен -- header показывает:
```
Шаг 1/5 Построение графа ● Исследование (68%)
```
