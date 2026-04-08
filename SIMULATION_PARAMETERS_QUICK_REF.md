# Simulation Pipeline - Quick Reference

## Configurable Parameters at a Glance

### 1. Agent Count
- **How to control:** Filter by `entity_types` in prepare_simulation API
- **Parallelization:** `parallel_profile_count` (default: 5)
- **Formula:** num_agents = count of extracted entities with profiles
- **Min test:** entity_types: ["Person"], parallel_profile_count: 2

### 2. Simulation Rounds
- **Parameter:** `OASIS_DEFAULT_MAX_ROUNDS`
- **Default:** 10
- **Set via:** Environment variable or API payload `max_rounds`
- **Min test:** OASIS_DEFAULT_MAX_ROUNDS=2

### 3. Document Chunking
- **chunk_size:** 500 (characters) - set in POST /api/graph/build
- **chunk_overlap:** 50 (characters) - set in POST /api/graph/build
- **Affects:** Number of embedding calls and NER extractions

### 4. Entity Extraction
- **Method:** LLM-based NER (Named Entity Recognition)
- **Limit:** None (extracts all detected entities)
- **Cost:** 1 LLM call per chunk

---

## API Request Payloads

### Create Simulation
```json
POST /api/simulation
{
  "project_id": "proj_xxx",       // REQUIRED
  "graph_id": "jaypolymind_xxx",  // optional
  "enable_twitter": true,          // optional
  "enable_reddit": true            // optional
}
```

### Prepare Simulation (ASYNC)
```json
POST /api/simulation/prepare
{
  "simulation_id": "sim_xxx",              // REQUIRED
  "entity_types": ["Person"],              // optional (FILTERS AGENTS)
  "use_llm_for_profiles": true,           // optional
  "parallel_profile_count": 2,            // optional (default: 5)
  "force_regenerate": false               // optional
}
```

### Run Simulation
```json
POST /api/simulation/run
{
  "simulation_id": "sim_xxx",    // REQUIRED
  "max_rounds": 2                // optional (overrides default)
}
```

---

## Performance Costs

| Operation | LLM Calls | Embeddings | Notes |
|-----------|-----------|-----------|-------|
| Build graph | N/A (NER done per chunk) | 1 per chunk | Bottleneck: embedding + NER |
| Prepare sim | 1 per agent | 0 | Generate profiles |
| Run sim | 1 per agent per round | 0 | Interview loop |
| **Total** | **num_agents × (1 + rounds)** | **ceil(doc_size/500)** | Linear in agents & rounds |

---

## Minimal Test Configuration

### Environment
```bash
OASIS_DEFAULT_MAX_ROUNDS=2
LLM_MODEL_NAME=qwen2.5:32b
EMBEDDING_MODEL=openai/text-embedding-3-small
```

### API Sequence (5 steps)
1. **POST /api/graph/build** (small doc, chunk_size=500)
2. **POST /api/simulation** (minimal platforms)
3. **POST /api/simulation/prepare** (entity_types: ["Person"], parallel_count: 2)
4. **GET /api/simulation/prepare/status** (monitor task_id)
5. **POST /api/simulation/run** (max_rounds: 2)

**Expected: ~5-10 LLM calls total for test**

---

## Key Files

- **Config defaults:** `backend/app/config.py`
- **API endpoints:** `backend/app/api/simulation.py`
- **Profile generation:** `backend/app/services/oasis_profile_generator.py`
- **Entity extraction:** `backend/app/storage/ner_extractor.py`
- **Execution:** `backend/app/services/simulation_runner.py`

---

## Optimization Tips

1. **Reduce agents:** Use `entity_types` to filter (e.g., only "Person")
2. **Reduce rounds:** Set `OASIS_DEFAULT_MAX_ROUNDS=2` for testing
3. **Reduce embeddings:** Increase `chunk_size` to 1000+ (fewer chunks)
4. **Parallel speed:** Increase `parallel_profile_count` to 10 (but increases LLM calls)

