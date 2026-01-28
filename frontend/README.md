# Frontend Dashboard

A lightweight HTML/CSS/JS dashboard that reads campaign finance committee data from the FastAPI backend (Postgres-backed) and displays:

- Top committees by receipts for a given cycle
- Committee search by name
- Click-to-view committee totals (receipts, disbursements, cash on hand, debt)

## Tech
- Vanilla HTML/CSS/JS (no framework)
- Fetch API for requests
- Designed to deploy as static files (GitHub Pages / Netlify)

---

## Requirements
- Backend running locally (Hour 4)
- Database populated (Hour 3 ingestion)

---

## Run locally

### 1) Start the backend API (Terminal A)
From the repo root:

```bash
uvicorn backend.src.api:app --reload --port 8000

