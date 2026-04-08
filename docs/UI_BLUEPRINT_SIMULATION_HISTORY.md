# UI Blueprint: Simulation History Management
# JayPolyMind -- Управление историей симуляций
# Версия: 1.0 | Дата: 2026-04-08

---

## 1. USER STORIES

### US-1: Просмотр списка симуляций

КАК пользователь платформы
Я ХОЧУ видеть все симуляции проекта в табличном виде
ЧТОБЫ быстро оценить статус и найти нужную симуляцию

КРИТЕРИИ ПРИЕМКИ:
- Таблица отображает все симуляции текущего проекта
- Каждая строка: название, статус, дата, прогресс раундов, этапы
- Сортировка по дате (новые первыми) по умолчанию
- Клик по строке открывает навигацию к симуляции
- Читаемость при 20+ записях (скролл, не пагинация)

### US-2: Удаление симуляций

КАК пользователь платформы
Я ХОЧУ удалять одну или несколько симуляций
ЧТОБЫ очистить историю от ненужных/ошибочных запусков

КРИТЕРИИ ПРИЕМКИ:
- Одиночное удаление через иконку в строке
- Пакетное удаление через чекбоксы
- Модальное подтверждение с перечнем удаляемого
- Каскад: данные симуляции + связанный отчет

### US-3: Удаление проекта целиком

КАК пользователь платформы
Я ХОЧУ удалить весь проект с каскадным удалением
ЧТОБЫ полностью очистить неактуальный проект

КРИТЕРИИ ПРИЕМКИ:
- Кнопка визуально отделена от таблицы
- Усиленное предупреждение в модалке
- Каскад: проект + симуляции + отчеты + Neo4j граф
- Явное указание необратимости

---

## 2. ASCII WIREFRAMES

### 2.1 Полный вид таблицы с тулбаром

```
ЗАМЕНА: fan-stack карточки --> табличный список
КОМПОНЕНТ: HistoryDatabase.vue
ШРИФТ: JetBrains Mono | АКЦЕНТ: #FF5722 | ФОН: #EAEAEA / #FFFFFF

-------- История симуляций --------   <-- section-header (существующий паттерн)

+--------------------------------------------------------------------------+
| TOOLBAR                                                                   |
| [ ] Выбрать все      Сортировка: [По дате (новые)  v]                     |
+--------------------------------------------------------------------------+
|  [ ]  Название              Статус         Дата       Раунды  Этапы  Дейст|
+-----+----------------------+-------------+----------+-------+------+-----+
| [ ] | Анализ рынка электро | * Завершена  | 04-07    | 10/10 | F F F| O X |
|     |                      |   (#4CAF50)  | 14:32    | ===== |      |     |
+-----+----------------------+-------------+----------+-------+------+-----+
| [ ] | Тестирование бренда  | * В процессе | 04-07    | 6/10  | F F  | O X |
|     |  нового продукта...  |   (#FF9800)  | 11:05    | ====  |      |     |
+-----+----------------------+-------------+----------+-------+------+-----+
| [ ] | Оценка конкурентов   | * Ошибка     | 04-06    | 3/10  | F    | O X |
|     |  на маркетплейсах... |   (#F44336)  | 09:21    | ==    |      |     |
+-----+----------------------+-------------+----------+-------+------+-----+
| [ ] | Прогноз спроса на    | * Не запущ.  | 04-05    | 0/10  |      | O X |
|     |  зимнюю коллекцию... |   (#9E9E9E)  | 16:44    |       |      |     |
+-----+----------------------+-------------+----------+-------+------+-----+

Обозначения:
  * = цветная точка статуса        F = filled diamond (этап завершен)
  O = иконка "открыть"             X = иконка "удалить" (корзина)
  ===== = mini progress-bar

--- Удалить проект ---
+--------------------------------------------------------------------------+
| [!] Удалить проект   Каскадное удаление данных проекта     [Удалить BTN] |
+--------------------------------------------------------------------------+
```

### 2.2 Детальная строка таблицы

```
СТРОКА -- нормальное состояние | bg: #FFFFFF | border-bottom: 1px solid #E0E0E0

+-----+---------------------------+--------------+----------+-------+--------+------+
| [CB]| НАЗВАНИЕ                  | СТАТУС       | ДАТА     | РАУНДЫ| ЭТАПЫ  |ДЕЙСТ |
+-----+---------------------------+--------------+----------+-------+--------+------+
|     |                           |              |          |       |        |      |
| [ ] | Анализ рынка электро...   | * Завершена  | 04-07    | 10/10 | F F F  | O  X |
|     | SIM_A1B2C3                |              | 14:32    | ===== |        |      |
|     |                           |              |          |       |        |      |
+-----+---------------------------+--------------+----------+-------+--------+------+

[CB]  = чекбокс 18px, sharp corners, border: 1px solid #E0E0E0
*     = status-dot 8px
10/10 = текст прогресса
===== = progress-bar 3px высота, цвет по статусу
F     = filled diamond (завершенный этап)
O     = стрелка "открыть" 16px
X     = корзина "удалить" 16px, hover color: #F44336
SIM_A1B2C3 = ID, мелкий шрифт, color: #9E9E9E
```

