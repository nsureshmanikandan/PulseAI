# PulseAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build PulseAI — an enterprise-ready, AI-powered multi-tab Excel analytics dashboard with NL chat, auto-insights, executive + analyst views, and a switchable LLM backend.

**Architecture:** Modular FastAPI monolith with Celery async workers handles ingestion, analytics, and PandasAI queries. React SPA with Zustand state connects via REST + WebSocket for streaming AI responses. PostgreSQL stores metadata; Redis handles caching and the Celery message queue.

**Tech Stack:** React 18 + Vite + Plotly.js + AG Grid + Zustand | FastAPI + Celery + PandasAI + openpyxl + SQLAlchemy | PostgreSQL 16 + Redis 7 | Azure Blob Storage | Docker Compose | pytest + Vitest + Playwright

---

## File Map

```
PulseAI/
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── ExecutiveDashboard/index.tsx
│   │   │   ├── AnalystWorkbench/index.tsx
│   │   │   ├── AIChat/index.tsx
│   │   │   └── DataSources/index.tsx
│   │   ├── components/
│   │   │   ├── charts/PlotlyChart.tsx
│   │   │   ├── charts/RechartsBar.tsx
│   │   │   ├── tables/DataGrid.tsx
│   │   │   ├── ai/ChatPanel.tsx
│   │   │   ├── ai/InsightCard.tsx
│   │   │   ├── ai/NarrativeSummary.tsx
│   │   │   ├── filters/FilterBar.tsx
│   │   │   ├── layout/Sidebar.tsx
│   │   │   ├── layout/TopBar.tsx
│   │   │   └── layout/TieredToggle.tsx
│   │   ├── store/
│   │   │   └── useAppStore.ts
│   │   ├── hooks/
│   │   │   ├── useDataset.ts
│   │   │   ├── useAIQuery.ts
│   │   │   └── useWebSocket.ts
│   │   └── services/
│   │       ├── api.ts
│   │       └── websocket.ts
│   └── tests/
│       ├── components/
│       └── e2e/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── datasets.py
│   │   │   ├── analytics.py
│   │   │   ├── ai.py
│   │   │   └── websocket.py
│   │   └── middleware.py
│   ├── modules/
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py
│   │   │   ├── schema_detector.py
│   │   │   └── relationship_finder.py
│   │   ├── analytics/
│   │   │   ├── __init__.py
│   │   │   ├── stats_engine.py
│   │   │   ├── chart_builder.py
│   │   │   └── kpi_extractor.py
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── llm_factory.py
│   │       ├── pandasai_agent.py
│   │       ├── insight_engine.py
│   │       ├── narrative.py
│   │       └── streaming.py
│   ├── workers/
│   │   ├── __init__.py
│   │   └── tasks.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── adapter.py
│   └── tests/
│       ├── conftest.py
│       ├── test_parser.py
│       ├── test_schema_detector.py
│       ├── test_relationship_finder.py
│       ├── test_stats_engine.py
│       ├── test_chart_builder.py
│       ├── test_kpi_extractor.py
│       ├── test_pandasai_agent.py
│       └── test_routes.py
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── Dockerfile.worker
└── .env.example
```

---

## Phase 1 — Project Scaffolding & Docker

### Task 1: Repository structure + environment config

**Files:**
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `docker/Dockerfile.backend`
- Create: `docker/Dockerfile.frontend`
- Create: `docker/Dockerfile.worker`

- [ ] **Step 1: Create `.env.example`**

```bash
# LLM
LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Storage
STORAGE_BACKEND=local
AZURE_STORAGE_CONNECTION_STRING=
AWS_S3_BUCKET=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
LOCAL_STORAGE_PATH=./uploads

# Database
DATABASE_URL=postgresql://pulseai:pulseai@postgres:5432/pulseai
REDIS_URL=redis://redis:6379/0

# App
MAX_UPLOAD_SIZE_MB=50
CELERY_TASK_TIMEOUT=60
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

- [ ] **Step 2: Create `docker-compose.yml`**

```yaml
version: "3.9"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/uploads
    env_file: .env
    depends_on:
      - postgres
      - redis

  worker:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.worker
    volumes:
      - ./backend:/app
      - ./uploads:/uploads
    env_file: .env
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: pulseai
      POSTGRES_PASSWORD: pulseai
      POSTGRES_DB: pulseai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

- [ ] **Step 3: Create `docker/Dockerfile.backend`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 4: Create `docker/Dockerfile.worker`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "workers.tasks", "worker", "--loglevel=info", "--concurrency=4"]
```

- [ ] **Step 5: Create `docker/Dockerfile.frontend`**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

- [ ] **Step 6: Commit**

```bash
git init
git add .env.example docker-compose.yml docker/
git commit -m "feat: add docker compose and dockerfiles"
```

---

### Task 2: Backend scaffolding — FastAPI app + config + DB models

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `backend/main.py`
- Create: `backend/models/db.py`
- Create: `backend/api/middleware.py`

- [ ] **Step 1: Create `backend/requirements.txt`**

```txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
celery==5.3.6
redis==5.0.4
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
openpyxl==3.1.2
pandas==2.2.2
pandasai==2.3.0
openai==1.30.0
anthropic==0.28.0
python-multipart==0.0.9
python-dotenv==1.0.1
pydantic-settings==2.2.1
azure-storage-blob==12.20.0
boto3==1.34.0
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-mock==3.14.0
```

- [ ] **Step 2: Create `backend/config.py`**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    llm_provider: str = "azure_openai"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    storage_backend: str = "local"
    azure_storage_connection_string: str = ""
    aws_s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    local_storage_path: str = "./uploads"

    database_url: str = "postgresql://pulseai:pulseai@postgres:5432/pulseai"
    redis_url: str = "redis://redis:6379/0"

    max_upload_size_mb: int = 50
    celery_task_timeout: int = 60
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 3: Create `backend/models/db.py`**

```python
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from backend.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    blob_path = Column(String, nullable=False)
    storage_backend = Column(String, nullable=False)
    tab_names = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    tabs = relationship("TabProfile", back_populates="dataset", cascade="all, delete-orphan")
    relationships = relationship("TabRelationship", back_populates="dataset", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="dataset", cascade="all, delete-orphan")


class TabProfile(Base):
    __tablename__ = "tab_profiles"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    tab_name = Column(String, nullable=False)
    row_count = Column(Integer)
    column_profiles = Column(JSON)
    dataset = relationship("Dataset", back_populates="tabs")


class TabRelationship(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    tab_a = Column(String, nullable=False)
    tab_b = Column(String, nullable=False)
    column_a = Column(String, nullable=False)
    column_b = Column(String, nullable=False)
    confidence = Column(String)
    dataset = relationship("Dataset", back_populates="relationships")


class SavedQuery(Base):
    __tablename__ = "saved_queries"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    chart_config = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    dataset = relationship("Dataset", back_populates="chat_sessions")


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Create `backend/api/middleware.py`**

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
```

- [ ] **Step 5: Create `backend/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import get_settings
from backend.models.db import create_tables
from backend.api.middleware import error_handler_middleware
from backend.api.routes import datasets, analytics, ai, websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="PulseAI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(error_handler_middleware)

app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "PulseAI"}
```

- [ ] **Step 6: Write test for health endpoint**

Create `backend/tests/conftest.py`:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    with patch("backend.models.db.create_tables"):
        from backend.main import app
        return TestClient(app)
```

Create `backend/tests/test_routes.py`:
```python
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 7: Run test**

```bash
cd backend
pytest tests/test_routes.py::test_health -v
```
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with config, DB models, middleware"
```

---

