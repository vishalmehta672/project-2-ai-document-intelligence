# AI Document Intelligence System

## Overview

This project is an AI-powered document processing pipeline that extracts structured information from uploaded documents (such as invoices) using LLMs.

The system processes documents asynchronously using background workers and stores extracted data in a database for later querying and analytics.

---

## System Architecture

```
                ┌───────────────┐
                │     User      │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   FastAPI     │
                │  Upload API   │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   Redis Queue │
                │ (Task Broker) │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Celery Worker │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ PDF Parser    │
                │ (PyMuPDF)     │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ LLM Extraction│
                │ (OpenAI API)  │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ PostgreSQL DB │
                │ Structured    │
                │ Invoice Data  │
                └───────────────┘
```

---

## Processing Flow

1. User uploads a document through the FastAPI endpoint.
2. The API sends a processing task to the Redis queue.
3. A Celery worker picks up the task.
4. The worker parses the PDF and extracts raw text.
5. The extracted text is sent to an LLM for structured data extraction.
6. The extracted structured data is stored in PostgreSQL.
7. Users can query processed documents through API endpoints.

---

## Tech Stack

**Backend**

* FastAPI
* Python

**Async Processing**

* Redis
* Celery

**AI Layer**

* OpenAI API

**Document Processing**

* PyMuPDF

**Database**

* PostgreSQL

**Infrastructure**

* Docker
* GitHub Actions (CI/CD)
