# Deep Research v2 -- полная архитектура

## Проблемы v1

1. **Данные не доходят до графа**: `enriched_context` влияет только на онтологию, NER работает по оригинальному документу
2. **Нет видимости**: пользователь не видит что происходит во время research
3. **Один раунд**: 8 запросов за 30 сек -- слишком поверхностно
4. **Нет review**: пользователь не может убрать ложные факты до генерации
5. **Citations не персистятся**: после генерации онтологии research данные теряются

## Архитектура v2

### Принцип: research как отдельный async этап с review gate

```
Upload -> Text extraction -> [Deep Research Task] -> [User Review] -> Ontology -> Graph Build -> Neo4j
                                    |                      |                          |
                               3-round search         approve/edit           NER + Citations
                               SearXNG API            findings               injection
```

### Компонент 1: Итеративный research pipeline

**Файл**: `backend/app/services/deep_research.py` (переписать)

3 раунда поиска вместо одного:

| Раунд | Вход | LLM вызов | Поиск | Выход |
|-------|------|-----------|-------|-------|
| 1 | Документ (8000 chars) + requirement | Генерация 8 запросов | 8 parallel | key_claims + results |
| 2 | Результаты R1 + gaps | Follow-up 4-6 запросов | 4-6 parallel | confirmed + new gaps |
| 3 | Результаты R1+R2 + remaining gaps | Final 2-4 запросов | 2-4 parallel | final findings |
| Синтез | Все результаты | Объединение + citations | -- | ResearchResult |

**Итого**: 4 LLM вызова + 14-18 поисковых запросов, ~60-90 секунд.

```python
class IterativeResearchPipeline:
    """3-раундовый research с анализом пробелов"""

    MAX_DOC_PREVIEW = 8000  # больше контекста для лучших запросов
    MAX_ROUNDS = 3

    async def execute(self, document_texts, requirement) -> ResearchResult:
        # Раунд 1: начальные запросы
        round1 = self._generate_queries(document_texts, requirement)
        round1_results = self._parallel_search(round1.queries)

        # Раунд 2: анализ пробелов + follow-up
        gaps = self._analyze_gaps(round1.key_claims, round1_results)
        round2_queries = self._generate_followup(gaps)
        round2_results = self._parallel_search(round2_queries)

        # Раунд 3: финальные уточнения
        remaining_gaps = self._analyze_gaps(round1.key_claims,
                                             round1_results + round2_results)
        if remaining_gaps:
            round3_queries = self._generate_followup(remaining_gaps)
            round3_results = self._parallel_search(round3_queries)

        # Синтез
        all_results = round1_results + round2_results + round3_results
        return self._synthesize(all_results, round1.key_claims)
```

### Компонент 2: Async task + progress

**Файл**: `backend/app/api/graph.py` (модификация)

Research запускается как TaskManager задача с прогрессом:

```python
# POST /api/graph/ontology/generate
# Вместо синхронного вызова:

if enable_research:
    task_id = task_manager.create_task("deep_research")

    def research_worker():
        pipeline = IterativeResearchPipeline()
        # Каждый раунд обновляет прогресс
        pipeline.on_progress = lambda round, total: \
            task_manager.update_progress(task_id, round / total)
        return pipeline.execute(document_texts, requirement)

    task_manager.run_async(task_id, research_worker)
    return jsonify({"research_task_id": task_id, "status": "researching"})
```

Frontend поллит `GET /api/graph/research/status/{task_id}` и показывает прогресс.

### Компонент 3: Review gate

**Endpoints**:
- `GET /api/graph/research/status/{task_id}` -- статус + прогресс (0-100%)
- `GET /api/graph/research/results/{task_id}` -- findings для review
- `POST /api/graph/research/confirm/{task_id}` -- подтвердить (с опциональным списком excluded findings)
- `DELETE /api/graph/research/finding/{task_id}/{finding_id}` -- удалить конкретный факт

После confirm -- продолжается генерация онтологии с подтвержденными findings.

### Компонент 4: Neo4j Citation nodes (вариант C)

**Файл**: `backend/app/storage/neo4j_storage.py` (добавить методы)

```cypher
-- Создание Citation ноды
CREATE (c:Citation {
    id: $id,
    fact: $fact,
    source_url: $source_url,
    source_title: $source_title,
    confidence: $confidence,
    status: $status,  -- confirmed/contradicted/unverified
    created_at: datetime()
})

-- Связь с Entity
MATCH (e:Entity {name: $entity_name})
MATCH (c:Citation {id: $citation_id})
CREATE (e)-[:SOURCED_FROM {relation_type: $type}]->(c)
```

Связи создаются на этапе синтеза: LLM определяет какие entities упоминаются в каждом факте.

### Компонент 5: NER enrichment

**Файл**: `backend/app/storage/ner_extractor.py` (модификация промпта)

Добавить `research_facts` секцию в системный промпт NER:

```python
# В _SYSTEM_PROMPT добавить:
"""
## Verified Facts from Web Research
The following facts were verified through web search. If the text chunk
references any of these entities or facts, extract them even if the mention
is indirect:

{research_facts}
"""
```

Это позволяет NER находить сущности упомянутые в research, даже если документ упоминает их косвенно.

### Компонент 6: Report agent tool

**Файл**: `backend/app/services/graph_tools.py` (добавить инструмент)

