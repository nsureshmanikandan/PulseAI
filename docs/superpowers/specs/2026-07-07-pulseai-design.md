# PulseAI — Enterprise Data Dashboard Design Spec

**Date:** 2026-07-07  
**Status:** Approved  
**Tagline:** Real-time pulse of your data

---

## Overview

PulseAI is a generic, domain-agnostic enterprise data analytics platform. Users upload Excel files (multi-tab) or connect persistent data sources, then explore data through auto-generated dashboards, interactive charts, and a natural language AI chat interface powered by PandasAI + Azure OpenAI GPT-4o (configurable).

---

## Users

Two tiers sharing the same app — toggled via a UI switch:

- **Executive view:** KPI cards, summary charts, AI-written narrative, high-level insights
- **Analyst view:** Full drill-down, cross-tab joins, custom charts, pivot-style exploration

No authentication required — shared team access.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Plotly.js, Recharts, AG Grid, Zustand |
| Backend | FastAPI (Python), Celery (async workers) |
| AI | PandasAI SmartDatalake, configurable LLM |
| LLM (default) | Azure OpenAI GPT-4o |
| LLM (switchable) | OpenAI GPT-4o, Anthropic Claude (via env var) |
| Database | PostgreSQL (metadata) |
| Cache / Queue | Redis |
| File Storage | Azure Blob Storage / S3 / local |
| Deployment | Docker Compose (dev), Azure Container Apps (prod) |
| Testing | pytest, Vitest, Playwright |

---

## Architecture — Modular Monolith with Async Workers

```
React SPA
  └── REST + WebSocket
        └── FastAPI Backend
              ├── Ingestion Module
              ├── Analytics Module
              └── AI / PandasAI Module
                    └── Celery Workers (async AI jobs)
                          ├── PostgreSQL
                          ├── Redis
                          └── Azure Blob / S3
```

---

## Backend Modules

### Ingestion
- `parser.py` — openpyxl: parse all Excel tabs into pandas DataFrames
- `schema_detector.py` — auto-classify columns: numeric, categorical, datetime, text
- `relationship_finder.py` — detect cross-tab joins by matching column names/values

### Analytics
- `stats_engine.py` — descriptive stats, distributions, outlier detection
- `chart_builder.py` — generate Plotly-compatible JSON configs
- `kpi_extractor.py` — auto-select top numeric columns for executive KPI cards

### AI
- `pandasai_agent.py` — PandasAI SmartDatalake wrapping all tabs simultaneously
- `insight_engine.py` — auto-run anomaly detection on dataset load
- `narrative.py` — GPT-4o writes 3-sentence data story for executive view
- `streaming.py` — token streaming via WebSocket back to React

---

## LLM Provider — Switchable via Environment Variable

```bash
LLM_PROVIDER=azure_openai   # azure_openai | openai | claude
```

Zero code changes required to swap LLM. Factory pattern in `config.py` handles provider instantiation.

---

## Data Flows

### Upload Flow
1. User uploads .xlsx via UI
2. File stored in Azure Blob / S3
3. Celery task: parse tabs → DataFrames → profile schema
4. Relationship detection across tabs
5. Metadata saved to PostgreSQL
6. Auto-insights triggered
7. WebSocket notifies UI: "Dataset ready"

### AI Chat Flow
1. User asks NL question in ChatPanel
2. FastAPI enqueues Celery task
3. Worker loads DataFrames (Redis cache or re-parsed from storage)
4. PandasAI SmartDatalake.chat(question) → GPT-4o generates + executes pandas code
5. Result: Plotly JSON / DataFrame / text
6. Streamed back via WebSocket
7. React renders chart inline in chat with narrative explanation

### Executive Dashboard Flow
1. Dataset loaded → kpi_extractor selects top numeric KPIs
2. stats_engine computes summaries per tab
3. GPT-4o writes narrative paragraph
4. Dashboard renders: KPI cards + charts + AI narrative

### Analyst Flow
1. User selects columns/tabs/filters manually
2. chart_builder generates Plotly config on demand
3. Cross-tab joins via detected relationships
4. Results cached in Redis (5 min TTL)

---

## Frontend Structure

```
src/
├── pages/
│   ├── ExecutiveDashboard/
│   ├── AnalystWorkbench/
│   ├── AIChat/
│   └── DataSources/
├── components/
│   ├── charts/          # Plotly.js + Recharts wrappers
│   ├── tables/          # AG Grid
│   ├── ai/              # ChatPanel, InsightCard, NarrativeSummary
│   ├── filters/         # Global filter bar
│   └── layout/          # Sidebar, TopBar, TieredToggle
├── store/               # Zustand
├── hooks/               # useDataset, useAIQuery, useWebSocket
└── services/            # Axios client, WebSocket manager
```

---

## PostgreSQL Schema

| Table | Purpose |
|---|---|
| `datasets` | File metadata, blob path, upload time, tab names |
| `tab_profiles` | Per-tab column types, row count, null %, stats |
| `relationships` | Detected cross-tab column links |
| `saved_queries` | User-saved NL queries + chart configs |
| `chat_sessions` | Chat history per dataset |

---

## Docker Services

| Service | Purpose |
|---|---|
| `frontend` | React SPA (Vite → Nginx) |
| `backend` | FastAPI API server |
| `worker` | Celery AI background jobs |
| `redis` | Cache + message queue |
| `postgres` | Metadata store |

---

## Error Handling

- Non-.xlsx / >50MB / password-protected files rejected with clear UI error
- AI query failures return graceful fallback message, never crash UI
- Celery tasks timeout at 60s with user-facing retry option
- Partial tab parse failures: other tabs still load; failed tab marked unavailable
- LLM 429/500: optional retry with fallback provider

---

## Testing Strategy

| Layer | Tool | Scope |
|---|---|---|
| Backend unit | pytest | Parser, schema detector, chart builder |
| Backend integration | pytest + testcontainers | FastAPI routes with real PostgreSQL/Redis |
| AI module | pytest + mocked LLM | PandasAI mocked — no real Azure calls in CI |
| Frontend unit | Vitest + React Testing Library | Components, hooks, store |
| E2E | Playwright | Upload → dashboard → AI chat → chart rendered |

---

## Environment Variables

```bash
# LLM
LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Storage
STORAGE_BACKEND=azure_blob    # azure_blob | s3 | local
AZURE_STORAGE_CONNECTION_STRING=
AWS_S3_BUCKET=

# Data
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# App
MAX_UPLOAD_SIZE_MB=50
CELERY_TASK_TIMEOUT=60
```

---

## Project Location

`C:\Users\n.sureshmanikandan\Repo1\PulseAI`
