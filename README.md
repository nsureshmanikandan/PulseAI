# PulseAI — Enterprise Data Analytics Dashboard

Multi-tab Excel analysis with AI-powered insights, Executive/Analyst tiered views, and GPT-4o chat via Accenture GenAI Gateway.

---

## Prerequisites

- Python 3.13
- Node.js 18+

---

## Setup

### 1. Clone & configure environment

```powershell
cd C:\Users\n.sureshmanikandan\Repo1\PulseAI
copy .env.example .env   # already done — .env is pre-configured
```

`.env` is already configured for local dev (SQLite, lbpass gateway). No changes needed.

### 2. Install Python dependencies

```powershell
# From project root (PulseAI\)
pip install -r backend\requirements.txt
```

### 3. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

---

## Running Locally

Open **two separate terminal windows**, both starting from the project root `C:\Users\n.sureshmanikandan\Repo1\PulseAI`.

### Terminal 1 — Backend API

```powershell
cd C:\Users\n.sureshmanikandan\Repo1\PulseAI
python -m uvicorn backend.main:app --reload --port 8000
```

> **Important:** Always run from the project root, not from inside `backend\`. The `backend.main` module path requires the parent directory on `sys.path`.
>
> Do **not** use `uvicorn backend.main:app` directly — the `uvicorn` script on PATH may point to a stale Python install. Use `python -m uvicorn` instead.

Verify the backend is up:

```
http://localhost:8000/health   → {"status": "ok"}
http://localhost:8000/docs     → Swagger UI
```

### Terminal 2 — Frontend

```powershell
cd C:\Users\n.sureshmanikandan\Repo1\PulseAI\frontend
npm run dev
```

Open the app at **http://localhost:5173**

---

## Running Tests

```powershell
# From project root
python -m pytest backend/tests/ -v
```

All 43 tests should pass. SQLite is used automatically — no database setup required.

---

## Project Structure

```
PulseAI/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (reads .env)
│   ├── models/db.py             # SQLAlchemy models
│   ├── api/routes/              # datasets, analytics, ai, websocket
│   ├── modules/
│   │   ├── analytics/           # stats_engine, kpi_extractor, chart_builder
│   │   ├── ai/                  # llm_factory, narrative, insight_engine
│   │   └── excel/               # parser, schema_detector, relationship_finder
│   ├── storage/adapter.py       # local / Azure Blob / S3
│   ├── workers/tasks.py         # Celery upload pipeline
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/               # ExecutiveDashboard, AnalystWorkbench, AIChat, DataSources
│   │   ├── components/          # charts, tables, ai, layout
│   │   ├── hooks/               # useDataset, useWebSocket
│   │   └── store/useAppStore.ts # Zustand store
│   └── index.html
├── .env                         # Local dev config (not committed)
├── .env.example                 # Template
└── docker-compose.yml           # Full stack with PostgreSQL + Redis
```

---

## Environment Variables

| Variable | Description | Local default |
|---|---|---|
| `LLM_PROVIDER` | `azure_openai` / `openai` / `claude` | `azure_openai` |
| `LBPASS_API_KEY` | Accenture lbpass API key | set in `.env` |
| `AZURE_OPENAI_ENDPOINT` | Gateway base URL | set in `.env` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o` |
| `DATABASE_URL` | SQLite for local, Postgres for prod | `sqlite:///./pulseai.db` |
| `REDIS_URL` | Redis (required for Celery) | `redis://localhost:6379/0` |
| `STORAGE_BACKEND` | `local` / `azure` / `s3` | `local` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |

---

## Docker (full stack)

```powershell
docker compose up --build
```

Starts backend, frontend, PostgreSQL, and Redis. App available at **http://localhost:3000**.
