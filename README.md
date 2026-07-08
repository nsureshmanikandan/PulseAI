# PulseAI — Enterprise Data Analytics Dashboard

> **Turn raw Excel & CSV data into decisions — instantly.**
> Upload any file, get AI-powered dashboards, interactive charts, and GPT-4o chat in under 2 minutes. No SQL. No code. No BI tool training.

Built with **React 18 + FastAPI + GPT-4o** via Azure GenAI Gateway.

---

## What PulseAI Does

| Feature | Description |
|---|---|
| **Executive Dashboard** | Auto-generates KPI cards, AI narrative, and 6 chart types from any uploaded dataset |
| **Analyst Workbench** | Point-and-click custom chart builder — bar, scatter, histogram, box plot, heatmap, pie/donut |
| **AI Chat** | Ask questions in plain English — get formatted tables, insights, and analysis via GPT-4o |
| **Multi-Tab Excel** | All sheets loaded simultaneously; tab switcher in the top bar |
| **FK Relationships** | Auto-detects foreign key links between Excel tabs (e.g. `customer_id` across 3 sheets) |
| **Suggested Questions** | 10 dataset-specific questions generated per tab — summary, ranking, filter, cross-tab, trend |
| **Use Cases** | Pre-built demos for Banking, Insurance, Retail, and HR analytics |

---

## Screenshots

| Executive Dashboard | AI Chat with Tables | Data Sources |
|---|---|---|
| KPI cards + AI narrative + 6 auto-charts | GFM tables with zebra rows, NLP summary | Dark theme, tab pills, FK relationship map |

---

## Industry Use Cases

### Banking & Financial Services — Loan Portfolio Risk
Upload `Banking_LoanPortfolio.xlsx` and ask:
- *"Show all loans where dpd > 60 as a table"*
- *"Top 10 customers by outstanding balance"*
- *"Cross-tab: loan_type vs loan_status"*
- *"What % of loans are in Default or Watch status?"*
- *"Correlation between credit_score and outstanding_balance"*

### Insurance — Claims Analytics & Fraud Detection
Upload `Insurance_Claims.xlsx` and ask:
- *"Show claims where amount > 50000 as a table"*
- *"Which claimants appear more than 3 times?"*
- *"Group by claim_type and show average payout"*
- *"Are there outliers in claim processing time?"*
- *"Distribution of claim amounts by region"*

### Retail & E-Commerce — Sales Performance
Upload `Retail_Sales.xlsx` (3 tabs: Sales, Products, Returns) and ask:
- *"Top 10 products by revenue as a table"*
- *"Region vs category cross-tab breakdown"*
- *"Which products have return rate above average?"*
- *"Month-over-month revenue trend"*
- *"Correlation between discount and units sold"*

### HR & Workforce — People Analytics & Attrition
Upload `HR_Workforce.xlsx` (3 tabs: Employees, Performance, Attrition) and ask:
- *"Show employees with tenure < 1 year and low rating"*
- *"Salary distribution by grade and department"*
- *"Which departments have highest attrition rate?"*
- *"Cross-tab: gender vs promotion rate"*
- *"Are there compensation outliers by role?"*

---

## Test Data

Ready-to-use demo files in `test_data/`:

| File | Rows / Tabs | Use Case |
|---|---|---|
| `Banking_LoanPortfolio.xlsx` | 300 rows, 1 tab | Loan risk, DPD, credit scores, collateral |
| `Insurance_Claims.xlsx` | 400 rows, 1 tab | Claims, fraud flags, processing time |
| `Retail_Sales.xlsx` | 800 + 100 + 120 rows, 3 tabs | Sales, Products, Returns with FK link |
| `HR_Workforce.xlsx` | 500 + 1500 + 80 rows, 3 tabs | Employees, Performance, Attrition |
| `FinanceData_MultiTab.xlsx` | 2,530 rows, 6 tabs | Full FK relationship demo (finance) |
| `PulseAI_Presentation.pptx` | 13 slides | Enterprise deck for customer briefings |

---

## Prerequisites

- Python 3.13
- Node.js 18+

---

## Setup

### 1. Clone & configure environment

```powershell
cd C:\Users\n.sureshmanikandan\Repo1\PulseAI
copy .env.example .env
```

`.env` is pre-configured for local dev (SQLite + lbpass gateway). No changes needed.

### 2. Install Python dependencies

```powershell
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

Open **two terminal windows** from the project root.

### Terminal 1 — Backend API

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Verify:
```
http://localhost:8000/health   →  {"status": "ok"}
http://localhost:8000/docs     →  Swagger UI (all API endpoints)
```

> Always run from the **project root**, not from inside `backend\`. Use `python -m uvicorn` (not `uvicorn` directly).

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

Open **http://localhost:5173**

---

## Key AI Chat Capabilities

| Question Type | Example |
|---|---|
| **Summary stats** | *"Summarize this dataset"* |
| **Ranking table** | *"Top 10 loans by outstanding balance"* |
| **Filtered table** | *"Show all claims where amount > 50000"* |
| **Group-by** | *"Group by loan_type and show average balance"* |
| **Cross-tab** | *"Cross-tab: segment vs loan_status"* |
| **Correlation** | *"Correlation between credit_score and balance"* |
| **Outlier detection** | *"Are there outliers in processing_days?"* |
| **Trend** | *"Month-over-month revenue trend"* |
| **Above/below average** | *"Show employees with salary above average"* |
| **Segment breakdown** | *"Distribution of loan_type by city"* |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/datasets/` | List all uploaded datasets |
| `POST` | `/api/datasets/upload` | Upload Excel or CSV file |
| `GET` | `/api/datasets/{id}` | Get dataset with tab names |
| `GET` | `/api/datasets/{id}/relationships` | Auto-detected FK relationships between tabs |
| `DELETE` | `/api/datasets/{id}` | Delete dataset |
| `GET` | `/api/analytics/{id}/kpis/{tab}` | KPI cards for a tab |
| `GET` | `/api/analytics/{id}/auto-charts/{tab}` | Auto-generated chart configs |
| `GET` | `/api/ai/{id}/narrative/{tab}` | GPT-4o AI narrative summary |
| `GET` | `/api/ai/{id}/insights/{tab}` | Auto-detected anomalies & insights |
| `GET` | `/api/ai/{id}/suggested-questions/{tab}` | 10 suggested AI Chat questions |
| `WS` | `/ws/chat/{id}/{tab}` | WebSocket AI Chat (streaming) |