### 2.3 Состояния строки

```
-- NORMAL --  bg: #FFFFFF | cursor: pointer
+-----+---------------------------+--------------+----------+-------+--------+------+
| [ ] | Анализ рынка электро...   | * Завершена  | 04-07    | 10/10 | F F F  | O  X |
+-----+---------------------------+--------------+----------+-------+--------+------+

-- HOVER --  bg: #F5F5F5 | border-left: 3px solid #FF5722
+-----+---------------------------+--------------+----------+-------+--------+------+
|#[ ] | Анализ рынка электро...   | * Завершена  | 04-07    | 10/10 | F F F  | O  X |
+-----+---------------------------+--------------+----------+-------+--------+------+

-- SELECTED --  bg: #FFF3E0 | border-left: 3px solid #FF5722
+-----+---------------------------+--------------+----------+-------+--------+------+
|#[x] | Анализ рынка электро...   | * Завершена  | 04-07    | 10/10 | F F F  | O  X |
+-----+---------------------------+--------------+----------+-------+--------+------+

СТАТУСЫ:
  * Завершена    #4CAF50   bar: 100% зеленый
  * В процессе   #FF9800   bar: частично оранжевый
  * Ошибка       #F44336   bar: частично красный
  * Не запущена  #9E9E9E   bar: пустой

ЭТАПЫ (diamond-иконки):
  _ _ _   ничего             все пустые #E0E0E0
  F _ _   только граф        первый #FF5722
  F F _   граф + среда       два заполнены
  F F F   всё + отчет        все заполнены

  Tooltip при hover:
    1-й = "Построение графа"
    2-й = "Настройка среды"
    3-й = "Отчет"
```


---

## 3. INTERACTION FLOWS

### 3.1 View and Navigate

STATE: Loading
+------------+
| Loading... |  --> API: GET /api/projects
+------------+

STATE: Table loaded
+------------+
| N rows     |  --> User sees list
+------------+
      |
      | click on row (not checkbox/actions)
      v
STATE: Navigation
+-------------------+
| router.push(...)  |  --> go to simulation
+-------------------+

### 3.2 Single Delete Flow

STEPS:
1. User sees table with simulations
2. User hovers row (hover state activates)
3. User clicks trash icon [X] in Actions column
4. System shows modal
5. User sees simulation name + deletion list
6a. User clicks [Otmena] --> modal closes
6b. User clicks [Udalit] -->
    7. System sends DELETE /api/simulation/{id}
    8. System shows spinner on button
    9. System closes modal
    10. System removes row with slide-up animation
    11. System shows toast

DIAGRAM:

[Table] --click [X]--> [Modal] --[Otmena]--> [Table]
                            |
                        [Udalit]
                            |
                       [API DELETE]
                        |       |
                     success   error
                        |       |
                  [Toast OK] [Toast err]

### 3.3 Bulk Delete Flow

1. User clicks checkboxes (or Select All)
2. Bulk action bar appears: Vybrano: N
3. User clicks [Udalit vybrannye]
4. Modal: Udalit N simulyacij?
5a. [Otmena] --> selection preserved
5b. [Udalit] --> batch DELETE --> Toast --> reset

### 3.4 Delete Project Flow

1. User clicks button below table
2. Modal with strong warning
3a. [Otmena] --> close
3b. [Udalit proekt] --> cascade DELETE --> redirect home


---

## 4. COMPONENT SPECIFICATIONS

### 4.1 Table Columns

| Column      | Width        | Align  |
|-------------|--------------|--------|
| Checkbox    | 40px fixed   | center |
| Nazvanie    | flex: 1      | left   |
| Status      | 140px fixed  | left   |
| Data        | 120px fixed  | left   |
| Raundy      | 100px fixed  | center |
| Etapy       | 100px fixed  | center |
| Dejstviya   | 80px fixed   | center |

Min width: ~700px, overflow-x: auto on mobile

### 4.2 Progress Bar (Raundy column)

Container: 60px x 3px, bg: #E0E0E0
Fill: 3px, bg = status color

0/10:   |                              |  empty
3/10:   |=========                     |  30%, #FF9800
7/10:   |=====================         |  70%, #FF9800
10/10:  |==============================|  100%, #4CAF50
3/10err:|=========                     |  30%, #F44336

Text N/N above bar, JetBrains Mono 12px, #616161

### 4.3 Delete Project Button

Below table, margin-top: 32px

