# Main Project Report — CampusMate AI Student Operations & Workflow Agent

**Program:** EWB AI/ML & Future AI Agents  
**Student:** [Your name]  
**GitHub repository:** [Your repository URL]  
**Status:** Run locally, capture genuine screenshots, and fill in your results before submission.

## 1. Problem statement
Student records often require repetitive create/update/delete actions, summaries, and follow-up workflows. CampusMate exposes student operations through an API, provides carefully constrained data questions, aggregates course statistics, and can send lifecycle events to an automation workflow.

## 2. Objectives
1. Build persistent CRUD endpoints using Python, FastAPI, SQLAlchemy and SQLite.
2. Separate configuration, schemas, models, database code, routes and services.
3. Validate requests and handle errors.
4. Provide deterministic, database-grounded answers with optional local Ollama language generation.
5. Record student lifecycle events and optionally notify n8n via a JSON webhook.
6. Demonstrate local containerized n8n persistence using Docker Compose.

## 3. Architecture
```text
Client / Swagger UI
        |
      FastAPI
   /     |      \
CRUD   AI Query   Analytics / Workflow Events
  |       |                |
SQLAlchemy query service   SQLite event log
  |       |                |
SQLite student records    Optional n8n webhook -> n8n workflow
          |
   Optional local Ollama (answer phrasing only)
```

## 4. Safety and trust boundaries
The AI component cannot execute unrestricted SQL. Supported question patterns are mapped to predefined ORM queries in Python. Only selected student fields (ID, name, date of birth, course) are supplied as AI context; contact details are excluded. If Ollama is disabled or unavailable, the backend returns a deterministic answer generated from retrieved records. Webhook delivery is optional and failure does not undo a successful student operation.

## 5. Main modules
- `app/config.py`: environment-driven typed settings.
- `app/database.py`: SQLAlchemy engine/session and table initialization.
- `app/models.py`: student and workflow-event table definitions.
- `app/schemas.py`: validated request and response types.
- `app/routes/`: isolated CRUD, AI, analytics and workflow endpoints.
- `app/services/ai_service.py`: allow-listed retrieval patterns and optional Ollama response generation.
- `app/services/workflow_service.py`: stores event history and delivers optional webhook notifications.
- `docker-compose.yml`: local n8n runtime with a persistent named volume.

## 6. API demonstration plan
1. Create two fictional students with different courses.
2. List and filter them using `/students`.
3. Ask `/ai/ask` how many students exist and ask for students born after a year.
4. Retrieve `/analytics/summary` and confirm course counts match the records.
5. Update and delete a student; inspect `/workflow/events`.
6. If Docker/n8n is configured, activate a webhook workflow and demonstrate a JSON event arriving in its execution history.

## 7. Test evidence
Run `python -m pytest -v`. Record the actual pass/fail count below after execution. Do not claim external Ollama/n8n integration was verified unless you ran those services.

**Local API test result:** [Fill in actual result]  
**Ollama integration result:** [Not configured / tested and result]  
**n8n integration result:** [Not configured / tested and result]

## 8. Deployment note
The class notes introduce domains, server ports, reverse proxies, Linux navigation and systemd. This package keeps the demo local. Public deployment should be a separate step with authentication, HTTPS, secrets management, a reverse proxy, firewall rules and a production database setup.
