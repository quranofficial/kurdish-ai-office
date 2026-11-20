# Architecture

```text
Web Dashboard (future) ─┐
                        ├── FastAPI backend ── Supabase PostgreSQL
Telegram Bot (future) ──┘          │
                                   ├── Agent registry (16 specialists)
                                   ├── Deterministic task router
                                   ├── Task/approval service
                                   └── LLM execution adapter (future)
```

Both clients will use the same backend and authorization rules. The browser must never receive server secrets.

## Agent routing

The registry defines 16 agents. The current router uses deterministic keyword matching to select a specialist. Requests without a clear specialist match go to the AI Manager for triage. This is a safe initial routing layer, not autonomous reasoning.

## Task lifecycle

- Ordinary tasks are stored as `queued`.
- Sensitive actions are stored as `waiting_approval`.
- This phase does not execute tasks or contact external services.
- Later execution workers must claim queued tasks, record agent runs, and persist results.

## Security boundaries

- `OFFICE_API_KEY` protects task creation until user authentication is implemented.
- Supabase service-role credentials stay server-side.
- RLS is enabled for all office tables; no anonymous/authenticated browser policies are added.
- Payments, outbound messages, publishing, deletion, and other high-impact operations require explicit human approval.
