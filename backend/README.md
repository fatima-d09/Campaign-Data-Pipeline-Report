# Backend API – Campaign Data Pipeline

This backend service ingests public campaign finance data from the Federal Election Commission (FEC) API, stores normalized results in PostgreSQL, and exposes a REST API for reporting and dashboards.

## Stack
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Docker (local DB)
- FEC Public API

---

## Architecture Overview
FEC API
↓
Ingestion Pipeline (Python)
↓
PostgreSQL
↓
FastAPI REST Endpoints
↓
Frontend Dashboard (HTML/CSS/JS)

---

## Prerequisites
- Python 3.11+
- Docker + Docker Compose
- FEC API key (free)

---

## Environment Variables

Create a local `.env` file in `backend/` (do not commit this file):

```env
FEC_API_KEY=your_fec_api_key
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/campaign_db