+--------------------------------------------------------------------------+
|  [!] Udalit proekt                                                        |
|  Kaskadnoe udalenie vsekh dannykh proekta                                |
|                                           +-------------------+          |
|                                           | Udalit proekt     |          |
|                                           +-------------------+          |
|                                            border: 1px #F44336           |
|                                            color: #F44336               |
|                                            bg: transparent              |
|                                            hover: bg #F44336 color #FFF |
+--------------------------------------------------------------------------+
bg: #FFF | border: 1px solid #E0E0E0 | padding: 20px 24px | sharp corners

### 4.4 Toast Notifications

Position: bottom-right, 24px from edge
Animation: slide-up + fade-in, 300ms
Auto-hide: 3000ms

Success: +-------------------------------+
         | [v] Simulyaciya udalena       |
         +-------------------------------+
         bg: #FFF, border-left: 4px solid #4CAF50

Error:   +-------------------------------+
         | [!] Oshibka pri udalenii      |
         +-------------------------------+
         bg: #FFF, border-left: 4px solid #F44336

Bulk:    +-------------------------------+
         | [v] Udaleno 3 simulyacii      |
         +-------------------------------+

---

## 5. RESPONSIVE BEHAVIOR

### 5.1 Desktop (>1024px)
Full table with all columns visible

### 5.2 Tablet (768-1024px)
Etapy column hidden, diamonds move under name
Date shortened to MM-DD

### 5.3 Mobile (<768px)
Card-list layout instead of table
Bulk bar: position fixed at bottom

+-------------------------------------------------------+
| [ ] Analiz rynka elektromobilej v Rossii...            |
|  * Zavershena        2026-04-07 14:32                  |
|  10/10 ==============================                   |
|  F F F                                     -> [x]      |
+-------------------------------------------------------+


---

## 6. CSS DESIGN TOKENS

--color-accent: #FF5722;
--color-bg-page: #EAEAEA;
--color-bg-card: #FFFFFF;
--color-border: #E0E0E0;
--color-text-primary: #212121;
--color-text-secondary: #616161;
--color-text-muted: #9E9E9E;
--color-text-disabled: #BDBDBD;

--color-status-complete: #4CAF50;
--color-status-progress: #FF9800;
--color-status-error: #F44336;
--color-status-idle: #9E9E9E;

--color-hover-bg: #F5F5F5;
--color-selected-bg: #FFF3E0;
--color-danger-bg: #F44336;
--color-danger-text: #FFFFFF;
--color-warning-bg: #FFF3E0;

--font-family: JetBrains Mono, monospace;
--font-size-h2: 18px;
--font-size-body: 14px;
--font-size-small: 13px;
--font-size-xs: 12px;

--border-radius: 0px;
--transition-fast: 150ms ease;
--transition-normal: 200ms ease;
--transition-slow: 300ms ease;

---

## 7. CODE MAPPING

### 7.1 Reusable from HistoryDatabase.vue

getProgressClass(simulation)  --> no changes
formatDate(dateStr)           --> no changes
formatTime(dateStr)           --> no changes
truncateText(text, maxLength) --> no changes
getSimulationTitle(req)       --> no changes
formatSimulationId(id)        --> no changes
formatRounds(simulation)      --> no changes
navigateToProject(project)    --> rename to navigateToSimulation

### 7.2 New Functions

toggleSelectAll()
toggleSelect(simulationId)
sortSimulations(field, dir)
deleteSimulation(id)          --> API call single delete
deleteBulk(ids[])             --> API call batch delete
deleteProject(projectId)      --> API call cascade delete
openDeleteModal(type, data)   --> type: single/bulk/project
closeDeleteModal()
getStageIcons(project)        --> map project_id/report_id to diamonds

### 7.3 New API Endpoints (backend)

DELETE /api/simulation/{simulation_id}
DELETE /api/simulation/bulk         body: { simulation_ids: [...] }
DELETE /api/project/{project_id}    cascade: project + sims + reports + Neo4j

---

## 8. EDGE CASES

### 8.1 Long simulation name
Truncate with ... in table, full name in tooltip and modal

### 8.2 Deleting last simulation
Table fades out, empty state appears
Delete Project button remains visible

### 8.3 Delete while simulation running
Extra warning in modal:
  Simulyaciya vypolnyaetsya. Udalenie prervyot vypolnenie.
Button text changes to: Prervat i udalit

### 8.4 Network error during delete
Spinner stops, modal stays open
Inline error in modal:
  [!] Ne udalos udalit. Poprobujte snova.
Button changes to: Povtorit

### 8.5 Russian pluralization
1 simulyaciya   --> Udalit 1 simulyaciyu?
2 simulyacii    --> Udalit 2 simulyacii?
5 simulyacij    --> Udalit 5 simulyacij?
21 simulyaciya  --> Udalit 21 simulyaciyu?

Function: pluralize(n, [simulyaciyu, simulyacii, simulyacij])
