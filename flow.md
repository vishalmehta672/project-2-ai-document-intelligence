                ┌──────────────┐
                │   User       │
                └──────┬───────┘
                       │
                       ▼
                FastAPI API
                       │
                       ▼
                Redis Queue
                       │
                       ▼
                Celery Worker
                       │
                       ▼
                 PDF Parser
                       │
                       ▼
                LLM Extraction
                       │
                       ▼
                 PostgreSQL
                       │
                       ▼
                 Query APIs