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


-- Agent registry fields and the initial 16 specialist employees.
alter table public.office_agents
    add column if not exists capabilities jsonb not null default '[]'::jsonb,
    add column if not exists system_prompt text not null default '';

insert into public.office_agents (agent_key, name, department, role_description, capabilities)
values
('ceo','AI CEO','Leadership','Sets office goals, priorities, and cross-team direction.','["strategy","prioritization","executive_summary"]'::jsonb),
('manager','AI Manager','Leadership','Breaks requests into tasks and coordinates specialist agents.','["planning","delegation","coordination"]'::jsonb),
('supervisor','AI Supervisor','Leadership','Monitors task progress, blockers, and delivery quality.','["monitoring","escalation","progress_review"]'::jsonb),
('research','Research Agent','Research','Finds and organizes evidence and source material.','["research","source_gathering","summarization"]'::jsonb),
('analyst','Analyst Agent','Research','Analyzes structured information, trends, and options.','["analysis","metrics","insights"]'::jsonb),
('fact_checker','Fact Checker','Quality','Checks factual claims, consistency, and evidence quality.','["verification","fact_checking","citation_review"]'::jsonb),
('writer','Writer Agent','Content','Drafts clear documents, posts, and business communications.','["writing","editing","copywriting"]'::jsonb),
('translator','Translator Agent','Content','Translates and localizes text while preserving meaning.','["translation","localization","proofreading"]'::jsonb),
('secretary','Secretary Agent','Operations','Organizes notes, agendas, minutes, and administrative records.','["summaries","meeting_notes","organization"]'::jsonb),
('sales','Sales Agent','Growth','Prepares sales research, outreach drafts, and lead follow-up plans.','["sales_research","lead_qualification","outreach_drafts"]'::jsonb),
('support','Customer Support Agent','Growth','Drafts customer responses and support knowledge articles.','["customer_support","response_drafting","triage"]'::jsonb),
('marketing','Marketing Agent','Growth','Plans campaigns, audiences, and marketing content.','["campaigns","social_content","positioning"]'::jsonb),
('finance','Finance Agent','Business','Organizes budgets, expense analysis, and financial summaries.','["budgeting","expense_analysis","financial_reporting"]'::jsonb),
('developer','Developer Agent','Engineering','Plans and implements software changes and integrations.','["software_design","coding","debugging"]'::jsonb),
('qa','QA Agent','Engineering','Creates test plans and checks software or process quality.','["testing","quality_assurance","test_planning"]'::jsonb),
('automation','Automation Agent','Engineering','Designs repeatable workflows and safe automations.','["workflow_design","automation","scheduling"]'::jsonb)
on conflict (agent_key) do update set
    name = excluded.name,
    department = excluded.department,
    role_description = excluded.role_description,
    capabilities = excluded.capabilities,
    updated_at = now();

-- The backend uses the service-role key only on the server. No browser roles
-- receive access here; RLS remains enabled on every office table.
grant all on table public.office_agents to service_role;
grant all on table public.office_tasks to service_role;
grant all on table public.office_activity_logs to service_role;

-- Keep updated_at accurate whenever an office record changes.
create or replace function public.set_office_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists office_agents_set_updated_at on public.office_agents;
create trigger office_agents_set_updated_at
before update on public.office_agents
for each row execute function public.set_office_updated_at();

drop trigger if exists office_tasks_set_updated_at on public.office_tasks;
create trigger office_tasks_set_updated_at
before update on public.office_tasks
for each row execute function public.set_office_updated_at();
