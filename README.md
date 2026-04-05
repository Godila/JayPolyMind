<div align="center">

# JayPolyMind

**Simulate public opinion before you publish.**

*Upload any document — press release, policy draft, product pitch — and get hundreds of AI agents with unique personalities reacting to it in real time.*

[![GitHub Stars](https://img.shields.io/github/stars/Godila/JayPolyMind?style=flat-square&color=DAA520)](https://github.com/Godila/JayPolyMind/stargazers)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](./LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-jpm.haragy.top-38BDF8?style=flat-square)](https://jpm.haragy.top/)

</div>

## What is JayPolyMind?

JayPolyMind is a multi-agent swarm intelligence engine that turns any document into a living simulation of public reaction. Before you launch — see how different audience segments will respond, what objections they'll raise, and how sentiment evolves over time.

**Live demo:** [jpm.haragy.top](https://jpm.haragy.top/) — demo mode available without registration.

## How it works

### 5-step pipeline

**Step 1 — Graph Build**
Upload a document (PDF, MD, TXT). JayPolyMind extracts entities, facts, and relationships and builds a knowledge graph in Neo4j. This becomes the shared memory for all agents.

**Step 2 — Env Setup**
The system generates agent personas — each with a unique psychological profile, opinion bias, profession, age, MBTI, and reaction pattern. You can also add custom agents manually with preset personality archetypes (Skeptic, Enthusiast, Expert, Influencer, Observer) and behavioral toggles.

**Step 3 — Simulation**
Agents interact across two parallel social platforms (Twitter-style feed + Reddit-style community). They post, reply, argue, follow each other, and shift opinions round by round. Sentiment evolution is tracked in real time.

**Step 4 — Report**
A ReportAgent analyzes the simulation, interviews a focus group of agents, searches the knowledge graph, and generates a structured analytical report with section-by-section breakdown and key insights.

**Step 5 — Interaction**
Chat with any agent from the simulation. Ask why they reacted the way they did. Run batch surveys across the agent population. The ReportAgent answers follow-up questions with full access to the graph and simulation data.

## Key features

- **Custom agents** — add your own personas before simulation with personality presets and stance/activity toggles
- **Demo mode** — one-click auto-fill with curated scenarios (product launch, regulatory analysis, corporate transformation, communications campaign)
- **ReportAgent chat** — conversational interface with 4 tools: InsightForge, PanoramaSearch, QuickSearch, AgentInterview
- **Real-time timeline** — dual-platform action feed with round-by-round simulation progress
- **Any LLM** — works with Ollama (local), Claude, GPT-4, or any OpenAI-compatible API

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/Godila/JayPolyMind.git
cd JayPolyMind
cp .env.example .env
# Edit .env with your LLM API key and model settings
docker compose up -d
```

Open `http://localhost:3000`.

### Manual

```bash
# 1. Start Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/jaypolymind neo4j:5.18-community

# 2. Backend
cd backend && pip install -r requirements.txt && python run.py

# 3. Frontend
cd frontend && npm install && npm run dev
```

## Configuration

```bash
# .env — copy from .env.example

LLM_API_KEY=your-api-key          # or "ollama" for local
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:32b

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=jaypolymind

EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434

ADMIN_LOGIN=admin
ADMIN_PASSWORD=changeme
```

Compatible with any OpenAI-format API — swap `LLM_BASE_URL` and `LLM_API_KEY` for Claude, GPT, DeepSeek, or any hosted provider.

## Architecture

```
Document → Knowledge Graph (Neo4j) → Agent Profiles → OASIS Simulation → ReportAgent → Interactive Chat
```

- **Storage layer**: Neo4j CE 5.18 with hybrid search (0.7 × vector + 0.3 × BM25)
- **Simulation engine**: [OASIS by CAMEL-AI](https://github.com/camel-ai/oasis) — dual-platform multi-agent simulation
- **LLM interface**: unified OpenAI-compatible client, pluggable provider
- **Frontend**: Vue 3 + Vite, real-time updates via polling
- **Backend**: Flask + blueprint architecture, dependency injection via `app.extensions`

## Hardware

| | Minimum | Recommended |
|---|---|---|
| RAM | 16 GB | 32 GB |
| VRAM | 10 GB (14b model) | 24 GB (32b model) |
| Disk | 20 GB | 50 GB |

CPU-only works but is slower. Use `qwen2.5:14b` or `qwen2.5:7b` for lighter setups.

## Use cases

- **PR & communications** — test how a press release lands with different audience segments before publishing
- **Product launches** — simulate market reaction to pricing, positioning, or feature sets
- **Policy analysis** — model stakeholder responses to draft regulations or corporate policy changes
- **Corporate comms** — forecast employee reaction to organizational changes before rollout
- **Research** — explore opinion dynamics, echo chambers, and sentiment propagation in controlled environments

## License

AGPL-3.0. Simulation engine powered by [OASIS](https://github.com/camel-ai/oasis) from the CAMEL-AI team.
