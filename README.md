# Kurdish AI Office — Professional Edition

Starter foundation for a shared AI Office controlled from a web dashboard and Telegram.

## Stack
- Python 3.12 + FastAPI
- Supabase PostgreSQL (schema migration included)
- GitHub Actions CI
- Telegram and web clients will connect to the same API

## Local setup
1. Copy `.env.example` to `.env` and fill in values.
2. Create a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000/docs`

The API starts without Supabase credentials; database-backed features are intentionally not enabled until credentials are configured.

## Supabase
Run `supabase/migrations/0001_initial_schema.sql` in the Supabase SQL Editor.
Enable Row Level Security before exposing data to client applications. The service-role key must only be used server-side.

## Security
- Never commit `.env`.
- Do not put Supabase service-role keys or AI provider keys in browser code.
- External actions (sending email, payments, publishing, deleting data) must require explicit approval.
- This starter does not execute external actions yet.