### Task 3: React frontend scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/store/useAppStore.ts`
- Create: `frontend/src/services/api.ts`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "pulseai-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "zustand": "^4.5.2",
    "plotly.js": "^2.33.0",
    "react-plotly.js": "^2.6.0",
    "recharts": "^2.12.7",
    "ag-grid-react": "^32.0.0",
    "ag-grid-community": "^32.0.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-select": "^2.1.1",
    "lucide-react": "^0.390.0",
    "tailwindcss": "^3.4.4",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@types/plotly.js": "^2.33.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.4.5",
    "vite": "^5.3.1",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.6",
    "@playwright/test": "^1.45.0"
  }
}
```

- [ ] **Step 2: Run `npm install` in frontend directory**

```bash
cd frontend && npm install
```

- [ ] **Step 3: Create `frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true }
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts']
  }
})
```

- [ ] **Step 4: Create `frontend/src/store/useAppStore.ts`**

```typescript
import { create } from 'zustand'

export interface TabProfile {
  tabName: string
  rowCount: number
  columnProfiles: Record<string, { type: string; nullPct: number; uniqueCount: number }>
}

export interface Dataset {
  id: string
  name: string
  tabNames: string[]
  tabs: TabProfile[]
  createdAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  chartConfig?: object
  timestamp: string
}

interface AppStore {
  activeDataset: Dataset | null
  datasets: Dataset[]
  view: 'executive' | 'analyst'
  activeTab: string | null
  chatMessages: ChatMessage[]
  setActiveDataset: (dataset: Dataset | null) => void
  setDatasets: (datasets: Dataset[]) => void
  setView: (view: 'executive' | 'analyst') => void
  setActiveTab: (tab: string | null) => void
  addChatMessage: (msg: ChatMessage) => void
  clearChat: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  activeDataset: null,
  datasets: [],
  view: 'executive',
  activeTab: null,
  chatMessages: [],
  setActiveDataset: (dataset) => set({ activeDataset: dataset, activeTab: dataset?.tabNames[0] ?? null }),
  setDatasets: (datasets) => set({ datasets }),
  setView: (view) => set({ view }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  addChatMessage: (msg) => set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),
}))
```

- [ ] **Step 5: Create `frontend/src/services/api.ts`**

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail ?? 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export const datasetsApi = {
  list: () => api.get('/api/datasets'),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/datasets/upload', form)
  },
  get: (id: string) => api.get(`/api/datasets/${id}`),
  delete: (id: string) => api.delete(`/api/datasets/${id}`),
}

export const analyticsApi = {
  kpis: (datasetId: string) => api.get(`/api/analytics/kpis/${datasetId}`),
  stats: (datasetId: string, tabName: string) => api.get(`/api/analytics/stats/${datasetId}/${tabName}`),
  chart: (datasetId: string, payload: object) => api.post(`/api/analytics/chart/${datasetId}`, payload),
  relationships: (datasetId: string) => api.get(`/api/analytics/relationships/${datasetId}`),
}

export const aiApi = {
  narrative: (datasetId: string) => api.get(`/api/ai/narrative/${datasetId}`),
  insights: (datasetId: string) => api.get(`/api/ai/insights/${datasetId}`),
  saveQuery: (payload: object) => api.post('/api/ai/save-query', payload),
}

export default api
```

