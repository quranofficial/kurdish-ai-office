-- Kurdish AI Office: initial data model.
-- Apply through Supabase SQL Editor. RLS is enabled; add policies as auth flows are implemented.

create extension if not exists pgcrypto;

create table if not exists public.office_agents (
    id uuid primary key default gen_random_uuid(),
    agent_key text not null unique,
    name text not null,
    department text not null,
    role_description text not null default '',
    status text not null default 'idle'
        check (status in ('idle','working','paused','error')),
    is_enabled boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.office_tasks (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    description text not null default '',
    status text not null default 'queued'
        check (status in ('queued','assigned','in_progress','waiting_approval','completed','failed','cancelled')),
    priority text not null default 'normal'
        check (priority in ('low','normal','high','urgent')),
    created_by uuid,
    assigned_agent_id uuid references public.office_agents(id) on delete set null,
    result jsonb,
    requires_approval boolean not null default false,
    approved_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.office_activity_logs (
    id uuid primary key default gen_random_uuid(),
    actor_type text not null check (actor_type in ('user','agent','system')),
    actor_id text,
    action text not null,
    entity_type text,
    entity_id uuid,
    details jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists office_tasks_status_created_idx
    on public.office_tasks(status, created_at desc);
create index if not exists office_activity_created_idx
    on public.office_activity_logs(created_at desc);

alter table public.office_agents enable row level security;
alter table public.office_tasks enable row level security;
alter table public.office_activity_logs enable row level security;

-- No public policies are created in this foundation.
-- Add authenticated-user policies only after the user/auth model is finalized.