---

## Project Structure

```
PulseAI/
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Settings (reads .env)
│   ├── models/db.py                   # SQLAlchemy models (Dataset, TabProfile, TabRelationship)
│   ├── api/routes/
│   │   ├── datasets.py                # Upload, list, get, delete, relationships
│   │   ├── analytics.py               # KPIs, auto-charts (6 types, 12-color palette)
│   │   ├── ai.py                      # Narrative, insights, suggested questions
│   │   └── websocket.py               # AI Chat (table-intent detection, DataFrame pre-filter)
│   ├── modules/
│   │   ├── analytics/
│   │   │   ├── stats_engine.py        # Column stats, outlier detection
│   │   │   ├── kpi_extractor.py       # Sum/avg/min/max per numeric column
│   │   │   └── chart_builder.py       # Histogram, scatter, heatmap, bar, donut, box
│   │   ├── ai/
│   │   │   ├── llm_factory.py         # Pluggable LLM (Azure OpenAI / OpenAI / Claude)
│   │   │   ├── narrative.py           # GPT-4o dataset narrative generator
│   │   │   └── insight_engine.py      # Anomaly & outlier detection
│   │   └── ingestion/
│   │       ├── parser.py              # Multi-tab Excel + CSV parser
│   │       ├── schema_detector.py     # Column type & category detection
│   │       └── relationship_finder.py # FK detection between tabs
│   ├── storage/adapter.py             # Local / Azure Blob / S3
│   ├── workers/tasks.py               # Upload pipeline (parse → schema → relationships → insights)
│   └── tests/                         # 43 pytest tests
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ExecutiveDashboard/    # KPIs + AI narrative + 6 auto-charts
│   │   │   ├── AnalystWorkbench/      # Custom chart builder
│   │   │   ├── AIChat/                # WebSocket chat + GFM table rendering
│   │   │   ├── DataSources/           # Upload manager + FK relationship viewer
│   │   │   ├── UseCases/              # Banking / Insurance / Retail / HR demos
│   │   │   └── ROIBenefits/           # ROI stats + persona benefit cards
│   │   ├── components/
│   │   │   ├── layout/                # Sidebar (grouped nav), TopBar (tab switcher)
│   │   │   ├── ai/                    # NarrativeSummary, InsightCard
│   │   │   └── filters/               # FilterBar
│   │   ├── hooks/
│   │   │   ├── useDataset.ts          # Dataset CRUD + async tab healing
│   │   │   ├── useWebSocket.ts        # AI Chat WebSocket
│   │   │   └── useHealActiveTab.ts    # Self-healing active tab on page load
│   │   └── store/useAppStore.ts       # Zustand global state
│   └── index.html
├── scripts/
│   ├── generate_finance_excel.py      # Generates FinanceData_MultiTab.xlsx (6 tabs)
│   ├── generate_usecase_data.py       # Generates 4 use-case Excel files
│   └── generate_ppt.py                # Generates 13-slide enterprise PPT
├── test_data/                         # Ready-to-use demo files
├── docs/                              # Design spec & implementation plan
├── .env.example                       # Environment variable template
└── docker-compose.yml                 # Full stack (backend + frontend + PostgreSQL + Redis)
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | `azure_openai` / `openai` / `claude` | `azure_openai` |
| `LBPASS_API_KEY` | Azure GenAI Gateway API key | set in `.env` |
| `AZURE_OPENAI_ENDPOINT` | Gateway base URL | set in `.env` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o` |
| `DATABASE_URL` | SQLite for local, Postgres for prod | `sqlite:///./pulseai.db` |
| `STORAGE_BACKEND` | `local` / `azure` / `s3` | `local` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |

---

## Running Tests

```powershell
python -m pytest backend/tests/ -v
```

43 tests covering parsers, schema detection, relationship finder, stats engine, chart builder, and API routes.

---

## Docker (full stack)

```powershell
docker compose up --build
```

Starts backend (port 8000), frontend (port 3000), PostgreSQL, and Redis.

---

## ROI at a Glance

| Metric | Value |
|---|---|
| Time to first insight | < 2 minutes from upload |
| Code required | Zero — no SQL, Python, or BI tool |
| Chart types auto-generated | 6 (histogram, bar, scatter, heatmap, box, donut) |
| AI questions per tab | 10 suggested + unlimited free-form |
| Excel tabs supported | Unlimited (tested with 6-tab, 2,530-row file) |
| AI engine | GPT-4o via Azure GenAI Gateway |

---

## Tech Stack

**Frontend:** React 18 · TypeScript · Vite · Tailwind CSS · Plotly.js · Zustand · remark-gfm

**Backend:** FastAPI · Python 3.13 · SQLAlchemy · pandas 2.2 · openpyxl 3.1.5 · Uvicorn

**AI:** GPT-4o · Azure lbpass GenAI Gateway · WebSocket streaming

**Data:** SQLite (local) · PostgreSQL (prod) · Local file storage (swappable to Azure Blob / S3)

---

*Powered by GPT-4o · Azure GenAI Gateway · Built on React + FastAPI*
