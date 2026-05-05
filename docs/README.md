# AI College ROI Advisor (Restart)

This project rebuilds the ROI advisor with a clean backend, cached data access, and an unchanged frontend UI.

## Structure

- frontend/ - UI (copied from Website-Backup with no visual changes)
- backend/ - API, services, ingestion, and database models
- data/ - SQLite database file (default)
- vector_db/ - Chroma vector store

## Quick Start

1) Create and activate a Python environment.
2) Install backend dependencies:

```
pip install -r requirements.txt
```

3) Initialize the database schema:

```
sqlite3 data/universities.db < backend/database/schema.sql
```

4) Start the backend:

```
python -m backend.app
```

5) Install frontend dependencies and run UI:

```
npm install
npm run dev
```

## Environment Variables

See .env for defaults:

- OPENAI_API_KEY
- OPENAI_MODEL (default gpt-5.2)
- DATABASE_URL (default SQLite)
- REDIS_URL
- COLLEGE_SCORECARD_API_KEY
- COST_OF_LIVING_PATH (optional CSV from datasets/cost-of-living)

## Ingestion Pipelines

- ROR import:
  - Download ror-data.json.zip
  - Run: `python -m backend.ingestion.ror_importer path/to/ror-data.json.zip`

- College Scorecard import:
  - Set COLLEGE_SCORECARD_API_KEY
  - Run: `python -m backend.ingestion.scorecard_importer`

- RAG ingestion:
  - Put .txt files in a folder
  - Run: `python -m backend.ingestion.rag_ingestion path/to/folder`

## Sprint Tests

Sprint 1: Chat system
- Prompt: "Is college worth it?"
- Expect <3s response

Sprint 2: Resolver
- Inputs: NJIT, Rutgers NB, Rutgers-New Brunswick
- Expect correct matches via aliases/fuzzy matching

Sprint 3: Tuition database
- Ensure Scorecard data is loaded
- Query: /api/chat with a university name

Sprint 4: Redis cache
- First request ~300ms, second <50ms

Sprint 5: Graph system
- Ask: "Compare NJIT vs Rutgers"
- Expect chart in UI

Sprint 6: RAG knowledge
- Ask: "What scholarships does Rutgers offer?"
- Expect answer referencing RAG context

Sprint 7: ROI engine
- Ask: "Compare three universities"
- Expect ROI ranking
