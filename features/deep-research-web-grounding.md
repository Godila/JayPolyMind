# Deep Research: веб-заземление онтологии

## Context

Сейчас при генерации онтологии в JayPolyMind факты берутся **только из загруженных файлов**. LLM сама определяет, что является "источником правды", опираясь исключительно на текст документов. Если документ содержит неточности, устаревшие данные или однобокую информацию -- онтология это воспроизведет.

**Цель**: добавить этап "Deep Research" -- автоматический поиск в интернете перед генерацией онтологии, чтобы:
- Верифицировать ключевые утверждения из документов
- Обогатить сущности реальными данными (должности, связи, даты)
- Добавить citation/provenance для фактов
- Обнаружить упущенных стейкхолдеров и связи

## Точка интеграции

**Между строками 220 и 222 в `graph.py`** -- после извлечения текста, до вызова `OntologyGenerator.generate()`.

Результат research подается через уже существующий параметр `additional_context` (строка 171 `ontology_generator.py`). **Сам ontology_generator.py менять не нужно.**

```
Files -> FileParser -> TextProcessor -> [DeepResearchService] -> OntologyGenerator -> GraphBuilder
                                              |
                                        Tavily / DuckDuckGo API
```

## Новые файлы

### 1. `backend/app/services/web_search.py` (~120 строк)

Абстракция поиска по паттерну GraphStorage (abstract base + concrete):

```python
class SearchResult:
    title: str
    url: str
    content: str       # извлеченный текст страницы
    score: float
    published_date: Optional[str]

class WebSearchClient(ABC):
    def search(query, max_results=5, search_depth="basic") -> List[SearchResult]

class SearXNGSearchClient(WebSearchClient):    # primary -- self-hosted metasearch
class DuckDuckGoSearchClient(WebSearchClient): # fallback (бесплатный)

def create_search_client() -> WebSearchClient:
    # SearXNG если SEARXNG_URL задан, иначе DuckDuckGo
```

**Почему SearXNG**: self-hosted, агрегирует 70+ поисковых движков, Docker-образ, JSON API, никаких API-ключей, никаких лимитов. DuckDuckGo как fallback без Docker.

### 2. `backend/app/services/deep_research.py` (~250 строк)

Основной сервис исследования:

```python
class ResearchResult:
    enriched_context: str           # текст для additional_context
    citations: List[Dict[str,str]]  # [{fact, source_url, source_title}]
    queries_used: List[str]
    total_sources: int

class DeepResearchService:
    def research(document_texts, simulation_requirement,
                 max_queries=8, max_results_per_query=3) -> ResearchResult
```

**Пайплайн внутри research()**:

1. **Генерация запросов** (1 вызов LLM, chat_json, temp=0.3):
   - Вход: первые 5000 символов документа + simulation_requirement
   - Выход: `{key_claims: [...], entities_to_verify: [...], search_queries: [...]}`
   - До 8 поисковых запросов

2. **Параллельный веб-поиск** (ThreadPoolExecutor, 5 workers):
   - По паттерну `graph_builder.py:add_text_batches()` (строки 185-254)
   - Каждый запрос -- единица работы
   - До 3 результатов на запрос

3. **Дедупликация** по URL

4. **Синтез** (1 вызов LLM, chat_json, temp=0.2, max_tokens=4096):
   - Вход: результаты поиска (до 15K символов) + ключевые утверждения документа
   - Выход: структурированный enriched_context + citations
   - Формат: факт -> подтверждение/опровержение -> источник

## Изменения в существующих файлах

### 3. `backend/app/config.py` -- добавить конфиг (после строки 76)

```python
SEARXNG_URL = os.environ.get('SEARXNG_URL', 'http://searxng:8080')
DEEP_RESEARCH_ENABLED = os.environ.get('DEEP_RESEARCH_ENABLED', 'false').lower() == 'true'
DEEP_RESEARCH_MAX_QUERIES = int(os.environ.get('DEEP_RESEARCH_MAX_QUERIES', '8'))
DEEP_RESEARCH_MAX_RESULTS = int(os.environ.get('DEEP_RESEARCH_MAX_RESULTS', '3'))
```

### 4. `backend/app/api/graph.py` -- вставка research между строками 220-222

```python
# --- Deep Research (optional) ---
enable_research = request.form.get('enable_research', '').lower()
if enable_research == 'true' or (enable_research == '' and Config.DEEP_RESEARCH_ENABLED):
    try:
        from ..services.deep_research import DeepResearchService
        researcher = DeepResearchService()
        research_result = researcher.research(
            document_texts=document_texts,
            simulation_requirement=simulation_requirement
        )
        if research_result.enriched_context:
            additional_context = (additional_context or '') + \
                f"\n\n## Web Research Findings\n\n{research_result.enriched_context}"
        project.research_citations = research_result.citations
        project.research_queries = research_result.queries_used
    except Exception as e:
        logger.warning(f"Deep Research failed, continuing without: {e}")
```

**Критично**: research обернут в try/except -- падение НЕ блокирует генерацию онтологии.

### 5. `backend/app/models/project.py` -- добавить поля

```python
research_citations: Optional[List[Dict[str, str]]] = None
research_queries: Optional[List[str]] = None
```

+ обновить `to_dict()` и `from_dict()`

### 6. `.env.example` -- документировать переменные

```env
# Deep Research (optional web grounding)
SEARXNG_URL=http://searxng:8080
DEEP_RESEARCH_ENABLED=false
```

### 7. `docker-compose.prod.yml` / `docker-compose.yml` -- SearXNG сервис

```yaml
searxng:
  image: searxng/searxng:latest
  environment:
    SEARXNG_BASE_URL: http://searxng:8080/
  volumes:
    - searxng_data:/etc/searxng
  networks:
    - app-net
  restart: unless-stopped
```

### 8. `requirements.txt` -- зависимости

```
duckduckgo-search>=6.0.0   # fallback only, SearXNG uses requests (already installed)
```

### 9. Frontend -- toggle в форме загрузки

Добавить чекбокс "Enable Deep Research" в форму. При включении: `formData.append('enable_research', 'true')`. Опционально: отображение citations в результатах.

## Порядок реализации

1. `web_search.py` -- абстракция поиска (тестируется изолированно)
2. `deep_research.py` -- сервис исследования
3. `config.py` -- конфигурация
4. `.env.example` + `docker-compose.prod.yml` -- env переменные
5. `requirements.txt` -- зависимости
6. `project.py` -- расширение модели
7. `graph.py` -- интеграция в эндпоинт
8. Frontend -- toggle + отображение citations

## Производительность

| Этап | Время |
|------|-------|
| Генерация запросов (LLM) | ~3-5 сек |
| 8 параллельных поисков | ~5-10 сек |
| Синтез (LLM) | ~5-10 сек |
| **Итого overhead** | **~15-25 сек** |

Допустимо: генерация онтологии -- разовая операция, а graph build после нее занимает минуты.

## Бюджет

- SearXNG: 0 стоимости, self-hosted, без лимитов
- DuckDuckGo fallback: 0 стоимости
- LLM вызовы: 2 на генерацию (запросы + синтез) -- через тот же LLM_API_KEY

## Верификация

1. Запустить `web_search.py` standalone с тестовым запросом
2. Запустить `deep_research.py` с тестовым документом, проверить enriched_context
3. POST `/graph/ontology/generate` с `enable_research=true`, сравнить онтологию с/без research
4. Тест деградации: невалидный TAVILY_API_KEY -- онтология генерируется без research
5. Проверить citations в ответе API и в project.json
