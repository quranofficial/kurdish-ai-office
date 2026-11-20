# Architecture

```text
Web Dashboard ─┐
               ├── FastAPI backend ── Supabase PostgreSQL
Telegram Bot ──┘          │
                          ├── AI provider adapter
                          ├── Task/approval service
                          └── Agent orchestration (future phase)
```

Both clients use the same backend and authorization rules. The browser never receives server secrets.
Agents are task workers with explicit capabilities; the manager plans and routes tasks.
High-impact actions remain in `waiting_approval` until an authorized human approves them.
