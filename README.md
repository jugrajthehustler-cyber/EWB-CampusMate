# Project 3 — CampusMate: AI Student Operations & Workflow Agent (Main Project)

## Overview
CampusMate brings together the CRUD API, the guarded local AI assistant, course analytics, event/audit logging, and an optional n8n webhook. It applies the class notes on modular FastAPI architecture, environment configuration, SQLAlchemy models/schemas, Ollama, JSON/webhooks, Docker volumes, and deployment fundamentals.

## Features
- Student CRUD API and filtering.
- `/ai/ask`: bounded, database-grounded questions with optional Ollama phrasing.
- `/analytics/summary`: total records and course-wise counts.
- `/workflow/events`: inspect recent student lifecycle events.
- Optional `N8N_WEBHOOK_URL`: send a small JSON event to an n8n webhook after student create/update/delete.
- Events are recorded locally even if the external webhook is not configured or unavailable.
- Optional Docker Compose file to run n8n locally with persistent volume storage.
- Unit/API tests.

## Setup API on Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Optional Ollama
Install Ollama, run `ollama pull llama3.2`, install `requirements-ai.txt`, set `OLLAMA_ENABLED=true` in `.env`, then restart the API. Without Ollama, the API and deterministic fact-based responses still work.

## Optional n8n workflow automation
1. Install Docker Desktop and start it.
2. From this folder, run `docker compose up -d`.
3. Open http://localhost:5678 and complete n8n's local setup.
4. In n8n, create a workflow with a **Webhook** trigger and activate it. Copy its Test/Production webhook URL as appropriate.
5. Set `N8N_WEBHOOK_URL` in `.env` to the URL reachable from the host, such as `http://127.0.0.1:5678/webhook/YOUR_PATH`.
6. Restart the FastAPI app. Create or update a fictional student and check `/workflow/events` and the n8n execution list.

Keep n8n bound to localhost for local learning; do not expose an unauthenticated workflow dashboard to the public internet. Webhook delivery failure does not roll back a completed student change.

## Docker Compose note
The compose file stores n8n state in a named Docker volume. This is the same persistent-volume concept covered in the course notes. `docker compose down` stops services; the volume remains unless explicitly removed.

## Tests
```powershell
python -m pytest -v
```

## Main endpoints
- Student endpoints: `POST/GET/PATCH/PUT/DELETE /students...`
- AI: `POST /ai/ask`
- Analytics: `GET /analytics/summary`
- Workflow event history: `GET /workflow/events`
- Health: `GET /health`

## Limitations and next enhancements
This is an educational local prototype. For real deployment, add authentication/authorization, rate limits, structured logging, database migrations, a durable asynchronous job queue, HTTPS and a properly configured reverse proxy. Do not store actual student PII in a public demo.


## Optional API container
The included `Dockerfile` packages the API. For local learning you can use the Python/venv instructions above. Before exposing a container outside localhost, add authentication, secrets management, HTTPS/reverse proxy, and appropriate network rules. The Docker Compose file in this project is for the n8n service only.
