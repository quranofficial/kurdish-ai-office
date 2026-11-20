# Kurdish AI Office — Professional Edition

A Sorani-first AI Office with a web dashboard, 16 specialist agents, and a Telegram webhook integration.

## Included

- 16-agent catalog: CEO, Manager, Supervisor, Research, Analyst, Fact Checker, Writer, Translator, Secretary, Sales, Customer Support, Marketing, Finance, Developer, QA, and Automation.
- Sorani-aware keyword routing and per-agent instructions.
- Web dashboard served by FastAPI at `/`.
- AI chat endpoint using the OpenAI Responses API.
- Telegram webhook endpoint with Telegram's secret-token header validation.
- Task creation endpoint with a human-approval state for sensitive requests.
- GitHub Actions tests.

**Important limits:** AI replies are generated text, not autonomous external actions. The assistant cannot send emails, publish posts, edit external files, or make payments. Task records require the Supabase migration and credentials. The Telegram bot needs a bot token, webhook secret, a deployed HTTPS URL, and webhook registration.

## Stack

- Python 3.12, FastAPI, Vercel Python runtime
- OpenAI Responses API
- Supabase PostgreSQL
- python-telegram-bot
- GitHub Actions

## Deploy on Vercel

1. Import this GitHub repository into Vercel.
2. Set the server-side environment variables listed below in Vercel Project Settings.
3. Deploy. The root `index.py` exports the FastAPI app; `.python-version` pins Python 3.12.
4. The dashboard is served at the deployed root URL.

Vercel functions have execution limits. This deployment serves HTTP requests; persistent background workers and long-running jobs require a separate worker/queue service.

## Environment variables

Set secrets only in the server/deployment environment. Never commit real values.

- `OPENAI_API_KEY` — required for AI replies.
- `OPENAI_MODEL` — defaults to `gpt-6.2-sol`.
- `OFFICE_API_KEY` — protects dashboard AI/task endpoints; use a long random value.
- `TELEGRAM_BOT_TOKEN` — required for Telegram.
- `TELEGRAM_WEBHOOK_SECRET` — random secret used to authenticate Telegram webhook requests.
- `PUBLIC_APP_URL` — deployed HTTPS base URL, used only by the webhook registration script.
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` — required for persistent task records.

## Telegram setup

1. Create a bot with Telegram's BotFather and set `TELEGRAM_BOT_TOKEN` in Vercel.
2. Generate a strong webhook secret using letters, numbers, underscores, and hyphens; set it as `TELEGRAM_WEBHOOK_SECRET`.
3. Set `PUBLIC_APP_URL` to the deployed HTTPS Vercel URL.
4. With the same variables available locally, run `python scripts/set_telegram_webhook.py` once after deployment. It registers `/api/v1/telegram/webhook` with Telegram.
5. Send a message to the bot. It routes the message to a specialist agent and replies.

The webhook endpoint validates Telegram's `X-Telegram-Bot-Api-Secret-Token` header. Do not expose the bot token or webhook secret in browser code or GitHub.

## API

- `GET /` — web dashboard.
- `GET /health` — service/configuration status; no secret values are returned.
- `GET /api/v1/agents` — public catalog of 16 agents.
- `POST /api/v1/assistant/respond` — AI response; requires `Authorization: Bearer <OFFICE_API_KEY>`.
- `POST /api/v1/tasks` — creates a queued Supabase task; requires the same office key and database setup.
- `POST /api/v1/telegram/webhook` — Telegram webhook; requires the configured Telegram secret-token header.

For the web AI chat, enter `OFFICE_API_KEY` in the dashboard's key field. The key is held in page memory only and is not stored by the app.

## Supabase setup

Run `supabase/migrations/0001_initial_schema.sql` in the Supabase SQL Editor only after reviewing it. It creates the core tables and seeds the 16 agent records. Row Level Security is enabled; the server-side `service_role` receives table grants. Never put that key in the browser.

If the project's Data API does not expose the tables, check Supabase's Data API exposed-schema settings.

## Local setup

1. Copy `.env.example` to `.env` and fill in server-side values.
2. Create a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run: `uvicorn app.main:app --reload`.
5. Open `http://127.0.0.1:8000`.

## Safety

- AI and task endpoints stay locked when `OFFICE_API_KEY` is absent.
- OpenAI, Supabase, Telegram, and office keys are server-side only.
- The assistant has no external-action tools. Sensitive requests require human approval and a separately authorized integration.
- Do not enable browser access to office tables until authenticated-user ownership and matching RLS policies exist.
