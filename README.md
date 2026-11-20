# Kurdish AI Office — Professional Edition

Shared backend foundation for the Kurdish AI Office web dashboard and Telegram bot.

## Current phase

- 16-agent registry with specialist departments and Sorani-aware deterministic routing.
- Protected task-submission endpoint backed by Supabase.
- Human-approval gate for sensitive task requests.
- AI response endpoint using the OpenAI Responses API.
- Per-agent role instructions, same-language responses, and no external tools or side effects.
- GitHub Actions CI with unit tests.

**Current limitation:** the AI endpoint generates text responses only. It does not yet claim, persist, or execute queued Supabase tasks. Dashboard and Telegram integration are still upcoming.

## Stack

- Python 3.12 + FastAPI
- OpenAI Responses API
- Supabase PostgreSQL
- GitHub Actions

## Deployment (Vercel)

The FastAPI backend is configured for Vercel's native Python runtime:
- Root `index.py` exports the ASGI application.
- `.python-version` pins Python 3.12.
- `vercel.json` excludes tests and documentation from the function bundle.
- Connect this GitHub repository to a Vercel project, then add the server-side environment variables in Vercel Project Settings. Never place secrets in GitHub files or browser code.

Vercel's Python runtime supports FastAPI. Function execution limits apply, so this deployment is intended for the HTTP API; long-running background workers will need a separate queue/worker design.

## Local setup

1. Copy `.env.example` to `.env` and fill in server-side values.
2. Create a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000/docs`

The API starts without external credentials. The public agent catalog remains available. AI responses require `OPENAI_API_KEY` and `OFFICE_API_KEY`. Task creation additionally requires Supabase credentials and the schema migration.

## API

- `GET /health` — service/configuration status (does not expose secrets).
- `GET /api/v1/agents` — list the 16 registered agents.
- `POST /api/v1/assistant/respond` — generate an AI response with a selected or automatically routed agent.
- `POST /api/v1/tasks` — create a queued task in Supabase.

All write/AI endpoints require `Authorization: Bearer <OFFICE_API_KEY>`.

Example AI request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/assistant/respond \
  -H "Authorization: Bearer $OFFICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":"تکایە ئەم دەقە وەرگێڕە بۆ ئینگلیزی"}'
```

To select an agent explicitly, include `"agent_key":"translator"`. Valid keys are returned by `GET /api/v1/agents`.

## Supabase setup

Run `supabase/migrations/0001_initial_schema.sql` in the Supabase SQL Editor. This creates the core tables and seeds the 16 agent records. Row Level Security is enabled; only the server-side `service_role` receives table grants in this starter.

If the project uses Supabase Data API and the tables are not reachable through PostgREST, check the project's Data API exposed-schema settings. Do not expose the service-role key to a browser.

## Required secrets

Set these only in the server environment or deployment secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OFFICE_API_KEY` (use a long random value)
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (defaults to `gpt-6.2-sol`)
- `TELEGRAM_BOT_TOKEN` (for the later Telegram phase)

Never commit `.env` or put service-role/API keys in frontend code.

## Safety model

- AI and task endpoints remain locked when `OFFICE_API_KEY` is absent.
- OpenAI and Supabase keys are server-side only.
- The AI response service has no tools and cannot perform external actions.
- Sensitive task requests remain `waiting_approval`; this phase does not execute them.
- Do not enable browser access to office tables until an explicit authenticated-user ownership model and matching RLS policies exist.
