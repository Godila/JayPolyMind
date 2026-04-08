# Simulation Pipeline Configuration Reference

## 1. Agent Count Control

**How agents are determined:**
- Agents are created from entities extracted from the knowledge graph
- Number of agents = number of extracted entities with OASIS profiles generated
- Agent count is **NOT directly configurable** — it's derived from the graph

**Indirect controls:**
- `entity_types` parameter in `/api/simulation/prepare` — filters which entity types to generate profiles for
- `parallel_profile_count` (default: 5) — how many profiles to generate in parallel, affects generation speed but not count

**Location:** `backend/app/services/oasis_profile_generator.py`

---

## 2. Rounds Configuration

**Parameter:** `OASIS_DEFAULT_MAX_ROUNDS`

**Default:** 10 rounds

**Override methods:**
1. Environment variable: `OASIS_DEFAULT_MAX_ROUNDS=5`
2. Intelligent LLM generation (default) — system auto-generates based on context
3. Via API payload: `max_rounds` field in run simulation endpoint (if supported)

**Location:** `backend/app/config.py` line showing:
```python
OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
```

---

## 3. Document Processing & Entity Extraction

### Chunk Configuration

| Parameter | Default | Override | Location |
|-----------|---------|----------|----------|
| `chunk_size` | 500 | API param `chunk_size` in `/api/graph/build` | `Config.DEFAULT_CHUNK_SIZE` |
| `chunk_overlap` | 50 | API param `chunk_overlap` | `Config.DEFAULT_CHUNK_OVERLAP` |

### Entity Extraction

- **Method:** LLM-based NER (Named Entity Recognition)
- **Service:** `NER Extractor` calls LLM to extract entities + relationships
- **Entity limit:** None (extracts all detected entities)
- **Process:** Text chunks → embedding → LLM NER → Neo4j graph storage
- **Location:** `backend/app/storage/ner_extractor.py`

---

## 4. Simulation API Endpoint Specifications

### POST /api/simulation (Create Simulation)

```json
{
  "project_id": "proj_xxxx",          // Required
  "graph_id": "jaypolymind_xxxx",     // Optional (defaults to project.graph_id)
  "enable_twitter": true,              // Optional (default true)
  "enable_reddit": true                // Optional (default true)
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_xxxx",
    "project_id": "proj_xxxx",
    "graph_id": "jaypolymind_xxxx",
    "status": "created",
    "enable_twitter": true,
    "enable_reddit": true,
    "created_at": "2025-12-01T10:00:00"
  }
}
```

---

### POST /api/simulation/prepare (Prepare Environment)

**Async operation** — returns immediately with `task_id` to monitor progress

```json
{
  "simulation_id": "sim_xxxx",                   // Required
  "entity_types": ["Student", "PublicFigure"],  // Optional (filters entity types)
  "use_llm_for_profiles": true,                 // Optional (default true)
  "parallel_profile_count": 5,                  // Optional (default 5)
  "force_regenerate": false                     // Optional (default false)
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_xxxx",
    "task_id": "task_xxxx",
    "status": "preparing",
    "message": "Preparation task started",
    "already_prepared": false
  }
}
```

**Preparation steps:**
1. Read and filter entities from knowledge graph
2. Generate OASIS Agent Profile for each entity (with retry mechanism)
3. LLM intelligently generates simulation configuration
4. Save configuration files and preset scripts

---

### GET /api/simulation/entities/<graph_id>

Query knowledge graph entities

**Parameters:**
- `entity_types` (optional): comma-separated list of entity types to filter
- `enrich` (optional, default true): include related edge information

---

## 5. Performance Bottlenecks

### LLM Calls

| Phase | Calls | Per | Total |
|-------|-------|-----|-------|
| Profile generation | 1 | agent | `num_agents` |
| Interview loop | 1 | agent per round | `num_agents × num_rounds` |
| **Total** | — | — | `num_agents × (1 + num_rounds)` |

### Embedding Calls

| Phase | Calls | Per | Notes |
|-------|-------|-----|-------|
| Graph build | 1 | chunk | `ceil(doc_length / chunk_size)` |
| Simulation run | Minimal | — | Graph already built |

**Bottleneck identified:** Graph building stage (chunk embedding + NER extraction)

### Interview Prompt Configuration

```python
INTERVIEW_PROMPT_PREFIX = """Based on your persona, all your past memories and actions, \
reply directly to me with text without calling any tools. Respond in Russian:"""
```

- **Cost:** 1 LLM prompt per agent per round
- **Optimization:** Prefix prevents tool-calling overhead

---

## 6. Minimal Test Configuration

### Environment Variables
```bash
export OASIS_DEFAULT_MAX_ROUNDS=2
export EMBEDDING_MODEL=openai/text-embedding-3-small
```

### API Call Sequence

**Step 1: Create Graph**
```bash
POST /api/graph/build
{
  "project_id": "test_proj",
  "file": "test_doc.txt",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

**Step 2: Create Simulation**
```bash
POST /api/simulation
{
  "project_id": "test_proj",
  "enable_twitter": true,
  "enable_reddit": true
}
```
→ Returns `simulation_id`

**Step 3: Prepare Simulation**
```bash
POST /api/simulation/prepare
{
  "simulation_id": "sim_xxxx",
  "entity_types": ["Person"],        // Single type = fewer agents
  "parallel_profile_count": 2,       // Minimal parallelism
  "force_regenerate": false
}
```
→ Returns `task_id` for async monitoring

**Step 4: Monitor Preparation**
```bash
GET /api/simulation/prepare/status?task_id=task_xxxx
```

**Step 5: Run Simulation**
```bash
POST /api/simulation/run
{
  "simulation_id": "sim_xxxx",
  "max_rounds": 2                    // Override default
}
```

---

## 7. Configuration Files Location

| File | Contains |
|------|----------|
| `backend/app/config.py` | All defaults (chunk size, rounds, LLM config) |
| `backend/app/api/simulation.py` | API endpoint definitions |
| `backend/app/services/simulation_runner.py` | Simulation execution logic |
| `backend/app/services/oasis_profile_generator.py` | Agent profile generation |
| `backend/app/services/simulation_manager.py` | Simulation state management |

---

## 8. Key Configuration Summary

```python
# Config.py defaults
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
OASIS_DEFAULT_MAX_ROUNDS = 10
EMBEDDING_MODEL = "openai/text-embedding-3-small"
LLM_MODEL_NAME = "qwen2.5:32b"

# Prepare simulation defaults
PARALLEL_PROFILE_COUNT = 5
USE_LLM_FOR_PROFILES = True

# Simulation platforms
OASIS_TWITTER_ACTIONS = ['CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST']
OASIS_REDDIT_ACTIONS = ['LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT', ...]
```

