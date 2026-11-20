# Kurdish AI Office — Professional Edition

Shared backend foundation for the Kurdish AI Office web dashboard and Telegram bot.

## Current phase

- 16-agent registry with specialist departments and capabilities.
- Deterministic task routing to a specialist (or the AI Manager for triage).
- Protected task-submission endpoint.
- Human-approval gate for sensitive actions such as publishing, payments, sending messages, and deletion.
- Supabase schema for agents, tasks, and activity logs.
- GitHub Actions CI with unit tests.

**Important:** agents are registered and task routing is implemented, but LLM-powered task execution, the web dashboard, and Telegram bot are not implemented yet. Tasks are queued; no external action is executed by this starter.

## Stack

- Python 3.12 + FastAPI
- Supabase PostgreSQL
- GitHub Actions

## Local setup

1. Copy `.env.example` to `.env` and fill in the server-side values.
2. Create a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000/docs`

The API starts without database credentials. The public agent catalog remains available; task creation stays locked until both `OFFICE_API_KEY` and Supabase credentials are configured.

## API

- `GET /health` — service/configuration status (does not expose secrets).
- `GET /api/v1/agents` — list the 16 registered agents.
- `POST /api/v1/tasks` — create a queued task. Requires `Authorization: Bearer <OFFICE_API_KEY>`.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks \
  -H "Authorization: Bearer $OFFICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Translate this announcement into Kurdish","description":"Keep the tone formal."}'
```

## Supabase setup

Run `supabase/migrations/0001_initial_schema.sql` in the Supabase SQL Editor. This creates the core tables and seeds the 16 agent records. Row Level Security is enabled; only the server-side `service_role` receives table grants in this starter.

If the project uses Supabase Data API and the tables are not reachable through PostgREST, check the project's Data API exposed-schema settings. Do not solve this by exposing the service-role key to a browser.

## Required secrets

Set these only in the server environment or deployment secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OFFICE_API_KEY` (use a long random value)
- `OPENAI_API_KEY` (needed in a later phase for AI execution)
- `TELEGRAM_BOT_TOKEN` (needed in a later phase for Telegram)

Never commit `.env` or put service-role/API keys in frontend code.

## Safety model

- The task endpoint is locked when `OFFICE_API_KEY` is absent.
- The service-role key is used only by the backend.
- Sensitive actions are marked `waiting_approval`; this phase does not execute them.
- Do not enable browser access to office tables until an explicit authenticated-user ownership model and matching RLS policies exist.