```python
class CitationSearchTool:
    """Поиск citations для entity"""
    name = "get_entity_citations"
    description = "Find web sources that verify or contradict facts about an entity"

    def execute(self, entity_name: str) -> str:
        query = """
        MATCH (e:Entity)-[r:SOURCED_FROM]->(c:Citation)
        WHERE e.name CONTAINS $name
        RETURN c.fact, c.source_url, c.source_title, c.confidence, c.status
        """
        results = self.storage.query(query, {"name": entity_name})
        return self._format_citations(results)
```

### Компонент 7: Frontend -- StepResearch.vue

**Файл**: `frontend/src/components/StepResearch.vue` (новый)

Этап между загрузкой файлов и graph build:

```
+------------------------------------------+
| Deep Research                    Round 2/3 |
| ========================================== |
|                                            |
| [=============================>    ] 72%   |
| Searching: "JPMorgan CEO succession"       |
|                                            |
| Findings (12):                             |
| +----------------------------------------+ |
| | [x] Jamie Dimon is CEO of JPMorgan     | |
| |     Source: reuters.com | Confirmed     | |
| +----------------------------------------+ |
| | [x] Revenue was $130B in 2023          | |
| |     Source: wsj.com | Confirmed         | |
| +----------------------------------------+ |
| | [ ] Company founded in 1799            | |
| |     Source: wikipedia.org | Unverified  | |
| +----------------------------------------+ |
|                                            |
| [Skip Research]  [Confirm & Continue ->]   |
+------------------------------------------+
```

## Промпты (подробно)

### Промпт 1: Генерация запросов (Раунд 1)

```
You are a research analyst preparing to verify claims in a document.

DOCUMENT (first 8000 chars):
{document_preview}

SIMULATION REQUIREMENT:
{simulation_requirement}

Analyze the document and generate search queries to verify its claims.

Return JSON:
{
  "key_claims": [
    {"claim": "...", "importance": "high/medium", "category": "fact/person/org/date/financial"}
  ],
  "entities_to_verify": [
    {"name": "...", "type": "person/org/product", "context": "mentioned as..."}
  ],
  "search_queries": [
    {"query": "...", "language": "en/ru/...", "target": "which claim this verifies"}
  ]
}

Rules:
- Generate queries in BOTH the document's language AND English
- Focus on verifiable factual claims, not opinions
- Prioritize: people's roles/titles, financial figures, dates, org relationships
- Max 8 queries, each targeting a specific claim
```

### Промпт 2: Анализ пробелов (Раунды 2-3)

```
You are analyzing research progress to identify gaps.

ORIGINAL CLAIMS:
{key_claims}

SEARCH RESULTS SO FAR:
{accumulated_results}

Determine:
1. Which claims are now CONFIRMED (with source)?
2. Which claims are CONTRADICTED (with counter-evidence)?
3. Which claims remain UNVERIFIED (no relevant results)?

Return JSON:
{
  "confirmed": [{"claim": "...", "source_url": "...", "source_title": "..."}],
  "contradicted": [{"claim": "...", "counter_evidence": "...", "source_url": "..."}],
  "unresolved_gaps": ["claim that needs more search"],
  "follow_up_queries": [
    {"query": "...", "language": "...", "target_gap": "which unresolved claim"}
  ]
}

Rules:
- Only mark as confirmed if source explicitly supports the claim
- Generate 4-6 follow-up queries for unresolved gaps
- Try different search angles (synonym, related org, news vs wiki)
```

### Промпт 3: Синтез

```
You are synthesizing web research findings into a structured report.

ALL SEARCH RESULTS:
{all_results}

ORIGINAL CLAIMS:
{key_claims}

Create a comprehensive research report.

Return JSON:
{
  "findings": [
    {
      "id": "f1",
      "fact": "verified statement",
      "status": "confirmed/contradicted/unverified",
      "confidence": "high/medium/low",
      "source_url": "...",
      "source_title": "...",
      "related_entities": ["entity names mentioned"],
      "original_claim": "which document claim this relates to"
    }
  ],
  "enriched_context": "Narrative summary for ontology generation...",
  "summary": {
    "total_claims": N,
    "confirmed": N,
    "contradicted": N,
    "unverified": N
  }
}
```

## Порядок реализации

| # | Файл | Что | Зависимости |
|---|------|-----|-------------|
| 1 | `deep_research.py` | Переписать: 3-раундовый pipeline | web_search.py (уже есть) |
| 2 | `graph.py` | Async task + research endpoints | deep_research.py |
| 3 | `neo4j_storage.py` | Citation CRUD методы | -- |
| 4 | `neo4j_schema.py` | Citation constraint/index | -- |
| 5 | `ner_extractor.py` | research_facts в промпт | -- |
| 6 | `graph_builder.py` | Передача research_facts в NER | deep_research.py |
| 7 | `graph_tools.py` | CitationSearchTool | neo4j_storage.py |
| 8 | `report_agent.py` | Регистрация citation tool | graph_tools.py |
| 9 | `StepResearch.vue` | Review UI | API endpoints |
| 10 | `Process.vue` | Интеграция StepResearch | StepResearch.vue |

## Оценка сложности

- Backend (шаги 1-8): ~5-7 дней
- Frontend (шаги 9-10): ~2-3 дня
- Тестирование + отладка: ~2 дня
- **Итого**: ~9-12 дней