- [ ] **Step 6: Create `frontend/src/App.tsx`**

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/layout/Sidebar'
import { TopBar } from './components/layout/TopBar'
import { ExecutiveDashboard } from './pages/ExecutiveDashboard'
import { AnalystWorkbench } from './pages/AnalystWorkbench'
import { AIChat } from './pages/AIChat'
import { DataSources } from './pages/DataSources'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-gray-100">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <TopBar />
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/executive" replace />} />
              <Route path="/executive" element={<ExecutiveDashboard />} />
              <Route path="/analyst" element={<AnalystWorkbench />} />
              <Route path="/chat" element={<AIChat />} />
              <Route path="/sources" element={<DataSources />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
```

- [ ] **Step 7: Create `frontend/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 8: Write store test**

Create `frontend/src/tests/setup.ts`:
```typescript
import '@testing-library/jest-dom'
```

Create `frontend/tests/store.test.ts`:
```typescript
import { renderHook, act } from '@testing-library/react'
import { useAppStore } from '../src/store/useAppStore'

test('setActiveDataset updates store and sets first tab as active', () => {
  const { result } = renderHook(() => useAppStore())
  const dataset = { id: '1', name: 'Test', tabNames: ['Sheet1', 'Sheet2'], tabs: [], createdAt: '' }
  act(() => result.current.setActiveDataset(dataset))
  expect(result.current.activeDataset?.id).toBe('1')
  expect(result.current.activeTab).toBe('Sheet1')
})
```

- [ ] **Step 9: Run test**

```bash
cd frontend && npm test -- tests/store.test.ts
```
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold React frontend with Zustand store and API service"
```

---

## Phase 2 — Backend Ingestion Module

### Task 4: Excel parser

**Files:**
- Create: `backend/modules/ingestion/parser.py`
- Create: `backend/tests/test_parser.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_parser.py`:
```python
import pytest
import pandas as pd
from pathlib import Path
import openpyxl

@pytest.fixture
def sample_xlsx(tmp_path):
    path = tmp_path / "test.xlsx"
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Sales"
    ws1.append(["Date", "Product", "Revenue", "Units"])
    ws1.append(["2024-01-01", "Widget A", 1000, 10])
    ws1.append(["2024-01-02", "Widget B", 2000, 20])
    ws2 = wb.create_sheet("Costs")
    ws2.append(["Date", "Category", "Amount"])
    ws2.append(["2024-01-01", "Marketing", 500])
    wb.save(path)
    return path

def test_parse_returns_all_tabs(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert set(result.keys()) == {"Sales", "Costs"}

def test_parse_returns_dataframes(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert isinstance(result["Sales"], pd.DataFrame)
    assert len(result["Sales"]) == 2

def test_parse_preserves_columns(sample_xlsx):
    from backend.modules.ingestion.parser import parse_excel
    result = parse_excel(str(sample_xlsx))
    assert list(result["Sales"].columns) == ["Date", "Product", "Revenue", "Units"]
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd backend && pytest tests/test_parser.py -v
```
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement `backend/modules/ingestion/parser.py`**

```python
import pandas as pd
from typing import Dict


def parse_excel(file_path: str) -> Dict[str, pd.DataFrame]:
    """Parse all tabs of an Excel file into a dict of DataFrames."""
    xl = pd.ExcelFile(file_path, engine="openpyxl")
    result = {}
    for sheet_name in xl.sheet_names:
        try:
            df = xl.parse(sheet_name)
            df.columns = [str(c).strip() for c in df.columns]
            result[sheet_name] = df
        except Exception:
            pass  # skip unparseable tabs; caller handles missing keys
    return result
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_parser.py -v
```
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/ingestion/parser.py backend/tests/test_parser.py
git commit -m "feat: add Excel parser module"
```

---

### Task 5: Schema detector

**Files:**
- Create: `backend/modules/ingestion/schema_detector.py`
- Create: `backend/tests/test_schema_detector.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_schema_detector.py
import pandas as pd
import pytest
from backend.modules.ingestion.schema_detector import detect_schema

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "Revenue": [1000.0, 2000.0],
        "Category": ["A", "B"],
        "Notes": ["long text here", "another note"],
    })

def test_detects_datetime_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Date"]["type"] == "datetime"

def test_detects_numeric_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Revenue"]["type"] == "numeric"

def test_detects_categorical_column(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Category"]["type"] == "categorical"

def test_includes_null_percentage(sample_df):
    schema = detect_schema(sample_df)
    assert "null_pct" in schema["Revenue"]
    assert schema["Revenue"]["null_pct"] == 0.0

def test_includes_unique_count(sample_df):
    schema = detect_schema(sample_df)
    assert schema["Category"]["unique_count"] == 2
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_schema_detector.py -v
```

- [ ] **Step 3: Implement `backend/modules/ingestion/schema_detector.py`**

```python
import pandas as pd
from typing import Dict, Any


def detect_schema(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Classify each column by type and compute basic profile stats."""
    schema = {}
    for col in df.columns:
        series = df[col]
        null_pct = round(series.isna().mean() * 100, 2)
        unique_count = int(series.nunique(dropna=True))
        col_type = _classify_column(series)
        schema[col] = {"type": col_type, "null_pct": null_pct, "unique_count": unique_count}
    return schema


def _classify_column(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    # Try coercing object columns that look like dates
    if series.dtype == object:
        try:
            pd.to_datetime(series.dropna().head(20), infer_datetime_format=True)
            return "datetime"
        except Exception:
            pass
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    unique_ratio = series.nunique(dropna=True) / max(len(series.dropna()), 1)
    if unique_ratio < 0.5:
        return "categorical"
    return "text"
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_schema_detector.py -v
```
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/ingestion/schema_detector.py backend/tests/test_schema_detector.py
git commit -m "feat: add schema detector module"
```

---

### Task 6: Relationship finder

**Files:**
- Create: `backend/modules/ingestion/relationship_finder.py`
- Create: `backend/tests/test_relationship_finder.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_relationship_finder.py
import pandas as pd
from backend.modules.ingestion.relationship_finder import find_relationships

def test_finds_exact_column_name_match():
    dfs = {
        "Orders": pd.DataFrame({"customer_id": [1, 2, 3], "amount": [100, 200, 300]}),
        "Customers": pd.DataFrame({"customer_id": [1, 2, 3], "name": ["A", "B", "C"]}),
    }
    rels = find_relationships(dfs)
    assert len(rels) == 1
    assert rels[0]["column_a"] == "customer_id"
    assert rels[0]["column_b"] == "customer_id"

def test_no_relationship_when_no_shared_columns():
    dfs = {
        "Sales": pd.DataFrame({"revenue": [100], "units": [10]}),
        "Costs": pd.DataFrame({"expense": [50], "category": ["A"]}),
    }
    rels = find_relationships(dfs)
    assert rels == []

def test_relationship_has_required_keys():
    dfs = {
        "A": pd.DataFrame({"id": [1, 2]}),
        "B": pd.DataFrame({"id": [1, 2]}),
    }
    rels = find_relationships(dfs)
    assert all(k in rels[0] for k in ["tab_a", "tab_b", "column_a", "column_b", "confidence"])
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_relationship_finder.py -v
```

- [ ] **Step 3: Implement `backend/modules/ingestion/relationship_finder.py`**

```python
import pandas as pd
from itertools import combinations
from typing import Dict, List


def find_relationships(dfs: Dict[str, pd.DataFrame]) -> List[dict]:
    """Detect potential join columns between DataFrame pairs by matching column names."""
    relationships = []
    tab_pairs = list(combinations(dfs.keys(), 2))
    for tab_a, tab_b in tab_pairs:
        cols_a = set(dfs[tab_a].columns)
        cols_b = set(dfs[tab_b].columns)
        shared = cols_a & cols_b
        for col in shared:
            series_a = dfs[tab_a][col].dropna()
            series_b = dfs[tab_b][col].dropna()
            overlap = len(set(series_a) & set(series_b))
            if overlap > 0:
                confidence = "high" if overlap / max(len(set(series_a)), 1) > 0.5 else "low"
                relationships.append({
                    "tab_a": tab_a,
                    "tab_b": tab_b,
                    "column_a": col,
                    "column_b": col,
                    "confidence": confidence,
                })
    return relationships
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_relationship_finder.py -v
```
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/ingestion/relationship_finder.py backend/tests/test_relationship_finder.py
git commit -m "feat: add cross-tab relationship finder"
```

---

## Phase 3 — Backend Analytics Module

### Task 7: Stats engine + KPI extractor

**Files:**
- Create: `backend/modules/analytics/stats_engine.py`
- Create: `backend/modules/analytics/kpi_extractor.py`
- Create: `backend/tests/test_stats_engine.py`
- Create: `backend/tests/test_kpi_extractor.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_stats_engine.py
import pandas as pd
from backend.modules.analytics.stats_engine import compute_stats

def test_computes_mean_for_numeric():
    df = pd.DataFrame({"revenue": [100, 200, 300]})
    stats = compute_stats(df)
    assert stats["revenue"]["mean"] == 200.0

def test_computes_outlier_flag():
    df = pd.DataFrame({"revenue": [100, 110, 105, 10000]})
    stats = compute_stats(df)
    assert stats["revenue"]["has_outliers"] is True

def test_skips_non_numeric_columns():
    df = pd.DataFrame({"name": ["a", "b"], "value": [1, 2]})
    stats = compute_stats(df)
    assert "name" not in stats
    assert "value" in stats
```

```python
# backend/tests/test_kpi_extractor.py
import pandas as pd
from backend.modules.analytics.kpi_extractor import extract_kpis

def test_extracts_top_numeric_columns():
    df = pd.DataFrame({"revenue": [100, 200], "cost": [50, 80], "name": ["A", "B"]})
    kpis = extract_kpis(df)
    assert any(k["column"] == "revenue" for k in kpis)
    assert not any(k["column"] == "name" for k in kpis)

def test_kpi_includes_sum_and_mean():
    df = pd.DataFrame({"revenue": [100, 200]})
    kpis = extract_kpis(df)
    kpi = kpis[0]
    assert "sum" in kpi
    assert "mean" in kpi
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest tests/test_stats_engine.py tests/test_kpi_extractor.py -v
```

- [ ] **Step 3: Implement `backend/modules/analytics/stats_engine.py`**

```python
import pandas as pd
from typing import Dict, Any


def compute_stats(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Compute descriptive statistics for all numeric columns."""
    stats = {}
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        has_outliers = bool(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).any())
        stats[col] = {
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "sum": round(float(series.sum()), 4),
            "has_outliers": has_outliers,
        }
    return stats
```

- [ ] **Step 4: Implement `backend/modules/analytics/kpi_extractor.py`**

```python
import pandas as pd
from typing import List, Dict, Any


def extract_kpis(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """Extract top numeric columns as KPI cards for executive view."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    kpis = []
    for col in numeric_cols[:top_n]:
        series = df[col].dropna()
        kpis.append({
            "column": col,
            "sum": round(float(series.sum()), 2),
            "mean": round(float(series.mean()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "count": int(len(series)),
        })
    return kpis
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_stats_engine.py tests/test_kpi_extractor.py -v
```
Expected: 5 PASS

- [ ] **Step 6: Commit**

```bash
git add backend/modules/analytics/ backend/tests/test_stats_engine.py backend/tests/test_kpi_extractor.py
git commit -m "feat: add stats engine and KPI extractor"
```

---

### Task 8: Chart builder

**Files:**
- Create: `backend/modules/analytics/chart_builder.py`
- Create: `backend/tests/test_chart_builder.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_chart_builder.py
import pandas as pd
from backend.modules.analytics.chart_builder import build_chart

def test_bar_chart_returns_plotly_json():
    df = pd.DataFrame({"Category": ["A", "B", "C"], "Revenue": [100, 200, 150]})
    config = build_chart(df, chart_type="bar", x="Category", y="Revenue")
    assert config["type"] == "bar"
    assert "data" in config
    assert len(config["data"][0]["x"]) == 3

def test_line_chart_returns_plotly_json():
    df = pd.DataFrame({"Month": ["Jan", "Feb"], "Sales": [500, 700]})
    config = build_chart(df, chart_type="line", x="Month", y="Sales")
    assert config["type"] == "line"

def test_invalid_chart_type_raises():
    df = pd.DataFrame({"x": [1], "y": [2]})
    with pytest.raises(ValueError, match="Unsupported chart type"):
        build_chart(df, chart_type="radar", x="x", y="y")
```

Add `import pytest` at top of test file.

- [ ] **Step 2: Implement `backend/modules/analytics/chart_builder.py`**

```python
import pandas as pd
from typing import Optional

SUPPORTED_TYPES = {"bar", "line", "scatter", "pie", "histogram", "heatmap"}


def build_chart(df: pd.DataFrame, chart_type: str, x: str, y: Optional[str] = None) -> dict:
    """Generate a Plotly-compatible chart config dict from a DataFrame."""
    if chart_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported chart type: {chart_type}. Choose from {SUPPORTED_TYPES}")

    if chart_type == "bar":
        return {"type": "bar", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "bar"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "line":
        return {"type": "line", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "scatter", "mode": "lines+markers"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "scatter":
        return {"type": "scatter", "data": [{"x": df[x].tolist(), "y": df[y].tolist(), "type": "scatter", "mode": "markers"}],
                "layout": {"xaxis": {"title": x}, "yaxis": {"title": y}}}

    if chart_type == "pie":
        return {"type": "pie", "data": [{"labels": df[x].tolist(), "values": df[y].tolist(), "type": "pie"}], "layout": {}}

    if chart_type == "histogram":
        return {"type": "histogram", "data": [{"x": df[x].tolist(), "type": "histogram"}],
                "layout": {"xaxis": {"title": x}}}

    if chart_type == "heatmap":
        pivot = df.pivot_table(index=df.columns[0], columns=df.columns[1], values=y, aggfunc="sum").fillna(0)
        return {"type": "heatmap", "data": [{"z": pivot.values.tolist(), "x": pivot.columns.tolist(),
                "y": pivot.index.tolist(), "type": "heatmap"}], "layout": {}}

    return {}
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_chart_builder.py -v
```
Expected: 3 PASS

- [ ] **Step 4: Commit**

```bash
git add backend/modules/analytics/chart_builder.py backend/tests/test_chart_builder.py
git commit -m "feat: add Plotly chart builder"
```

---

## Phase 4 — AI Module + API Routes

### Task 9: LLM factory + PandasAI agent

**Files:**
- Create: `backend/modules/ai/llm_factory.py`
- Create: `backend/modules/ai/pandasai_agent.py`
- Create: `backend/tests/test_pandasai_agent.py`

- [ ] **Step 1: Create `backend/modules/ai/llm_factory.py`**

```python
from backend.config import get_settings

settings = get_settings()


def get_llm():
    """Return a PandasAI-compatible LLM instance based on LLM_PROVIDER env var."""
    provider = settings.llm_provider

    if provider == "azure_openai":
        from pandasai.llm import AzureOpenAI
        return AzureOpenAI(
            deployment_name=settings.azure_openai_deployment,
            api_token=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-02-15-preview",
        )

    if provider == "openai":
        from pandasai.llm import OpenAI
        return OpenAI(api_token=settings.openai_api_key, model="gpt-4o")

    if provider == "claude":
        from langchain_anthropic import ChatAnthropic
        from pandasai.llm.langchain import LangchainLLM
        return LangchainLLM(ChatAnthropic(
            model="claude-sonnet-5",
            api_key=settings.anthropic_api_key,
        ))

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Choose azure_openai | openai | claude")
```

- [ ] **Step 2: Write failing test for PandasAI agent**

```python
# backend/tests/test_pandasai_agent.py
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def sample_dfs():
    return {
        "Sales": pd.DataFrame({"Month": ["Jan", "Feb"], "Revenue": [1000, 2000]}),
        "Costs": pd.DataFrame({"Month": ["Jan", "Feb"], "Amount": [500, 600]}),
    }

def test_query_returns_string_response(sample_dfs):
    mock_llm = MagicMock()
    with patch("backend.modules.ai.pandasai_agent.get_llm", return_value=mock_llm):
        with patch("backend.modules.ai.pandasai_agent.SmartDatalake") as MockLake:
            mock_instance = MockLake.return_value
            mock_instance.chat.return_value = "Revenue peaked in February at 2000"
            from backend.modules.ai.pandasai_agent import query_dataframes
            result = query_dataframes(sample_dfs, "What is the peak revenue month?")
            assert "February" in result["answer"]

def test_query_handles_llm_exception(sample_dfs):
    mock_llm = MagicMock()
    with patch("backend.modules.ai.pandasai_agent.get_llm", return_value=mock_llm):
        with patch("backend.modules.ai.pandasai_agent.SmartDatalake") as MockLake:
            MockLake.return_value.chat.side_effect = Exception("LLM timeout")
            from backend.modules.ai.pandasai_agent import query_dataframes
            result = query_dataframes(sample_dfs, "Show me trends")
            assert result["error"] is not None
```

- [ ] **Step 3: Implement `backend/modules/ai/pandasai_agent.py`**

```python
import pandas as pd
from typing import Dict, Any
from pandasai import SmartDatalake
from backend.modules.ai.llm_factory import get_llm


def query_dataframes(dfs: Dict[str, pd.DataFrame], question: str) -> Dict[str, Any]:
    """Run a natural language query over multiple DataFrames using PandasAI SmartDatalake."""
    try:
        llm = get_llm()
        lake = SmartDatalake(list(dfs.values()), config={"llm": llm, "verbose": False, "save_charts": False})
        response = lake.chat(question)
        # PandasAI may return a DataFrame, a string, or a chart path
        if isinstance(response, pd.DataFrame):
            return {"answer": response.to_dict(orient="records"), "type": "table", "error": None}
        if isinstance(response, str) and response.endswith(".png"):
            return {"answer": None, "type": "chart_path", "chart_path": response, "error": None}
        return {"answer": str(response), "type": "text", "error": None}
    except Exception as exc:
        return {"answer": None, "type": "error", "error": str(exc)}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_pandasai_agent.py -v
```
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/modules/ai/ backend/tests/test_pandasai_agent.py
git commit -m "feat: add LLM factory and PandasAI SmartDatalake agent"
```

---

### Task 10: Narrative + insight engine

**Files:**
- Create: `backend/modules/ai/narrative.py`
- Create: `backend/modules/ai/insight_engine.py`

- [ ] **Step 1: Implement `backend/modules/ai/narrative.py`**

```python
import pandas as pd
from typing import Dict
from backend.modules.analytics.stats_engine import compute_stats
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.ai.llm_factory import get_llm


def generate_narrative(dfs: Dict[str, pd.DataFrame]) -> str:
    """Generate a 3-sentence executive summary of the dataset using the configured LLM."""
    summary_lines = []
    for tab_name, df in dfs.items():
        kpis = extract_kpis(df)
        for kpi in kpis[:2]:
            summary_lines.append(f"Tab '{tab_name}': {kpi['column']} — total {kpi['sum']}, avg {kpi['mean']}")

    context = "\n".join(summary_lines)
    prompt = (
        f"You are a data analyst. Based on this data summary, write exactly 3 sentences "
        f"for an executive dashboard. Be concise and highlight key numbers.\n\n{context}"
    )

    try:
        # Use the LLM directly for narrative (not PandasAI)
        llm = get_llm()
        # PandasAI LLM objects expose .call() or we use the underlying client
        if hasattr(llm, "call"):
            return llm.call([{"role": "user", "content": prompt}])
        # Fallback: return structured summary without LLM
        return f"Dataset contains {len(dfs)} sheet(s) with key metrics. " + " ".join(summary_lines[:2])
    except Exception:
        return f"Dataset loaded with {len(dfs)} sheet(s). Key metrics: {'; '.join(summary_lines[:3])}."
```

- [ ] **Step 2: Implement `backend/modules/ai/insight_engine.py`**

```python
import pandas as pd
from typing import Dict, List


def detect_insights(dfs: Dict[str, pd.DataFrame]) -> List[dict]:
    """Auto-detect anomalies and insights across all DataFrames."""
    insights = []
    for tab_name, df in dfs.items():
        numeric_cols = df.select_dtypes(include="number").columns
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 3:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            outliers = series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)]
            if len(outliers) > 0:
                insights.append({
                    "tab": tab_name,
                    "type": "outlier",
                    "column": col,
                    "message": f"{len(outliers)} outlier(s) detected in '{col}' on sheet '{tab_name}'",
                    "severity": "warning",
                })
            # Check for all-null column
            if series.isna().all():
                insights.append({
                    "tab": tab_name,
                    "type": "empty_column",
                    "column": col,
                    "message": f"Column '{col}' in sheet '{tab_name}' has no data",
                    "severity": "info",
                })
    return insights
```

- [ ] **Step 3: Commit**

```bash
git add backend/modules/ai/narrative.py backend/modules/ai/insight_engine.py
git commit -m "feat: add narrative generator and insight engine"
```

---

### Task 11: Storage adapter + Celery workers

**Files:**
- Create: `backend/storage/adapter.py`
- Create: `backend/workers/tasks.py`

- [ ] **Step 1: Implement `backend/storage/adapter.py`**

```python
import os
import shutil
from pathlib import Path
from backend.config import get_settings

settings = get_settings()


def save_file(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file to configured storage backend. Returns blob path."""
    backend = settings.storage_backend

    if backend == "local":
        path = Path(settings.local_storage_path) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file_bytes)
        return str(path)

    if backend == "azure_blob":
        from azure.storage.blob import BlobServiceClient
        client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        container = client.get_container_client("pulseai-uploads")
        try:
            container.create_container()
        except Exception:
            pass
        container.upload_blob(filename, file_bytes, overwrite=True)
        return f"azure://{filename}"

    if backend == "s3":
        import boto3
        s3 = boto3.client("s3", aws_access_key_id=settings.aws_access_key_id,
                          aws_secret_access_key=settings.aws_secret_access_key)
        s3.put_object(Bucket=settings.aws_s3_bucket, Key=filename, Body=file_bytes)
        return f"s3://{settings.aws_s3_bucket}/{filename}"

    raise ValueError(f"Unknown storage backend: {backend}")


def load_file(blob_path: str) -> bytes:
    """Load a file from configured storage backend."""
    if blob_path.startswith("azure://"):
        from azure.storage.blob import BlobServiceClient
        filename = blob_path.replace("azure://", "")
        client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
        return client.get_blob_client("pulseai-uploads", filename).download_blob().readall()

    if blob_path.startswith("s3://"):
        import boto3
        parts = blob_path.replace("s3://", "").split("/", 1)
        s3 = boto3.client("s3")
        return s3.get_object(Bucket=parts[0], Key=parts[1])["Body"].read()

    return Path(blob_path).read_bytes()
```

- [ ] **Step 2: Implement `backend/workers/tasks.py`**

```python
import uuid
import tempfile
import os
from celery import Celery
from backend.config import get_settings

settings = get_settings()

celery_app = Celery("pulseai", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_time_limit = settings.celery_task_timeout


@celery_app.task(bind=True, name="process_dataset")
def process_dataset(self, dataset_id: str, blob_path: str):
    """Parse Excel file, detect schema + relationships, save profiles to DB."""
    from backend.storage.adapter import load_file
    from backend.modules.ingestion.parser import parse_excel
    from backend.modules.ingestion.schema_detector import detect_schema
    from backend.modules.ingestion.relationship_finder import find_relationships
    from backend.modules.ai.insight_engine import detect_insights
    from backend.models.db import SessionLocal, Dataset, TabProfile, TabRelationship
    import json

    file_bytes = load_file(blob_path)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        dfs = parse_excel(tmp_path)
        db = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                return {"status": "error", "message": "Dataset not found"}

            dataset.tab_names = list(dfs.keys())

            for tab_name, df in dfs.items():
                schema = detect_schema(df)
                profile = TabProfile(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset_id,
                    tab_name=tab_name,
                    row_count=len(df),
                    column_profiles=schema,
                )
                db.add(profile)

            for rel in find_relationships(dfs):
                db.add(TabRelationship(
                    id=str(uuid.uuid4()),
                    dataset_id=dataset_id,
                    tab_a=rel["tab_a"],
                    tab_b=rel["tab_b"],
                    column_a=rel["column_a"],
                    column_b=rel["column_b"],
                    confidence=rel["confidence"],
                ))

            db.commit()
        finally:
            db.close()

        return {"status": "ready", "tabs": list(dfs.keys()), "insights": detect_insights(dfs)}
    finally:
        os.unlink(tmp_path)


@celery_app.task(bind=True, name="run_ai_query")
def run_ai_query(self, dataset_id: str, blob_path: str, question: str, session_id: str):
    """Run a PandasAI query and return result for WebSocket delivery."""
    from backend.storage.adapter import load_file
    from backend.modules.ingestion.parser import parse_excel
    from backend.modules.ai.pandasai_agent import query_dataframes
    import tempfile, os

    file_bytes = load_file(blob_path)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        dfs = parse_excel(tmp_path)
        result = query_dataframes(dfs, question)
        result["session_id"] = session_id
        return result
    finally:
        os.unlink(tmp_path)
```

- [ ] **Step 3: Commit**

```bash
git add backend/storage/ backend/workers/
git commit -m "feat: add storage adapter and Celery workers"
```

---

### Task 12: API routes

**Files:**
- Create: `backend/api/routes/datasets.py`
- Create: `backend/api/routes/analytics.py`
- Create: `backend/api/routes/ai.py`
- Create: `backend/api/routes/websocket.py`
- Create: `backend/api/__init__.py`
- Create: `backend/api/routes/__init__.py`

- [ ] **Step 1: Create `backend/api/routes/datasets.py`**

```python
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models.db import get_db, Dataset
from backend.storage.adapter import save_file
from backend.workers.tasks import process_dataset
from backend.config import get_settings

settings = get_settings()
router = APIRouter()


@router.get("/")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return [{"id": d.id, "name": d.name, "tabNames": d.tab_names, "createdAt": str(d.created_at)} for d in datasets]


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_size_mb}MB limit")

    dataset_id = str(uuid.uuid4())
    blob_path = save_file(content, f"{dataset_id}/{file.filename}")

    dataset = Dataset(id=dataset_id, name=file.filename, blob_path=blob_path,
                      storage_backend=settings.storage_backend, tab_names=[])
    db.add(dataset)
    db.commit()

    task = process_dataset.delay(dataset_id, blob_path)
    return {"id": dataset_id, "taskId": task.id, "status": "processing"}


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": dataset.id,
        "name": dataset.name,
        "tabNames": dataset.tab_names,
        "tabs": [{"tabName": t.tab_name, "rowCount": t.row_count, "columnProfiles": t.column_profiles} for t in dataset.tabs],
        "relationships": [{"tabA": r.tab_a, "tabB": r.tab_b, "columnA": r.column_a, "columnB": r.column_b} for r in dataset.relationships],
        "createdAt": str(dataset.created_at),
    }


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(dataset)
    db.commit()
    return {"status": "deleted"}
```

- [ ] **Step 2: Create `backend/api/routes/analytics.py`**

```python
import tempfile, os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models.db import get_db, Dataset
from backend.storage.adapter import load_file
from backend.modules.ingestion.parser import parse_excel
from backend.modules.analytics.stats_engine import compute_stats
from backend.modules.analytics.kpi_extractor import extract_kpis
from backend.modules.analytics.chart_builder import build_chart

router = APIRouter()


def _load_dfs(dataset_id: str, db: Session):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    file_bytes = load_file(dataset.blob_path)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        return parse_excel(tmp_path)
    finally:
        os.unlink(tmp_path)


@router.get("/kpis/{dataset_id}")
def get_kpis(dataset_id: str, db: Session = Depends(get_db)):
    dfs = _load_dfs(dataset_id, db)
    result = {}
    for tab_name, df in dfs.items():
        result[tab_name] = extract_kpis(df)
    return result


@router.get("/stats/{dataset_id}/{tab_name}")
def get_stats(dataset_id: str, tab_name: str, db: Session = Depends(get_db)):
    dfs = _load_dfs(dataset_id, db)
    if tab_name not in dfs:
        raise HTTPException(status_code=404, detail=f"Tab '{tab_name}' not found")
    return compute_stats(dfs[tab_name])


@router.post("/chart/{dataset_id}")
def get_chart(dataset_id: str, payload: dict, db: Session = Depends(get_db)):
    dfs = _load_dfs(dataset_id, db)
    tab_name = payload.get("tab")
    if tab_name not in dfs:
        raise HTTPException(status_code=400, detail=f"Tab '{tab_name}' not found")
    try:
        return build_chart(dfs[tab_name], chart_type=payload["chartType"], x=payload["x"], y=payload.get("y"))
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
```

- [ ] **Step 3: Create `backend/api/routes/ai.py`**

```python
import tempfile, os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models.db import get_db, Dataset, SavedQuery
from backend.storage.adapter import load_file
from backend.modules.ingestion.parser import parse_excel
from backend.modules.ai.narrative import generate_narrative
from backend.modules.ai.insight_engine import detect_insights
import uuid

router = APIRouter()


def _load_dfs(dataset_id: str, db: Session):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    file_bytes = load_file(dataset.blob_path)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        return parse_excel(tmp_path)
    finally:
        os.unlink(tmp_path)


@router.get("/narrative/{dataset_id}")
def get_narrative(dataset_id: str, db: Session = Depends(get_db)):
    dfs = _load_dfs(dataset_id, db)
    return {"narrative": generate_narrative(dfs)}


@router.get("/insights/{dataset_id}")
def get_insights(dataset_id: str, db: Session = Depends(get_db)):
    dfs = _load_dfs(dataset_id, db)
    return {"insights": detect_insights(dfs)}


@router.post("/save-query")
def save_query(payload: dict, db: Session = Depends(get_db)):
    query = SavedQuery(
        id=str(uuid.uuid4()),
        dataset_id=payload["datasetId"],
        question=payload["question"],
        chart_config=payload.get("chartConfig"),
    )
    db.add(query)
    db.commit()
    return {"id": query.id}
```

- [ ] **Step 4: Create `backend/api/routes/websocket.py`**

```python
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.workers.tasks import run_ai_query

router = APIRouter()
active_connections: dict[str, WebSocket] = {}


@router.websocket("/chat/{dataset_id}")
async def chat_websocket(websocket: WebSocket, dataset_id: str):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    active_connections[session_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            question = message.get("question", "")

            await websocket.send_json({"type": "thinking", "session_id": session_id})

            from backend.models.db import SessionLocal, Dataset
            db = SessionLocal()
            try:
                dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if not dataset:
                    await websocket.send_json({"type": "error", "message": "Dataset not found"})
                    continue
                blob_path = dataset.blob_path
            finally:
                db.close()

            task = run_ai_query.delay(dataset_id, blob_path, question, session_id)
            result = task.get(timeout=60)
            result["type"] = "result"
            await websocket.send_json(result)

    except WebSocketDisconnect:
        active_connections.pop(session_id, None)
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        active_connections.pop(session_id, None)
```

- [ ] **Step 5: Create `__init__.py` files**

```bash
touch backend/api/__init__.py backend/api/routes/__init__.py backend/modules/__init__.py
touch backend/modules/ingestion/__init__.py backend/modules/analytics/__init__.py backend/modules/ai/__init__.py
touch backend/workers/__init__.py backend/storage/__init__.py backend/models/__init__.py backend/tests/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add backend/api/ backend/modules/ai/ backend/storage/ backend/workers/
git commit -m "feat: add all API routes, WebSocket chat, storage adapter, Celery workers"
```

---

## Phase 5 — React Frontend Core + Executive Dashboard

### Task 13: Layout components

**Files:**
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/components/layout/TopBar.tsx`
- Create: `frontend/src/components/layout/TieredToggle.tsx`

- [ ] **Step 1: Create `frontend/src/components/layout/Sidebar.tsx`**

```tsx
import { NavLink } from 'react-router-dom'
import { BarChart2, Brain, Database, TrendingUp } from 'lucide-react'
import clsx from 'clsx'

const links = [
  { to: '/executive', icon: TrendingUp, label: 'Executive' },
  { to: '/analyst', icon: BarChart2, label: 'Analyst' },
  { to: '/chat', icon: Brain, label: 'AI Chat' },
  { to: '/sources', icon: Database, label: 'Data Sources' },
]

export function Sidebar() {
  return (
    <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-xl font-bold text-blue-400">PulseAI</h1>
        <p className="text-xs text-gray-500 mt-0.5">Real-time pulse of your data</p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) =>
            clsx('flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
              isActive ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white')}>
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/layout/TopBar.tsx`**

```tsx
import { useAppStore } from '../../store/useAppStore'
import { TieredToggle } from './TieredToggle'

export function TopBar() {
  const { activeDataset, datasets, setActiveDataset } = useAppStore()

  return (
    <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <select
          className="bg-gray-800 text-gray-200 text-sm rounded-lg px-3 py-1.5 border border-gray-700"
          value={activeDataset?.id ?? ''}
          onChange={(e) => {
            const ds = datasets.find((d) => d.id === e.target.value)
            setActiveDataset(ds ?? null)
          }}>
          <option value="">— Select dataset —</option>
          {datasets.map((d) => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
        {activeDataset && (
          <span className="text-xs text-gray-500">{activeDataset.tabNames.length} sheet(s)</span>
        )}
      </div>
      <TieredToggle />
    </header>
  )
}
```

- [ ] **Step 3: Create `frontend/src/components/layout/TieredToggle.tsx`**

```tsx
import { useAppStore } from '../../store/useAppStore'
import clsx from 'clsx'

export function TieredToggle() {
  const { view, setView } = useAppStore()
  return (
    <div className="flex items-center bg-gray-800 rounded-lg p-1 gap-1">
      {(['executive', 'analyst'] as const).map((v) => (
        <button key={v} onClick={() => setView(v)}
          className={clsx('px-3 py-1 text-xs rounded-md capitalize transition-colors',
            view === v ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white')}>
          {v}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat: add Sidebar, TopBar, TieredToggle layout components"
```

---

### Task 14: Chart + table components

**Files:**
- Create: `frontend/src/components/charts/PlotlyChart.tsx`
- Create: `frontend/src/components/tables/DataGrid.tsx`

- [ ] **Step 1: Create `frontend/src/components/charts/PlotlyChart.tsx`**

```tsx
import Plot from 'react-plotly.js'

interface PlotlyChartProps {
  config: {
    data: Plotly.Data[]
    layout?: Partial<Plotly.Layout>
  }
  className?: string
}

export function PlotlyChart({ config, className }: PlotlyChartProps) {
  return (
    <Plot
      data={config.data}
      layout={{
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#e5e7eb' },
        margin: { t: 30, r: 10, b: 40, l: 50 },
        ...config.layout,
      }}
      config={{ displayModeBar: false, responsive: true }}
      className={className}
      style={{ width: '100%', height: '100%' }}
    />
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/tables/DataGrid.tsx`**

```tsx
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

interface DataGridProps {
  rows: Record<string, unknown>[]
  height?: number
}

export function DataGrid({ rows, height = 400 }: DataGridProps) {
  if (!rows.length) return <p className="text-gray-500 text-sm">No data</p>

  const colDefs = Object.keys(rows[0]).map((key) => ({
    field: key,
    sortable: true,
    filter: true,
    resizable: true,
  }))

  return (
    <div className="ag-theme-alpine-dark" style={{ height }}>
      <AgGridReact rowData={rows} columnDefs={colDefs} pagination paginationPageSize={50} />
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/charts/ frontend/src/components/tables/
git commit -m "feat: add Plotly chart and AG Grid table components"
```

---

### Task 15: Executive Dashboard page

**Files:**
- Create: `frontend/src/pages/ExecutiveDashboard/index.tsx`
- Create: `frontend/src/components/ai/NarrativeSummary.tsx`
- Create: `frontend/src/components/ai/InsightCard.tsx`

- [ ] **Step 1: Create `frontend/src/components/ai/NarrativeSummary.tsx`**

```tsx
import { useEffect, useState } from 'react'
import { aiApi } from '../../services/api'

export function NarrativeSummary({ datasetId }: { datasetId: string }) {
  const [narrative, setNarrative] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    aiApi.narrative(datasetId)
      .then((r) => setNarrative(r.data.narrative))
      .catch(() => setNarrative('Unable to generate summary.'))
      .finally(() => setLoading(false))
  }, [datasetId])

  if (loading) return <div className="animate-pulse h-16 bg-gray-800 rounded-lg" />

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
      <h3 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">AI Summary</h3>
      <p className="text-gray-300 text-sm leading-relaxed">{narrative}</p>
    </div>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/ai/InsightCard.tsx`**

```tsx
interface Insight { tab: string; type: string; message: string; severity: string }

export function InsightCard({ insight }: { insight: Insight }) {
  const color = insight.severity === 'warning' ? 'border-yellow-600 bg-yellow-900/20' : 'border-blue-600 bg-blue-900/20'
  return (
    <div className={`border rounded-lg p-3 text-sm ${color}`}>
      <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{insight.tab}</span>
      <p className="text-gray-200 mt-1">{insight.message}</p>
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/pages/ExecutiveDashboard/index.tsx`**

```tsx
import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { analyticsApi, aiApi } from '../../services/api'
import { PlotlyChart } from '../../components/charts/PlotlyChart'
import { NarrativeSummary } from '../../components/ai/NarrativeSummary'
import { InsightCard } from '../../components/ai/InsightCard'

export function ExecutiveDashboard() {
  const { activeDataset } = useAppStore()
  const [kpis, setKpis] = useState<Record<string, any[]>>({})
  const [insights, setInsights] = useState<any[]>([])

  useEffect(() => {
    if (!activeDataset) return
    analyticsApi.kpis(activeDataset.id).then((r) => setKpis(r.data))
    aiApi.insights(activeDataset.id).then((r) => setInsights(r.data.insights))
  }, [activeDataset])

  if (!activeDataset) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>Select a dataset from the top bar to get started.</p>
      </div>
    )
  }

  const allKpis = Object.values(kpis).flat()

  return (
    <div className="space-y-6">
      <NarrativeSummary datasetId={activeDataset.id} />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {allKpis.slice(0, 8).map((kpi) => (
          <div key={kpi.column} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <p className="text-xs text-gray-400 truncate">{kpi.column}</p>
            <p className="text-2xl font-bold text-white mt-1">{kpi.sum?.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">avg {kpi.mean?.toLocaleString()}</p>
          </div>
        ))}
      </div>

      {/* Auto Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(kpis).map(([tab, tabKpis]) =>
          tabKpis.slice(0, 1).map((kpi) => (
            <div key={`${tab}-${kpi.column}`} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">{tab} — {kpi.column}</h3>
              <PlotlyChart
                config={{
                  data: [{ x: ['Min', 'Mean', 'Max'], y: [kpi.min, kpi.mean, kpi.max], type: 'bar' }],
                  layout: { height: 200 }
                }}
              />
            </div>
          ))
        )}
      </div>

      {/* Insights */}
      {insights.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Auto-Detected Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.map((ins, i) => <InsightCard key={i} insight={ins} />)}
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/ExecutiveDashboard/ frontend/src/components/ai/
git commit -m "feat: add Executive Dashboard with KPI cards, AI narrative, insights"
```

---

## Phase 6 — Analyst Workbench + AI Chat + Data Sources

### Task 16: Analyst Workbench

**Files:**
- Create: `frontend/src/pages/AnalystWorkbench/index.tsx`
- Create: `frontend/src/components/filters/FilterBar.tsx`

- [ ] **Step 1: Create `frontend/src/components/filters/FilterBar.tsx`**

```tsx
import { useAppStore } from '../../store/useAppStore'

interface FilterBarProps {
  onTabChange: (tab: string) => void
  onChartTypeChange: (type: string) => void
  selectedTab: string
  chartType: string
}

export function FilterBar({ onTabChange, onChartTypeChange, selectedTab, chartType }: FilterBarProps) {
  const { activeDataset } = useAppStore()
  const chartTypes = ['bar', 'line', 'scatter', 'pie', 'histogram']

  return (
    <div className="flex flex-wrap gap-3 p-4 bg-gray-800 rounded-xl border border-gray-700">
      <div>
        <label className="text-xs text-gray-400 block mb-1">Sheet</label>
        <select className="bg-gray-700 text-gray-200 text-sm rounded px-2 py-1.5"
          value={selectedTab} onChange={(e) => onTabChange(e.target.value)}>
          {activeDataset?.tabNames.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      <div>
        <label className="text-xs text-gray-400 block mb-1">Chart Type</label>
        <select className="bg-gray-700 text-gray-200 text-sm rounded px-2 py-1.5"
          value={chartType} onChange={(e) => onChartTypeChange(e.target.value)}>
          {chartTypes.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create `frontend/src/pages/AnalystWorkbench/index.tsx`**

```tsx
import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { analyticsApi } from '../../services/api'
import { FilterBar } from '../../components/filters/FilterBar'
import { PlotlyChart } from '../../components/charts/PlotlyChart'
import { DataGrid } from '../../components/tables/DataGrid'

export function AnalystWorkbench() {
  const { activeDataset } = useAppStore()
  const [selectedTab, setSelectedTab] = useState('')
  const [chartType, setChartType] = useState('bar')
  const [stats, setStats] = useState<Record<string, any>>({})
  const [chartConfig, setChartConfig] = useState<any>(null)
  const [columns, setColumns] = useState<string[]>([])
  const [xCol, setXCol] = useState('')
  const [yCol, setYCol] = useState('')

  useEffect(() => {
    if (activeDataset?.tabNames.length) {
      setSelectedTab(activeDataset.tabNames[0])
    }
  }, [activeDataset])

  useEffect(() => {
    if (!activeDataset || !selectedTab) return
    analyticsApi.stats(activeDataset.id, selectedTab).then((r) => {
      setStats(r.data)
      const cols = Object.keys(r.data)
      setColumns(cols)
      setXCol(cols[0] ?? '')
      setYCol(cols[1] ?? cols[0] ?? '')
    })
  }, [activeDataset, selectedTab])

  const buildChart = () => {
    if (!activeDataset || !xCol) return
    analyticsApi.chart(activeDataset.id, { tab: selectedTab, chartType, x: xCol, y: yCol })
      .then((r) => setChartConfig(r.data))
  }

  if (!activeDataset) return (
    <div className="flex items-center justify-center h-full text-gray-500">
      <p>Select a dataset to explore.</p>
    </div>
  )

  const statsRows = Object.entries(stats).map(([col, vals]: any) => ({ column: col, ...vals }))

  return (
    <div className="space-y-5">
      <FilterBar onTabChange={setSelectedTab} onChartTypeChange={setChartType}
        selectedTab={selectedTab} chartType={chartType} />

      <div className="grid grid-cols-3 gap-3 bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div>
          <label className="text-xs text-gray-400 block mb-1">X Axis</label>
          <select className="bg-gray-700 text-gray-200 text-sm rounded px-2 py-1.5 w-full"
            value={xCol} onChange={(e) => setXCol(e.target.value)}>
            {columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Y Axis</label>
          <select className="bg-gray-700 text-gray-200 text-sm rounded px-2 py-1.5 w-full"
            value={yCol} onChange={(e) => setYCol(e.target.value)}>
            {columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="flex items-end">
          <button onClick={buildChart}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-1.5 rounded-lg">
            Generate Chart
          </button>
        </div>
      </div>

      {chartConfig && (
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700" style={{ height: 400 }}>
          <PlotlyChart config={chartConfig} />
        </div>
      )}

      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Column Statistics</h3>
        <DataGrid rows={statsRows} height={300} />
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/AnalystWorkbench/ frontend/src/components/filters/
git commit -m "feat: add Analyst Workbench with interactive charts and stats table"
```

---

### Task 17: AI Chat page

**Files:**
- Create: `frontend/src/hooks/useWebSocket.ts`
- Create: `frontend/src/components/ai/ChatPanel.tsx`
- Create: `frontend/src/pages/AIChat/index.tsx`

- [ ] **Step 1: Create `frontend/src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url: string | null, onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!url) return
    const socket = new WebSocket(url)
    ws.current = socket
    socket.onmessage = (e) => onMessage(JSON.parse(e.data))
    socket.onerror = () => onMessage({ type: 'error', message: 'WebSocket connection error' })
    return () => socket.close()
  }, [url])

  const send = useCallback((data: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  return { send }
}
```

- [ ] **Step 2: Create `frontend/src/pages/AIChat/index.tsx`**

```tsx
import { useState, useRef, useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'
import { PlotlyChart } from '../../components/charts/PlotlyChart'
import { Send, Bot, User } from 'lucide-react'
import { v4 as uuidv4 } from 'uuid'

export function AIChat() {
  const { activeDataset, chatMessages, addChatMessage, clearChat } = useAppStore()
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const wsUrl = activeDataset
    ? `${import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'}/ws/chat/${activeDataset.id}`
    : null

  const { send } = useWebSocket(wsUrl, (data) => {
    if (data.type === 'thinking') { setThinking(true); return }
    setThinking(false)
    if (data.type === 'result' || data.type === 'error') {
      addChatMessage({
        id: uuidv4(),
        role: 'assistant',
        content: data.answer ?? data.message ?? 'Sorry, I could not process that.',
        chartConfig: data.type === 'result' && data.answer && typeof data.answer === 'object' && !Array.isArray(data.answer) ? data.answer : undefined,
        timestamp: new Date().toISOString(),
      })
    }
  })

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [chatMessages, thinking])

  const sendMessage = () => {
    if (!input.trim() || !activeDataset) return
    addChatMessage({ id: uuidv4(), role: 'user', content: input, timestamp: new Date().toISOString() })
    send({ question: input })
    setInput('')
  }

  if (!activeDataset) return (
    <div className="flex items-center justify-center h-full text-gray-500">
      <p>Select a dataset to start chatting.</p>
    </div>
  )

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-gray-300">Chat with <span className="text-blue-400">{activeDataset.name}</span></h2>
        <button onClick={clearChat} className="text-xs text-gray-500 hover:text-gray-300">Clear</button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {chatMessages.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-12">
            <Bot size={32} className="mx-auto mb-3 text-gray-600" />
            <p>Ask anything about your data.</p>
            <p className="text-xs mt-1">e.g. "Show me monthly revenue trends" or "Which category has the most outliers?"</p>
          </div>
        )}
        {chatMessages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'}`}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={`max-w-2xl ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-800 border border-gray-700'} rounded-xl px-4 py-3`}>
              <p className="text-sm text-gray-100">{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</p>
              {msg.chartConfig && (
                <div className="mt-3" style={{ height: 300 }}>
                  <PlotlyChart config={msg.chartConfig as any} />
                </div>
              )}
            </div>
          </div>
        ))}
        {thinking && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center"><Bot size={14} /></div>
            <div className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => <span key={i} className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-4 flex gap-2">
        <input
          className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          placeholder="Ask a question about your data..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage} disabled={!input.trim() || thinking}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 rounded-xl transition-colors">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/AIChat/ frontend/src/hooks/useWebSocket.ts
git commit -m "feat: add AI Chat page with WebSocket streaming and inline Plotly charts"
```

---

### Task 18: Data Sources page

**Files:**
- Create: `frontend/src/pages/DataSources/index.tsx`
- Create: `frontend/src/hooks/useDataset.ts`

- [ ] **Step 1: Create `frontend/src/hooks/useDataset.ts`**

```typescript
import { useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'
import { datasetsApi } from '../services/api'

export function useDataset() {
  const { datasets, setDatasets, setActiveDataset, activeDataset } = useAppStore()

  const refresh = () => {
    datasetsApi.list().then((r) => setDatasets(r.data))
  }

  useEffect(() => { refresh() }, [])

  const upload = async (file: File) => {
    await datasetsApi.upload(file)
    refresh()
  }

  const remove = async (id: string) => {
    await datasetsApi.delete(id)
    if (activeDataset?.id === id) setActiveDataset(null)
    refresh()
  }

  return { datasets, upload, remove, refresh }
}
```

- [ ] **Step 2: Create `frontend/src/pages/DataSources/index.tsx`**

```tsx
import { useCallback } from 'react'
import { useDataset } from '../../hooks/useDataset'
import { Upload, Trash2, FileSpreadsheet } from 'lucide-react'

export function DataSources() {
  const { datasets, upload, remove } = useDataset()

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file?.name.endsWith('.xlsx')) upload(file)
  }, [upload])

  const onFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) upload(file)
  }

  return (
    <div className="space-y-6">
      <div
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
        onClick={() => document.getElementById('file-input')?.click()}>
        <Upload size={32} className="mx-auto text-gray-500 mb-3" />
        <p className="text-gray-400 text-sm">Drag & drop an Excel file, or click to browse</p>
        <p className="text-gray-600 text-xs mt-1">.xlsx only, max 50MB</p>
        <input id="file-input" type="file" accept=".xlsx" className="hidden" onChange={onFileInput} />
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Uploaded Datasets ({datasets.length})</h3>
        <div className="space-y-2">
          {datasets.map((ds) => (
            <div key={ds.id} className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3">
              <FileSpreadsheet size={18} className="text-green-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-200 truncate">{ds.name}</p>
                <p className="text-xs text-gray-500">{ds.tabNames.length} sheet(s) · {ds.createdAt?.slice(0, 10)}</p>
              </div>
              <button onClick={() => remove(ds.id)} className="text-gray-600 hover:text-red-400 transition-colors">
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          {!datasets.length && <p className="text-gray-600 text-sm">No datasets yet.</p>}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/DataSources/ frontend/src/hooks/useDataset.ts
git commit -m "feat: add Data Sources page with drag-and-drop upload"
```

---

### Task 19: End-to-end smoke test + Docker verify

**Files:**
- Create: `frontend/tests/e2e/upload-and-chat.spec.ts`

- [ ] **Step 1: Write E2E test**

```typescript
// frontend/tests/e2e/upload-and-chat.spec.ts
import { test, expect } from '@playwright/test'
import path from 'path'

test('upload Excel file and see Executive Dashboard', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await page.click('text=Data Sources')
  const fileInput = page.locator('#file-input')
  await fileInput.setInputFiles(path.join(__dirname, 'fixtures/sample.xlsx'))
  await expect(page.locator('text=sheet(s)')).toBeVisible({ timeout: 15000 })
})

test('navigate to Executive Dashboard and see KPI cards', async ({ page }) => {
  await page.goto('http://localhost:5173/executive')
  // With no dataset selected, shows empty state
  await expect(page.locator('text=Select a dataset')).toBeVisible()
})

test('AI Chat shows empty state without dataset', async ({ page }) => {
  await page.goto('http://localhost:5173/chat')
  await expect(page.locator('text=Select a dataset to start chatting')).toBeVisible()
})
```

- [ ] **Step 2: Create `frontend/tests/e2e/fixtures/sample.xlsx` for tests**

Create a minimal test fixture:
```bash
cd frontend/tests/e2e && mkdir -p fixtures
```
Then add a minimal `sample.xlsx` (2 tabs, a few rows) via Python:
```bash
python3 -c "
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'Sales'
ws.append(['Month', 'Revenue'])
ws.append(['Jan', 1000])
ws.append(['Feb', 2000])
wb.save('frontend/tests/e2e/fixtures/sample.xlsx')
"
```

- [ ] **Step 3: Verify Docker Compose builds and starts all services**

```bash
docker compose build
docker compose up -d
docker compose ps
```
Expected: All 5 services (frontend, backend, worker, postgres, redis) show `running`.

- [ ] **Step 4: Run E2E tests against running stack**

```bash
cd frontend && npx playwright test tests/e2e/
```

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "feat: complete PulseAI — E2E tests, Docker verified, all features implemented"
```

---

## Summary

| Phase | Tasks | Output |
|---|---|---|
| 1 | 1–3 | Docker Compose + FastAPI scaffold + React scaffold |
| 2 | 4–6 | Excel parser + schema detector + relationship finder |
| 3 | 7–8 | Stats engine + KPI extractor + chart builder |
| 4 | 9–12 | LLM factory + PandasAI agent + narrative + all API routes |
| 5 | 13–15 | Layout + charts + Executive Dashboard |
| 6 | 16–19 | Analyst Workbench + AI Chat + Data Sources + E2E |
